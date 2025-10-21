from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.measurement_comparison import (  # noqa: E402, E501
    draw_measurement_comparison,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.measurement_comparison import (  # noqa: E402, E501
    MeasuredObject,
    MeasurementComparison,
)

logger = logging.getLogger("coach_bot_tools.measurement_comparison")


def generate_coach_bot_measurement_comparison_image(
    objects: List[Dict[str, Any]]
) -> str:
    """
    Generate a measurement comparison visualization showing multiple objects with their lengths.
    
    Creates a visual comparison of 2-3 objects showing their relative lengths. Each object
    can be displayed with or without measurement units (buttons or unit squares). Useful
    for teaching measurement concepts, length comparison, and understanding measurement units.
    
    Parameters
    ----------
    objects : List[Dict[str, any]]
        List of 2-3 objects to compare, each containing:
        - object_name: Type of object (straw, arrow, pencil, etc.)
        - length: Length in measurement units (1-12)
        - label: Display label (e.g., "Pencil A", "Straw B")
        - unit: Measurement unit to display ("button", "unit_squares", or None)
        - unit_display_error: Optional error type ("gap", "overlap", or None)
        
    Returns
    -------
    str
        The URL of the generated measurement comparison image
    """
    
    # Use standardized logging
    object_count = len(objects)
    has_units = any(obj.get("unit") for obj in objects)
    has_errors = any(obj.get("unit_display_error") for obj in objects)
    log_tool_generation("measurement_comparison_image", object_count=object_count, 
                       has_units=has_units, has_errors=has_errors)
    
    # Convert input dictionaries to MeasuredObject instances
    # Let Pydantic handle enum conversions and validation automatically
    measured_objects = []
    for i, obj_data in enumerate(objects):
        try:
            measured_obj = MeasuredObject(
                object_name=obj_data["object_name"],  # Pydantic converts string to MeasuredItemName
                length=obj_data["length"],
                label=obj_data["label"],
                unit=obj_data.get("unit"),
                unit_display_error=obj_data.get("unit_display_error")
            )
            measured_objects.append(measured_obj)
        except ValueError as e:
            raise ValueError(f"Invalid data for object {i+1}: {str(e)}") from e
    
    # Create and validate the MeasurementComparison using Pydantic
    # This validates object count (2-3), unit consistency, and all field constraints
    measurement_comparison = MeasurementComparison(root=measured_objects)
    
    # Generate the image using the measurement comparison function
    image_file_path = draw_measurement_comparison(measurement_comparison)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_measurement_comparison_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for measurement comparison generation."""
    # Note: This uses an enhanced static spec because the wrapper interface is flattened
    # (takes List[Dict]) while the Pydantic model uses nested 
    # MeasurementComparison(root=List[MeasuredObject])
    spec = {
        "type": "function",
        "name": "generate_coach_bot_measurement_comparison_image",
        "description": (
            "Generate measurement comparison visualizations for teaching length concepts and "
            "measurement skills. Creates side-by-side comparisons of 2-3 everyday objects (straws, "
            "arrows, pencils) showing their relative lengths with optional measurement units "
            "(buttons or unit squares). Perfect for teaching measurement estimation, direct "
            "comparison, and unit counting. By default, shows ACCURATE measurements where the "
            "number of units exactly matches the length. Only add intentional display errors "
            "(gaps/overlaps) when explicitly requested for teaching measurement accuracy concepts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "objects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "object_name": {
                                "type": "string",
                                "enum": ["straw", "arrow", "pencil"],
                                "description": (
                                    "Type of everyday object to display in the comparison. Each "
                                    "object has a distinctive visual appearance: straws are thin "
                                    "cylindrical objects, arrows are pointed directional "
                                    "indicators, pencils are writing instruments."
                                )
                            },
                            "length": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 12,
                                "description": (
                                    "Length of the object measured in standardized units (1-12). "
                                    "This determines the visual length of the object and the "
                                    "number of measurement units displayed if units are enabled. "
                                    "Choose varied lengths to create meaningful comparisons."
                                )
                            },
                            "label": {
                                "type": "string",
                                "description": (
                                    "Clear display label shown above the object (e.g., 'Pencil A', "
                                    "'Straw B', 'Red Arrow'). Essential for distinguishing "
                                    "multiple objects of the same type. Use descriptive labels "
                                    "that help students identify and discuss each object."
                                ),
                                "maxLength": 20
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["button", "unit squares"],
                                "description": (
                                    "Optional measurement unit visualization to display along the "
                                    "object. 'button' shows circular button-like units, 'unit "
                                    "squares' shows square grid units. When present, all objects "
                                    "in the comparison must use the same unit type. Omit to show "
                                    "objects without measurement units for pure length estimation."
                                )
                            },
                            "unit_display_error": {
                                "type": "string",
                                "enum": ["gap", "overlap"],
                                "description": (
                                    "ONLY use when explicitly requested for teaching measurement "
                                    "errors. 'gap' shows FEWER units than the actual length "
                                    "(missing units error), 'overlap' shows MORE units than the "
                                    "actual length (extra overlapping units error). Examples: 5 "
                                    "units with 'gap' shows 4 units, 5 units with 'overlap' shows "
                                    "6 units. IMPORTANT: Omit this parameter entirely for normal "
                                    "accurate measurements - only include when the user "
                                    "specifically asks for measurement errors."
                                )
                            }
                        },
                        "required": ["object_name", "length", "label"]
                    },
                    "description": (
                        "Array of 2-3 objects for visual length comparison. Objects are displayed "
                        "horizontally aligned for easy comparison. When units are specified, all "
                        "objects must use the same unit type to ensure valid comparisons. Varies "
                        "lengths create educational contrast."
                    ),
                    "minItems": 2,
                    "maxItems": 3
                }
            },
            "required": ["objects"]
        }
    }
    return spec, generate_coach_bot_measurement_comparison_image
