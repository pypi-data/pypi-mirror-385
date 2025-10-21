from __future__ import annotations

import logging
from typing import Callable, Optional

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.measurements import (  # noqa: E402
    draw_measurement,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.measurements_model import (  # noqa: E402, E501
    Measurements,
)

logger = logging.getLogger("coach_bot_tools.measurements")


def generate_coach_bot_measurement_image(
    measurement: float,
    units: str,
    color: Optional[str] = None
) -> str:
    """
    Generate a measurement visualization showing a specific measurement on measuring instruments.
    
    Creates visual representations of measurements using appropriate measuring instruments:
    - For liquids (milliliters, liters): Shows measuring cups with liquid levels
    - For weight (grams, kilograms): Shows analog scales with measurement hands
    
    Useful for teaching measurement reading, unit conversion, and measurement estimation.
    
    Parameters
    ----------
    measurement : float
        The measurement value. Decimal portions must be 0.25, 0.5, or 0.75 if used.
        Maximum values: liters (100), milliliters (1000), grams (1000), kilograms (1000)
    units : str
        The units of measurement ("milliliters", "liters", "grams", "kilograms")
    color : Optional[str]
        Color for liquid measurements ("red", "lightblue", "green", "yellow", "orange", "purple")
        
    Returns
    -------
    str
        The URL of the generated measurement image
    """
    
    # Use standardized logging
    log_tool_generation("measurement_image", measurement=measurement, units=units, color=color)
    
    # Create and validate Measurements using Pydantic
    # This handles all validation: range limits, decimal constraints, unit/color validation
    measurements = Measurements(
        measurement=measurement,
        units=units,
        color=color
    )
    
    # Generate the image using the measurements function
    image_file_path = draw_measurement(measurements)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_measurement_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for measurement generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_measurement_image",
        description=(
            "Generate measurement visualizations for teaching measurement concepts using realistic "
            "measuring instruments. Creates educational images showing specific measurements on "
            "appropriate tools: measuring cups with liquid levels for volume (milliliters, "
            "liters), or analog scales with measurement indicators for mass (grams, kilograms). "
            "Perfect for teaching measurement reading, unit conversion, estimation skills, and "
            "real-world measurement applications. Supports customizable liquid colors for enhanced "
            "visual learning."
        ),
        pydantic_model=Measurements,
        custom_descriptions={
            "measurement": (
                "The specific measurement value to display on the instrument. Supports decimal "
                "values but only in quarters (0.25, 0.5, 0.75) for realistic measurement "
                "precision. Range limits: liters (0-100), milliliters/grams/kilograms (0-1000)."
            ),
            "units": (
                "The unit of measurement determining the instrument type: 'milliliters' and "
                "'liters' show measuring cups with liquid, 'grams' and 'kilograms' show analog "
                "scales with dials."
            ),
            "color": (
                "Optional color for liquid measurements only (ignored for weight measurements). "
                "Choose from educational-friendly colors: red, lightblue, green, yellow, orange, "
                "purple."
            )
        }
    )
    return spec, generate_coach_bot_measurement_image
