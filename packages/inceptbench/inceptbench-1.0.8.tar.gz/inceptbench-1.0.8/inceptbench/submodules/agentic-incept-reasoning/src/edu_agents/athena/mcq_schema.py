from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

# Import shared components from base schema
from .base_schema import Image, StimulusContent, LearningContent, WorkedExample


class AnswerOption(BaseModel):
    """Answer option for multiple choice questions."""
    model_config = ConfigDict(extra='forbid')
    
    id: str
    answer: str
    correct: bool
    explanation: Optional[str] = None


class MultipleChoiceQuestion(BaseModel):
    """Complete multiple choice question schema."""
    model_config = ConfigDict(extra='forbid')
    
    question: str
    answer_options: List[AnswerOption] = Field(..., min_length=2)
    stimulus: List[StimulusContent]
    worked_example: WorkedExample
    learning_content: Optional[LearningContent] = None
