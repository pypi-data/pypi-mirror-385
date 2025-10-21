from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.graphing_piecewise import (  # noqa: E402, E501
    generate_piecewise_graph,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.graphing_piecewise_model import (  # noqa: E402, E501
    GraphingPiecewise,
)

logger = logging.getLogger("coach_bot_tools.piecewise_graphing")


def generate_coach_bot_piecewise_function_image(
    segments: List[Dict[str, Any]],
    x_axis_label: Optional[str] = None,
    y_axis_label: Optional[str] = None
) -> str:
    """
    Generate a piecewise function graph with connected segments.
    
    Creates a piecewise function visualization with 3-5 connected segments that can be
    linear or nonlinear. Useful for teaching function concepts, domain and range,
    and analyzing complex mathematical relationships.
    
    Parameters
    ----------
    segments : List[Dict[str, Any]]
        List of segment specifications, each containing:
        - start_coordinate: [x, y] coordinate where segment begins
        - end_coordinate: [x, y] coordinate where segment ends  
        - linear: True for straight line, False for curved segment
    x_axis_label : Optional[str]
        Label for the x-axis
    y_axis_label : Optional[str]
        Label for the y-axis
        
    Returns
    -------
    str
        The URL of the generated piecewise function graph image
    """
    
    # Use standardized logging
    log_tool_generation("piecewise_function_image", segment_count=len(segments), 
                       has_x_label=x_axis_label is not None, 
                       has_y_label=y_axis_label is not None)
    
    # Create and validate the GraphingPiecewise using Pydantic
    # This handles all validation: segment count (3-5), connectivity,
    # coordinate ranges (±10), and segment structure
    piecewise_stimulus = GraphingPiecewise(
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        segments=segments
    )
    
    # Generate the image using the piecewise function
    image_file_path = generate_piecewise_graph(piecewise_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_piecewise_function_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for piecewise function graphing."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_piecewise_function_image",
        description=(
            "Generate piecewise function graphs for advanced mathematics education. Creates "
            "sophisticated function visualizations with 3-5 connected segments that can be "
            "linear (straight lines) or nonlinear (curved). Perfect for teaching advanced "
            "algebra, pre-calculus, and calculus concepts including function analysis, "
            "domain and range, continuity, piecewise-defined functions, and complex "
            "mathematical relationships. Each segment connects precisely to the next, "
            "creating continuous or discontinuous functions for comprehensive mathematical "
            "exploration. Coordinates are constrained to ±10 range for optimal "
            "visualization. Ideal for function graphing exercises, mathematical modeling, "
            "calculus preparation, function transformation studies, and advanced problem "
            "solving activities. Supports both linear segments (straight line connections) "
            "and nonlinear segments (smooth curves) to represent diverse mathematical "
            "relationships and real-world applications."
        ),
        pydantic_model=GraphingPiecewise,
        custom_descriptions={
            "segments": (
                "List of connected function segments defining the piecewise function structure. "
                "Each segment must connect precisely to the next (end coordinate of one segment "
                "equals start coordinate of the next). CRITICAL: Must contain exactly 3-5 segments "
                "for optimal educational visualization. Each segment requires start_coordinate "
                "[x, y], end_coordinate [x, y], and linear boolean (true for straight lines, "
                "false for curves). MANDATORY: All coordinates must be INTEGERS only (no decimals "
                "or fractions) and within ±10 range for proper scaling. "
                "Example: [{'start_coordinate': [-5, 2], 'end_coordinate': [0, 4], 'linear': "
                "true}, {'start_coordinate': [0, 4], 'end_coordinate': [3, 1], 'linear': false}, "
                "{'start_coordinate': [3, 1], 'end_coordinate': [7, 6], 'linear': true}]. "
                "Perfect for teaching function continuity, domain analysis, and mathematical "
                "modeling."
            ),
            "x_axis_label": (
                "Optional educational label for the x-axis to provide mathematical context. "
                "Use descriptive labels that enhance learning: 'Time (hours)', 'Distance "
                "(meters)', 'Input Values', 'Domain', or subject-specific variables like 't', 'x', "
                "'n'. Clear axis labeling improves student comprehension of function relationships "
                "and real-world applications."
            ),
            "y_axis_label": (
                "Optional educational label for the y-axis to provide mathematical context. "
                "Use descriptive labels that enhance learning: 'Height (feet)', 'Cost ($)', "
                "'Output Values', 'Range', or function notation like 'f(x)', 'y', 'g(t)'. "
                "Proper axis labeling reinforces function notation and mathematical communication "
                "skills."
            )
        }
    )
    return spec, generate_coach_bot_piecewise_function_image
