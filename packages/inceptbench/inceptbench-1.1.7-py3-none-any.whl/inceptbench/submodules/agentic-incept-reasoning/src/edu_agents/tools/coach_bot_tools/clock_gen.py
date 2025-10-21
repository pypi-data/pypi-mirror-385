from __future__ import annotations

import logging
from typing import Callable

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.clocks import (  # noqa: E402
    create_clock,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.clock import (  # noqa: E402
    Clock,
)

logger = logging.getLogger("coach_bot_tools.clock")


def generate_coach_bot_clock_image(
    hour: int,
    minute: int,
    type: str = "analog"  # Changed from clock_type to match Pydantic model
) -> str:
    """
    Generate a clock image with enhanced styling for educational content.
    
    Parameters
    ----------
    hour : int
        The hour to display (0-23, will be converted to 12-hour format for analog clocks)
    minute : int
        The minute to display (0-59)
    type : str, default "analog"
        The type of clock to generate: "analog" or "digital"
        
    Returns
    -------
    str
        The URL of the generated clock image
    """
    
    # Use standardized logging
    log_tool_generation("clock_image", hour=hour, minute=minute, type=type)
    
    # Create the Clock stimulus description
    clock_data = Clock(
        type=type,
        hour=hour,
        minute=minute
    )
    
    # Generate the clock image using enhanced styling
    # This returns a file path to the generated image
    image_file_path = create_clock(clock_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_clock_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for enhanced clock generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_clock_image",
        description=(
            "Generate a clock image with enhanced styling for educational content. "
            "Supports both analog and digital clocks with professional styling including "
            "fancy arrow-style hands for analog clocks and digital font styling for digital clocks."
        ),
        pydantic_model=Clock,
        custom_descriptions={
            "hour": "The hour to display (0-23). For analog clocks, will be converted to 12-hour "
                    "format automatically.",
            "minute": "The minute to display (0-59).",
            "type": "The type of clock to generate. Use 'analog' for traditional clock face with "
                    "fancy arrow-style hands, or 'digital' for digital display with special "
                    "digital font styling."
        }
    )
    return spec, generate_coach_bot_clock_image