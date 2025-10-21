"""
Athena schema modules for structured educational content generation.

This package contains Pydantic models for different types of educational questions
and shared base components.
"""

from .base_schema import (
    Image, Video, VideoSubtitles, KeyFigure,
    TextualStimulus, ImageStimulus, StimulusContent,
    TextualLearningContent, VideoLearningContent, LearningContent,
    WorkedExampleStep, WorkedExample
)

from .mcq_schema import (
    AnswerOption, MultipleChoiceQuestion
)

from .text_entry_schema import (
    Explanation, TextEntryQuestion
)

from .amq_schema import (
    ContentCategory, CategorizedContent, StepDetail, PersonalizedAcademicInsight, DetailedExplanation,
    VoiceoverStepScript, VoiceoverScript, AMQMultipleChoice, AMQNumerical
)

__all__ = [
    # Base schema components
    "Image", "Video", "VideoSubtitles", "KeyFigure",
    "TextualStimulus", "ImageStimulus", "StimulusContent",
    "TextualLearningContent", "VideoLearningContent", "LearningContent",
    "WorkedExampleStep", "WorkedExample",
    
    # MCQ schema components  
    "AnswerOption", "MultipleChoiceQuestion",
    
    # Text entry schema components
    "Explanation", "TextEntryQuestion",
    
    # AMQ schema components
    "ContentCategory", "CategorizedContent", "StepDetail", "PersonalizedAcademicInsight", "DetailedExplanation",
    "VoiceoverStepScript", "VoiceoverScript", "AMQMultipleChoice", "AMQNumerical",
] 