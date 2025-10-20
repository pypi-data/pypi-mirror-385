from __future__ import annotations
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum

class ContentCategory(Enum):
    MCQ = "MCQ"
    NUMERICAL = "NUMERICAL"

class CategorizedContent(BaseModel):
    category: ContentCategory

class StepDetail(BaseModel):
    """Individual step in a worked example."""
    title: str = Field(description="Title of the step, e.g., 'Step 1: Identify the operation'")
    content: str = Field(description="Detailed content explaining the step using markdown formatting")
    image: Optional[str] = Field(default=None, description="Optional image URL for this step")
    image_alt_text: Optional[str] = Field(default=None, description="Alt text for the image if provided")

class PersonalizedAcademicInsight(BaseModel):
    """Academic insight explaining why an answer is correct or incorrect."""
    answer: str = Field(description="The answer option or value (correct or incorrect)")
    insight: str = Field(description="Explanation of why this answer is correct or incorrect")

class VoiceoverStepScript(BaseModel):
    """Voiceover script for an explanation step."""
    step_number: int = Field(description="The step number (1, 2, 3, etc.)")
    script: str = Field(description="Audio-friendly script for this step, with mathematical expressions converted to spoken form")

class VoiceoverScript(BaseModel):
    """Complete voiceover scripts for all components of the question."""
    question_script: str = Field(description="Audio-friendly script for the question, including description and mathematical expressions in spoken form")
    answer_choice_scripts: Optional[List[str]] = Field(default=None, description="Audio-friendly scripts for each answer choice (MCQ only), with mathematical expressions in spoken form")
    explanation_step_scripts: List[VoiceoverStepScript] = Field(description="Audio-friendly scripts for each explanation step, with mathematical expressions in spoken form")

class DetailedExplanation(BaseModel):
    """Step-by-step worked example with clear reasoning and personalized academic insights."""
    steps: List[StepDetail] = Field(description="List of steps in the worked example")
    personalized_academic_insights: List[PersonalizedAcademicInsight] = Field(
        description="Academic insights for all answers - includes the correct answer and why it's right, plus incorrect answers and why they're wrong"
    )

class AMQMultipleChoice(BaseModel):
    """AMQ format for multiple choice questions."""
    question: str = Field(description="The math problem statement in markdown WITHOUT answer choices, including any images")
    options: List[str] = Field(description="List of answer options")
    answer: str = Field(description="The correct answer option as plain text")
    explanation: str = Field(description="Brief explanation of the correct approach")
    detailed_explanation: DetailedExplanation = Field(description="Step-by-step worked example and personalized academic insights for all answers")
    voiceover_script: VoiceoverScript = Field(description="Audio-friendly scripts for question, answer choices, and explanation steps")

class AMQNumerical(BaseModel):
    """AMQ format for numerical answer questions."""
    question: str = Field(description="The math problem statement in markdown, including any images")
    answer: Union[int, float, str] = Field(description="The correct numerical answer as plain text")
    explanation: str = Field(description="Brief explanation of the correct approach")
    detailed_explanation: DetailedExplanation = Field(description="Step-by-step worked example and personalized academic insights for correct and plausible incorrect answers")
    voiceover_script: VoiceoverScript = Field(description="Audio-friendly scripts for question and explanation steps") 