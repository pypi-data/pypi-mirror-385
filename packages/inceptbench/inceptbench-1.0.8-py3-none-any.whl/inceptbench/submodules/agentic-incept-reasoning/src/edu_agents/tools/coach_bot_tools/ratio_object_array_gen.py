from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.ratio_object_array import (  # noqa: E402, E501
    draw_ratio_object_array,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.ratio_object_array import (  # noqa: E402, E501
    RatioObjectArray,
    RatioObjectCell,
    RatioObjectShape,
)

logger = logging.getLogger("coach_bot_tools.ratio_object_array")


def generate_coach_bot_ratio_object_array_image(
    rows: int,
    columns: int,
    objects: List[List[Dict[str, str]]],
    shape_size: Optional[float] = None
) -> str:
    """
    Generate an array of shapes to teach ratios and proportional relationships.
    
    Creates a grid layout with 2-4 distinct shape types (circles, squares, triangles,
    stars, hexagons) in different colors. Useful for teaching ratios, proportions,
    and visual comparison of quantities.
    
    Parameters
    ----------
    rows : int
        Number of rows in the grid (1-2 rows maximum)
    columns : int  
        Number of columns in the grid (1-12 columns maximum)
    objects : List[List[Dict[str, str]]]
        2D array of object specifications, each containing:
        - shape: One of 'circle', 'square', 'triangle', 'star', 'hexagon'
        - color: Matplotlib color name or hex code (e.g., 'red', '#FF0000')
    shape_size : Optional[float]
        Size of shapes (0.3-1.0). If not specified, auto-adjusts based on layout
        
    Returns
    -------
    str
        The URL of the generated ratio object array image
    """
    
    # Use standardized logging
    log_tool_generation("ratio_object_array_image", rows=rows, columns=columns,
                       total_objects=rows*columns, shape_size=shape_size)
    
    # Convert List[List[Dict]] to List[List[RatioObjectCell]] for Pydantic model
    # This handles the interface flattening: simple Dict → complex RatioObjectCell objects
    cell_objects = []
    for row in objects:
        cell_row = []
        for obj in row:
            # Create RatioObjectCell Pydantic objects with enum conversion
            # This handles string → RatioObjectShape enum conversion automatically
            cell = RatioObjectCell(
                shape=RatioObjectShape(obj['shape'].lower()),
                color=obj['color']
            )
            cell_row.append(cell)
        cell_objects.append(cell_row)
    
    # Create and validate the RatioObjectArray using Pydantic
    # This handles all validation: rows/columns ranges, total object count,
    # shape size constraints, and distinct shape requirements (2-4 shapes)
    array_stimulus = RatioObjectArray(
        rows=rows,
        columns=columns,
        objects=cell_objects,
        shape_size=shape_size
    )
    
    # Generate the image using the ratio object array function
    image_file_path = draw_ratio_object_array(array_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_ratio_object_array_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for ratio object array generation."""
    # Use enhanced static specification due to complex nested model transformation:
    # List[List[Dict]] wrapper interface vs List[List[RatioObjectCell]] Pydantic model
    spec = {
        "type": "function",
        "name": "generate_coach_bot_ratio_object_array_image",
        "description": (
            "Generate ratio object array visualizations for mathematics education focused on "
            "proportional reasoning, ratio analysis, and quantitative comparison skills. Creates "
            "structured grid layouts with 2-4 distinct geometric shapes (circles, squares, "
            "triangles, stars, hexagons) in various colors for teaching ratio concepts, "
            "proportional relationships, fraction comparisons, and visual quantity analysis. "
            "Perfect for elementary and middle school mathematics lessons covering ratios, "
            "proportions, fractions, and comparative reasoning. Grid layouts are optimized "
            "for educational clarity with automatic shape sizing and strategic color "
            "distributions. Excellent for worksheets, assessments, interactive learning "
            "activities, and mathematical problem-solving exercises that develop students' "
            "ability to identify, compare, and analyze proportional relationships through "
            "visual pattern recognition and quantitative reasoning."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "rows": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 2,
                    "description": (
                        "Number of rows in the ratio array grid (1-2 maximum for optimal "
                        "educational clarity). Single rows work well for basic ratio introduction "
                        "and simple comparisons. Two rows enable more complex proportional "
                        "relationships, advanced ratio analysis, and comparative reasoning "
                        "exercises. Layout choice affects educational complexity and student "
                        "engagement levels."
                    )
                },
                "columns": {
                    "type": "integer", 
                    "minimum": 1,
                    "maximum": 12,
                    "description": (
                        "Number of columns in the ratio array grid (1-12 maximum for practical "
                        "visualization). Column count determines the granularity of ratio "
                        "relationships and comparison opportunities. Fewer columns (2-4) work "
                        "well for introductory ratio concepts. More columns (6-12) enable "
                        "complex proportional analysis and advanced mathematical reasoning "
                        "exercises. Total objects limited to 10 for educational focus."
                    )
                },
                "objects": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 2,
                    "items": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 12,
                        "items": {
                            "type": "object",
                            "properties": {
                                "shape": {
                                    "type": "string",
                                    "enum": ["circle", "square", "triangle", "star", "hexagon"],
                                    "description": (
                                        "Geometric shape type for educational pattern recognition "
                                        "and visual distinction. Choose from: 'circle' (smooth, "
                                        "continuous), 'square' (regular, familiar), 'triangle' "
                                        "(angular, distinctive), 'star' (complex, engaging), "
                                        "'hexagon' (advanced geometry). Strategic shape selection "
                                        "enhances ratio visibility and student comprehension of "
                                        "proportional relationships."
                                    )
                                },
                                "color": {
                                    "type": "string",
                                    "description": (
                                        "Color specification using matplotlib color names ('red', "
                                        "'blue', 'green', 'yellow', 'orange', 'purple', 'brown', "
                                        "'pink', 'gray', 'cyan') or hex codes ('#FF0000', "
                                        "'#0000FF'). Strategic color choices improve ratio "
                                        "visibility, pattern recognition, and mathematical "
                                        "analysis. Use contrasting colors to highlight different "
                                        "categories and enhance educational clarity."
                                    )
                                }
                            },
                            "required": ["shape", "color"],
                            "additionalProperties": False
                        }
                    },
                    "description": (
                        "2D array structure defining the complete grid layout for ratio analysis. "
                        "Each outer array represents a row, each inner array contains column "
                        "specifications. CRITICAL EDUCATIONAL REQUIREMENTS: Must contain exactly "
                        "2-4 distinct shape types for meaningful ratio comparisons (not 1 or 5+). "
                        "Total objects across entire grid cannot exceed 10 for educational focus. "
                        "Array dimensions must match specified rows and columns exactly. Strategic "
                        "shape and color distribution creates optimal learning opportunities for "
                        "ratio identification, proportional reasoning, and quantitative analysis."
                    )
                },
                "shape_size": {
                    "type": "number",
                    "minimum": 0.3,
                    "maximum": 1.0,
                    "description": (
                        "Relative size of shapes for optimal educational visualization (0.3-1.0 "
                        "scale). If not specified, automatically adjusts for educational clarity: "
                        "0.5 for single-row layouts (compact, focused), 0.8 for multi-row layouts "
                        "(visible, clear separation). Smaller values (0.3-0.5) work well for "
                        "complex grids with many objects. Larger values (0.7-1.0) enhance "
                        "visibility for simple layouts and younger students. Size affects visual "
                        "clarity, pattern recognition, and student engagement with ratio concepts."
                    )
                }
            },
            "required": ["rows", "columns", "objects"]
        }
    }
    return spec, generate_coach_bot_ratio_object_array_image
