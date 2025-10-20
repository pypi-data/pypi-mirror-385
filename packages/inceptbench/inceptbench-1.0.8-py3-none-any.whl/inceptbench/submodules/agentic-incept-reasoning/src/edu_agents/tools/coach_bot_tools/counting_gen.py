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

from content_generators.additional_content.stimulus_image.drawing_functions.counting import (  # noqa: E402
    draw_counting,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.counting import (  # noqa: E402
    Counting,
)

logger = logging.getLogger("coach_bot_tools.counting")


def generate_coach_bot_counting_image(
    object_name: str,
    count: int
) -> str:
    """
    Generate a counting image with a specified number of objects.
    
    Creates an image showing a specific count of objects arranged in a natural,
    slightly irregular pattern. Objects are arranged in rows with some variation
    to make counting more engaging and realistic.
    
    Parameters
    ----------
    object_name : str
        The type of object to display. Must be one of: butterfly, button, cat, dog, fish, sun.
    count : int
        The number of objects to display (must be between 5 and 20)
        
    Returns
    -------
    str
        The URL of the generated counting image
    """
    
    # Use standardized logging
    log_tool_generation("counting_image", object_name=object_name, count=count)
    
    # Create and validate the Counting stimulus using Pydantic
    counting_stimulus = Counting(
        object_name=object_name,
        count=count
    )
    
    # Generate the image using the counting function
    image_file_path = draw_counting(counting_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_counting_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for counting image generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_counting_image",
        description=(
            "Generate a counting image with a specified number of objects. Creates an image "
            "showing objects arranged in a natural, slightly irregular pattern to make "
            "counting more engaging. Perfect for early math education and number recognition."
        ),
        pydantic_model=Counting,
        custom_descriptions={
            "object_name": (
                "The type of object to display. Available options: butterfly, button, cat, dog, "
                "fish, sun. Each object is designed for early childhood counting exercises."
            ),
            "count": "The number of objects to display (must be between 5 and 20 for optimal "
                     "visual clarity)"
        }
    )
    return spec, generate_coach_bot_counting_image
