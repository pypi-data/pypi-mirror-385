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

from content_generators.additional_content.stimulus_image.drawing_functions.combo_points_table_graph import (  # noqa: E402, E501
    draw_combo_points_table_graph,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.combo_points_table_graph import (  # noqa: E402, E501
    ComboPointsTableGraph,
)

logger = logging.getLogger("coach_bot_tools.combo_points_table_graph")


def generate_coach_bot_combo_points_table_graph_image(
    table: Optional[Dict[str, any]] = None,
    points: Optional[List[Dict[str, Union[str, float]]]] = None,
    graphs: Optional[List[Dict[str, any]]] = None,
    x_axis: Optional[Dict[str, Union[int, float]]] = None,
    y_axis: Optional[Dict[str, Union[int, float]]] = None,
    graph_title: Optional[str] = None,
    show_grid: bool = True,
    legend_position: str = "upper right",
    highlight_points: Optional[List[str]] = None
) -> str:
    """
    Generate a combined visualization with table and coordinate graph.
    
    Creates a comprehensive educational visualization combining data tables and 
    coordinate plane graphs. Supports function identification, proportional 
    relationship comparison, and function property analysis for 8th grade standards.
    
    Parameters
    ----------
    table : Optional[Dict[str, any]]
        Table specification containing:
        - title: Title for the table
        - headers: List of column headers
        - rows: List of row data (each row is a list of values)
    points : Optional[List[Dict[str, Union[str, float]]]]
        List of points to plot, each containing:
        - x: X-coordinate
        - y: Y-coordinate  
        - label: Label for the point
    graphs : Optional[List[Dict[str, any]]]
        List of graph specifications for lines, curves, etc.
    x_axis : Optional[Dict[str, Union[int, float]]]
        X-axis configuration:
        - min_value: Minimum value
        - max_value: Maximum value
        - tick_interval: Interval between ticks
    y_axis : Optional[Dict[str, Union[int, float]]]
        Y-axis configuration:
        - min_value: Minimum value
        - max_value: Maximum value
        - tick_interval: Interval between ticks
    graph_title : Optional[str]
        Title for the graph portion
    show_grid : bool
        Whether to show grid lines
    legend_position : str
        Position for the legend
    highlight_points : Optional[List[str]]
        List of point labels to highlight
        
    Returns
    -------
    str
        The URL of the generated combo graph image
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_combo_points_table_graph_image",
        table=table,
        points=points,
        graphs=graphs,
        x_axis=x_axis,
        y_axis=y_axis,
        graph_title=graph_title,
        show_grid=show_grid,
        legend_position=legend_position,
        highlight_points=highlight_points
    )
    
    # Create the ComboPointsTableGraph stimulus using Pydantic model validation
    # Pydantic automatically handles all Dict → Model conversions and validation
    combo_stimulus = ComboPointsTableGraph(
        table=table,  # Pydantic handles Dict → TableData conversion automatically
        points=points,  # Pydantic handles List[Dict] → List[Point] conversion automatically
        graphs=graphs,  # Pydantic handles List[Dict] → List[GraphSpec] conversion automatically
        x_axis=x_axis,  # Pydantic handles Dict → AxisSpec conversion automatically
        y_axis=y_axis,  # Pydantic handles Dict → AxisSpec conversion automatically
        graph_title=graph_title,
        show_grid=show_grid,
        legend_position=legend_position,
        highlight_points=highlight_points
    )
    
    # Generate the image using the combo function
    image_file_path = draw_combo_points_table_graph(combo_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_combo_points_table_graph_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for combo points table graph generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_combo_points_table_graph_image",
        description=(
            "Generate comprehensive educational visualizations combining data tables and "
            "coordinate plane graphs focused on algebraic reasoning and function analysis. "
            "Creates integrated table-graph combinations perfect for 8th grade mathematical "
            "standards including function identification, proportional relationship comparison, "
            "and function property analysis. CRITICAL FORMAT REQUIREMENTS: Table 'rows' "
            "parameter MUST contain ALL string values with quotes, even numbers: use "
            "[['0', '2'], ['1', '4'], ['2', '6']] NOT [[0, 2], [1, 4], [2, 6]]. Graph "
            "specifications MUST use 'type' field (not 'graph_type') with exact values: "
            "'line', 'quadratic', 'cubic', 'circle', 'scatter', etc. Supports multiple "
            "visualization types: scatter plots for data exploration, linear functions for "
            "proportional relationships, quadratic and higher-order functions for advanced "
            "concepts, and customizable axis configurations for various mathematical contexts. "
            "Perfect for worksheets, assessments, and mathematical modeling exercises."
        ),
        pydantic_model=ComboPointsTableGraph,
        custom_descriptions={
            "table": (
                "Optional data table specification for tabular representation alongside "
                "the coordinate graph. **MANDATORY STRING FORMAT**: 'headers' must be "
                "list of strings ['x', 'y']. 'rows' MUST be list of lists where EVERY "
                "SINGLE CELL VALUE IS A STRING - even numbers MUST be quoted as strings. "
                "CORRECT: [['0', '2'], ['1', '4'], ['2', '6']] with quotes around numbers. "
                "WRONG: [[0, 2], [1, 4], [2, 6]] without quotes - this will cause "
                "validation errors. ALL table cell values including numbers, decimals, "
                "and text MUST be strings with quotes. Optional 'title' provides "
                "educational context. Perfect for showing input-output relationships, "
                "function tables, experimental data, and comparative datasets."
            ),
            "points": (
                "Individual coordinate points to plot and label on the graph for precise "
                "mathematical analysis and student reference. Each point contains "
                "x-coordinate (number), y-coordinate (number), and descriptive label "
                "(string). Use for highlighting specific function values, intercepts, "
                "vertices, critical points, or data observations. Essential for teaching "
                "coordinate plane concepts, function evaluation, and connecting algebraic "
                "expressions to geometric representations. Supports educational exercises "
                "in plotting, coordinate identification, and graphical function analysis."
            ),
            "graphs": (
                "Mathematical function specifications for drawing lines, curves, and "
                "complex functions on the coordinate plane. CRITICAL FIELD REQUIREMENTS: "
                "Use 'type' field (NOT 'graph_type') with exact values: 'line', 'quadratic', "
                "'cubic', 'circle', 'scatter', 'curve', 'sideways_parabola', 'hyperbola', "
                "'ellipse', 'sqrt', 'rational'. For linear functions: provide 'slope' and "
                "'y_intercept'. For quadratic: provide 'a', 'b', 'c' coefficients. For "
                "circles: provide 'center_x', 'center_y', 'radius'. Each graph supports "
                "'color', 'label', 'equation', 'line_style', 'line_width' for visual "
                "customization. Essential for comprehensive mathematical education and "
                "function comparison exercises."
            ),
            "x_axis": (
                "Horizontal axis configuration defining the domain and visual scale for "
                "mathematical functions and data representation. Specify label for "
                "educational context (e.g., 'Time (hours)', 'Input Value', 'x'), "
                "min_value and max_value for appropriate mathematical range, and "
                "tick_interval for precise scaling. Strategic axis configuration enhances "
                "student understanding of function domains, coordinate systems, and "
                "mathematical scaling for various algebraic and statistical contexts."
            ),
            "y_axis": (
                "Vertical axis configuration defining the range and visual scale for "
                "function outputs and dependent variables. Specify label for educational "
                "context (e.g., 'Distance (miles)', 'Output Value', 'f(x)'), min_value "
                "and max_value for appropriate mathematical range, and tick_interval for "
                "precise scaling. Strategic axis configuration supports student comprehension "
                "of function ranges, dependent variable relationships, and mathematical "
                "scaling for diverse algebraic and data analysis scenarios."
            ),
            "graph_title": (
                "Optional descriptive title for the coordinate graph portion providing "
                "educational context and mathematical scenario identification. Use titles "
                "like 'Linear Function Analysis', 'Proportional Relationships', 'Data "
                "Exploration', or specific mathematical scenarios for enhanced student "
                "engagement and contextual learning. Clear titles support worksheet "
                "organization and assessment clarity."
            ),
            "show_grid": (
                "Boolean control for coordinate plane grid display enhancing mathematical "
                "precision and student measurement capabilities. Grid lines support "
                "accurate point plotting, function tracing, coordinate identification, "
                "and visual estimation skills. Enable for detailed mathematical work "
                "and coordinate exercises, disable for simplified presentations or "
                "aesthetic clarity in final assessments."
            ),
            "legend_position": (
                "Strategic placement of the graph legend for optimal educational clarity "
                "and visual organization. Choose 'upper right', 'upper left', 'lower right', "
                "or 'lower left' based on graph content and available space. Proper legend "
                "positioning ensures student identification of multiple functions, data "
                "series, or mathematical elements without obscuring critical graph features "
                "or educational content."
            ),
            "highlight_points": (
                "List of specific point labels to emphasize with special visual styling "
                "for focused mathematical attention and educational emphasis. Use to draw "
                "student attention to critical function features like intercepts, vertices, "
                "intersections, maximum/minimum values, or key data observations. Strategic "
                "highlighting supports guided mathematical analysis and assessment focus "
                "on essential algebraic concepts and function properties."
            )
        }
    )
    return spec, generate_coach_bot_combo_points_table_graph_image
