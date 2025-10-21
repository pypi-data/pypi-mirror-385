from __future__ import annotations

import logging
from typing import Callable

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.divide_items_into_array import (  # noqa: E402, E501
    draw_divide_items_into_array,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.divide_items_into_array import (  # noqa: E402, E501
    DivideItemsIntoArray,
)

logger = logging.getLogger("coach_bot_tools.divide_items_into_array")


def generate_coach_bot_divide_items_into_array_image(
    num_rows: int,
    num_columns: int
) -> str:
    """
    Generate a visual representation of items arranged in a rectangular array.
    
    Creates an image showing colored circles arranged in rows and columns to form 
    a grid pattern. Each row is bordered for visual clarity. Useful for teaching 
    multiplication, area concepts, and rectangular arrays.
    
    Parameters
    ----------
    num_rows : int
        The number of rows in the array (1-10)
    num_columns : int
        The number of columns in the array (1-10)
        
    Returns
    -------
    str
        The URL of the generated array image
    """
    
    log_tool_generation(
        "generate_coach_bot_divide_items_into_array_image",
        num_rows=num_rows,
        num_columns=num_columns
    )
    
    # Create and validate the DivideItemsIntoArray stimulus description
    divide_array = DivideItemsIntoArray(
        num_rows=num_rows,
        num_columns=num_columns
    )
    
    # Generate the image using the divide items into array function
    image_file_path = draw_divide_items_into_array(divide_array)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_divide_items_into_array_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for divide items into array generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_divide_items_into_array_image",
        description=(
            "Generate a visual representation of items arranged in a rectangular array for "
            "teaching multiplication and area concepts. Creates an image showing colored circles "
            "arranged in rows and columns to form a grid pattern with row borders for visual "
            "clarity. Perfect for elementary mathematics instruction, rectangular array "
            "visualization, multiplication understanding, and area model teaching. Supports 1-10 "
            "rows and 1-10 columns with automatic validation of educational constraints."
        ),
        pydantic_model=DivideItemsIntoArray
    )
    return spec, generate_coach_bot_divide_items_into_array_image
