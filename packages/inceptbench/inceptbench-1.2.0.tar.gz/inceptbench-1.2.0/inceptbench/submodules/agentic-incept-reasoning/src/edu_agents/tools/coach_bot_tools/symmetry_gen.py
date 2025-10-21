from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional, Union

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.symmetry_lines import (  # noqa: E402, E501
    generate_lines_of_symmetry,
    generate_symmetry_identification_task,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.symmetry_identification_model import (  # noqa: E402, E501
    SymmetryIdentification,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.symmetry_lines_model import (  # noqa: E402, E501
    LinesOfSymmetry,
)

logger = logging.getLogger("coach_bot_tools.symmetry")


def generate_coach_bot_lines_of_symmetry_image(
    shape_coordinates: List[List[float]],
    lines: List[Dict[str, Union[str, float, None]]]
) -> str:
    """
    Generate diagrams showing lines of symmetry for geometric shapes.
    
    Creates educational diagrams for teaching symmetry concepts with one true line 
    of symmetry and optional distractor lines. Perfect for assessment where students 
    identify which line is the actual line of symmetry.
    
    CRITICAL SYMMETRY REQUIREMENTS:
    - Exactly ONE line must be a mathematically true line of symmetry for the shape
    - Other lines should be "distractor" lines that are NOT true lines of symmetry
    - All lines must pass through the shape (have points inside the shape boundary)
    - Shape coordinates must form a non-self-intersecting polygon
    - Use symmetric shapes like rectangles, triangles, diamonds for predictable symmetry
    
    Parameters
    ----------
    shape_coordinates : List[List[float]]
        Vertices of a non-self-intersecting polygon (minimum 3 points)
        Each coordinate is [x, y]. Vertices should be in order (clockwise/counterclockwise)
        Example: [[-2, -1], [2, -1], [2, 1], [-2, 1]] for rectangle
    lines : List[Dict[str, Union[str, float, None]]]
        Line specifications (1-4 lines), each containing:
        - slope: Line slope (number) or null for vertical lines
        - intercept: Y-intercept (non-vertical) or X-intercept (vertical lines)  
        - label: Single character label ('A', 'B', 'C', or 'D')
        
        IMPORTANT: Exactly one line must be a true line of symmetry for the shape.
        Other lines should pass through the shape but NOT be lines of symmetry.
        
    Returns
    -------
    str
        The URL of the generated lines of symmetry image
        
    Examples
    --------
    Rectangle with vertical symmetry line and horizontal distractor:
    shape_coordinates = [[-2, -1], [2, -1], [2, 1], [-2, 1]]
    lines = [
        {"slope": None, "intercept": 0, "label": "A"},      # True symmetry (vertical)
        {"slope": 0, "intercept": 0.5, "label": "B"}       # False symmetry (horizontal offset)
    ]
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_lines_of_symmetry_image",
        shape_coordinates=shape_coordinates,
        lines=lines
    )
    
    # Create the LinesOfSymmetry stimulus using Pydantic model validation
    # Pydantic automatically handles List[Dict] → List[Line] conversion and all validation
    symmetry_stimulus = LinesOfSymmetry(
        shape_coordinates=shape_coordinates,
        lines=lines  # Pydantic handles Dict → Line conversion automatically
    )
    
    # Generate the image using the lines of symmetry function
    image_file_path = generate_lines_of_symmetry(symmetry_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_symmetry_identification_image(
    shape_type: str = "flower",
    shape_coordinates: Optional[List[List[float]]] = None,
    line: Dict[str, Union[str, float, None]] = None
) -> str:
    """
    Generate symmetry identification task diagrams for educational assessment.
    
    Creates clean symmetry identification tasks with predefined or custom shapes 
    and a single dashed line for students to evaluate. Supports multiple shape 
    types including flowers, geometric shapes, and everyday objects.
    
    Parameters
    ----------
    shape_type : str
        Type of shape to generate. Options: 'flower', 'sun', 'diamond', 'heart', 
        'house', 'wheel', 'football', 'polygon'
    shape_coordinates : Optional[List[List[float]]]
        Custom shape coordinates (only used if shape_type is 'polygon')
        Each coordinate is [x, y] format
    line : Dict[str, Union[str, float, None]]
        Line specification containing:
        - slope: Slope of the line (number or null for vertical lines)
        - intercept: Y-intercept for non-vertical, X-intercept for vertical lines
        - label: Descriptive label ('vertical', 'horizontal', 'diagonal', 'not_symmetry')
        
    Returns
    -------
    str
        The URL of the generated symmetry identification image
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_symmetry_identification_image",
        shape_type=shape_type,
        shape_coordinates=shape_coordinates,
        line=line
    )
    
    # Pydantic model will handle shape_type and shape_coordinates validation
    # Use default coordinates for predefined shapes
    if not shape_coordinates and shape_type != 'polygon':
        shape_coordinates = [[0, 0]]
    
    # Convert singular line parameter to plural lines for Pydantic model
    # Handle interface flattening: wrapper takes 'line: Dict' but model expects 
    # 'lines: List[IdentificationLine]'
    lines_data = []
    if line:
        lines_data = [line]  # Convert singular to list
    
    # Create the SymmetryIdentification stimulus using Pydantic model validation
    # Pydantic handles List[Dict] → List[IdentificationLine] conversion and validation
    identification_stimulus = SymmetryIdentification(
        shape_type=shape_type,
        shape_coordinates=shape_coordinates or [[0, 0]],  # Use default for predefined shapes  # noqa: E501
        lines=lines_data  # Pydantic handles conversion automatically
    )
    
    # Generate the image using the symmetry identification function
    image_file_path = generate_symmetry_identification_task(identification_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_lines_of_symmetry_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for lines of symmetry generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_lines_of_symmetry_image",
        description=(
            "Generate educational symmetry diagrams focused on geometric reasoning and "
            "spatial analysis skills development. Creates comprehensive symmetry exercises "
            "with one mathematically true line of symmetry and optional distractor lines "
            "for assessment and critical thinking. CRITICAL EDUCATIONAL REQUIREMENT: "
            "Exactly ONE line must be a true line of symmetry for the shape, with other "
            "lines serving as educational 'distractors' that pass through the shape but "
            "are NOT true lines of symmetry. Perfect for assessments where students "
            "identify the correct line of symmetry among multiple options. Supports "
            "comprehensive validation including polygon self-intersection checking, line "
            "positioning within shape boundaries, and mathematical symmetry verification. "
            "Excellent for worksheets, interactive exercises, geometric reasoning "
            "development, and spatial understanding enhancement."
        ),
        pydantic_model=LinesOfSymmetry,
        custom_descriptions={
            "shape_coordinates": (
                "Vertices of a non-self-intersecting polygon in order defining the "
                "geometric shape for symmetry analysis (minimum 3 points). Use simple "
                "symmetric shapes like rectangles [[-2,-1],[2,-1],[2,1],[-2,1]], "
                "squares, or isosceles triangles for predictable symmetry lines and "
                "clear educational outcomes. Each coordinate is [x, y] format. "
                "Vertices must be ordered consistently (clockwise or counterclockwise) "
                "without crossing edges. Avoid complex or irregular shapes that may "
                "have no clear lines of symmetry or multiple ambiguous symmetry lines."
            ),
            "lines": (
                "Line specifications (1-4 lines maximum) where exactly ONE must be a "
                "mathematically true line of symmetry for the given shape. Other lines "
                "should be educational 'distractors' that pass through the shape but "
                "are NOT true lines of symmetry. Each line contains: slope (number or "
                "null for vertical lines), intercept (y-intercept for non-vertical, "
                "x-intercept for vertical lines), and label (single character 'A', 'B', "
                "'C', or 'D'). CRITICAL: All lines must have points strictly inside the "
                "shape boundary, not just touch edges. This enables effective assessment "
                "where students analyze multiple options to identify the true symmetry line."
            )
        }
    )
    return spec, generate_coach_bot_lines_of_symmetry_image


def generate_coach_bot_symmetry_identification_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for symmetry identification generation."""
    # Use enhanced static specification due to interface flattening:
    # Wrapper takes 'line: Dict' but Pydantic model expects 'lines: List[IdentificationLine]'
    spec = {
        "type": "function",
        "name": "generate_coach_bot_symmetry_identification_image",
        "description": (
            "Generate symmetry identification task diagrams for educational assessment "
            "focused on spatial reasoning and geometric understanding development. "
            "Creates clean, focused symmetry identification exercises with predefined "
            "shape types (flower, sun, diamond, heart, house, wheel, football) or "
            "custom polygon shapes and a single dashed line for students to evaluate "
            "as a line of symmetry. Perfect for 'Is this a line of symmetry?' assessments "
            "and critical thinking exercises. Supports educational progression from "
            "familiar everyday objects to abstract geometric shapes. The generated "
            "diagrams provide clear visual feedback for symmetry concept development "
            "and spatial analysis skills. Excellent for worksheets, interactive "
            "lessons, assessment activities, and geometric reasoning practice."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "shape_type": {
                    "type": "string",
                    "enum": [
                        "flower", "sun", "diamond", "heart", 
                        "house", "wheel", "football", "polygon"
                    ],
                    "description": (
                        "Type of shape for symmetry identification analysis. Educational "
                        "shape options: 'flower' (natural symmetry, engaging for younger "
                        "students), 'sun' (radial symmetry concepts), 'diamond' (clear "
                        "geometric symmetry), 'heart' (familiar asymmetric challenges), "
                        "'house' (everyday object analysis), 'wheel' (circular symmetry), "
                        "'football' (oval symmetry concepts), 'polygon' (custom geometric "
                        "shapes requiring shape_coordinates). Choose based on learning "
                        "objectives and student developmental level."
                    ),
                    "default": "flower"
                },
                "shape_coordinates": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Coordinate pair [x, y] for polygon vertices"
                    },
                    "minItems": 3,
                    "description": (
                        "Custom polygon coordinates required ONLY when shape_type is "
                        "'polygon'. Define vertices in order (clockwise or counterclockwise) "
                        "to create the geometric shape for symmetry analysis. Each coordinate "
                        "is [x, y] format. Use simple, symmetric polygons like rectangles, "
                        "triangles, or regular polygons for clear symmetry identification "
                        "exercises. Ignored for predefined shape types (flower, sun, etc.)."
                    )
                },
                "line": {
                    "type": "object",
                    "properties": {
                        "slope": {
                            "type": ["number", "null"],
                            "description": (
                                "Slope of the evaluation line for symmetry assessment "
                                "(number for angled lines, null for vertical lines). "
                                "Strategic slope selection creates targeted learning: "
                                "0 for horizontal symmetry, null for vertical symmetry, "
                                "1 for diagonal symmetry, other values for custom angles. "
                                "Choose slopes that highlight the shape's symmetry properties."
                            )
                        },
                        "intercept": {
                            "type": "number",
                            "description": (
                                "Line intercept for positioning the evaluation line "
                                "(y-intercept for non-vertical lines, x-intercept for "
                                "vertical lines). Strategic positioning determines whether "
                                "the line creates true symmetry or serves as an educational "
                                "distractor. Use 0 for lines through center, offset values "
                                "for challenging non-symmetry examples."
                            )
                        },
                        "label": {
                            "type": "string",
                            "enum": ["vertical", "horizontal", "diagonal", "not_symmetry"],
                            "description": (
                                "Descriptive label indicating the line orientation and "
                                "educational purpose. Use 'vertical' for up-down symmetry "
                                "assessment, 'horizontal' for left-right analysis, "
                                "'diagonal' for angled symmetry evaluation, 'not_symmetry' "
                                "for lines that deliberately do NOT create symmetry for "
                                "critical thinking exercises and misconception identification."
                            )
                        }
                    },
                    "required": ["slope", "intercept", "label"],
                    "description": (
                        "Single line specification for symmetry evaluation exercise. "
                        "The line will be displayed as a dashed line overlaid on the "
                        "shape for students to analyze and determine if it represents "
                        "a true line of symmetry. Strategic line positioning enables "
                        "targeted assessment of symmetry understanding and spatial "
                        "reasoning skills development."
                    )
                }
            },
            "required": ["shape_type"]
        }
    }
    return spec, generate_coach_bot_symmetry_identification_image
