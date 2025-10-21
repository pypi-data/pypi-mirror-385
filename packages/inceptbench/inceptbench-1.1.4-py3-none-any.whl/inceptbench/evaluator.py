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
from incept_core.evaluator.v3 import call_single_shot_evaluator
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


class UniversalEvaluationRequest(BaseModel):
    generated_questions: List[UniversalGeneratedQuestionInput]
    submodules_to_run: List[Literal["quality_evaluator", "answer_verification", "external_edubench", "reading_question_qc", "math_content_evaluator"]] = ["quality_evaluator", "answer_verification", "reading_question_qc", "math_content_evaluator"]
    verbose: bool = False  # If False, returns only overall scores per module

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


class UniversalQuestionEvaluationScores(BaseModel):
    model_config = ConfigDict(
        # Exclude None values when serializing to JSON
        exclude_none=True
    )

    quality_evaluator: Optional[InternalEvaluatorResult | SimplifiedInternalEvaluatorResult] = None
    answer_verification: Optional[AnswerVerificationResult | SimplifiedAnswerVerificationResult] = None
    external_edubench: Optional[EdubenchScores | SimplifiedEdubenchScores] = None
    reading_question_qc: Optional[ReadingQuestionQCResult | SimplifiedReadingQuestionQCResult] = None
    math_content_evaluator: Optional[ContentEvaluatorResult | SimplifiedContentEvaluatorResult] = None
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

def _run_content_evaluation_task_sync(question_idx: int, question: UniversalGeneratedQuestionInput) -> Dict[str, Any]:
    """Synchronous wrapper for running content evaluation task."""

    # Check if evaluate_content is available
    if evaluate_content is None:
        logger.warning(f"Content evaluator not available for question {question_idx} - skipping")
        return {
            'question_idx': question_idx,
            'result': None,
            'error': 'Content evaluator not available - edu_agents.eval.content_evaluator could not be imported'
        }

    async def _async_task():
        logger.debug(f"Running content evaluation for question {question_idx}")

        try:
            # Build content string from question data
            content_parts = [
                f"**Question:** {question.question}",
                f"**Answer:** {question.answer}",
            ]

            if question.answer_explanation:
                content_parts.append(f"**Explanation:** {question.answer_explanation}")

            if question.answer_options:
                options_str = "\n".join([f"{k}: {v}" for k, v in question.answer_options.items()])
                content_parts.append(f"**Options:**\n{options_str}")

            if question.skill:
                content_parts.append(f"**Grade:** {question.skill.grade}")
                content_parts.append(f"**Subject:** {question.skill.subject}")
                if question.skill.difficulty:
                    content_parts.append(f"**Difficulty:** {question.skill.difficulty}")

            content = "\n\n".join(content_parts)

            # Evaluate content
            evaluation_json = await evaluate_content(content)

            # Parse the JSON response
            evaluation_data = json.loads(evaluation_json)

            return {
                'question_idx': question_idx,
                'result': evaluation_data
            }
        except Exception as e:
            logger.error(f"Error running content evaluation for question {question_idx}: {e}")
            return {
                'question_idx': question_idx,
                'result': None,
                'error': str(e)
            }

    # Run the async function in a new event loop
    return asyncio.run(_async_task())


def _run_reading_qc_task_sync(question_idx: int, question: UniversalGeneratedQuestionInput, claude_api_key: str, openai_api_key: str = None) -> Dict[str, Any]:
    """Synchronous wrapper for running reading question QC analysis."""

    async def _async_task():
        logger.debug(f"Running reading QC for question {question_idx}")

        # Initialize clients
        claude_client = anthropic.AsyncAnthropic(api_key=claude_api_key)
        openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

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

        try:
            result = await analyzer.analyze_question(question_item, semaphore=None)
            return {
                'question_idx': question_idx,
                'result': result
            }
        except Exception as e:
            logger.error(f"Error running reading QC for question {question_idx}: {e}")
            return {
                'question_idx': question_idx,
                'result': None,
                'error': str(e)
            }

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
    Benchmark mode: Process all questions in parallel for maximum throughput.

    Args:
        request: UniversalEvaluationRequest with list of questions
        max_workers: Number of parallel workers (default: 100)

    Returns:
        Dict with structure:
        {
            "request_id": str,
            "total_questions": int,
            "successful": int,
            "failed": int,
            "scores": List[Dict] - one score per question,
            "failed_ids": List[str],
            "evaluation_time_seconds": float
        }
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())

    logger.info(f"🚀 Benchmark mode: Processing {len(request.generated_questions)} questions with {max_workers} workers")

    scores = []
    failed_ids = []

    def process_single_question(question):
        """Process a single question and return result or error"""
        try:
            # Create a mini request with just this question
            mini_request = UniversalEvaluationRequest(
                submodules_to_run=request.submodules_to_run,
                generated_questions=[question],
                verbose=False  # Always use simplified mode for benchmarking
            )

            # Run evaluation
            response = universal_unified_benchmark(mini_request)

            # Extract the score
            if question.id in response.evaluations:
                eval_result = response.evaluations[question.id]

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
                    "id": question.id,
                    "success": True,
                    "final_score": eval_result.final_score,
                    "scores": scores_dict
                }
            else:
                return {
                    "id": question.id,
                    "success": False,
                    "error": "No evaluation result returned"
                }
        except Exception as e:
            logger.error(f"Failed to process question {question.id}: {e}")
            return {
                "id": question.id,
                "success": False,
                "error": str(e)
            }

    # Process all questions in parallel with progress bar
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(
            executor.map(process_single_question, request.generated_questions),
            total=len(request.generated_questions),
            desc="Evaluating questions"
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

    logger.info(f"✅ Benchmark complete: {len(scores)}/{len(request.generated_questions)} successful in {evaluation_time:.2f}s")

    return {
        "request_id": request_id,
        "total_questions": len(request.generated_questions),
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
    Processes each question and organizes results by question ID.
    """

    start_time = time.time()
    request_id = str(uuid.uuid4())

    logger.info(f"Universal evaluation request {request_id} with {len(request.generated_questions)} questions")

    modules_to_use = request.submodules_to_run
    evaluations = {}

    for question in request.generated_questions:
        evaluations[question.id] = UniversalQuestionEvaluationScores()

    # Run all enabled modules in parallel
    questions = request.generated_questions
    effective_edubench_tasks = ["QA", "EC", "IP", "AG", "QG", "TMG"]

    # Prepare storage for results
    edubench_task_results = []
    internal_eval_results = []
    verification_results = []
    reading_qc_results = []
    content_eval_results = []

    # Get API keys for reading QC
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    with ThreadPoolExecutor(max_workers=50) as executor:
        all_futures = []

        # Submit EduBench tasks if enabled
        if "external_edubench" in modules_to_use:
            logger.info(f"Submitting EduBench evaluation with {len(effective_edubench_tasks)} tasks for {len(questions)} questions")
            for i, q in enumerate(questions):
                for task_type in effective_edubench_tasks:
                    future = executor.submit(_run_edubench_task, i, task_type, q)
                    all_futures.append(('external_edubench', future))

        # Submit internal evaluator tasks if enabled
        if "quality_evaluator" in modules_to_use:
            logger.info(f"Submitting {len(questions)} internal evaluator tasks")
            for i, q in enumerate(questions):
                future = executor.submit(call_single_shot_evaluator, q, len(questions))
                all_futures.append(('quality_evaluator', i, future))

        # Submit answer verification tasks if enabled
        if "answer_verification" in modules_to_use:
            logger.info(f"Submitting {len(questions)} answer verification tasks")
            for i, q in enumerate(questions):
                future = executor.submit(verify_answer_with_gpt4, q.question, q.answer, q.answer_explanation)
                all_futures.append(('answer_verification', i, future))

        # Submit reading QC tasks if enabled and dependencies available
        if "reading_question_qc" in modules_to_use:
            logger.info(f"Submitting {len(questions)} reading QC tasks")
            for i, q in enumerate(questions):
                future = executor.submit(_run_reading_qc_task_sync, i, q, claude_api_key, openai_api_key)
                all_futures.append(('reading_question_qc', i, future))

        # Submit content evaluation tasks if enabled
        if "math_content_evaluator" in modules_to_use:
            logger.info(f"Submitting {len(questions)} content evaluation tasks")
            for i, q in enumerate(questions):
                future = executor.submit(_run_content_evaluation_task_sync, i, q)
                all_futures.append(('math_content_evaluator', i, future))

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
                    elif module_type == 'quality_evaluator':
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
    if "quality_evaluator" in modules_to_use and internal_eval_results:
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
                        evaluations[question.id].quality_evaluator = internal_result
                    else:
                        # Simplified result - just overall score
                        internal_result = SimplifiedInternalEvaluatorResult(
                            overall=result_dict.get('overall', 0.0)
                        )
                        evaluations[question.id].quality_evaluator = internal_result
                except Exception as e:
                    logger.error(f"Error converting internal evaluator result for question {question_idx}: {e}")
                    # Keep the raw dict if conversion fails
                    evaluations[question.id].quality_evaluator = None

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

        # Sort by question index to maintain order
        content_eval_results.sort(key=lambda x: x[0])

        for question_idx, result_dict in content_eval_results:
            question = questions[question_idx]
            if question.id in evaluations:
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
                            evaluations[question.id].math_content_evaluator = content_eval_obj
                        else:
                            # Simplified result - just overall score
                            content_eval_obj = SimplifiedContentEvaluatorResult(
                                overall_score=overall_score
                            )
                            evaluations[question.id].math_content_evaluator = content_eval_obj
                    else:
                        logger.warning(f"Content evaluation result for question {question_idx} is None or has error")
                        evaluations[question.id].math_content_evaluator = None
                except Exception as e:
                    logger.error(f"Error converting content evaluation result for question {question_idx}: {e}")
                    evaluations[question.id].math_content_evaluator = None

        logger.info(f"Assigned content evaluation results to {len(content_eval_results)} questions")

    # Calculate final scores for each question
    logger.info("Calculating final combined scores for each question")
    for question_id, evaluation in evaluations.items():
        scores_to_combine = []

        # Debug: Log what we have for this question
        has_internal = evaluation.quality_evaluator is not None
        has_verification = evaluation.answer_verification is not None
        has_edubench = evaluation.external_edubench is not None
        has_reading_qc = evaluation.reading_question_qc is not None
        has_content_eval = evaluation.math_content_evaluator is not None

        logger.info(f"Question {question_id}: quality_evaluator={has_internal}, answer_verification={has_verification}, external_edubench={has_edubench}, reading_question_qc={has_reading_qc}, math_content_evaluator={has_content_eval}")

        # Internal evaluator: already on 0-1 scale
        if evaluation.quality_evaluator:
            # Works for both InternalEvaluatorResult and SimplifiedInternalEvaluatorResult
            internal_score = evaluation.quality_evaluator.overall
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

        if "quality_evaluator" in modules_to_use and evaluation.quality_evaluator is not None:
            eval_dict["quality_evaluator"] = evaluation.quality_evaluator
        if "answer_verification" in modules_to_use and evaluation.answer_verification is not None:
            eval_dict["answer_verification"] = evaluation.answer_verification
        if "external_edubench" in modules_to_use and evaluation.external_edubench is not None:
            eval_dict["external_edubench"] = evaluation.external_edubench
        if "reading_question_qc" in modules_to_use and evaluation.reading_question_qc is not None:
            eval_dict["reading_question_qc"] = evaluation.reading_question_qc
        if "math_content_evaluator" in modules_to_use and evaluation.math_content_evaluator is not None:
            eval_dict["math_content_evaluator"] = evaluation.math_content_evaluator

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