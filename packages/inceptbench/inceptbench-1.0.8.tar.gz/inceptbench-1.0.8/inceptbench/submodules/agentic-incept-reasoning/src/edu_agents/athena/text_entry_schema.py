from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

# Import shared models from base schema
from .base_schema import StimulusContent, WorkedExample


class Explanation(BaseModel):
    """Explanation with title and text."""
    title: str
    text: str


class TextEntryQuestion(BaseModel):
    """Complete text entry question schema with fill-in-the-blank format."""
    question: str
    answer: List[str] = Field(..., min_length=1)
    stimulus: Optional[List[StimulusContent]] = None
    explanation: Optional[Explanation] = None
    instructions: Optional[str] = None
    worked_example: Optional[WorkedExample] = None
    
    @field_validator('question')
    @classmethod
    def validate_question_has_one_blank(cls, v: str) -> str:
        """Ensure the question contains exactly one <blank> placeholder."""
        blank_count = v.count('<blank>')
        if blank_count != 1:
            raise ValueError('Question must contain exactly one <blank> placeholder')
        return v 