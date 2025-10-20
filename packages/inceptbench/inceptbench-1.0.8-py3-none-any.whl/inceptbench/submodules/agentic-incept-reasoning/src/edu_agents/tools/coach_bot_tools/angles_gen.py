from __future__ import annotations

import logging
from typing import Callable, Dict, List

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.angles import (  # noqa: E402
    draw_fractional_angle_circle,
    generate_angle_types,
    generate_single_angle_type,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.angles import (  # noqa: E402
    Angle,
    AngleList,
    SingleAngle,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.fractional_angle import (  # noqa: E402, E501
    FractionalAngle,
)

logger = logging.getLogger("coach_bot_tools.angles")

def generate_coach_bot_single_angle_image(
    measure: int,
) -> str:
    """
    Generate a visual representation of a single angle using rays.
    
    Creates a clean angle diagram with two rays emanating from a vertex point,
    with appropriate angle markings (arc for general angles, square for right angles).
    
    Parameters
    ----------
    measure : int
        The angle measure in degrees (1-360)
        
    Returns
    -------
    str
        The URL of the generated single angle image
    """
    
    # Use standardized logging
    log_tool_generation("single_angle_image", measure=measure)
    
    # Create the SingleAngle stimulus description
    single_angle_data = SingleAngle(measure=measure)
    
    # Generate the image using the angle generation function
    image_file_path = generate_single_angle_type(single_angle_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_multiple_angles_image(
    angles: List[Dict[str, any]],
) -> str:
    """
    Generate a visual representation of multiple angles side by side.
    
    Creates a diagram showing multiple angles arranged horizontally, each with
    its own vertex and rays, labeled appropriately.
    
    Parameters
    ----------
    angles : List[Dict[str, any]]
        List of angle specifications, each containing:
        - measure: int (angle measure in degrees, 1-360)  
        - label: str (label for the angle, max 10 characters)
        
    Returns
    -------
    str
        The URL of the generated multiple angles image
    """
    
    # Use standardized logging  
    log_tool_generation("multiple_angles_image", angles=angles)
    
    # Create Angle objects from the input data
    angle_objects = []
    for angle_data in angles:
        angle_obj = Angle(
            measure=angle_data["measure"],
            label=angle_data["label"]
        )
        angle_objects.append(angle_obj)
    
    # Create the AngleList stimulus description
    angle_list_data = AngleList(angle_objects)
    
    # Generate the image using the angle generation function
    image_file_path = generate_angle_types(angle_list_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_fractional_angle_image(
    numerator: int,
    denominator: int,
    sector_color: str = "lightblue",
    show_fraction_label: bool = True,
    show_angle_measure: bool = False
) -> str:
    """
    Generate a circle divided into equal parts with a shaded sector representing a fraction.
    
    Creates a visual representation of how fractions relate to angle measures
    in a complete circle (360 degrees).
    
    Parameters
    ----------
    numerator : int
        The numerator of the fraction (number of shaded parts)
    denominator : int
        The denominator of the fraction (total number of parts)
    sector_color : str, default "lightblue"
        Color of the shaded sector (any valid matplotlib color)
    show_fraction_label : bool, default True
        Whether to show the fraction label on the diagram
    show_angle_measure : bool, default False
        Whether to show the calculated angle measure
        
    Returns
    -------
    str
        The URL of the generated fractional angle image
    """
    
    # Use standardized logging
    log_tool_generation("fractional_angle_image", numerator=numerator, 
                       denominator=denominator, sector_color=sector_color,
                       show_fraction_label=show_fraction_label,
                       show_angle_measure=show_angle_measure)
    
    # Create the FractionalAngle stimulus description
    fractional_angle_data = FractionalAngle(
        numerator=numerator,
        denominator=denominator,
        sector_color=sector_color,
        show_fraction_label=show_fraction_label,
        show_angle_measure=show_angle_measure
    )
    
    # Generate the image using the angle generation function
    image_file_path = draw_fractional_angle_circle(fractional_angle_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_single_angle_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for single angle generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_single_angle_image",
        description=(
            "Generate a visual representation of a single angle using rays. "
            "Creates a clean angle diagram with two rays emanating from a vertex point, "
            "with appropriate angle markings (arc for general angles, square for right angles)."
        ),
        pydantic_model=SingleAngle
    )
    return spec, generate_coach_bot_single_angle_image


def generate_coach_bot_multiple_angles_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for multiple angles generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_multiple_angles_image",
        description=(
            "Generate a visual representation of multiple angles side by side. "
            "Creates a diagram showing multiple angles arranged horizontally, each "
            "with its own vertex and rays, labeled appropriately."
        ),
        pydantic_model=AngleList,
        parameter_wrapper_name="angles",
        custom_descriptions={
            "angles": "List of angles to display, each with measure and label"
        }
    )
    return spec, generate_coach_bot_multiple_angles_image


def generate_coach_bot_fractional_angle_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for fractional angle generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_fractional_angle_image",
        description=(
            "Generate a circle divided into equal parts with a shaded sector representing "
            "a fraction. Creates a visual representation of how fractions relate to angle "
            "measures in a complete circle (360 degrees)."
        ),
        pydantic_model=FractionalAngle
    )
    return spec, generate_coach_bot_fractional_angle_image
