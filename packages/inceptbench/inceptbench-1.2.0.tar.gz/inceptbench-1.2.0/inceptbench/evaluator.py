"""
Unified Evaluator: Combines v3.py and edubench.py evaluators.
Single clean function that takes request + questions and runs both evaluations.
"""

import sys
import uuid
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from pydantic import BaseModel, ConfigDict
from typing import Any, List, Optional, Literal, Dict
import os
import json
import re
import requests
import asyncio
import anthropic
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add submodules to path
_submodules_base = Path(__file__).parent / "submodules"
_submodule_paths = [
    _submodules_base,  # For incept_core imports
    _submodules_base / "reading-question-qc",
    _submodules_base / "EduBench" / "code" / "evaluation",
    _submodules_base / "agentic-incept-reasoning",  # For utils imports
    _submodules_base / "agentic-incept-reasoning" / "src",  # For edu_agents imports
]

# Add all submodule paths to sys.path
for path in _submodule_paths:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Import from incept_core (extracted minimal files from incept-multilingual-generation)
from incept_core.evaluator.v3 import (
    call_single_shot_evaluator,
    build_single_shot_messages,
    EvaluationDimension,
    clip01
)
from incept_core.evaluator.llm_interface import simple_solve_with_llm
from incept_core.evaluator.edubench import verify_answer_with_gpt4, get_normal_answer
from evaluation import TASK_PROMPT_TEMPLATES
from qc_pipeline import QuestionQCAnalyzer

# Import evaluate_content using importlib to bypass package __init__.py files
# This avoids triggering the full dependency chain (tools, cairosvg, etc.)
def _import_evaluate_content():
    """Import evaluate_content directly without triggering package __init__.py files."""
    import importlib.util
    import sys

    try:
        # Get path to content_evaluator.py
        _agentic_src = Path(__file__).parent / "submodules" / "agentic-incept-reasoning" / "src"
        content_eval_path = _agentic_src / "edu_agents" / "eval" / "content_evaluator.py"

        if not content_eval_path.exists():
            return None

        # Create empty parent module namespaces to allow proper imports
        # This prevents triggering __init__.py files while allowing Pydantic to work
        if 'edu_agents' not in sys.modules:
            sys.modules['edu_agents'] = type(sys)('edu_agents')
        if 'edu_agents.core' not in sys.modules:
            sys.modules['edu_agents.core'] = type(sys)('edu_agents.core')
        if 'edu_agents.eval' not in sys.modules:
            sys.modules['edu_agents.eval'] = type(sys)('edu_agents.eval')

        # Load api_key_manager with proper module name
        api_key_path = _agentic_src / "edu_agents" / "core" / "api_key_manager.py"
        if api_key_path.exists() and 'edu_agents.core.api_key_manager' not in sys.modules:
            api_spec = importlib.util.spec_from_file_location("edu_agents.core.api_key_manager", api_key_path)
            if api_spec and api_spec.loader:
                api_module = importlib.util.module_from_spec(api_spec)
                sys.modules['edu_agents.core.api_key_manager'] = api_module
                api_spec.loader.exec_module(api_module)

        # Load content_evaluator with proper module name for Pydantic to work
        if 'edu_agents.eval.content_evaluator' not in sys.modules:
            spec = importlib.util.spec_from_file_location("edu_agents.eval.content_evaluator", content_eval_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules['edu_agents.eval.content_evaluator'] = module
                spec.loader.exec_module(module)

                # Rebuild Pydantic models after loading
                if hasattr(module, 'ComparisonResult'):
                    module.ComparisonResult.model_rebuild()
                if hasattr(module, 'PassFailResult'):
                    module.PassFailResult.model_rebuild()
                if hasattr(module, 'EvaluationResult'):
                    module.EvaluationResult.model_rebuild()

                return module.evaluate_content

        return sys.modules.get('edu_agents.eval.content_evaluator', {}).get('evaluate_content')

    except Exception:
        return None

evaluate_content = _import_evaluate_content()

class UniverslSkillInfoInput(BaseModel):
    title: str
    grade: str
    subject: str = "mathematics"
    difficulty: Optional[Literal["easy", "medium", "hard"]] = "medium"
    description: Optional[str] = None
    language: Literal['en', 'ar'] = 'en'

class UniversalGeneratedQuestionInput(BaseModel):
    id: str
    type: Literal["mcq", "fill-in"]  # MCQ and fill-in questions supported
    question: str
    answer: str
    answer_explanation: str
    answer_options: Optional[Dict[str, str]] = None  # Dict format for MCQ: {"A": "4 cm", "B": "0.4 cm", ...}
    skill: Optional[UniverslSkillInfoInput] = None
    image_url: Optional[str] = None
    additional_details: Optional[str] = None


class UniversalGeneratedTextInput(BaseModel):
    """
    Model for text/passage content (non-question formats)
    """
    id: str
    type: Literal["text", "passage", "explanation"]  # Text-based content types
    content: str  # Main text content
    title: Optional[str] = None  # Optional title
    skill: Optional[UniverslSkillInfoInput] = None
    image_url: Optional[str] = None
    additional_details: Optional[str] = None  # Context or metadata


class UniversalEvaluationRequest(BaseModel):
    # At least one of these must be provided
    generated_questions: Optional[List[UniversalGeneratedQuestionInput]] = None
    generated_content: Optional[List[UniversalGeneratedTextInput]] = None

    submodules_to_run: List[Literal["ti_question_qa", "answer_verification", "external_edubench", "reading_question_qc", "math_content_evaluator", "text_content_evaluator"]] = ["ti_question_qa", "answer_verification", "reading_question_qc", "math_content_evaluator"]
    verbose: bool = False  # If False, returns only overall scores per module

    def model_post_init(self, __context):
        """Validate that at least one content type is provided"""
        if not self.generated_questions and not self.generated_content:
            raise ValueError("At least one of 'generated_questions' or 'generated_content' must be provided")

        # Set defaults to empty lists if not provided
        if self.generated_questions is None:
            self.generated_questions = []
        if self.generated_content is None:
            self.generated_content = []

class EdubenchScores(BaseModel):
    qa_score: float
    ec_score: float
    ip_score: float
    ag_score: float
    qg_score: float
    tmg_score: float
    average_score: float


class InternalEvaluatorScores(BaseModel):
    correctness: float
    grade_alignment: float
    difficulty_alignment: float
    language_quality: float
    pedagogical_value: float
    explanation_quality: float
    instruction_adherence: float
    format_compliance: float
    query_relevance: float
    di_compliance: float


class DIScores(BaseModel):
    overall: float
    general_principles: float
    format_alignment: float
    grade_language: float


class SectionEvaluation(BaseModel):
    section_score: float
    issues: List[str]
    strengths: List[str]
    recommendation: str


class SectionEvaluations(BaseModel):
    question: SectionEvaluation
    scaffolding: SectionEvaluation


class InternalEvaluatorResult(BaseModel):
    scores: InternalEvaluatorScores
    issues: List[str]
    strengths: List[str]
    overall: float
    recommendation: str
    suggested_improvements: List[str]
    di_scores: DIScores
    section_evaluations: SectionEvaluations


class AnswerVerificationResult(BaseModel):
    is_correct: bool
    correct_answer: str
    confidence: int
    reasoning: str


class ReadingQuestionQCResult(BaseModel):
    overall_score: float
    distractor_checks: Dict[str, Any]
    question_checks: Dict[str, Any]
    passed: bool


# Simplified models for non-verbose mode
class SimplifiedInternalEvaluatorResult(BaseModel):
    overall: float


class SimplifiedAnswerVerificationResult(BaseModel):
    is_correct: bool


class SimplifiedEdubenchScores(BaseModel):
    average_score: float


class SimplifiedReadingQuestionQCResult(BaseModel):
    overall_score: float


class ContentEvaluatorResult(BaseModel):
    """Detailed content evaluation result"""
    overall_rating: str  # SUPERIOR, ACCEPTABLE, INFERIOR
    curriculum_alignment: str  # PASS or FAIL
    cognitive_demand: str
    accuracy_and_rigor: str
    image_quality: str
    reveals_misconceptions: str
    question_type_appropriateness: str
    engagement_and_relevance: str
    instructional_support: str
    clarity_and_accessibility: str
    pass_count: int
    fail_count: int
    overall_score: float  # 0-1 scale based on pass/fail ratio


class SimplifiedContentEvaluatorResult(BaseModel):
    """Simplified content evaluation result with just overall score"""
    overall_score: float


class TextContentEvaluatorResult(BaseModel):
    """Detailed text content pedagogical evaluation result using v3 dimensions"""
    correctness: float
    grade_alignment: float
    language_quality: float
    pedagogical_value: float
    explanation_quality: float
    di_compliance: float
    instruction_adherence: float
    query_relevance: float
    overall: float
    recommendation: str  # accept, revise, reject
    issues: List[str]
    strengths: List[str]
    suggested_improvements: List[str]
    di_scores: DIScores


class SimplifiedTextContentEvaluatorResult(BaseModel):
    """Simplified text content evaluation result with just overall score"""
    overall: float


class UniversalQuestionEvaluationScores(BaseModel):
    model_config = ConfigDict(
        # Exclude None values when serializing to JSON
        exclude_none=True
    )

    ti_question_qa: Optional[InternalEvaluatorResult | SimplifiedInternalEvaluatorResult] = None
    answer_verification: Optional[AnswerVerificationResult | SimplifiedAnswerVerificationResult] = None
    external_edubench: Optional[EdubenchScores | SimplifiedEdubenchScores] = None
    reading_question_qc: Optional[ReadingQuestionQCResult | SimplifiedReadingQuestionQCResult] = None
    math_content_evaluator: Optional[ContentEvaluatorResult | SimplifiedContentEvaluatorResult] = None
    text_content_evaluator: Optional[TextContentEvaluatorResult | SimplifiedTextContentEvaluatorResult] = None
    final_score: Optional[float] = None  # Combined score from all evaluations (0-1 scale)


class UniversalEvaluationResponse(BaseModel):
    request_id: str
    evaluations: Dict[str, UniversalQuestionEvaluationScores]
    evaluation_time_seconds: float

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def score_edubench_response_with_llm(task_type: str, response: str, prompt: str, question_context: Dict[str, Any] = None) -> float:
    """
    Score EduBench response using GPT-4 following EduBench's official evaluation methodology.

    Based on EduBench paper: https://arxiv.org/pdf/2505.16160
    Uses their 3 evaluation principles:
    1. Scenario Adaptability
    2. Factual & Reasoning Accuracy
    3. Pedagogical Application

    Args:
        task_type: The EduBench task type (QA, EC, IP, AG, QG, TMG)
        response: The model's response to evaluate
        prompt: The original prompt sent to the model

    Returns:
        Score from 0-10
    """
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        logger.warning("No OpenAI API key found, skipping LLM scoring")
        return 0.0

    # Build context information
    context_info = ""
    if question_context:
        if "question" in question_context:
            context_info += f"\nQuestion: {question_context['question']}"
        if "answer" in question_context:
            context_info += f"\nCorrect Answer: {question_context['answer']}"
        if "explanation" in question_context:
            context_info += f"\nExpected Explanation: {question_context['explanation'][:300]}"
        if "difficulty" in question_context:
            context_info += f"\nDifficulty Level: {question_context['difficulty']}"
        if "grade" in question_context:
            context_info += f"\nGrade Level: {question_context['grade']}"

    # EduBench official evaluation dimensions
    evaluation_prompt = f"""You are an expert evaluator following the EduBench evaluation methodology.

IMPORTANT: You are evaluating responses from EDU-Qwen2.5-7B, a 7B parameter model that tends to be:
- Verbose and repetitive (may repeat answers multiple times)
- Sometimes provides multiple JSON blocks instead of one
- May include extra explanations beyond what was asked
- May echo parts of the prompt in the response

DO NOT penalize these stylistic issues. Focus ONLY on the core educational content quality.

Evaluate the BEST interpretation of the response across these dimensions:

**1. Scenario Adaptability:**
- Instruction Following & Task Completion (did it accomplish the core task?)
- Role & Tone Consistency (appropriate educational tone?)
- Content Relevance & Scope Control (relevant to the question?)
- Scenario Element Integration (addresses the educational context?)

**2. Factual & Reasoning Accuracy:**
- Basic Factual Accuracy (is the core answer correct?)
- Domain Knowledge Accuracy (demonstrates subject understanding?)
- Reasoning Process Rigor (logical steps present?)
- Error Identification & Correction Precision (for EC tasks: correctly identifies issues?)

**3. Pedagogical Application:**
- Clarity, Simplicity & Inspiration (understandable despite verbosity?)
- Motivation, Guidance & Positive Feedback (supportive tone?)
- Personalization, Adaptation & Learning Support (helpful for learning?)
- Higher-Order Thinking & Skill Development (promotes understanding?)

**Context:**{context_info}

**Task Type:** {task_type}

**Prompt Sent to Model:**
{prompt}

**Model Response (may be verbose/repetitive):**
{response}

**Scoring Guidelines:**
Extract the BEST answer from the response (ignore repetitions). Score based on:
- 0-3: Factually wrong or completely missing the task
- 4-6: Partially correct but missing key elements or has significant errors
- 7-8: Correct and educationally sound despite verbosity
- 9-10: Excellent content with comprehensive, accurate pedagogical value

DO NOT deduct points for:
- Verbosity or repetition
- Multiple JSON blocks
- Extra explanations
- Formatting issues

DO deduct points for:
- Factual errors
- Missing required task elements
- Poor pedagogical approach
- Incorrect reasoning

Return ONLY a JSON object:
{{"score": <number 0-10>, "reasoning": "<brief explanation focusing on content quality>"}}"""

    try:
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }

        response_obj = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            timeout=270,
            json={
                "model": "gpt-5",
                "messages": [{"role": "user", "content": evaluation_prompt}]
            }
        )

        if response_obj.status_code == 200:
            content = response_obj.json()['choices'][0]['message']['content']
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                score = result.get('score', 0)
                logger.debug(f"{task_type} LLM score: {score}/10 - {result.get('reasoning', '')[:100]}")
                return float(score)

        logger.warning(f"Failed to get LLM score for {task_type}: {response_obj.status_code}")
        return 0.0

    except Exception as e:
        logger.error(f"Error scoring {task_type} with LLM: {e}")
        return 0.0

def _run_content_evaluation_task_sync(item_idx: int, item) -> Dict[str, Any]:
    """Synchronous wrapper for running content evaluation task.

    Accepts both UniversalGeneratedQuestionInput and UniversalGeneratedTextInput.
    """

    # Check if evaluate_content is available
    if evaluate_content is None:
        logger.warning(f"Content evaluator not available for item {item_idx} - skipping")
        return {
            'question_idx': item_idx,
            'result': None,
            'error': 'Content evaluator not available - edu_agents.eval.content_evaluator could not be imported'
        }

    async def _async_task():
        logger.debug(f"Running content evaluation for item {item_idx}")

        try:
            # Build content string based on item type
            content_parts = []

            # Check if this is a question or text content
            is_question = hasattr(item, 'question') and item.question is not None

            if is_question:
                # Question format
                content_parts = [
                    f"**Question:** {item.question}",
                    f"**Answer:** {item.answer}",
                ]

                if item.answer_explanation:
                    content_parts.append(f"**Explanation:** {item.answer_explanation}")

                if hasattr(item, 'answer_options') and item.answer_options:
                    options_str = "\n".join([f"{k}: {v}" for k, v in item.answer_options.items()])
                    content_parts.append(f"**Options:**\n{options_str}")
            else:
                # Text content format
                if hasattr(item, 'title') and item.title:
                    content_parts.append(f"**Title:** {item.title}")
                content_parts.append(f"**Content:** {item.content}")

            # Add common metadata
            if item.skill:
                content_parts.append(f"**Grade:** {item.skill.grade}")
                content_parts.append(f"**Subject:** {item.skill.subject}")
                if item.skill.difficulty:
                    content_parts.append(f"**Difficulty:** {item.skill.difficulty}")

            content = "\n\n".join(content_parts)

            # Evaluate content
            evaluation_json = await evaluate_content(content)

            # Parse the JSON response
            evaluation_data = json.loads(evaluation_json)

            return {
                'question_idx': item_idx,
                'result': evaluation_data
            }
        except Exception as e:
            logger.error(f"Error running content evaluation for item {item_idx}: {e}")
            return {
                'question_idx': item_idx,
                'result': None,
                'error': str(e)
            }

    # Run the async function in a new event loop
    return asyncio.run(_async_task())


def call_text_content_evaluator(text_content: UniversalGeneratedTextInput, total_items: int) -> Dict[str, Any]:
    """
    Evaluate text content using v3 evaluator's pedagogical dimensions.
    Adapted from call_single_shot_evaluator but for text/passage content.

    Returns normalized scores (0-1) across relevant dimensions:
    - CORRECTNESS: Factual accuracy of content
    - GRADE_ALIGNMENT: Appropriate for target grade level
    - LANGUAGE_QUALITY: Clarity, grammar, age-appropriate language
    - PEDAGOGICAL_VALUE: Educational impact and learning value
    - EXPLANATION_QUALITY: How well content explains concepts
    - DI_COMPLIANCE: Adherence to Direct Instruction principles
    - INSTRUCTION_ADHERENCE: Follows requirements/specifications
    - QUERY_RELEVANCE: Matches intended topic/skill
    """
    import time
    import json

    # Build evaluation messages for text content
    messages = _build_text_evaluation_messages(text_content, total_items)

    # Time the LLM call
    llm_start = time.time()

    # Use the same LLM interface as v3 evaluator
    data = simple_solve_with_llm(messages=messages)

    llm_time = time.time() - llm_start
    logger.debug(f"⏱️ Text content LLM evaluation call: {llm_time:.2f}s")

    # Normalize scores to 0..1 (same as v3)
    sr = data.get("scores", {})
    scores = {
        EvaluationDimension.CORRECTNESS: clip01(sr.get("correctness", 5) / 10.0),
        EvaluationDimension.GRADE_ALIGNMENT: clip01(sr.get("grade_alignment", 5) / 10.0),
        EvaluationDimension.LANGUAGE_QUALITY: clip01(sr.get("language_quality", 5) / 10.0),
        EvaluationDimension.PEDAGOGICAL_VALUE: clip01(sr.get("pedagogical_value", 5) / 10.0),
        EvaluationDimension.EXPLANATION_QUALITY: clip01(sr.get("explanation_quality", 5) / 10.0),
        EvaluationDimension.INSTRUCTION_ADHERENCE: clip01(sr.get("instruction_adherence", 5) / 10.0),
        EvaluationDimension.QUERY_RELEVANCE: clip01(sr.get("query_relevance", 5) / 10.0),
    }

    issues = list(data.get("issues", []))[:10]
    strengths = list(data.get("strengths", []))[:10]
    suggestions = list(data.get("suggested_improvements", []))[:10]
    recommendation = data.get("recommendation", "revise")
    if recommendation not in {"accept", "revise", "reject"}:
        recommendation = "revise"

    # Calculate overall score
    overall = sum(scores.values()) / max(1, len(scores))

    # DI scores
    di_scores_raw = data.get("di_scores", {}) or {}
    di_overall_raw = di_scores_raw.get("overall", sr.get("di_compliance", 5))
    di_scores = {
        "overall": clip01(float(di_overall_raw) / 10.0),
        "general_principles": clip01(float(di_scores_raw.get("general_principles", di_overall_raw)) / 10.0),
        "format_alignment": clip01(float(di_scores_raw.get("format_alignment", di_overall_raw)) / 10.0),
        "grade_language": clip01(float(di_scores_raw.get("grade_language", di_overall_raw)) / 10.0),
    }
    scores[EvaluationDimension.DI_COMPLIANCE] = di_scores["overall"]

    return {
        "scores": scores,
        "issues": issues,
        "strengths": strengths,
        "overall": overall,
        "recommendation": recommendation,
        "suggested_improvements": suggestions,
        "di_scores": di_scores,
        "section_evaluations": {
            "content": {
                "section_score": overall * 10.0,  # Convert back to 0-10 for consistency
                "issues": issues,
                "strengths": strengths,
                "recommendation": recommendation
            }
        }
    }


def _build_text_evaluation_messages(content: UniversalGeneratedTextInput, total_items: int) -> List[Dict[str, str]]:
    """
    Build LLM messages for evaluating text content (not questions).
    Adapted from build_single_shot_messages but focused on content evaluation.
    """
    from incept_core.direct_instruction.principles_constants import (
        DI_INDIVIDUAL_QUESTION_PRINCIPLES,
        DI_SCAFFOLDING_PRINCIPLES,
        GRADE_VOCABULARY_EXAMPLES_AR,
        GRADE_VOCABULARY_EXAMPLES_EN,
    )

    # Build request metadata
    req_meta = {
        "requested_grade": content.skill.grade if content.skill else None,
        "requested_language": content.skill.language if content.skill else "en",
        "content_type": content.type,
        "requested_difficulty": content.skill.difficulty if content.skill else "medium",
        "total_items": total_items,
        "topic": content.skill.title if content.skill else None,
        "subject": content.skill.subject if content.skill else "general",
        "additional_context": content.additional_details if content.additional_details else "",
    }

    language = str(req_meta.get("requested_language") or "english").lower()
    grade = req_meta.get("requested_grade")
    grade_examples = None
    if grade is not None:
        try:
            grade_key = f"Grade{int(grade)}"
            store = GRADE_VOCABULARY_EXAMPLES_AR if language.startswith("ar") else GRADE_VOCABULARY_EXAMPLES_EN
            grade_examples = store.get(grade_key)
        except Exception:
            grade_examples = None

    system = (
        "You are an expert educational content evaluator specializing in text-based educational materials. "
        "Your role is to assess the pedagogical value, accuracy, and appropriateness of educational text content.\n\n"
        "EVALUATION CONTEXT:\n"
        "You are evaluating TEXT CONTENT (passages, explanations, educational text) - NOT questions.\n"
        "Focus on content quality, educational value, and pedagogical effectiveness.\n\n"
        "KEY EVALUATION DIMENSIONS FOR TEXT CONTENT:\n\n"
        "1. **Correctness (0-10)**: Factual accuracy and reliability\n"
        "   - Are all facts, concepts, and examples accurate?\n"
        "   - Are there any misconceptions or errors?\n"
        "   - Is the information up-to-date and scientifically sound?\n\n"
        "2. **Grade Alignment (0-10)**: Age and grade appropriateness\n"
        "   - Is the complexity appropriate for the target grade?\n"
        "   - Are concepts introduced at the right developmental level?\n"
        "   - Are prior knowledge assumptions reasonable?\n\n"
        "3. **Language Quality (0-10)**: Clarity and linguistic appropriateness\n"
        "   - Is the language clear and grammatically correct?\n"
        "   - Is vocabulary appropriate for the grade level?\n"
        "   - Are sentences well-structured and easy to follow?\n\n"
        "4. **Pedagogical Value (0-10)**: Educational effectiveness\n"
        "   - Does the content promote meaningful learning?\n"
        "   - Are concepts explained in a way that builds understanding?\n"
        "   - Does it connect to real-world applications or prior knowledge?\n\n"
        "5. **Explanation Quality (0-10)**: How well concepts are explained\n"
        "   - Are explanations clear and well-structured?\n"
        "   - Does it use examples, analogies, or visuals effectively?\n"
        "   - Does it break down complex ideas into manageable parts?\n\n"
        "6. **DI Compliance (0-10)**: Direct Instruction principles\n"
        "   - Is the content structured and systematic?\n"
        "   - Does it follow explicit instruction principles?\n"
        "   - Is it appropriate for guided learning?\n\n"
        "7. **Instruction Adherence (0-10)**: Meets requirements\n"
        "   - Does content match the requested topic/subject?\n"
        "   - Is the length and depth appropriate?\n"
        "   - Does it follow any specified format or style?\n\n"
        "8. **Query Relevance (0-10)**: Topic alignment (VETO POWER)\n"
        "   - Does content directly address the intended topic?\n"
        "   - Is it focused and on-target?\n"
        "   - Score < 4.0 = AUTO-REJECT for off-topic content\n\n"
        "DIRECT INSTRUCTION (DI) EVALUATION:\n"
        "- Assess alignment with DI principles (clarity, structure, scaffolding)\n"
        "- Check for grade-appropriate language and vocabulary\n"
        "- Evaluate if content is suitable for explicit instruction\n\n"
        "RECOMMENDATION LOGIC:\n"
        "- REJECT if: query_relevance < 4.0 (off-topic), correctness < 4.0 (factually wrong), or major pedagogical issues\n"
        "- REVISE if: content is on-topic and accurate but needs improvement in clarity, structure, or pedagogical approach\n"
        "- ACCEPT if: content is accurate, on-topic, grade-appropriate, and pedagogically sound\n\n"
        "OUTPUT REQUIREMENTS:\n"
        "Return STRICT JSON with this schema:\n"
        "{\n"
        "  \"scores\": {\n"
        "    \"correctness\": 0-10,\n"
        "    \"grade_alignment\": 0-10,\n"
        "    \"language_quality\": 0-10,\n"
        "    \"pedagogical_value\": 0-10,\n"
        "    \"explanation_quality\": 0-10,\n"
        "    \"di_compliance\": 0-10,\n"
        "    \"instruction_adherence\": 0-10,\n"
        "    \"query_relevance\": 0-10\n"
        "  },\n"
        "  \"issues\": [string],\n"
        "  \"strengths\": [string],\n"
        "  \"suggested_improvements\": [string],\n"
        "  \"recommendation\": \"accept\" | \"revise\" | \"reject\",\n"
        "  \"di_scores\": {\n"
        "    \"overall\": 0-10,\n"
        "    \"general_principles\": 0-10,\n"
        "    \"format_alignment\": 0-10,\n"
        "    \"grade_language\": 0-10\n"
        "  }\n"
        "}"
    )

    user = {
        "content": {
            "type": content.type,
            "title": content.title if content.title else "Untitled",
            "text": content.content,
            "skill": content.skill.title if content.skill else None,
            "subject": content.skill.subject if content.skill else "general",
            "grade": content.skill.grade if content.skill else None,
            "difficulty": content.skill.difficulty if content.skill else "medium",
            "image_url": content.image_url if content.image_url else None,
        },
        "request_context": req_meta,
        "di_guidance": {
            "individual_principles": DI_INDIVIDUAL_QUESTION_PRINCIPLES.strip(),
            "scaffolding_principles": DI_SCAFFOLDING_PRINCIPLES.strip(),
            "grade_language_examples": grade_examples,
            "weighting": {
                "general_principles": 0.4,
                "format_alignment": 0.35,
                "grade_language": 0.25
            }
        },
        "evaluation_instructions": (
            "Evaluate this educational text content across all dimensions.\n"
            "Provide specific evidence for each score.\n"
            "Check factual accuracy carefully.\n"
            "Assess pedagogical effectiveness and grade appropriateness.\n"
            "Verify content matches the intended topic (query_relevance).\n"
            "Return ONLY valid JSON - no additional text."
        )
    }

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
    ]
    return messages


def _run_text_content_evaluator_task(item_idx: int, text_content: UniversalGeneratedTextInput, total_items: int) -> Dict[str, Any]:
    """
    Run text content pedagogical evaluation task.
    Evaluates text content for pedagogical value, DI alignment, and internal standards.
    """
    logger.debug(f"Running text content pedagogical evaluation for item {item_idx}")

    try:
        result_dict = call_text_content_evaluator(text_content, total_items)
        return {
            'question_idx': item_idx,
            'result': result_dict
        }
    except Exception as e:
        logger.error(f"Error running text content evaluation for item {item_idx}: {e}")
        return {
            'question_idx': item_idx,
            'result': None,
            'error': str(e)
        }


def _run_reading_qc_task_sync(question_idx: int, question: UniversalGeneratedQuestionInput, claude_api_key: str, openai_api_key: str = None, max_retries: int = 3) -> Dict[str, Any]:
    """Synchronous wrapper for running reading question QC analysis with retry logic."""

    async def _async_task():
        logger.debug(f"Running reading QC for question {question_idx}")

        # Initialize clients
        claude_client = anthropic.AsyncAnthropic(api_key=claude_api_key)
        openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

        try:
            # Create analyzer
            analyzer = QuestionQCAnalyzer(
                claude_client=claude_client,
                openai_client=openai_client,
                claude_model="claude-sonnet-4-5-20250929",
                openai_model="gpt-4o"
            )

            # Convert question to the format expected by QuestionQCAnalyzer
            question_item = {
                'question_id': question.id,
                'question_type': 'MCQ' if question.type == 'mcq' else 'MP',
                'passage_text': question.additional_details or '',
                'grade': int(question.skill.grade) if question.skill and question.skill.grade.isdigit() else 5,
                'structured_content': {
                    'question': question.question,
                    'choices': question.answer_options or {},
                    'correct_answer': question.answer,
                    'CCSS': question.skill.title if question.skill else '',
                    'CCSS_description': question.skill.description if question.skill else '',
                    'DOK': question.skill.difficulty if question.skill else 'medium'
                }
            }

            # Retry logic for API failures
            last_error = None
            for attempt in range(max_retries):
                try:
                    result = await analyzer.analyze_question(question_item, semaphore=None)
                    return_value = {
                        'question_idx': question_idx,
                        'result': result
                    }
                    break
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"Reading QC attempt {attempt + 1}/{max_retries} failed for question {question_idx}, retrying in {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Reading QC failed for question {question_idx} after {max_retries} attempts: {e}")
                        return_value = {
                            'question_idx': question_idx,
                            'result': None,
                            'error': str(e)
                        }
        finally:
            # Properly close clients before event loop teardown
            try:
                await claude_client.close()
                if openai_client:
                    await openai_client.close()
            except Exception as e:
                logger.debug(f"Error closing clients: {e}")

        return return_value

    # Run the async function in a new event loop
    return asyncio.run(_async_task())

def _run_edubench_task(question_idx: int, task_type: str, question: UniversalGeneratedQuestionInput) -> Dict[str, Any]:
    """Run single EduBench task - just returns raw response like batch_edubench."""
    logger.debug(f"Running {task_type} task for question {question_idx}")

    # Extract explanation - always present as required field
    detailed_explanation = question.answer_explanation

    # Build prompt based on task type
    if task_type == "QA":
        prompt = TASK_PROMPT_TEMPLATES["QA"](question.question)
    elif task_type == "EC":
        prompt = TASK_PROMPT_TEMPLATES["EC"](question.question, question.answer)
    elif task_type == "IP":
        base_prompt = TASK_PROMPT_TEMPLATES["IP"](question.question)
        prompt = f"{base_prompt}\n\nReference scaffolding (detailed step-by-step guidance):\n{detailed_explanation}"
    elif task_type == "AG":
        base_prompt = TASK_PROMPT_TEMPLATES["AG"](question.question, question.answer)
        prompt = f"{base_prompt}\n\nReference explanation:\n{detailed_explanation}"
    elif task_type == "QG":
        # Extract knowledge point from skill (optional field)
        if question.skill:
            knowledge_point = question.skill.title
            subject = question.skill.subject
            level = question.skill.difficulty
        else:
            # Fallback if no skill provided
            knowledge_point = question.question.split('.')[0] if '.' in question.question else question.question[:50]
            subject = "mathematics"
            level = "medium"

        question_type = question.type  # "mcq" or "fill-in"
        prompt = TASK_PROMPT_TEMPLATES["QG"](knowledge_point, subject, question_type, level)
    elif task_type == "TMG":
        # Extract knowledge point from skill (optional field)
        if question.skill:
            knowledge_point = question.skill.title
        else:
            # Fallback if no skill provided
            knowledge_point = "General educational content"

        base_prompt = TASK_PROMPT_TEMPLATES["TMG"](knowledge_point)
        prompt = f"{base_prompt}\n\nReference scaffolding example:\n{detailed_explanation}"
    else:
        prompt = ""

    response = get_normal_answer(prompt, 'EDU-Qwen2.5-7B')

    # an llm call to score the response
    evaluation = score_edubench_response_with_llm(task_type, response, prompt, question_context={
        "question": question.question,
        "answer": question.answer,
        "explanation": detailed_explanation,
        "difficulty": question.skill.difficulty if question.skill else "medium",
        "grade": question.skill.grade if question.skill else "unknown"
    })

    result = {
        "question_idx": question_idx,
        "task_type": task_type,
        "response": response,
        "evaluation": evaluation,
    }

    return result


def benchmark_parallel(request: UniversalEvaluationRequest, max_workers: int = 100) -> Dict[str, Any]:
    """
    Benchmark mode: Process all items (questions and content) in parallel for maximum throughput.

    Args:
        request: UniversalEvaluationRequest with questions and/or content
        max_workers: Number of parallel workers (default: 100)

    Returns:
        Dict with structure:
        {
            "request_id": str,
            "total_items": int,
            "successful": int,
            "failed": int,
            "scores": List[Dict] - one score per item,
            "failed_ids": List[str],
            "evaluation_time_seconds": float
        }
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())

    # Merge all items
    all_items = (request.generated_questions or []) + (request.generated_content or [])

    logger.info(f"🚀 Benchmark mode: Processing {len(all_items)} items ({len(request.generated_questions or [])} questions, {len(request.generated_content or [])} content) with {max_workers} workers")

    scores = []
    failed_ids = []

    def process_single_item(item):
        """Process a single item (question or content) and return result or error"""
        try:
            # Create a mini request with just this item
            # Determine if it's a question or content based on attributes
            is_question = hasattr(item, 'question') and item.question is not None

            if is_question:
                mini_request = UniversalEvaluationRequest(
                    submodules_to_run=request.submodules_to_run,
                    generated_questions=[item],
                    generated_content=[],
                    verbose=False  # Always use simplified mode for benchmarking
                )
            else:
                mini_request = UniversalEvaluationRequest(
                    submodules_to_run=request.submodules_to_run,
                    generated_questions=[],
                    generated_content=[item],
                    verbose=False  # Always use simplified mode for benchmarking
                )

            # Run evaluation
            response = universal_unified_benchmark(mini_request)

            # Extract the score
            if item.id in response.evaluations:
                eval_result = response.evaluations[item.id]

                # Convert Pydantic models to dicts for JSON serialization
                scores_dict = {}
                for module in request.submodules_to_run:
                    module_result = getattr(eval_result, module, None)
                    if module_result is not None:
                        # Convert Pydantic model to dict
                        scores_dict[module] = module_result.model_dump(exclude_none=True)
                    else:
                        scores_dict[module] = None

                return {
                    "id": item.id,
                    "success": True,
                    "final_score": eval_result.final_score,
                    "scores": scores_dict
                }
            else:
                return {
                    "id": item.id,
                    "success": False,
                    "error": "No evaluation result returned"
                }
        except Exception as e:
            logger.error(f"Failed to process item {item.id}: {e}")
            return {
                "id": item.id,
                "success": False,
                "error": str(e)
            }

    # Process all items in parallel with progress bar
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(
            executor.map(process_single_item, all_items),
            total=len(all_items),
            desc="Evaluating items"
        ))

    # Collect results
    for result in results:
        if result["success"]:
            scores.append({
                "id": result["id"],
                "final_score": result["final_score"],
                "scores": result["scores"]
            })
        else:
            failed_ids.append(result["id"])
            logger.warning(f"Question {result['id']} failed: {result.get('error', 'Unknown error')}")

    evaluation_time = time.time() - start_time

    logger.info(f"✅ Benchmark complete: {len(scores)}/{len(all_items)} successful in {evaluation_time:.2f}s")

    return {
        "request_id": request_id,
        "total_items": len(all_items),
        "total_questions": len(request.generated_questions or []),
        "total_content": len(request.generated_content or []),
        "successful": len(scores),
        "failed": len(failed_ids),
        "scores": scores,
        "failed_ids": failed_ids,
        "evaluation_time_seconds": evaluation_time,
        "avg_score": sum(s["final_score"] for s in scores) / len(scores) if scores else 0.0
    }


def universal_unified_benchmark(request: UniversalEvaluationRequest) -> UniversalEvaluationResponse:
    """
    Main entry point for universal evaluation.
    Processes both questions and text content, organizing results by item ID.
    """

    start_time = time.time()
    request_id = str(uuid.uuid4())

    # Merge questions and content into unified list with type tracking
    all_items = []
    for q in (request.generated_questions or []):
        all_items.append(('question', q))
    for c in (request.generated_content or []):
        all_items.append(('content', c))

    logger.info(f"Universal evaluation request {request_id} with {len(request.generated_questions or [])} questions and {len(request.generated_content or [])} text content items")

    modules_to_use = request.submodules_to_run
    evaluations = {}

    # Initialize evaluations for all items
    for item_type, item in all_items:
        evaluations[item.id] = UniversalQuestionEvaluationScores()

    # Run all enabled modules in parallel
    questions = request.generated_questions or []
    text_content = request.generated_content or []
    effective_edubench_tasks = ["QA", "EC", "IP", "AG", "QG", "TMG"]

    # Prepare storage for results
    edubench_task_results = []
    internal_eval_results = []
    verification_results = []
    reading_qc_results = []
    content_eval_results = []
    text_content_eval_results = []

    # Get API keys for reading QC
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Use conservative parallelism to avoid overwhelming APIs
    # answer_verification uses OpenAI, reading_qc/content use Anthropic
    max_workers = 5  # Reduced from 10 to avoid API overload
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        all_futures = []

        # Submit EduBench tasks if enabled (questions only)
        if "external_edubench" in modules_to_use and questions:
            logger.info(f"Submitting EduBench evaluation with {len(effective_edubench_tasks)} tasks for {len(questions)} questions")
            for i, q in enumerate(questions):
                for task_type in effective_edubench_tasks:
                    future = executor.submit(_run_edubench_task, i, task_type, q)
                    all_futures.append(('external_edubench', future))

        # Submit internal evaluator tasks if enabled (questions only for now)
        if "ti_question_qa" in modules_to_use and questions:
            logger.info(f"Submitting {len(questions)} internal evaluator tasks for questions")
            for i, q in enumerate(questions):
                future = executor.submit(call_single_shot_evaluator, q, len(questions))
                all_futures.append(('ti_question_qa', i, future))

        # Submit answer verification tasks if enabled (questions only - text has no answer)
        if "answer_verification" in modules_to_use and questions:
            logger.info(f"Submitting {len(questions)} answer verification tasks")
            for i, q in enumerate(questions):
                # For MCQ questions, resolve the answer choice to its actual text
                answer_to_verify = q.answer
                if q.type == "mcq" and q.answer_options and q.answer in q.answer_options:
                    answer_to_verify = q.answer_options[q.answer]
                    logger.debug(f"Q{i+1}: Resolved MCQ answer '{q.answer}' to '{answer_to_verify}'")

                future = executor.submit(verify_answer_with_gpt4, q.question, answer_to_verify, q.answer_explanation)
                all_futures.append(('answer_verification', i, future))

        # Submit reading QC tasks if enabled (questions only)
        if "reading_question_qc" in modules_to_use and questions:
            logger.info(f"Submitting {len(questions)} reading QC tasks")
            for i, q in enumerate(questions):
                future = executor.submit(_run_reading_qc_task_sync, i, q, claude_api_key, openai_api_key)
                all_futures.append(('reading_question_qc', i, future))

        # Submit content evaluation tasks if enabled
        # Works for both questions and text content
        if "math_content_evaluator" in modules_to_use:
            if questions:
                logger.info(f"Submitting {len(questions)} content evaluation tasks for questions")
                for i, q in enumerate(questions):
                    future = executor.submit(_run_content_evaluation_task_sync, i, q)
                    all_futures.append(('math_content_evaluator', i, future))
            if text_content:
                logger.info(f"Submitting {len(text_content)} content evaluation tasks for text")
                for i, c in enumerate(text_content):
                    # Offset index by number of questions to avoid collisions
                    idx = len(questions) + i
                    future = executor.submit(_run_content_evaluation_task_sync, idx, c)
                    all_futures.append(('math_content_evaluator', idx, future))

        # Submit text content pedagogical evaluator tasks if enabled (text content only)
        if "text_content_evaluator" in modules_to_use and text_content:
            logger.info(f"Submitting {len(text_content)} text content pedagogical evaluation tasks")
            total_items = len(all_items)
            for i, c in enumerate(text_content):
                # Offset index by number of questions to avoid collisions
                idx = len(questions) + i
                future = executor.submit(_run_text_content_evaluator_task, idx, c, total_items)
                all_futures.append(('text_content_evaluator', idx, future))

        # Collect all results with a single progress bar
        if all_futures:
            logger.info(f"Running {len(all_futures)} total tasks in parallel")
            with tqdm(total=len(all_futures), desc="Running All Evaluation Tasks") as pbar:
                for future_info in all_futures:
                    module_type = future_info[0]

                    if module_type == 'external_edubench':
                        _, future = future_info
                        result = future.result()
                        edubench_task_results.append(result)
                    elif module_type == 'ti_question_qa':
                        _, question_idx, future = future_info
                        result = future.result()
                        internal_eval_results.append((question_idx, result))
                    elif module_type == 'answer_verification':
                        _, question_idx, future = future_info
                        result = future.result()
                        verification_results.append((question_idx, result))
                    elif module_type == 'reading_question_qc':
                        _, question_idx, future = future_info
                        result = future.result()
                        reading_qc_results.append((question_idx, result))
                    elif module_type == 'math_content_evaluator':
                        _, question_idx, future = future_info
                        result = future.result()
                        content_eval_results.append((question_idx, result))
                    elif module_type == 'text_content_evaluator':
                        _, item_idx, future = future_info
                        result = future.result()
                        text_content_eval_results.append((item_idx, result))

                    pbar.update(1)

    # Process EduBench results
    if "external_edubench" in modules_to_use and edubench_task_results:
        logger.info(f"Processing {len(edubench_task_results)} EduBench task results")

        # Organize results by question
        question_scores = {}  # {question_idx: {task_type: score}}

        for result in edubench_task_results:
            question_idx = result['question_idx']
            task_type = result['task_type']
            evaluation_score = result['evaluation']

            if question_idx not in question_scores:
                question_scores[question_idx] = {}

            question_scores[question_idx][task_type] = evaluation_score

        # Build EdubenchScores for each question
        for i, question in enumerate(questions):
            scores = question_scores.get(i, {})
            average_score = sum(scores.values()) / len(scores) if scores else 0.0

            if request.verbose:
                # Full detailed result
                edubench_scores = EdubenchScores(
                    qa_score=scores.get('QA', 0.0),
                    ec_score=scores.get('EC', 0.0),
                    ip_score=scores.get('IP', 0.0),
                    ag_score=scores.get('AG', 0.0),
                    qg_score=scores.get('QG', 0.0),
                    tmg_score=scores.get('TMG', 0.0),
                    average_score=average_score
                )
            else:
                # Simplified result - just average score
                edubench_scores = SimplifiedEdubenchScores(
                    average_score=average_score
                )

            if question.id in evaluations:
                evaluations[question.id].external_edubench = edubench_scores

        logger.info(f"Built EduBench scores for {len(question_scores)} questions")

    # Process internal evaluator results
    if "ti_question_qa" in modules_to_use and internal_eval_results:
        logger.info(f"Processing {len(internal_eval_results)} internal evaluation results")

        # Sort by question index to maintain order
        internal_eval_results.sort(key=lambda x: x[0])

        for question_idx, result_dict in internal_eval_results:
            question = questions[question_idx]
            if question.id in evaluations:
                # Convert dict to Pydantic model
                try:
                    if request.verbose:
                        # Full detailed result
                        # Convert EvaluationDimension keys to strings and extract scores
                        scores_dict = {
                            k.value if hasattr(k, 'value') else str(k): v
                            for k, v in result_dict['scores'].items()
                        }

                        internal_result = InternalEvaluatorResult(
                            scores=InternalEvaluatorScores(**scores_dict),
                            issues=result_dict.get('issues', []),
                            strengths=result_dict.get('strengths', []),
                            overall=result_dict.get('overall', 0.0),
                            recommendation=result_dict.get('recommendation', 'revise'),
                            suggested_improvements=result_dict.get('suggested_improvements', []),
                            di_scores=DIScores(**result_dict.get('di_scores', {})),
                            section_evaluations=SectionEvaluations(
                                question=SectionEvaluation(**result_dict['section_evaluations']['question']),
                                scaffolding=SectionEvaluation(**result_dict['section_evaluations']['scaffolding'])
                            )
                        )
                        evaluations[question.id].ti_question_qa = internal_result
                    else:
                        # Simplified result - just overall score
                        internal_result = SimplifiedInternalEvaluatorResult(
                            overall=result_dict.get('overall', 0.0)
                        )
                        evaluations[question.id].ti_question_qa = internal_result
                except Exception as e:
                    logger.error(f"Error converting internal evaluator result for question {question_idx}: {e}")
                    # Keep the raw dict if conversion fails
                    evaluations[question.id].ti_question_qa = None

        logger.info(f"Assigned internal evaluator results to {len(internal_eval_results)} questions")

    # Process answer verification results
    if "answer_verification" in modules_to_use and verification_results:
        logger.info(f"Processing {len(verification_results)} answer verification results")

        # Sort by question index to maintain order
        verification_results.sort(key=lambda x: x[0])

        for question_idx, result_dict in verification_results:
            question = questions[question_idx]
            if question.id in evaluations:
                # Convert dict to Pydantic model
                try:
                    if request.verbose:
                        # Full detailed result
                        verification_result = AnswerVerificationResult(
                            is_correct=result_dict.get('is_correct', False),
                            correct_answer=result_dict.get('correct_answer', ''),
                            confidence=result_dict.get('confidence', 0),
                            reasoning=result_dict.get('reasoning', '')
                        )
                        evaluations[question.id].answer_verification = verification_result
                    else:
                        # Simplified result - just is_correct
                        verification_result = SimplifiedAnswerVerificationResult(
                            is_correct=result_dict.get('is_correct', False)
                        )
                        evaluations[question.id].answer_verification = verification_result
                except Exception as e:
                    logger.error(f"Error converting answer verification result for question {question_idx}: {e}")
                    # Keep None if conversion fails
                    evaluations[question.id].answer_verification = None

        logger.info(f"Assigned answer verification results to {len(verification_results)} questions")

    # Process reading QC results
    if "reading_question_qc" in modules_to_use and reading_qc_results:
        logger.info(f"Processing {len(reading_qc_results)} reading QC results")

        # Sort by question index to maintain order
        reading_qc_results.sort(key=lambda x: x[0])

        for question_idx, result_dict in reading_qc_results:
            question = questions[question_idx]
            if question.id in evaluations:
                # Extract and convert the result
                try:
                    qc_result = result_dict.get('result')
                    if qc_result and 'error' not in result_dict:
                        # Extract scores
                        overall_score = qc_result.get('overall_score', 0.0)

                        if request.verbose:
                            # Full detailed result
                            # Extract checks - the 'checks' field contains all check results
                            all_checks = qc_result.get('checks', {})

                            # Separate distractor and question checks based on category
                            distractor_checks = {k: v for k, v in all_checks.items() if v.get('category') == 'distractor'}
                            question_checks = {k: v for k, v in all_checks.items() if v.get('category') == 'question'}

                            # Determine if passed (threshold: 0.8)
                            passed = overall_score >= 0.8

                            reading_qc_obj = ReadingQuestionQCResult(
                                overall_score=overall_score,
                                distractor_checks=distractor_checks,
                                question_checks=question_checks,
                                passed=passed
                            )
                            evaluations[question.id].reading_question_qc = reading_qc_obj
                        else:
                            # Simplified result - just overall score
                            reading_qc_obj = SimplifiedReadingQuestionQCResult(
                                overall_score=overall_score
                            )
                            evaluations[question.id].reading_question_qc = reading_qc_obj
                    else:
                        logger.warning(f"Reading QC result for question {question_idx} is None or has error")
                        evaluations[question.id].reading_question_qc = None
                except Exception as e:
                    logger.error(f"Error converting reading QC result for question {question_idx}: {e}")
                    evaluations[question.id].reading_question_qc = None

        logger.info(f"Assigned reading QC results to {len(reading_qc_results)} questions")

    # Process content evaluation results
    if "math_content_evaluator" in modules_to_use and content_eval_results:
        logger.info(f"Processing {len(content_eval_results)} content evaluation results")

        # Sort by item index to maintain order
        content_eval_results.sort(key=lambda x: x[0])

        for item_idx, result_dict in content_eval_results:
            # Determine which item this is (question or text content)
            if item_idx < len(questions):
                item = questions[item_idx]
            else:
                item = text_content[item_idx - len(questions)]

            if item.id in evaluations:
                try:
                    eval_result = result_dict.get('result')
                    if eval_result and 'error' not in result_dict:
                        # Count pass/fail
                        criteria = [
                            'curriculum_alignment', 'cognitive_demand', 'accuracy_and_rigor',
                            'image_quality', 'reveals_misconceptions', 'question_type_appropriateness',
                            'engagement_and_relevance', 'instructional_support', 'clarity_and_accessibility'
                        ]

                        pass_count = sum(1 for c in criteria if eval_result.get(c, {}).get('result') == 'PASS')
                        fail_count = len(criteria) - pass_count
                        overall_score = pass_count / len(criteria) if criteria else 0.0

                        if request.verbose:
                            # Full detailed result
                            content_eval_obj = ContentEvaluatorResult(
                                overall_rating=eval_result.get('overall', {}).get('result', 'UNKNOWN'),
                                curriculum_alignment=eval_result.get('curriculum_alignment', {}).get('result', 'UNKNOWN'),
                                cognitive_demand=eval_result.get('cognitive_demand', {}).get('result', 'UNKNOWN'),
                                accuracy_and_rigor=eval_result.get('accuracy_and_rigor', {}).get('result', 'UNKNOWN'),
                                image_quality=eval_result.get('image_quality', {}).get('result', 'UNKNOWN'),
                                reveals_misconceptions=eval_result.get('reveals_misconceptions', {}).get('result', 'UNKNOWN'),
                                question_type_appropriateness=eval_result.get('question_type_appropriateness', {}).get('result', 'UNKNOWN'),
                                engagement_and_relevance=eval_result.get('engagement_and_relevance', {}).get('result', 'UNKNOWN'),
                                instructional_support=eval_result.get('instructional_support', {}).get('result', 'UNKNOWN'),
                                clarity_and_accessibility=eval_result.get('clarity_and_accessibility', {}).get('result', 'UNKNOWN'),
                                pass_count=pass_count,
                                fail_count=fail_count,
                                overall_score=overall_score
                            )
                            evaluations[item.id].math_content_evaluator = content_eval_obj
                        else:
                            # Simplified result - just overall score
                            content_eval_obj = SimplifiedContentEvaluatorResult(
                                overall_score=overall_score
                            )
                            evaluations[item.id].math_content_evaluator = content_eval_obj
                    else:
                        logger.warning(f"Content evaluation result for item {item_idx} is None or has error")
                        evaluations[item.id].math_content_evaluator = None
                except Exception as e:
                    logger.error(f"Error converting content evaluation result for item {item_idx}: {e}")
                    evaluations[item.id].math_content_evaluator = None

        logger.info(f"Assigned content evaluation results to {len(content_eval_results)} items")

    # Process text content evaluator results
    if "text_content_evaluator" in modules_to_use and text_content_eval_results:
        logger.info(f"Processing {len(text_content_eval_results)} text content evaluator results")

        # Sort by item index to maintain order
        text_content_eval_results.sort(key=lambda x: x[0])

        for item_idx, result_dict in text_content_eval_results:
            # Text content evaluator only applies to text content (offset by questions count)
            item = text_content[item_idx - len(questions)]

            if item.id in evaluations:
                try:
                    eval_result = result_dict.get('result')
                    if eval_result and 'error' not in result_dict:
                        if request.verbose:
                            # Full detailed result
                            text_eval_obj = TextContentEvaluatorResult(
                                correctness=eval_result['scores'].get(EvaluationDimension.CORRECTNESS, 0.0),
                                grade_alignment=eval_result['scores'].get(EvaluationDimension.GRADE_ALIGNMENT, 0.0),
                                language_quality=eval_result['scores'].get(EvaluationDimension.LANGUAGE_QUALITY, 0.0),
                                pedagogical_value=eval_result['scores'].get(EvaluationDimension.PEDAGOGICAL_VALUE, 0.0),
                                explanation_quality=eval_result['scores'].get(EvaluationDimension.EXPLANATION_QUALITY, 0.0),
                                di_compliance=eval_result['scores'].get(EvaluationDimension.DI_COMPLIANCE, 0.0),
                                instruction_adherence=eval_result['scores'].get(EvaluationDimension.INSTRUCTION_ADHERENCE, 0.0),
                                query_relevance=eval_result['scores'].get(EvaluationDimension.QUERY_RELEVANCE, 0.0),
                                overall=eval_result.get('overall', 0.0),
                                recommendation=eval_result.get('recommendation', 'revise'),
                                issues=eval_result.get('issues', []),
                                strengths=eval_result.get('strengths', []),
                                suggested_improvements=eval_result.get('suggested_improvements', []),
                                di_scores=DIScores(**eval_result.get('di_scores', {}))
                            )
                            evaluations[item.id].text_content_evaluator = text_eval_obj
                        else:
                            # Simplified result - just overall score
                            text_eval_obj = SimplifiedTextContentEvaluatorResult(
                                overall=eval_result.get('overall', 0.0)
                            )
                            evaluations[item.id].text_content_evaluator = text_eval_obj
                    else:
                        logger.warning(f"Text content evaluation result for item {item_idx} is None or has error")
                        evaluations[item.id].text_content_evaluator = None
                except Exception as e:
                    logger.error(f"Error converting text content evaluation result for item {item_idx}: {e}")
                    evaluations[item.id].text_content_evaluator = None

        logger.info(f"Assigned text content evaluation results to {len(text_content_eval_results)} items")

    # Calculate final scores for each question
    logger.info("Calculating final combined scores for each question")
    for question_id, evaluation in evaluations.items():
        scores_to_combine = []

        # Debug: Log what we have for this question
        has_internal = evaluation.ti_question_qa is not None
        has_verification = evaluation.answer_verification is not None
        has_edubench = evaluation.external_edubench is not None
        has_reading_qc = evaluation.reading_question_qc is not None
        has_content_eval = evaluation.math_content_evaluator is not None
        has_text_content_eval = evaluation.text_content_evaluator is not None

        logger.info(f"Question {question_id}: ti_question_qa={has_internal}, answer_verification={has_verification}, external_edubench={has_edubench}, reading_question_qc={has_reading_qc}, math_content_evaluator={has_content_eval}, text_content_evaluator={has_text_content_eval}")

        # Internal evaluator: already on 0-1 scale
        if evaluation.ti_question_qa:
            # Works for both InternalEvaluatorResult and SimplifiedInternalEvaluatorResult
            internal_score = evaluation.ti_question_qa.overall
            scores_to_combine.append(internal_score)
            logger.info(f"  - Internal evaluator: {internal_score:.3f}")

        # Answer verification: only penalize if incorrect (don't inflate score if correct)
        if evaluation.answer_verification:
            # Works for both AnswerVerificationResult and SimplifiedAnswerVerificationResult
            if not evaluation.answer_verification.is_correct:
                # If answer is incorrect, add 0 to severely penalize the score
                scores_to_combine.append(0.0)
                logger.info(f"  - Answer verification: 0.000 (is_correct=False - PENALIZED)")
            else:
                # If answer is correct, don't add to scores (neutral - doesn't inflate)
                logger.info(f"  - Answer verification: PASS (is_correct=True - not counted in score)")

        # EduBench: convert from 0-10 to 0-1 scale
        if evaluation.external_edubench:
            # Works for both EdubenchScores and SimplifiedEdubenchScores
            edubench_normalized = evaluation.external_edubench.average_score / 10.0
            scores_to_combine.append(edubench_normalized)
            logger.info(f"  - EduBench: {edubench_normalized:.3f} (avg={evaluation.external_edubench.average_score:.2f}/10)")

        # Reading QC: already on 0-1 scale
        if evaluation.reading_question_qc:
            # Works for both ReadingQuestionQCResult and SimplifiedReadingQuestionQCResult
            reading_qc_score = evaluation.reading_question_qc.overall_score
            scores_to_combine.append(reading_qc_score)
            logger.info(f"  - Reading QC: {reading_qc_score:.3f}")

        # Content evaluator: already on 0-1 scale
        if evaluation.math_content_evaluator:
            # Works for both ContentEvaluatorResult and SimplifiedContentEvaluatorResult
            content_eval_score = evaluation.math_content_evaluator.overall_score
            scores_to_combine.append(content_eval_score)
            logger.info(f"  - Content evaluator: {content_eval_score:.3f}")

        # Text content pedagogical evaluator: already on 0-1 scale
        if evaluation.text_content_evaluator:
            # Works for both TextContentEvaluatorResult and SimplifiedTextContentEvaluatorResult
            text_content_score = evaluation.text_content_evaluator.overall
            scores_to_combine.append(text_content_score)
            logger.info(f"  - Text content evaluator: {text_content_score:.3f}")

        # Calculate weighted average of all available scores
        if scores_to_combine:
            evaluation.final_score = sum(scores_to_combine) / len(scores_to_combine)
            logger.info(f"Question {question_id}: final_score = {evaluation.final_score:.3f} (from {len(scores_to_combine)} modules)")
        else:
            evaluation.final_score = None
            logger.warning(f"Question {question_id}: No scores available to calculate final_score - all evaluations are None!")

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Universal evaluation request {request_id} completed in {elapsed_time:.2f} seconds")

    # Filter out evaluators that weren't requested
    filtered_evaluations = {}
    for question_id, evaluation in evaluations.items():
        # Build dict with only requested evaluators (and only non-None values)
        eval_dict = {}

        if "ti_question_qa" in modules_to_use and evaluation.ti_question_qa is not None:
            eval_dict["ti_question_qa"] = evaluation.ti_question_qa
        if "answer_verification" in modules_to_use and evaluation.answer_verification is not None:
            eval_dict["answer_verification"] = evaluation.answer_verification
        if "external_edubench" in modules_to_use and evaluation.external_edubench is not None:
            eval_dict["external_edubench"] = evaluation.external_edubench
        if "reading_question_qc" in modules_to_use and evaluation.reading_question_qc is not None:
            eval_dict["reading_question_qc"] = evaluation.reading_question_qc
        if "math_content_evaluator" in modules_to_use and evaluation.math_content_evaluator is not None:
            eval_dict["math_content_evaluator"] = evaluation.math_content_evaluator
        if "text_content_evaluator" in modules_to_use and evaluation.text_content_evaluator is not None:
            eval_dict["text_content_evaluator"] = evaluation.text_content_evaluator

        # Always include final_score if not None
        if evaluation.final_score is not None:
            eval_dict["final_score"] = evaluation.final_score

        # Create object from dict (Pydantic will only include provided keys)
        filtered_eval = UniversalQuestionEvaluationScores(**eval_dict)
        filtered_evaluations[question_id] = filtered_eval

    return UniversalEvaluationResponse(
        request_id=request_id,
        evaluations=filtered_evaluations,
        evaluation_time_seconds=elapsed_time
    )


if __name__ == "__main__":
    with open("qs.json", "r") as f:
        example_data = json.load(f)
    example_request = UniversalEvaluationRequest(**example_data)
    response = universal_unified_benchmark(example_request)
    print(response.model_dump_json(indent=2, exclude_none=True))