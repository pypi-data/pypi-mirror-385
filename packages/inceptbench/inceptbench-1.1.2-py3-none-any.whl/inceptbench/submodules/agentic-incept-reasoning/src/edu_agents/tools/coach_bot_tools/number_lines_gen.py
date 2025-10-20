from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.number_lines import (  # noqa: E402
    create_decimal_comparison_number_line,
    create_extended_unit_fraction_number_line,
    create_fixed_step_number_line,
    create_number_line,
    create_unit_fraction_number_line,
    create_vertical_number_line,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.number_line import (  # noqa: E402
    DecimalComparisonNumberLine,
    ExtendedRange,
    ExtendedUnitFractionDotPoint,
    ExtendedUnitFractionNumberLine,
    FixedStepNumberLine,
    NumberLine,
    Point,
    Range,
    UnitFractionNumberLine,
    UnitFractionPoint,
)

logger = logging.getLogger("coach_bot_tools.number_lines_gen")


def generate_coach_bot_number_line_image(
    range_min: int,
    range_max: int,
    points: Optional[List[Dict[str, any]]] = None
) -> str:
    """
    Generate a basic number line with integer range and optional labeled points.
    
    Creates a horizontal number line with automatic tick spacing. Minor ticks are automatically
    added based on the range size. Useful for teaching basic number concepts, ordering,
    and number relationships.
    
    Parameters
    ----------
    range_min : int
        The minimum value on the number line
    range_max : int  
        The maximum value on the number line
    points : Optional[List[Dict[str, any]]]
        Optional list of points to mark on the line, each containing:
        - label: Display label (letter, number, decimal, fraction, or measurement unit)
        - value: Numeric position on the number line
        
    Returns
    -------
    str
        The URL of the generated number line image
    """
    
    log_tool_generation("generate_coach_bot_number_line_image", 
                        range_min=range_min, range_max=range_max, 
                        points_count=len(points) if points else 0)
    
    # Create Range object
    number_range = Range(min=range_min, max=range_max)
    
    # Create Point objects if provided
    point_objects = []
    if points:
        for point_data in points:
            point_obj = Point(
                label=point_data["label"],
                value=point_data["value"]
            )
            point_objects.append(point_obj)
    
    # Create the NumberLine stimulus
    number_line = NumberLine(
        range=number_range,
        points=point_objects
    )
    
    # Generate the image using the number line function
    image_file_path = create_number_line(number_line)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_fixed_step_number_line_image(
    range_min: int,
    range_max: int,
    step_size: float,
    minor_divisions: int = 2,
    points: Optional[List[Dict[str, any]]] = None
) -> str:
    """
    Generate a number line with fixed step size for major ticks.
    
    Creates a number line with precise control over major tick spacing instead of automatic
    step size calculation. Useful when you need specific intervals or when teaching about
    specific increments.
    
    Parameters
    ----------
    range_min : int
        The minimum value on the number line
    range_max : int
        The maximum value on the number line
    step_size : float
        The step size for major ticks (must be greater than 0)
    minor_divisions : int
        Number of minor divisions between each major tick (default: 2)
    points : Optional[List[Dict[str, any]]]
        Optional list of points to mark on the line, each containing:
        - label: Display label
        - value: Numeric position on the number line
        
    Returns
    -------
    str
        The URL of the generated fixed step number line image
    """
    
    log_tool_generation("generate_coach_bot_fixed_step_number_line_image", 
                        range_min=range_min, range_max=range_max, 
                        step_size=step_size, minor_divisions=minor_divisions,
                        points_count=len(points) if points else 0)
    
    # Create Range object
    number_range = Range(min=range_min, max=range_max)
    
    # Create Point objects if provided
    point_objects = []
    if points:
        for point_data in points:
            point_obj = Point(
                label=point_data["label"],
                value=point_data["value"]
            )
            point_objects.append(point_obj)
    
    # Create the FixedStepNumberLine stimulus (Pydantic handles validation)
    fixed_step_line = FixedStepNumberLine(
        range=number_range,
        points=point_objects,
        step_size=step_size,
        minor_divisions=minor_divisions
    )
    
    # Generate the image using the fixed step number line function
    image_file_path = create_fixed_step_number_line(fixed_step_line)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_unit_fraction_number_line_image(
    minor_divisions: int,
    dot_point: Dict[str, any]
) -> str:
    """
    Generate a unit fraction number line from 0 to 1 with equal divisions.
    
    Creates a number line spanning 0 to 1 with the specified number of equal divisions.
    Shows a marked point on the line. Useful for teaching fraction concepts, part-whole
    relationships, and fraction equivalence.
    
    Parameters
    ----------
    minor_divisions : int
        Number of equal divisions to create between 0 and 1
    dot_point : Dict[str, any]
        Point to mark on the line, containing:
        - label: Display label for the point
        - value: Position on the line (0.0 to 1.0)
        
    Returns
    -------
    str
        The URL of the generated unit fraction number line image
    """
    
    log_tool_generation("generate_coach_bot_unit_fraction_number_line_image", 
                        minor_divisions=minor_divisions, 
                        dot_point_value=dot_point["value"],
                        dot_point_label=dot_point["label"])
    
    # Create the point object (Pydantic handles validation)
    point_obj = UnitFractionPoint(
        label=dot_point["label"],
        value=dot_point["value"]
    )
    
    # Create the UnitFractionNumberLine stimulus
    unit_fraction_line = UnitFractionNumberLine(
        range=Range(min=0, max=1),
        points=[point_obj],
        minor_divisions=minor_divisions
    )
    
    # Generate the image using the unit fraction number line function
    image_file_path = create_unit_fraction_number_line(unit_fraction_line)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_extended_unit_fraction_number_line_image(
    range_min: float,
    range_max: float,
    minor_divisions: int,
    endpoint_fraction: str,
    dot_point: Dict[str, any],
    show_all_tick_labels: bool = False,
    labeled_fraction: Optional[str] = None
) -> str:
    """
    Generate an extended unit fraction number line that can go beyond 1.
    
    Creates a number line for fractions that may extend past 1. Shows fraction divisions
    and can optionally label all tick marks or just specific ones. Useful for teaching
    improper fractions, mixed numbers, and fraction comparisons.
    
    Parameters
    ----------
    range_min : float
        The minimum value on the number line (typically 0)
    range_max : float
        The maximum value on the number line (the fraction endpoint)
    minor_divisions : int
        Number of equal divisions in the range
    endpoint_fraction : str
        String representation of the endpoint fraction (e.g., "3/2", "5/4")
    dot_point : Dict[str, any]
        Point to mark on the line, containing:
        - label: Display label for the point
        - value: Length/amount that the bar represents
        - dot_start_tick: Which tick the bar should start from (optional, default: 0)
        - red: Whether the dot should be red instead of blue (optional, default: False)
    show_all_tick_labels : bool
        Whether to show labels on all tick marks (default: False)
    labeled_fraction : Optional[str]
        Specific fraction tick to label (e.g., "1/2")
        
    Returns
    -------
    str
        The URL of the generated extended unit fraction number line image
    """
    
    log_tool_generation("generate_coach_bot_extended_unit_fraction_number_line_image", 
                        range_min=range_min, range_max=range_max, 
                        minor_divisions=minor_divisions, endpoint_fraction=endpoint_fraction,
                        dot_point_value=dot_point["value"],
                        show_all_tick_labels=show_all_tick_labels)
    
    # Create the dot point object
    dot_point_obj = ExtendedUnitFractionDotPoint(
        label=dot_point["label"],
        value=dot_point["value"],
        dot_start_tick=dot_point.get("dot_start_tick", 0),
        red=dot_point.get("red", False)
    )
    
    # Create the ExtendedUnitFractionNumberLine stimulus
    extended_line = ExtendedUnitFractionNumberLine(
        range=ExtendedRange(min=range_min, max=range_max),
        dot_point=dot_point_obj,
        minor_divisions=minor_divisions,
        endpoint_fraction=endpoint_fraction,
        show_all_tick_labels=show_all_tick_labels,
        labeled_fraction=labeled_fraction
    )
    
    # Generate the image using the extended unit fraction number line function
    image_file_path = create_extended_unit_fraction_number_line(extended_line)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_decimal_comparison_number_line_image(
    range_min: float,
    range_max: float,
    points: Optional[List[Dict[str, any]]] = None
) -> str:
    """
    Generate a decimal comparison number line with exactly 10 divisions.
    
    Creates a number line specifically for decimal comparisons with either 0.1 or 0.01
    increments based on the range span. Always shows exactly 10 equal divisions between
    the min and max values. Useful for teaching decimal place value and decimal comparison.
    
    Parameters
    ----------
    range_min : float
        The minimum value on the number line
    range_max : float
        The maximum value on the number line
        Range span should be either 1.0 (for 0.1 increments) or 0.1 (for 0.01 increments)
    points : Optional[List[Dict[str, any]]]
        Optional list of points to mark on the line, each containing:
        - label: Display label for the point
        - value: Position on the line
        
    Returns
    -------
    str
        The URL of the generated decimal comparison number line image
    """
    
    log_tool_generation("generate_coach_bot_decimal_comparison_number_line_image", 
                        range_min=range_min, range_max=range_max, 
                        points_count=len(points) if points else 0)
    
    # Validate range span
    range_span = range_max - range_min
    if not (abs(range_span - 1.0) < 1e-10 or abs(range_span - 0.1) < 1e-10):
        raise ValueError(
            "Range span must be either 1.0 (for 0.1 increments) or 0.1 (for 0.01 increments)"
        )
    
    # Create Point objects if provided
    point_objects = []
    if points:
        for point_data in points:
            if not (range_min <= point_data["value"] <= range_max):
                raise ValueError(
                    f"Point {point_data['label']} with value {point_data['value']} "
                    f"is outside the range [{range_min}, {range_max}]"
                )
            
            point_obj = Point(
                label=point_data["label"],
                value=point_data["value"]
            )
            point_objects.append(point_obj)
    
    # Create the DecimalComparisonNumberLine stimulus
    decimal_line = DecimalComparisonNumberLine(
        range=ExtendedRange(min=range_min, max=range_max),
        points=point_objects
    )
    
    # Generate the image using the decimal comparison number line function
    image_file_path = create_decimal_comparison_number_line(decimal_line)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_vertical_number_line_image(
    range_min: int,
    range_max: int,
    points: Optional[List[Dict[str, any]]] = None
) -> str:
    """
    Generate a vertical number line with integer range and optional labeled points.
    
    Creates a vertical number line with automatic tick spacing. Similar to the basic
    number line but oriented vertically. Useful for teaching concepts that benefit
    from vertical orientation, such as temperature, elevation, or coordinate plane y-axis.
    
    Parameters
    ----------
    range_min : int
        The minimum value on the number line
    range_max : int
        The maximum value on the number line
    points : Optional[List[Dict[str, any]]]
        Optional list of points to mark on the line, each containing:
        - label: Display label
        - value: Numeric position on the number line
        
    Returns
    -------
    str
        The URL of the generated vertical number line image
    """
    
    log_tool_generation("generate_coach_bot_vertical_number_line_image", 
                        range_min=range_min, range_max=range_max, 
                        points_count=len(points) if points else 0)
    
    # Create Range object
    number_range = Range(min=range_min, max=range_max)
    
    # Create Point objects if provided
    point_objects = []
    if points:
        for point_data in points:
            if not (range_min <= point_data["value"] <= range_max):
                raise ValueError(
                    f"Point {point_data['label']} with value {point_data['value']} "
                    f"is outside the range [{range_min}, {range_max}]"
                )
            
            point_obj = Point(
                label=point_data["label"],
                value=point_data["value"]
            )
            point_objects.append(point_obj)
    
    # Create the NumberLine stimulus (same structure as horizontal)
    number_line = NumberLine(
        range=number_range,
        points=point_objects
    )
    
    # Generate the image using the vertical number line function
    image_file_path = create_vertical_number_line(number_line)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


# Tool specifications

def generate_coach_bot_number_line_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for basic number line generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_number_line_image",
        "description": (
            "Generate a basic horizontal number line with integer range and optional labeled "
            "points. Creates educational visualizations with automatic tick spacing for teaching "
            "number concepts, ordering, number relationships, and mathematical reasoning. Perfect "
            "for elementary through middle school mathematics instruction with customizable point "
            "markers for specific learning objectives."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "range_min": {
                    "type": "integer",
                    "description": "The minimum value on the number line for educational range "
                                   "setting"
                },
                "range_max": {
                    "type": "integer",
                    "description": "The maximum value on the number line for educational range "
                                   "setting"
                },
                "points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "pattern": r"^-?[a-zA-Z]$|^-?\d+$|^-?\d+/\d+$|^-?\d+(\.\d+)?\s?(°C|°F|mm|cm|m|km|mg|g|kg|lb|oz|in|ft|ml|l|gal|fl oz)$",  # noqa: E501
                                "description": "Display label for the point: letter (A-Z), "
                                               "integer, decimal, fraction, or measurement with "
                                               "units"
                            },
                            "value": {
                                "type": "number",
                                "description": "Numeric position of the point on the number line "
                                               "(must be within the specified range)"
                            }
                        },
                        "required": ["label", "value"]
                    },
                    "description": "Optional educational points to mark on the line for specific "
                                   "learning objectives and assessment"
                }
            },
            "required": ["range_min", "range_max"]
        }
    }
    return spec, generate_coach_bot_number_line_image


def generate_coach_bot_fixed_step_number_line_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for fixed step number line generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_fixed_step_number_line_image",
        "description": (
            "Generate a number line with fixed step size for precise educational control over tick "
            "spacing. Creates horizontal number lines with custom major tick intervals and minor "
            "divisions for teaching skip counting, multiplication patterns, and specific "
            "mathematical increments. Perfect for systematic counting instruction and pattern "
            "recognition exercises in elementary mathematics."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "range_min": {
                    "type": "integer",
                    "description": "The minimum value on the number line"
                },
                "range_max": {
                    "type": "integer",
                    "description": "The maximum value on the number line"
                },
                "step_size": {
                    "type": "number",
                    "exclusiveMinimum": 0,
                    "description": "The step size for major ticks (must be greater than 0)"
                },
                "minor_divisions": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 2,
                    "description": "Number of minor divisions between each major tick"
                },
                "points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": "Display label for the point"
                            },
                            "value": {
                                "type": "number",
                                "description": "Numeric position on the number line"
                            }
                        },
                        "required": ["label", "value"]
                    },
                    "description": "Optional list of points to mark on the line"
                }
            },
            "required": ["range_min", "range_max", "step_size"]
        }
    }
    return spec, generate_coach_bot_fixed_step_number_line_image


def generate_coach_bot_unit_fraction_number_line_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for unit fraction number line generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_unit_fraction_number_line_image",
        "description": (
            "Generate a unit fraction number line from 0 to 1 with equal divisions. Creates a "
            "number line spanning 0 to 1 with the specified number of equal divisions. Shows a "
            "marked point on the line. Useful for teaching fraction concepts, part-whole "
            "relationships, and fraction equivalence."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "minor_divisions": {
                    "type": "integer",
                    "minimum": 2,
                    "description": "Number of equal divisions to create between 0 and 1"
                },
                "dot_point": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "pattern": "^[a-zA-Z]$|^0$|^1$|^\\d+\\.\\d+$|^\\d+/\\d+$",
                            "description": "Display label for the point (letter, 0, 1, decimal, or "
                                           "fraction)"
                        },
                        "value": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Position on the line (0.0 to 1.0)"
                        }
                    },
                    "required": ["label", "value"],
                    "description": "Point to mark on the line"
                }
            },
            "required": ["minor_divisions", "dot_point"]
        }
    }
    return spec, generate_coach_bot_unit_fraction_number_line_image


def generate_coach_bot_extended_unit_fraction_number_line_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for extended unit fraction number line 
    generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_extended_unit_fraction_number_line_image",
        "description": (
            "Generate an extended unit fraction number line that can go beyond 1. Creates a "
            "number line for fractions that may extend past 1. Shows fraction divisions and "
            "can optionally label all tick marks or specific ones. Useful for teaching improper "
            "fractions, mixed numbers, and fraction comparisons."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "range_min": {
                    "type": "number",
                    "description": "The minimum value on the number line (typically 0)"
                },
                "range_max": {
                    "type": "number",
                    "description": "The maximum value on the number line (the fraction endpoint)"
                },
                "minor_divisions": {
                    "type": "integer",
                    "minimum": 2,
                    "description": "Number of equal divisions in the range"
                },
                "endpoint_fraction": {
                    "type": "string",
                    "description": "String representation of the endpoint fraction (e.g., '3/2', "
                                   "'5/4')"
                },
                "dot_point": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Display label for the point (e.g., 'A')"
                        },
                        "value": {
                            "type": "number",
                            "description": "Length/amount that the bar represents (e.g., 2/4 = "
                                           "0.5). The bar will extend this much from the start "
                                           "tick."
                        },
                        "dot_start_tick": {
                            "type": "integer",
                            "minimum": 0,
                            "default": 0,
                            "description": "Which tick the blue bar should start from (0-based). "
                                           "Default is 0 (start of number line)."
                        },
                        "red": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether the dot point should be red instead of blue. "
                                           "Default is False (blue)."
                        }
                    },
                    "required": ["label", "value"],
                    "description": "Dot point configuration with bar visualization"
                },
                "show_all_tick_labels": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to show labels on all tick marks"
                },
                "labeled_fraction": {
                    "type": "string",
                    "description": "Specific fraction tick to label (e.g., '1/2')"
                }
            },
            "required": ["range_min", "range_max", "minor_divisions", "endpoint_fraction",
                        "dot_point"]
        }
    }
    return spec, generate_coach_bot_extended_unit_fraction_number_line_image


def generate_coach_bot_decimal_comparison_number_line_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for decimal comparison number line 
    generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_decimal_comparison_number_line_image",
        "description": (
            "Generate a decimal comparison number line with exactly 10 divisions. Creates a number "
            "line specifically for decimal comparisons with either 0.1 or 0.01 increments based on "
            "the range span. Always shows exactly 10 equal divisions. Useful for teaching decimal "
            "place value and decimal comparison."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "range_min": {
                    "type": "number",
                    "description": "The minimum value on the number line"
                },
                "range_max": {
                    "type": "number",
                    "description": "The maximum value on the number line. Range span should be "
                                   "either 1.0 (for 0.1 increments) or 0.1 (for 0.01 increments)"
                },
                "points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": "Display label for the point"
                            },
                            "value": {
                                "type": "number",
                                "description": "Position on the line"
                            }
                        },
                        "required": ["label", "value"]
                    },
                    "description": "Optional list of points to mark on the line"
                }
            },
            "required": ["range_min", "range_max"]
        }
    }
    return spec, generate_coach_bot_decimal_comparison_number_line_image


def generate_coach_bot_vertical_number_line_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for vertical number line generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_vertical_number_line_image",
        "description": (
            "Generate a vertical number line with integer range and optional labeled points. "
            "Creates a vertical number line with automatic tick spacing. Similar to the basic "
            "number line but oriented vertically. Useful for teaching concepts that benefit from "
            "vertical orientation, such as temperature, elevation, or coordinate plane y-axis."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "range_min": {
                    "type": "integer",
                    "description": "The minimum value on the number line"
                },
                "range_max": {
                    "type": "integer",
                    "description": "The maximum value on the number line"
                },
                "points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": "Display label for the point"
                            },
                            "value": {
                                "type": "number",
                                "description": "Numeric position on the number line"
                            }
                        },
                        "required": ["label", "value"]
                    },
                    "description": "Optional list of points to mark on the line"
                }
            },
            "required": ["range_min", "range_max"]
        }
    }
    return spec, generate_coach_bot_vertical_number_line_image
