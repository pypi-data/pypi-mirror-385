from __future__ import annotations

import logging
from typing import Callable, Dict, List

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.rulers import (  # noqa: E402
    draw_ruler_measured_objects,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.ruler import (  # noqa: E402
    MeasuredItem,
    MeasuredItemName,
    MeasurementUnit,
    Ruler,
    RulerStimulus,
)

logger = logging.getLogger("coach_bot_tools.rulers")


def generate_coach_bot_ruler_measurement_image(
    items: List[Dict[str, any]]
) -> str:
    """
    Generate rulers with measured objects for teaching measurement concepts.
    
    Creates realistic ruler visualizations with objects placed at specific positions
    for measurement activities. Supports both inch and centimeter rulers with proper
    tick marks and scaling. Useful for teaching measurement, estimation, and unit conversion.
    
    Important Ruler Limits:
    - Centimeter rulers: Maximum 12cm total length (start_position + length ≤ 12)
    - Inch rulers: Maximum 8 inches total length (start_position + length ≤ 8)
    - Rulers auto-adjust to fit objects but cannot exceed these limits
    
    Parameters
    ----------
    items : List[Dict[str, any]]
        List of measured item specifications (1-3 items maximum), each containing:
        - name: Object name - 'pencil', 'arrow', or 'straw'
        - length: Length of the object in the ruler's units
        - start_position: Starting position on ruler (default 0.0)
        - unit: Measurement unit - 'inches', 'centimeters', 'in', or 'cm'
        - label: Optional custom label (overrides default name)
        
    Returns
    -------
    str
        The URL of the generated ruler measurement image
    """
    
    # Use standardized logging
    log_tool_generation("ruler_measurement_image", item_count=len(items))
    
    # Convert List[Dict] to List[MeasuredItem] for Pydantic model
    # This handles interface flattening: simple Dict → complex MeasuredItem + Ruler objects
    measured_items = []
    for item_data in items:
        # Handle unit abbreviations (in, cm → inches, centimeters)
        unit_value = item_data['unit'].lower()
        if unit_value == 'in':
            unit_value = 'inches'
        elif unit_value == 'cm':
            unit_value = 'centimeters'
        
        # Create nested Ruler object with enum conversion
        ruler = Ruler(unit=MeasurementUnit(unit_value))
        
        # Create MeasuredItem with enum conversions and nested Ruler
        measured_item = MeasuredItem(
            name=MeasuredItemName(item_data['name'].lower()),
            length=float(item_data['length']),
            start_position=float(item_data.get('start_position', 0.0)),
            ruler=ruler,
            label=item_data.get('label')
        )
        measured_items.append(measured_item)
    
    # Create and validate the RulerStimulus using Pydantic
    # This handles all validation: item count (1-3), length/position ranges,
    # ruler size limits (12cm/8in), and enum validation
    ruler_stimulus = RulerStimulus(items=measured_items)
    
    # Generate the image using the ruler function
    image_file_path = draw_ruler_measured_objects(ruler_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_ruler_measurement_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for ruler measurement generation."""
    # Use enhanced static specification due to complex nested model transformation:
    # List[Dict] wrapper interface vs List[MeasuredItem] with nested Ruler objects
    spec = {
        "type": "function",
        "name": "generate_coach_bot_ruler_measurement_image",
        "description": (
            "Generate realistic ruler measurement visualizations for mathematics education "
            "focused on measurement concepts, unit understanding, and spatial reasoning skills. "
            "Creates accurate ruler images with objects positioned at specific measurements "
            "for teaching length estimation, measurement reading, unit conversion, and "
            "precision concepts. Supports both imperial (inches) and metric (centimeters) "
            "measurement systems with proper tick marks, numerical labels, and educational "
            "scaling. Perfect for elementary and middle school mathematics lessons covering "
            "measurement, estimation, data collection, and mathematical modeling. Objects "
            "include pencils, arrows, and straws with customizable positioning and labeling. "
            "CRITICAL PHYSICAL CONSTRAINTS: Centimeter rulers limited to 12cm maximum total "
            "length (start_position + object_length ≤ 12cm). Inch rulers limited to 8 inches "
            "maximum total length (start_position + object_length ≤ 8in). Rulers automatically "
            "adjust size to accommodate objects within these realistic limits. Excellent for "
            "worksheets, assessments, interactive learning activities, and hands-on "
            "measurement exercises that develop students' measurement literacy and "
            "mathematical reasoning skills."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 3,
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "enum": ["pencil", "arrow", "straw"],
                                "description": (
                                    "Object name for measurement visualization and educational "
                                    "context. Choose from: 'pencil' (familiar classroom object for "
                                    "practical measurement lessons), 'arrow' (geometric shape for "
                                    "directional measurement concepts), 'straw' (cylindrical "
                                    "object for length comparison activities). Object choice "
                                    "affects visual recognition and student engagement with "
                                    "measurement tasks."
                                )
                            },
                            "length": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 30,
                                "description": (
                                    "Length of the object in the specified measurement units (1-30 "
                                    "range). This value determines the object's span on the ruler "
                                    "and teaches students about measurement precision and unit "
                                    "relationships. CRITICAL CONSTRAINT: The total space required "
                                    "(start_position + length) must not exceed ruler limits: ≤12cm "
                                    "for centimeter rulers, ≤8in for inch rulers. Choose realistic "
                                    "educational values that fit within these physical constraints "
                                    "while providing meaningful measurement learning opportunities."
                                )
                            },
                            "start_position": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 25,
                                "description": (
                                    "Starting position of the object on the ruler (0-25 range, "
                                    "0.0 = zero mark). This parameter teaches students about "
                                    "measurement reference points, object positioning, and spatial "
                                    "relationships. Non-zero start positions demonstrate that "
                                    "objects don't always begin at the ruler's origin, developing "
                                    "advanced measurement reading skills. CRITICAL CONSTRAINT: "
                                    "Total space required (start_position + length) must fit "
                                    "within ruler limits. Use strategic positioning to create "
                                    "educational measurement scenarios while respecting physical "
                                    "constraints."
                                ),
                                "default": 0.0
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["inches", "centimeters", "in", "cm"],
                                "description": (
                                    "Measurement unit system for the ruler and object "
                                    "measurements. Choose from: 'inches' or 'in' (imperial system, "
                                    "max 8in total ruler length), 'centimeters' or 'cm' (metric "
                                    "system, max 12cm total ruler length). Unit selection affects "
                                    "ruler appearance, tick mark density, numerical labels, and "
                                    "educational focus. Imperial units teach fractions and "
                                    "traditional measurements. Metric units emphasize decimal "
                                    "relationships and international standards. Strategic unit "
                                    "choice enhances lesson objectives and student measurement "
                                    "literacy development."
                                )
                            },
                            "label": {
                                "type": "string",
                                "description": (
                                    "Optional custom label that overrides the default object name "
                                    "for enhanced educational context and personalization. Use "
                                    "descriptive labels that connect to lesson content: 'My "
                                    "Pencil', 'Classroom Ruler', 'Science Lab Tool', or "
                                    "subject-specific terminology. Custom labels improve student "
                                    "engagement, provide real-world connections, and support "
                                    "differentiated instruction approaches. Labels appear directly "
                                    "on the ruler visualization for clear object identification "
                                    "and measurement reference."
                                )
                            }
                        },
                        "required": ["name", "length", "unit"],
                        "additionalProperties": False
                    },
                    "description": (
                        "List of measured item specifications for comprehensive ruler-based "
                        "measurement education (1-3 items maximum for visual clarity). Each "
                        "item represents a complete measurement scenario with object, ruler, "
                        "and positioning data. CRITICAL PHYSICAL CONSTRAINTS enforce realistic "
                        "ruler limitations: Total ruler length = start_position + object_length. "
                        "Centimeter rulers: maximum 12cm total length for standard classroom "
                        "rulers. Inch rulers: maximum 8 inches total length for practical "
                        "educational tools. These constraints teach students about real-world "
                        "measurement tool limitations and promote accurate mathematical modeling. "
                        "Strategic item selection and positioning create diverse educational "
                        "opportunities: single items for basic measurement, multiple items for "
                        "comparison activities, varied positioning for advanced spatial reasoning."
                    )
                }
            },
            "required": ["items"]
        }
    }
    return spec, generate_coach_bot_ruler_measurement_image
