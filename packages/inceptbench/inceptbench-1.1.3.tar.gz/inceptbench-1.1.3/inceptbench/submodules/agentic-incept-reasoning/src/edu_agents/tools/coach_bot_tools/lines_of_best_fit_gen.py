from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.lines_of_best_fit import (  # noqa: E402, E501
    draw_lines_of_best_fit,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.lines_of_best_fit_model import (  # noqa: E402, E501
    Line,
    LinesOfBestFit,
)

logger = logging.getLogger("coach_bot_tools.lines_of_best_fit")


def generate_coach_bot_lines_of_best_fit_image(
    lines: List[Dict[str, Any]]
) -> str:
    """
    Generate a scatter plot with multiple lines of best fit options.
    
    Creates a scatter plot with generated data points and displays multiple potential
    lines of best fit for students to evaluate. Exactly one line must be marked as
    the correct best fit line. Useful for teaching statistical analysis and 
    correlation concepts.
    
    CRITICAL LIMITATION: The coordinate space is HARDCODED to 0-10 for both x and y axes.
    Any line values extending outside this range will be clipped/truncated at the boundaries.
    All lines must cross through this FIXED 10x10 coordinate space (x: 0-10, y: 0-10)
    in the positive quadrant for proper visibility.
    
    Parameters
    ----------
    lines : List[Dict[str, any]]
        List of exactly 4 line specifications, each containing:
        - slope: The slope of the line (recommend -3 to 3 for visibility)
        - y_intercept: The y-intercept (recommend 0-10 to avoid clipping)
        - label: Display label for the line (e.g., "Line A", "Line B")
        - best_fit: Boolean indicating if this is the correct line of best fit
        
    Returns
    -------
    str
        The URL of the generated lines of best fit image
    """
    
    # Use standardized logging
    best_fit_count = sum(line_data.get("best_fit", False) for line_data in lines)
    log_tool_generation("lines_of_best_fit_image", line_count=len(lines),
                        best_fit_count=best_fit_count)
    
    # Convert and validate input data to Pydantic models
    # Note: Pydantic model handles validation for exactly one best_fit line and 10x10 space crossing
    line_objects = []
    for line_data in lines:
        line_obj = Line(
            slope=line_data["slope"],
            y_intercept=line_data["y_intercept"],
            label=line_data["label"],
            best_fit=line_data["best_fit"]
        )
        line_objects.append(line_obj)
    
    # Create and validate the LinesOfBestFit stimulus using Pydantic
    # This validates exactly one best_fit line and 10x10 space crossing constraints
    lines_stimulus = LinesOfBestFit(lines=line_objects)
    
    # Generate the image using the lines of best fit function
    image_file_path = draw_lines_of_best_fit(lines_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_lines_of_best_fit_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for lines of best fit generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_lines_of_best_fit_image",
        description=(
            "Generate scatter plots with multiple lines of best fit for statistical analysis "
            "education. Creates educational visualizations showing data points with exactly 4 "
            "potential trend lines, where students must identify the correct line of best fit. "
            "Perfect for teaching correlation, regression analysis, and statistical reasoning. "
            "CRITICAL LIMITATION: The coordinate space is HARDCODED to 0-10 for both x and y axes "
            "- any line values outside this range will be clipped/truncated at the boundaries. "
            "All lines are automatically validated to ensure visibility within this fixed "
            "coordinate space."
        ),
        pydantic_model=LinesOfBestFit,
        custom_descriptions={
            "lines": (
                "Array of exactly 4 potential trend lines for statistical comparison. Each line "
                "must be geometrically valid (crosses the FIXED 10×10 coordinate space from x=0 to "
                "x=10, y=0 to y=10) and exactly one must be the correct statistical best fit. "
                "⚠️ CRITICAL LIMITATION: The coordinate space is hardcoded - any line extending "
                "beyond these bounds will be clipped. Lines should represent plausible but "
                "distinct trend interpretations to create meaningful educational comparisons for "
                "teaching statistical analysis and correlation concepts."
            )
        }
    )
    return spec, generate_coach_bot_lines_of_best_fit_image
