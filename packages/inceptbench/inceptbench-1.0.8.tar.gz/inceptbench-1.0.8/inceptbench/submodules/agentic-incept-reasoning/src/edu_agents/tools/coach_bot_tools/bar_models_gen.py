from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional, Union

from .coach_bot_utils import log_tool_generation, setup_coach_bot_imports, upload_coach_bot_image

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.bar_models import (  # noqa: E402
    draw_bar_model_stimulus,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.bar_model_stimulus import (  # noqa: E402, E501
    BarModel,
    BarModelStimulus,
    BarSection,
    ComparisonBarModel,
)

logger = logging.getLogger("coach_bot_tools.bar_models")


def generate_coach_bot_single_bar_model_image(
    sections: List[Dict[str, any]],
    total_value: Optional[Union[int, float, str]] = None,
    total_label: Optional[str] = None,
    show_section_values: bool = True,
    show_total_value: bool = True,
    section_width_mode: str = "equal"
) -> str:
    """
    Generate a single bar model (tape diagram).
    
    Creates a bar model with sections that can represent parts of a whole,
    commonly used for teaching word problems and mathematical relationships.
    
    Parameters
    ----------
    sections : List[Dict[str, any]]
        List of sections for the bar model. Each section should contain:
        - value: Union[int, float, str] - The value for this section (can be number or variable)
        - label: Optional[str] - Optional label for this section
        - color: Optional[str] - Color for this section (hex code or color name)
    total_value : Optional[Union[int, float, str]], default None
        The total value represented by the entire bar
    total_label : Optional[str], default None
        Label for the total (e.g., 'Total candies', '9 candies')
    show_section_values : bool, default True
        Whether to show values inside or near each section
    show_total_value : bool, default True
        Whether to show the total value above the bar
    section_width_mode : str, default "equal"
        Whether sections are sized "proportional" to their values or "equal"
        
    Returns
    -------
    str
        The URL of the generated single bar model image
    """
    
    log_tool_generation(
        "generate_coach_bot_single_bar_model_image",
        sections=sections,
        total_value=total_value,
        total_label=total_label,
        show_section_values=show_section_values,
        show_total_value=show_total_value,
        section_width_mode=section_width_mode
    )
    
    # Smart filtering to avoid visual clutter
    
    # 1. Don't show total_value if it's just "?" (not informative)
    filtered_show_total_value = show_total_value and (
        total_value is not None and str(total_value).strip() != "?"
    )
    
    # 2. Remove section labels that are identical to section values (avoid duplication)
    filtered_sections = []
    for section_data in sections:
        value = section_data.get("value")
        label = section_data.get("label")
        
        # Remove label if it's identical to the value (avoid showing "3" both inside and below)
        if label is not None and str(label).strip() == str(value).strip():
            filtered_label = None
        else:
            filtered_label = label
            
        filtered_sections.append({
            "value": value,
            "label": filtered_label,
            "color": section_data.get("color")
        })
    
    logger.info(f"After filtering - show_total_value: {filtered_show_total_value}")
    logger.info(f"After filtering - sections: {filtered_sections}")
    
    # Create BarSection objects
    bar_sections = []
    for section_data in filtered_sections:
        bar_section = BarSection(
            value=section_data.get("value"),
            label=section_data.get("label"),
            color=section_data.get("color")
        )
        bar_sections.append(bar_section)
    
    # Create and validate the BarModel
    bar_model = BarModel(
        total_value=total_value,
        total_label=total_label,
        sections=bar_sections,
        show_section_values=show_section_values,
        show_total_value=filtered_show_total_value,  # Use filtered value
        section_width_mode=section_width_mode
    )
    
    # Create and validate the BarModelStimulus
    bar_model_stimulus = BarModelStimulus(
        model_type="single_bar",
        single_bar=bar_model
    )
    
    # Generate the image using the bar model function
    image_file_path = draw_bar_model_stimulus(bar_model_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_comparison_bar_models_image(
    bars: List[Dict[str, any]],
    title: Optional[str] = None,
    comparison_type: str = "difference"
) -> str:
    """
    Generate comparison bar models (multiple bar models).
    
    Creates multiple bar models arranged for comparison, useful for teaching
    comparison problems and part-whole relationships.
    
    Parameters
    ----------
    bars : List[Dict[str, any]]
        List of bar models to compare. Each bar should contain:
        - sections: List[Dict] - List of sections (same format as single bar)
        - total_value: Optional[Union[int, float, str]] - Total value for this bar
        - total_label: Optional[str] - Label for this bar's total
        - title: Optional[str] - Title for this individual bar
    title : Optional[str], default None
        Overall title for the comparison
    comparison_type : str, default "difference"
        Type of comparison: "difference", "ratio", or "part_whole"
        
    Returns
    -------
    str
        The URL of the generated comparison bar models image
    """
    
    log_tool_generation(
        "generate_coach_bot_comparison_bar_models_image",
        bars=bars,
        title=title,
        comparison_type=comparison_type
    )
    
    # Create BarModel objects
    bar_models = []
    for bar_data in bars:
        # Create sections for this bar
        bar_sections = []
        for section_data in bar_data.get("sections", []):
            bar_section = BarSection(
                value=section_data.get("value"),
                label=section_data.get("label"),
                color=section_data.get("color")
            )
            bar_sections.append(bar_section)
        
        # Create and validate the bar model
        bar_model = BarModel(
            title=bar_data.get("title"),
            total_value=bar_data.get("total_value"),
            total_label=bar_data.get("total_label"),
            sections=bar_sections,
            show_section_values=bar_data.get("show_section_values", True),
            show_total_value=bar_data.get("show_total_value", True),
            section_width_mode=bar_data.get("section_width_mode", "equal")
        )
        bar_models.append(bar_model)
    
    # Create and validate the ComparisonBarModel
    comparison_bar_model = ComparisonBarModel(
        title=title,
        bars=bar_models,
        comparison_type=comparison_type
    )
    
    # Create and validate the BarModelStimulus
    bar_model_stimulus = BarModelStimulus(
        model_type="comparison_bars",
        comparison_bars=comparison_bar_model
    )
    
    # Generate the image using the bar model function
    image_file_path = draw_bar_model_stimulus(bar_model_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_single_bar_model_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for single bar model generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_single_bar_model_image",
        "description": (
            "Generate a single bar model (tape diagram) for mathematical problem solving. "
            "Creates a horizontal bar divided into sections representing parts of a whole, "
            "commonly used for teaching word problems, addition/subtraction, and part-whole "
            "relationships. Features intelligent visual filtering to reduce clutter and enhance "
            "educational clarity. Ideal for elementary mathematics instruction and visual problem "
            "representation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "value": {
                                "anyOf": [
                                    {"type": "integer"},
                                    {"type": "number"},
                                    {"type": "string"}
                                ],
                                "description": (
                                    "The numeric value or variable for this section (e.g., 5, 2.5, "
                                    "'x', '?'). For educational problems, can represent "
                                    "quantities, unknowns, or algebraic variables. String values "
                                    "are useful for missing quantities ('?') or variables ('x', "
                                    "'y')."
                                )
                            },
                            "label": {
                                "type": "string",
                                "description": (
                                    "Optional descriptive label for this section (e.g., 'apples', "
                                    "'Group A', 'remaining'). Only include when different from the "
                                    "value to avoid visual duplication. Useful for providing "
                                    "context about what the section represents in the problem."
                                )
                            },
                            "color": {
                                "type": "string",
                                "description": (
                                    "Color for this section (hex code like '#FF5733' or color name "
                                    "like 'red', 'blue'). Use different colors to distinguish "
                                    "between different types of quantities or groups. Common "
                                    "educational colors: blue, green, orange, red, purple."
                                )
                            }
                        },
                        "required": ["value"]
                    },
                    "description": (
                        "Array of 1-8 sections that make up the bar model. Each section represents "
                        "a part of the whole with its own value, optional label, and optional "
                        "color. Sections are displayed left-to-right in the order provided."
                    ),
                    "minItems": 1,
                    "maxItems": 8
                },
                "total_value": {
                    "anyOf": [
                        {"type": "integer"},
                        {"type": "number"},
                        {"type": "string"}
                    ],
                    "description": (
                        "The total value represented by the entire bar (e.g., 15, 24.5, '3x+5'). "
                        "Can be the sum of section values or a separate total for problem-solving "
                        "contexts. Use '?' for unknown totals in word problems. Automatically "
                        "hidden if set to '?' to reduce clutter."
                    )
                },
                "total_label": {
                    "type": "string",
                    "description": (
                        "Descriptive label for what the total represents (e.g., '16 apples', "
                        "'Total distance', 'All students'). Appears above the bar with a bracket. "
                        "Use to provide educational context about the quantity being modeled."
                    )
                },
                "show_section_values": {
                    "type": "boolean",
                    "description": (
                        "Whether to display the value inside or near each section. "
                        "Set to false to create cleaner visuals when values would clutter the "
                        "diagram. Defaults to true for educational clarity."
                    )
                },
                "show_total_value": {
                    "type": "boolean",
                    "description": (
                        "Whether to display the total value above the bar bracket. Automatically "
                        "hides '?' values to reduce visual clutter. Set to false when the total is "
                        "implied or would be redundant. Defaults to true."
                    )
                },
                "section_width_mode": {
                    "type": "string",
                    "description": (
                        "How to size the sections: 'proportional' makes sections visually "
                        "proportional to their numeric values (useful for showing relative "
                        "quantities), 'equal' makes all sections the same width (useful for "
                        "abstract problems with variables)."
                    ),
                    "enum": ["proportional", "equal"]
                }
            },
            "required": ["sections"]
        }
    }
    return spec, generate_coach_bot_single_bar_model_image


def generate_coach_bot_comparison_bar_models_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for comparison bar models generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_comparison_bar_models_image",
        "description": (
            "Generate comparison bar models (multiple tape diagrams) for mathematical problem "
            "solving. Creates 2-4 horizontal bar models arranged vertically for visual comparison, "
            "ideal for teaching comparison problems, before/after scenarios, part-whole "
            "relationships, and multi-step word problems. Each bar can have different sections, "
            "values, and labels to represent different quantities or scenarios being compared. "
            "Excellent for elementary mathematics instruction and comparative analysis."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "bars": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sections": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "value": {
                                            "anyOf": [
                                                {"type": "integer"},
                                                {"type": "number"},
                                                {"type": "string"}
                                            ],
                                            "description": (
                                                "The numeric value or variable for this section "
                                                "(e.g., 8, 3.5, 'x', '?'). Can represent known "
                                                "quantities, unknowns, or algebraic expressions."
                                            )
                                        },
                                        "label": {
                                            "type": "string",
                                            "description": (
                                                "Optional descriptive label for this section "
                                                "(e.g., 'sold', 'remaining', 'boys'). Provides "
                                                "educational context about what the section "
                                                "represents."
                                            )
                                        },
                                        "color": {
                                            "type": "string",
                                            "description": (
                                                "Color for this section (hex code or color name). "
                                                "Use consistent colors across bars to highlight "
                                                "relationships (e.g., all 'sold' sections in blue)."
                                            )
                                        }
                                    },
                                    "required": ["value"]
                                }
                            },
                            "total_value": {
                                "anyOf": [
                                    {"type": "integer"},
                                    {"type": "number"},
                                    {"type": "string"}
                                ],
                                "description": (
                                    "Total value represented by this bar (e.g., 15, 24.5, '2x+3'). "
                                    "Can be the sum of sections or a separate quantity for "
                                    "comparison."
                                )
                            },
                            "total_label": {
                                "type": "string",
                                "description": (
                                    "Descriptive label for this bar's total quantity (e.g., '20 "
                                    "apples', '15 students'). Use this OR 'title', not both, as "
                                    "they occupy the same visual space. Preferred when emphasizing "
                                    "the numeric total."
                                )
                            },
                            "title": {
                                "type": "string",
                                "description": (
                                    "Title/name for this individual bar (e.g., 'Class A', "
                                    "'Before', 'Sarah'). Use this OR 'total_label', not both, as "
                                    "they occupy the same visual space. Preferred when emphasizing "
                                    "the category being compared."
                                )
                            }
                        },
                        "required": ["sections"]
                    },
                    "description": (
                        "Array of 2-4 bar models to compare visually. Each bar represents a "
                        "different scenario, group, or time period. Bars are arranged vertically "
                        "with consistent alignment for easy visual comparison of quantities and "
                        "relationships."
                    ),
                    "minItems": 2,
                    "maxItems": 4
                },
                "title": {
                    "type": "string",
                    "description": (
                        "Overall title for the entire comparison display (e.g., 'Class Performance "
                        "Comparison', 'Before and After Treatment'). Use when you need to "
                        "establish the comparative context. Often individual bar titles/labels "
                        "provide clearer information than an overall title."
                    )
                },
                "comparison_type": {
                    "type": "string",
                    "description": (
                        "Type of mathematical relationship being illustrated: 'difference' for "
                        "showing quantitative differences (e.g., more/less problems), 'ratio' for "
                        "proportional comparisons, 'part_whole' for showing how different parts "
                        "relate to wholes."
                    ),
                    "enum": ["difference", "ratio", "part_whole"]
                }
            },
            "required": ["bars"]
        }
    }
    return spec, generate_coach_bot_comparison_bar_models_image
