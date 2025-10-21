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

from content_generators.additional_content.stimulus_image.drawing_functions.object_array import (  # noqa: E402
    draw_object_array,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.object_array import (  # noqa: E402, E501
    ObjectArray,
)

logger = logging.getLogger("coach_bot_tools.object_array")


def generate_coach_bot_object_array_image(
    object_name: str,
    rows: int,
    columns: int
) -> str:
    """
    Generate an array of objects arranged in a grid pattern.
    
    Creates a visual grid of identical objects (like animals, buttons, or other items) 
    arranged in rows and columns. Useful for teaching multiplication concepts, counting,
    arrays, and basic arithmetic operations.
    
    Parameters
    ----------
    object_name : str
        Type of object to display in the array. Must be one of:
        'button', 'dog', 'cat', 'butterfly', 'sun', 'fish'
    rows : int
        Number of rows in the array (2-7)
    columns : int
        Number of columns in the array (2-7)
        
    Returns
    -------
    str
        The URL of the generated object array image
    """
    
    # Use standardized logging
    log_tool_generation("object_array_image", object_name=object_name, rows=rows, columns=columns)
    
    # Create and validate the ObjectArray stimulus using Pydantic
    object_array = ObjectArray(
        object_name=object_name,
        rows=rows,
        columns=columns
    )
    
    # Generate the image using the object array function
    image_file_path = draw_object_array(object_array)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_object_array_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for object array generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_object_array_image",
        description=(
            "Generate an array of objects arranged in a grid pattern. Creates visual grids "
            "of identical objects (animals, buttons, etc.) for teaching multiplication "
            "concepts, counting, arrays, and basic arithmetic operations."
        ),
        pydantic_model=ObjectArray,
        custom_descriptions={
            "object_name": (
                "Type of object to display in the array. Available options: butterfly, button, "
                "cat, dog, fish, sun. Each object is designed for educational exercises in "
                "multiplication and arrays."
            ),
            "rows": "Number of rows in the array (must be between 2 and 7 for optimal visual "
                    "clarity)",
            "columns": "Number of columns in the array (must be between 2 and 7 for optimal visual "
                       "clarity)"
        }
    )
    return spec, generate_coach_bot_object_array_image
