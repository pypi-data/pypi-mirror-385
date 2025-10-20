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

from content_generators.additional_content.stimulus_image.drawing_functions.protractor import (  # noqa: E402
    draw_protractor,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.protractor import (  # noqa: E402
    Protractor,
    ProtractorPoint,
)

logger = logging.getLogger("coach_bot_tools.protractor")


def generate_coach_bot_protractor_image(
    points: List[Dict[str, any]]
) -> str:
    """
    Generate a protractor image with labeled angle measurements.
    
    Creates a visual protractor with rays extending from the center point P to
    labeled points at specified angles. Useful for teaching angle measurement,
    protractor reading skills, and angle identification.
    
    Parameters
    ----------
    points : List[Dict[str, any]]
        List of exactly 4 points to mark on the protractor. Each point contains:
        - label: Point label, must be one of 'R', 'S', 'T', 'V'
        - degree: Angle measurement in degrees (5-180)
        Points must be at least 5 degrees apart from each other.
        
    Returns
    -------
    str
        The URL of the generated protractor image
    """
    
    # Use standardized logging
    log_tool_generation("protractor_image", points=points)
    
    # Validate input
    if len(points) != 4:
        raise ValueError("Exactly 4 points must be provided for the protractor")
    
    # Create ProtractorPoint objects
    protractor_points = []
    for point_data in points:
        if "label" not in point_data or "degree" not in point_data:
            raise ValueError("Each point must have 'label' and 'degree' fields")
            
        # Validate label
        valid_labels = ["R", "S", "T", "V"]
        if point_data["label"] not in valid_labels:
            raise ValueError(
                f"Point label must be one of {valid_labels}, got '{point_data['label']}'"
            )
            
        # Validate degree
        degree = point_data["degree"]
        if not (5 <= degree <= 180):
            raise ValueError(f"Degree must be between 5 and 180, got {degree}")
        
        protractor_point = ProtractorPoint(
            label=point_data["label"],
            degree=degree
        )
        protractor_points.append(protractor_point)
    
    # Check for duplicate labels
    labels = [p.label for p in protractor_points]
    if len(set(labels)) != len(labels):
        raise ValueError("All point labels must be unique")
    
    # Create the Protractor stimulus
    protractor = Protractor(root=protractor_points)
    
    # Generate the image using the protractor function
    image_file_path = draw_protractor(protractor)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_protractor_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for protractor generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_protractor_image",
        description=(
            "Generate a protractor image with labeled angle measurements. Creates a visual "
            "protractor with rays extending from center point P to labeled points at "
            "specified angles. Useful for teaching angle measurement and protractor reading skills."
        ),
        pydantic_model=Protractor,
        parameter_wrapper_name="points",
        custom_descriptions={
            "points": (
                "Exactly 4 points to mark on the protractor. Points must be at least 5 degrees "
                "apart."
            )
        }
    )
    return spec, generate_coach_bot_protractor_image
