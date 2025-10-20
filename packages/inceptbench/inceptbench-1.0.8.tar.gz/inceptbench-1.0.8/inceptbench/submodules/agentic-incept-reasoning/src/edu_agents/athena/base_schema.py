from __future__ import annotations

from typing import List, Union, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class Image(BaseModel):
    """Image object with URL and optional metadata."""
    model_config = ConfigDict(extra='forbid')
    
    url: str
    credit: Optional[str] = Field(None, description="Accreditation for commercial use of the image")
    caption: Optional[str] = Field(None, description="Short contextual description of the image")


class VideoSubtitles(BaseModel):
    """Video subtitles configuration."""
    model_config = ConfigDict(extra='forbid')
    
    url: str
    type: str


class Video(BaseModel):
    """Video object with URL and optional subtitles."""
    model_config = ConfigDict(extra='forbid')
    
    url: str
    subtitles: Optional[VideoSubtitles] = None


class KeyFigure(BaseModel):
    """Key figure with name, optional image and biography."""
    model_config = ConfigDict(extra='forbid')
    
    name: str
    image: Optional[Image] = None
    biography_short: Optional[str] = None


class TextualStimulus(BaseModel):
    """Textual stimulus content."""
    model_config = ConfigDict(extra='forbid')
    
    type: Literal["text"] = "text"
    text: str


class ImageStimulus(BaseModel):
    """Image stimulus content."""
    model_config = ConfigDict(extra='forbid')
    
    type: Literal["image"] = "image"
    image: Image


class TextualLearningContent(BaseModel):
    """Textual learning content."""
    model_config = ConfigDict(extra='forbid')
    
    type: Literal["text"] = "text"
    text: str


class VideoLearningContent(BaseModel):
    """Video learning content."""
    model_config = ConfigDict(extra='forbid')
    
    type: Literal["video"] = "video"
    video: Video
    speaker: Optional[KeyFigure] = None
    transcript: Optional[str] = None


# Union types for polymorphic fields
StimulusContent = Union[TextualStimulus, ImageStimulus]
LearningContent = Union[TextualLearningContent, VideoLearningContent]


class WorkedExampleStep(BaseModel):
    """Individual step in a worked example."""
    model_config = ConfigDict(extra='forbid')
    
    order: int
    step: str
    stimulus: Optional[Image] = None


class WorkedExample(BaseModel):
    """Worked example with ordered steps."""
    model_config = ConfigDict(extra='forbid')
    
    steps: List[WorkedExampleStep] = Field(..., min_length=1) 