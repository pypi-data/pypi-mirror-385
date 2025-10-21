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

from content_generators.additional_content.stimulus_image.drawing_functions.divide_into_equal_groups import (  # noqa: E402, E501
    draw_divide_into_equal_groups,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.divide_into_equal_groups import (  # noqa: E402, E501
    DivideIntoEqualGroups,
)

logger = logging.getLogger("coach_bot_tools.divide_into_equal_groups")


def generate_coach_bot_divide_into_equal_groups_image(
    number_of_dots_per_group: int,
    number_of_groups: int
) -> str:
    """
    Generate a visual representation of dots divided into equal groups.
    
    Creates an image showing big circles (groups) with small colored dots inside each group.
    Useful for teaching division concepts, equal grouping, and multiplication arrays.
    
    Parameters
    ----------
    number_of_dots_per_group : int
        The number of dots in each group (1-10)
    number_of_groups : int
        The number of groups to create (1-10)
        
    Returns
    -------
    str
        The URL of the generated equal groups image
    """
    
    log_tool_generation(
        "generate_coach_bot_divide_into_equal_groups_image",
        number_of_dots_per_group=number_of_dots_per_group,
        number_of_groups=number_of_groups
    )
    
    # Create and validate the DivideIntoEqualGroups stimulus description
    divide_groups = DivideIntoEqualGroups(
        number_of_dots_per_group=number_of_dots_per_group,
        number_of_groups=number_of_groups
    )
    
    # Generate the image using the divide into equal groups function
    image_file_path = draw_divide_into_equal_groups(divide_groups)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_divide_into_equal_groups_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for divide into equal groups generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_divide_into_equal_groups_image",
        description=(
            "Generate a visual representation of dots divided into equal groups for teaching "
            "division and multiplication concepts. Creates an image showing big circles (groups) "
            "with small colored dots inside each group. Perfect for elementary mathematics "
            "instruction, visual division representation, equal grouping exercises, and "
            "multiplication arrays. Supports 1-10 dots per group and 1-10 groups with automatic "
            "validation of educational constraints."
        ),
        pydantic_model=DivideIntoEqualGroups
    )
    return spec, generate_coach_bot_divide_into_equal_groups_image
