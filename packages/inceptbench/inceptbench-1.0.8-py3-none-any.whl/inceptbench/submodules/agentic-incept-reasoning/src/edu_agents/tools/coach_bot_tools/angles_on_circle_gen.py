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

from content_generators.additional_content.stimulus_image.drawing_functions.angles_on_circle import (  # noqa: E402, E501
    draw_circle_angle_measurement,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.angle_on_circle import (  # noqa: E402, E501
    AngleRange,
    CircleAngle,
)

logger = logging.getLogger("coach_bot_tools.angles_on_circle")


def generate_coach_bot_angles_on_circle_image(
    angle_measure: int,
    start_position: int = 0,
    range_category: str = "basic",
    show_question: bool = False,
    sector_color: str = "lightgreen"
) -> str:
    """
    Generate a circle with degree markings for angle measurement exercises.
    
    Creates a circle with degree markings every 15° with major labels at cardinal
    directions and a shaded sector showing the angle to measure.
    
    Parameters
    ----------
    angle_measure : int
        The angle measure in degrees, must be a multiple of 15 (1-359)
    start_position : int, default 0
        Starting position of the angle in degrees (0° = rightmost position),
        must be a multiple of 15 (0-359)
    range_category : str, default "basic"
        Category of angle range: "basic" (1-180°), "intermediate" (181-359°), or "advanced"
    show_question : bool, default False
        Whether to show the measurement question in the diagram
    sector_color : str, default "lightgreen"
        Color of the shaded angle sector (any valid matplotlib color)
        
    Returns
    -------
    str
        The URL of the generated angle on circle image
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_angles_on_circle_image",
        angle_measure=angle_measure,
        start_position=start_position,
        range_category=range_category,
        show_question=show_question,
        sector_color=sector_color
    )
    
    # Convert string range_category to enum
    if range_category == "basic":
        range_enum = AngleRange.BASIC
    elif range_category == "intermediate":
        range_enum = AngleRange.INTERMEDIATE
    elif range_category == "advanced":
        range_enum = AngleRange.ADVANCED
    else:
        raise ValueError(f"Invalid range_category: {range_category}")
    
    # Create the CircleAngle stimulus description using Pydantic model validation
    circle_angle_data = CircleAngle(
        angle_measure=angle_measure,
        start_position=start_position,
        range_category=range_enum,
        show_question=show_question,
        sector_color=sector_color
    )
    
    # Generate the image using the angle measurement function
    image_file_path = draw_circle_angle_measurement(circle_angle_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_angles_on_circle_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for angles on circle generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_angles_on_circle_image",
        description=(
            "Generate a circle with degree markings for angle measurement exercises "
            "focused on geometric understanding and spatial reasoning development. "
            "Creates a circle with degree markings every 15° with major labels at "
            "cardinal directions (0°, 90°, 180°, 270°) and a customizable shaded "
            "sector showing the angle to measure. Perfect for teaching angle "
            "measurement concepts, protractor skills, and degree comprehension. "
            "Supports educational categorization (basic 1-180°, intermediate 181-359°, "
            "advanced for future expansion) and visual customization for enhanced "
            "learning experiences. Excellent for worksheets, assessments, interactive "
            "lessons, and geometric reasoning exercises."
        ),
        pydantic_model=CircleAngle,
        custom_descriptions={
            "angle_measure": (
                "The angle measure in degrees that will be highlighted in the shaded "
                "sector (1-359°, must be multiple of 15). This is the educational "
                "target angle for student measurement practice. Choose values "
                "appropriate for the learning objective: smaller angles (15°-90°) "
                "for introductory lessons, medium angles (105°-180°) for standard "
                "practice, larger angles (195°-359°) for advanced geometric concepts."
            ),
            "start_position": (
                "Starting position of the angle in degrees with 0° = rightmost "
                "position (must be multiple of 15, range 0-359°, default 0). This "
                "rotational offset allows positioning the angle sector for optimal "
                "educational presentation. Use 0° for standard orientation, 90° "
                "for vertical emphasis, or custom positions to align with specific "
                "learning activities and measurement objectives."
            ),
            "range_category": (
                "Educational category for angle range organization and curriculum "
                "alignment. Choose 'basic' for introductory angles (1-180°) focusing "
                "on acute, right, and obtuse angles; 'intermediate' for advanced "
                "angles (181-359°) covering reflex angles and full rotation concepts; "
                "'advanced' reserved for future educational expansions. This "
                "categorization helps maintain appropriate difficulty progression."
            ),
            "show_question": (
                "Whether to display the measurement question text directly in the "
                "diagram (default False). When True, adds educational text prompting "
                "students to measure the angle, creating self-contained assessment "
                "materials. When False, allows flexible question presentation in "
                "separate text for customizable instructional design."
            ),
            "sector_color": (
                "Color specification for the shaded angle sector using matplotlib "
                "color names ('lightgreen', 'blue', 'red') or hex codes ('#ff6b6b'). "
                "Strategic color choice enhances visual recognition and student "
                "engagement. Use contrasting colors for clarity, educational colors "
                "for thematic consistency, or distinctive colors for multi-angle "
                "comparison exercises."
            )
        }
    )
    return spec, generate_coach_bot_angles_on_circle_image
