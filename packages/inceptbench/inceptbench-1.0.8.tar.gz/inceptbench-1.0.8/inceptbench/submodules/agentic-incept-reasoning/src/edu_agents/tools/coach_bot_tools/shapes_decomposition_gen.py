from __future__ import annotations

import logging
from typing import Callable, List, Optional, Union

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.shapes_decomposition import (  # noqa: E402, E501
    create_dimensional_compound_area_figure,
    create_rhombus_with_diagonals_figure,
    create_shape_decomposition,
    create_shape_decomposition_decimal_only,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.shapes_decomposition import (  # noqa: E402, E501
    RhombusDiagonalsDescription,
    ShapeDecomposition,
)

logger = logging.getLogger("coach_bot_tools.shapes_decomposition")


def _validate_shape_decomposition_params(
    title: str,
    units: str,
    shapes: List[List[List[Union[int, float]]]],
    labels: List[List[List[Union[int, float]]]],
    gridlines: bool,
    shaded: Optional[List[int]] = None
) -> None:
    """
    Shared validation function for all shape decomposition tools.
    Validates all constraints to prevent Pydantic validation errors.
    """
    # Validate input parameters
    if not title or len(title) > 40:
        raise ValueError("Title must be 1-40 characters")
    if not units or len(units) > 3:
        raise ValueError("Units must be 1-3 characters")
    if units not in ['cm', 'm', 'in', 'ft']:
        raise ValueError("Units must be 'cm', 'm', 'in', or 'ft'")
    
    # Validate shapes
    if not shapes:
        raise ValueError("At least one shape must be provided")
    for i, shape in enumerate(shapes):
        if len(shape) < 3:
            raise ValueError(f"Shape {i} must have at least 3 points")
        for j, point in enumerate(shape):
            if len(point) != 2:
                raise ValueError(f"Shape {i}, point {j} must have exactly 2 coordinates")
    
    # Validate labels format
    for i, label in enumerate(labels):
        if len(label) != 2:
            raise ValueError(f"Label {i} must have exactly 2 points (start and end)")
        for j, point in enumerate(label):
            if len(point) != 2:
                raise ValueError(f"Label {i}, point {j} must have exactly 2 coordinates")
    
    # Validate that labels don't overlap (share 2+ common points)
    def generate_label_points(label):
        """Generate all points along a label line segment."""
        (x1, y1), (x2, y2) = label
        points = []
        if x1 == x2:  # Vertical line
            points = [(x1, y) for y in range(min(int(y1), int(y2)), max(int(y1), int(y2)) + 1)]
        elif y1 == y2:  # Horizontal line
            points = [(x, y1) for x in range(min(int(x1), int(x2)), max(int(x1), int(x2)) + 1)]
        else:
            raise ValueError(f"Label {label} must be horizontal (same y) or vertical (same x)")
        return points
    
    def labels_share_common_points(label1, label2):
        """Check if two labels share 2 or more common points."""
        points1 = set(generate_label_points(label1))
        points2 = set(generate_label_points(label2))
        common_points = points1 & points2
        return len(common_points) >= 2
    
    # Check all label pairs for overlap
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            label1, label2 = labels[i], labels[j]
            try:
                if labels_share_common_points(label1, label2):
                    raise ValueError(
                        f"Labels {label1} and {label2} share 2+ common points and cannot overlap. "
                        f"Ensure dimension labels don't have overlapping ranges on the same axis."
                    )
            except ValueError as e:
                if "must be horizontal" in str(e):
                    raise e  # Re-raise the horizontal/vertical validation error
                raise e  # Re-raise the overlap error
    
    # Validate label positioning relative to shapes (prevent labels inside shapes)
    def point_in_shape(point, shape_points):
        """Check if a point is inside a polygon using ray casting algorithm."""
        x, y = point
        n = len(shape_points)
        inside = False
        
        p1x, p1y = shape_points[0]
        for i in range(1, n + 1):
            p2x, p2y = shape_points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def validate_label_positioning(label, all_shapes):
        """Validate that label is not completely inside any shape."""
        (x1, y1), (x2, y2) = label
        midpoint_x = (x1 + x2) / 2
        midpoint_y = (y1 + y2) / 2
        
        for shape_idx, shape in enumerate(all_shapes):
            if point_in_shape((midpoint_x, midpoint_y), shape):
                # Label midpoint is inside this shape - check if it's on boundary
                # Generate perpendicular points to check if both are inside
                if x1 == x2:  # Vertical label
                    perp_points = [
                        (midpoint_x + 1, midpoint_y),
                        (midpoint_x - 1, midpoint_y)
                    ]
                else:  # Horizontal label
                    perp_points = [
                        (midpoint_x, midpoint_y + 1),
                        (midpoint_x, midpoint_y - 1)
                    ]
                
                # Check if both perpendicular points are inside the shape
                both_inside = all(point_in_shape(p, shape) for p in perp_points)
                if both_inside:
                    raise ValueError(
                        f"Label {label} is positioned completely inside shape {shape_idx}. "
                        f"Labels must be on shape boundaries/edges or outside shapes, not inside. "
                        f"Move the label to an edge of the shape or outside the shape area."
                    )
    
    # Check all labels for proper positioning
    for i, label in enumerate(labels):
        try:
            validate_label_positioning(label, shapes)
        except ValueError as e:
            raise ValueError(f"Label {i}: {str(e)}") from e
    
    # Validate gridlines constraint
    if not gridlines:
        has_horizontal = any(label[0][1] == label[1][1] for label in labels)
        has_vertical = any(label[0][0] == label[1][0] for label in labels)
        if not (has_horizontal and has_vertical):
            raise ValueError(
                "When gridlines=False, you must provide at least one horizontal label "
                "(same y coordinates) AND one vertical label (same x coordinates)."
            )
    
    # Validate shaded indices
    if shaded:
        for idx in shaded:
            if not isinstance(idx, int) or idx < 0 or idx >= len(shapes):
                raise ValueError(f"Shaded index {idx} is invalid (must be 0-{len(shapes)-1})")


def generate_coach_bot_shape_decomposition_image(
    title: str,
    units: str,
    gridlines: bool,
    shapes: List[List[List[Union[int, float]]]],
    labels: List[List[List[Union[int, float]]]],
    shaded: Optional[List[int]] = None,
    decimal_only: bool = False
) -> str:
    """
    Generate shape decomposition diagrams for area and perimeter problems.
    
    Creates geometric diagrams with labeled dimensions for teaching area calculation,
    perimeter measurement, and shape decomposition strategies. Supports both regular
    and compound shapes with customizable labeling and shading.
    
    🚨 CRITICAL LABEL POSITIONING CONSTRAINTS:
    - Labels must be horizontal (same y) or vertical (same x) line segments
    - Labels CANNOT share 2+ common points with each other
    - 🚨 CRITICAL: Same-length labels CANNOT have overlapping coordinate ranges
      * Two horizontal labels of same length cannot span same x-range
      * Two vertical labels of same length cannot span same y-range  
    - 🚨 CRITICAL: Labels must be positioned ON or ADJACENT TO shape boundaries/edges
    - Labels CANNOT be completely inside shapes (validation error: "Label positioned completely "
    "inside shape")
    - Labels CANNOT be too far from shapes (max 5 units away from any shape edge)
    - When gridlines=False: Must have at least one horizontal AND one vertical label
    - ✅ CORRECT: Label [[0,0],[4,0]] for bottom edge of rectangle [[0,0],[4,0],[4,3],[0,3]]
    - ✅ CORRECT: Label [[0,0],[0,3]] for left edge of rectangle [[0,0],[4,0],[4,3],[0,3]]
    - ❌ WRONG: Labels [[0,0],[20,0]] and [[0,12],[20,12]] (same length, same x-range 0-20)
    - ❌ WRONG: Label [[2,2],[2,10]] inside rectangle (causes "inside shape" error)
    - ❌ WRONG: Label [[10,10],[12,10]] too far from shapes (causes "too far" error)
    
    Parameters
    ----------
    title : str
        Title for the diagram (max 40 characters)
    units : str
        Unit abbreviation - must be 'cm', 'm', 'in', or 'ft' (max 3 characters)
    gridlines : bool
        Whether to show grid lines within shapes
    shapes : List[List[List[Union[int, float]]]]
        List of shapes, each defined by coordinate points [[x1,y1], [x2,y2], ...]
    labels : List[List[List[Union[int, float]]]]
        Dimension labels as line segments [[x1,y1], [x2,y2]] for measurements
    shaded : Optional[List[int]]
        Indices of shapes to shade (for subtraction problems)
    decimal_only : bool
        Whether to force decimal-only labels (no fractions)
        
    Returns
    -------
    str
        The URL of the generated shape decomposition image
    """
    
    log_tool_generation("generate_coach_bot_shape_decomposition_image", 
                        title=title, units=units, gridlines=gridlines, decimal_only=decimal_only,
                        shapes_count=len(shapes), labels_count=len(labels), shaded=shaded)
    
    # Use shared validation function
    _validate_shape_decomposition_params(title, units, shapes, labels, gridlines, shaded)
    
    # Create the ShapeDecomposition stimulus
    shape_decomp = ShapeDecomposition(
        title=title,
        units=units,
        gridlines=gridlines,
        shapes=shapes,
        labels=labels,
        shaded=shaded or []
    )
    
    # Generate the image using appropriate function
    if decimal_only:
        image_file_path = create_shape_decomposition_decimal_only(shape_decomp)
    else:
        image_file_path = create_shape_decomposition(shape_decomp)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_compound_area_figure_image(
    title: str,
    units: str,
    shapes: List[List[List[Union[int, float]]]],
    labels: List[List[List[Union[int, float]]]],
    shaded: Optional[List[int]] = None
) -> str:
    """
    Generate compound area figures for 6th grade dimensional reasoning.
    
    Creates clean compound shape diagrams with uniform coloring and decimal labels
    for teaching area calculation through decomposition. Designed specifically for
    6th grade standards requiring dimensional reasoning without gridlines.
    
    🚨 CRITICAL LABEL POSITIONING CONSTRAINTS (same validation as shape_decomposition):
    - Labels must be horizontal (same y) or vertical (same x) line segments
    - Labels CANNOT share 2+ common points with each other
    - 🚨 CRITICAL: Same-length labels CANNOT have overlapping coordinate ranges
      * Two horizontal labels of same length cannot span same x-range
      * Two vertical labels of same length cannot span same y-range
    - 🚨 CRITICAL: Labels must be positioned ON or ADJACENT TO shape boundaries/edges
    - Labels CANNOT be completely inside shapes (validation error: "Label positioned completely "
    "inside shape")
    - Labels CANNOT be too far from shapes (max 5 units away from any shape edge)
    - ALWAYS requires at least one horizontal AND one vertical label (gridlines=False)
    - ✅ SAFE STRATEGY: Use different lengths or non-overlapping ranges for multiple labels
    - ✅ CORRECT: Label positioned exactly on shape edges or just outside
    - ❌ WRONG: Labels [[0,0],[20,0]] and [[0,12],[20,12]] (same length, same x-range)
    - ❌ WRONG: Label completely inside shape area (causes critical validation error)
    
    Parameters
    ----------
    title : str
        Title for the diagram (max 40 characters) 
    units : str
        Unit abbreviation - must be 'cm', 'm', 'in', or 'ft'
    shapes : List[List[List[Union[int, float]]]]
        List of shapes, each defined by coordinate points
    labels : List[List[List[Union[int, float]]]]
        Dimension labels as line segments for measurements
    shaded : Optional[List[int]]
        Indices of shapes to shade (for subtraction problems)
        
    Returns
    -------
    str
        The URL of the generated compound area figure image
    """
    
    log_tool_generation("generate_coach_bot_compound_area_figure_image", 
                        title=title, units=units, shapes_count=len(shapes), 
                        labels_count=len(labels), shaded=shaded)
    
    # Validate dimensional labels are provided
    if not labels:
        raise ValueError("Dimensional labels are required for compound area figures")
    
    # Use shared validation function (gridlines always False for compound area figures)
    _validate_shape_decomposition_params(title, units, shapes, labels, False, shaded)
    
    # Create the ShapeDecomposition stimulus (gridlines forced to False)
    shape_decomp = ShapeDecomposition(
        title=title,
        units=units,
        gridlines=False,  # Always disabled for 6th grade dimensional reasoning
        shapes=shapes,
        labels=labels,
        shaded=shaded or []
    )
    
    # Generate the image using the compound area function
    image_file_path = create_dimensional_compound_area_figure(shape_decomp)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_rhombus_diagonals_image(
    units: str,
    d1: float,
    d2: Optional[float] = None,
    show_missing_placeholder: bool = False,
    placeholder_text: str = "?",
    title: Optional[str] = None,
    inside_labels: bool = True
) -> str:
    """
    Generate rhombus with diagonal measurements for area calculation.
    
    Creates a rhombus figure with diagonal lines and measurements labeled.
    Perfect for teaching rhombus area formula (A = d1 × d2 ÷ 2) and working
    with missing diagonal problems in geometry education.
    
    Parameters
    ----------
    units : str
        Measurement units - 'cm', 'm', 'in', or 'ft'
    d1 : float
        First diagonal length (1-50, max 1 decimal place)
    d2 : Optional[float]
        Second diagonal length (1-50, max 1 decimal place), None if unknown
    show_missing_placeholder : bool
        Whether to show placeholder text for missing diagonal
    placeholder_text : str
        Placeholder text for missing diagonal (max 4 characters)
    title : Optional[str]
        Optional title above the figure (max 40 characters)
    inside_labels : bool
        Whether labels are rendered inside along diagonals (always True)
        
    Returns
    -------
    str
        The URL of the generated rhombus diagonals image
    """
    
    log_tool_generation("generate_coach_bot_rhombus_diagonals_image", 
                        units=units, d1=d1, d2=d2, 
                        show_missing_placeholder=show_missing_placeholder,
                        placeholder_text=placeholder_text, title=title,
                        inside_labels=inside_labels)
    
    # Create RhombusDiagonalsDescription (Pydantic handles validation automatically)
    rhombus_desc = RhombusDiagonalsDescription(
        units=units,
        d1=d1,
        d2=d2,
        show_missing_placeholder=show_missing_placeholder,
        placeholder_text=placeholder_text,
        title=title,
        inside_labels=inside_labels
    )
    
    # Generate the image using the rhombus function
    image_file_path = create_rhombus_with_diagonals_figure(rhombus_desc)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_shape_decomposition_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for shape decomposition generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_shape_decomposition_image",
        "description": (
            "Generate shape decomposition diagrams for area and perimeter problems. "
            "Creates geometric diagrams with labeled dimensions for teaching area "
            "calculation, perimeter measurement, and shape decomposition strategies. "
            "CRITICAL: Labels must be horizontal/vertical line segments that don't "
            "overlap (share 2+ common points). Horizontal labels at same y-level "
            "cannot have overlapping x-ranges. Labels must be positioned on shape "
            "boundaries/edges or outside shapes, NOT completely inside shapes. When "
            "gridlines=False, must provide at least one horizontal AND one vertical label."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "maxLength": 40,
                    "description": "Title for the diagram"
                },
                "units": {
                    "type": "string",
                    "enum": ["cm", "m", "in", "ft"],
                    "description": "Unit of measurement"
                },
                "gridlines": {
                    "type": "boolean",
                    "description": (
                        "Whether to show grid lines within shapes. If False, must provide "
                        "at least one horizontal AND one vertical label."
                    )
                },
                "shapes": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "minItems": 3,
                        "description": "Shape defined by coordinate points [[x1,y1], [x2,y2], ...]"
                    },
                    "minItems": 1,
                    "description": "List of shapes to draw"
                },
                "labels": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "minItems": 2,
                        "maxItems": 2,
                        "description": (
                            "🚨 CRITICAL: Dimension label as line segment [[x1,y1], [x2,y2]]. "
                            "Must be horizontal (same y) or vertical (same x). MUST be positioned "
                            "ON or ADJACENT TO shape boundaries/edges - NOT inside shapes! "
                            "Same-length labels cannot have overlapping coordinate ranges. "
                            "Incorrect positioning causes validation errors."
                        )
                    },
                    "description": (
                        "🚨 CRITICAL: Dimension labels for measurements. Each label must be "
                        "horizontal or vertical. Same-length labels CANNOT have overlapping "
                        "coordinate ranges (e.g., two horizontal labels spanning same x-range). "
                        "MUST be positioned ON or ADJACENT TO shape boundaries/edges - NOT inside "
                        "shapes! Incorrect positioning causes validation errors."
                    )
                },
                "shaded": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Indices of shapes to shade (for subtraction problems)"
                },
                "decimal_only": {
                    "type": "boolean",
                    "description": "Force decimal-only labels (no fractions)",
                    "default": False
                }
            },
            "required": ["title", "units", "gridlines", "shapes", "labels"]
        }
    }
    return spec, generate_coach_bot_shape_decomposition_image


def generate_coach_bot_compound_area_figure_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for compound area figure generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_compound_area_figure_image",
        "description": (
            "Generate compound area figures for 6th grade dimensional reasoning. "
            "Creates clean compound shapes with uniform coloring and decimal labels "
            "for teaching area calculation through decomposition. 🚨 CRITICAL: Labels "
            "must be horizontal/vertical line segments. Same-length labels CANNOT have "
            "overlapping coordinate ranges (e.g., two horizontal labels spanning same x-range). "
            "Labels must be positioned ON shape boundaries/edges, NOT inside shapes. "
            "ALWAYS requires at least one horizontal AND one vertical label (gridlines disabled)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "maxLength": 40,
                    "description": "Title for the diagram"
                },
                "units": {
                    "type": "string",
                    "enum": ["cm", "m", "in", "ft"],
                    "description": "Unit of measurement"
                },
                "shapes": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "minItems": 3,
                        "description": "Shape defined by coordinate points"
                    },
                    "minItems": 1,
                    "description": "List of shapes to draw"
                },
                "labels": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "minItems": 2,
                        "maxItems": 2,
                        "description": (
                            "🚨 CRITICAL: Dimension label as line segment [[x1,y1], [x2,y2]]. "
                            "Must be horizontal (same y) or vertical (same x). MUST be positioned "
                            "ON or ADJACENT TO shape boundaries/edges - NOT inside shapes! "
                            "Same-length labels cannot have overlapping coordinate ranges. "
                            "Incorrect positioning causes validation errors."
                        )
                    },
                    "minItems": 1,
                    "description": (
                        "🚨 CRITICAL: Dimension labels (required for compound area figures). Must "
                        "have at least one horizontal AND one vertical label. Same-length labels "
                        "CANNOT have overlapping coordinate ranges. Each label must be "
                        "horizontal or vertical, and MUST be positioned on shape boundaries/edges."
                    )
                },
                "shaded": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Indices of shapes to shade (for subtraction problems)"
                }
            },
            "required": ["title", "units", "shapes", "labels"]
        }
    }
    return spec, generate_coach_bot_compound_area_figure_image


def generate_coach_bot_rhombus_diagonals_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for rhombus diagonals generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_rhombus_diagonals_image",
        description=(
            "Generate rhombus with diagonal measurements for area calculation. "
            "Creates a rhombus figure with diagonal lines and measurements labeled "
            "for teaching the rhombus area formula (A = d1 × d2 ÷ 2). Perfect for "
            "geometry education, missing diagonal problems, and area calculation "
            "exercises with visual support for mathematical understanding."
        ),
        pydantic_model=RhombusDiagonalsDescription,
        custom_descriptions={
            "units": (
                "Measurement units for diagonal lengths. Must be one of: 'cm', 'm', "
                "'in', or 'ft'. Essential for teaching dimensional analysis and "
                "measurement concepts in geometric area calculations."
            ),
            "d1": (
                "First (vertical) diagonal length in specified units (1-50, max 1 "
                "decimal place). Required diagonal measurement for rhombus area "
                "formula teaching and geometric visualization exercises."
            ),
            "d2": (
                "Second (horizontal) diagonal length in specified units (1-50, max 1 "
                "decimal place). Can be None/null for missing diagonal problems where "
                "students solve for unknown diagonal using area formula."
            ),
            "show_missing_placeholder": (
                "Whether to display placeholder text when second diagonal is unknown. "
                "Useful for creating assessment materials and problem-solving exercises "
                "where students identify missing information."
            ),
            "placeholder_text": (
                "Placeholder label for missing diagonal (max 4 characters). Common "
                "values include '?', 'x', or variable names. Enhances educational "
                "clarity in missing value problems and algebraic connections."
            ),
            "title": (
                "Optional descriptive title displayed above the rhombus figure (max 40 "
                "characters). Useful for problem context, worksheet organization, and "
                "educational material creation with clear labeling."
            ),
            "inside_labels": (
                "Whether diagonal labels are rendered inside along diagonal lines. "
                "Always True for proper rhombus area formula teaching. This parameter "
                "ensures labels are positioned directly on diagonal lines for clear "
                "geometric understanding and measurement visualization."
            )
        }
    )
    return spec, generate_coach_bot_rhombus_diagonals_image
