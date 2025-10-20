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

from content_generators.additional_content.stimulus_image.drawing_functions.graphing import (  # noqa: E402, I001
    plot_points,
    plot_points_four_quadrants,
    plot_points_quadrant_one,
    create_scatterplot,
    draw_stats_scatterplot,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.plot_points import (  # noqa: E402
    Point as PlotPoint,
    PointList,
    PointPlot,
    PointPlotWithContext,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.scatter_plot import (  # noqa: E402, E501
    ScatterPlot,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.stats_scatterplot import (  # noqa: E402, E501
    StatsScatterplot,
)

logger = logging.getLogger("coach_bot_tools.coordinate_graphing")


def generate_coach_bot_coordinate_points_image(
    points: List[Dict[str, Union[str, float]]],
    quadrant: str = "first"
) -> str:
    """
    Generate a coordinate plane with plotted points.
    
    Creates a coordinate plane graph with labeled points. Can display points
    in the first quadrant only or all four quadrants based on the data range.
    
    Parameters
    ----------
    points : List[Dict[str, Union[str, float]]]
        List of points to plot, each containing:
        - x: X-coordinate
        - y: Y-coordinate  
        - label: Label for the point
    quadrant : str
        "first" for first quadrant only, "four" for all four quadrants
        
    Returns
    -------
    str
        The URL of the generated coordinate points image
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_coordinate_points_image",
        points=points,
        quadrant=quadrant
    )
    
    # Create Point objects from the input data
    point_objects = []
    for point_data in points:
        point_obj = PlotPoint(
            x=point_data["x"],
            y=point_data["y"],
            label=point_data["label"]
        )
        point_objects.append(point_obj)
    
    if quadrant == "four":
        # Use four quadrant plotting
        point_list = PointList(root=point_objects)
        image_file_path = plot_points_four_quadrants(point_list)
    else:
        # Use first quadrant plotting 
        point_plot = PointPlot(points=point_objects)
        image_file_path = plot_points(point_plot)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_coordinate_points_with_context_image(
    points: List[Dict[str, Union[str, float]]],
    x_title: Optional[str] = None,
    y_title: Optional[str] = None
) -> str:
    """
    Generate a coordinate plane with contextual axis labels.
    
    Creates a first quadrant coordinate plane with custom axis labels,
    useful for real-world context problems with meaningful axis titles.
    
    IMPORTANT: All coordinates must be non-negative (x >= 0, y >= 0) for first quadrant plotting.
    
    Parameters
    ----------
    points : List[Dict[str, Union[str, float]]]
        List of points to plot, each containing:
        - x: X-coordinate (must be >= 0)
        - y: Y-coordinate (must be >= 0)
        - label: Label for the point
    x_title : Optional[str]
        Custom title for the x-axis
    y_title : Optional[str]
        Custom title for the y-axis
        
    Returns
    -------
    str
        The URL of the generated coordinate points with context image
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_coordinate_points_with_context_image",
        points=points,
        x_title=x_title,
        y_title=y_title
    )
    
    # Create the PointPlotWithContext stimulus using Pydantic model validation
    # Pydantic automatically handles List[Dict] → List[PointOneQuadrant] conversion
    point_plot_context = PointPlotWithContext(
        points=points,  # Pydantic handles Dict → PointOneQuadrant conversion automatically  # noqa: E501
        x_title=x_title or "",
        y_title=y_title or ""
    )
    
    # Generate the image using the context plotting function
    image_file_path = plot_points_quadrant_one(point_plot_context)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_scatter_plot_image(
    title: str,
    points: List[Dict[str, float]],
    x_axis: Dict[str, Union[str, float]],
    y_axis: Dict[str, Union[str, float]]
) -> str:
    """
    Generate a scatter plot with custom axes and scaling.
    
    Creates a scatter plot with configurable axis ranges and labels,
    useful for displaying correlations and statistical relationships.
    
    Parameters
    ----------
    title : str
        Title for the scatter plot
    points : List[Dict[str, float]]
        List of points to plot, each containing:
        - x: X-coordinate
        - y: Y-coordinate
    x_axis : Dict[str, Union[str, float]]
        X-axis configuration with:
        - label: Axis label
        - min_value: Minimum axis value
        - max_value: Maximum axis value
    y_axis : Dict[str, Union[str, float]]
        Y-axis configuration with:
        - label: Axis label
        - min_value: Minimum axis value
        - max_value: Maximum axis value
        
    Returns
    -------
    str
        The URL of the generated scatter plot image
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_scatter_plot_image",
        title=title,
        points=points,
        x_axis=x_axis,
        y_axis=y_axis
    )
    
    # Create the ScatterPlot stimulus using Pydantic model validation
    # Pydantic automatically handles all Dict → Model conversions
    scatter_plot = ScatterPlot(
        title=title,
        x_axis=x_axis,  # Pydantic handles Dict → Axis conversion automatically  # noqa: E501
        y_axis=y_axis,  # Pydantic handles Dict → Axis conversion automatically  # noqa: E501
        points=points   # Pydantic handles List[Dict] → List[Point] conversion automatically  # noqa: E501
    )
    
    # Generate the image using the scatter plot function
    image_file_path = create_scatterplot(scatter_plot)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_stats_scatter_plot_image(
    points: List[Dict[str, float]],
    line_of_best_fit: Dict[str, float]
) -> str:
    """
    Generate a statistical scatter plot with line of best fit.
    
    Creates a scatter plot highlighting points that lie exactly on the line
    of best fit in red, with other points in black. Useful for teaching
    linear regression and correlation analysis.
    
    IMPORTANT: All point coordinates (x and y values) must be within the
    range of -15 to 15 for proper statistical visualization and validation.
    
    Parameters
    ----------
    points : List[Dict[str, float]]
        List of points to plot, each containing:
        - x: X-coordinate (must be between -15 and 15)
        - y: Y-coordinate (must be between -15 and 15)
    line_of_best_fit : Dict[str, float]
        Line of best fit specification with:
        - slope: Slope of the line
        - intercept: Y-intercept of the line
        
    Returns
    -------
    str
        The URL of the generated statistical scatter plot image
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_stats_scatter_plot_image",
        points=points,
        line_of_best_fit=line_of_best_fit
    )
    
    # Create the StatsScatterplot stimulus using Pydantic model validation
    # Pydantic automatically handles all Dict → Model conversions
    stats_scatter = StatsScatterplot(
        points=points,  # Pydantic handles List[Dict] → List[Point] conversion automatically  # noqa: E501
        line_of_best_fit=line_of_best_fit  # Pydantic handles Dict → LineOfBestFit conversion automatically  # noqa: E501
    )
    
    # Generate the image using the stats scatter plot function
    image_file_path = draw_stats_scatterplot(stats_scatter)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_coordinate_points_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for coordinate points plotting."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_coordinate_points_image",
        "description": (
            "Generate a coordinate plane with plotted points. Creates a coordinate "
            "plane graph with labeled points. Can display points in the first quadrant "
            "only or all four quadrants based on the data range."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "number",
                                "description": "X-coordinate of the point"
                            },
                            "y": {
                                "type": "number",
                                "description": "Y-coordinate of the point"
                            },
                            "label": {
                                "type": "string",
                                "description": "Label for the point"
                            }
                        },
                        "required": ["x", "y", "label"]
                    },
                    "description": "List of points to plot on the coordinate plane"
                },
                "quadrant": {
                    "type": "string",
                    "enum": ["first", "four"],
                    "description": (
                        "Display mode: 'first' for first quadrant only, 'four' for all quadrants"
                    ),
                    "default": "first"
                }
            },
            "required": ["points"]
        }
    }
    return spec, generate_coach_bot_coordinate_points_image


def generate_coach_bot_coordinate_points_with_context_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for coordinate points with context."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_coordinate_points_with_context_image",
        description=(
            "Generate educational coordinate plane visualizations with contextual axis "
            "labels focused on first quadrant plotting and real-world mathematical "
            "applications. Creates professional coordinate graphs with custom axis "
            "titles perfect for contextual mathematics problems, data analysis exercises, "
            "and real-world scenario modeling. All coordinates must be non-negative "
            "(x ≥ 0, y ≥ 0) for first quadrant educational standards. Supports "
            "comprehensive point plotting with descriptive labels for enhanced student "
            "comprehension of coordinate systems, spatial relationships, and mathematical "
            "modeling. Perfect for worksheets, assessments, and interactive lessons "
            "that connect abstract coordinate concepts to practical applications in "
            "science, engineering, and everyday problem-solving contexts."
        ),
        pydantic_model=PointPlotWithContext,
        custom_descriptions={
            "points": (
                "List of coordinate points to plot in the first quadrant for educational "
                "coordinate plane exercises. Each point contains x-coordinate (≥ 0), "
                "y-coordinate (≥ 0), and descriptive label for mathematical learning. "
                "CRITICAL CONSTRAINT: All coordinates must be non-negative for first "
                "quadrant plotting standards. Use meaningful labels that connect to "
                "real-world contexts (e.g., 'School', 'Library', 'Park') for enhanced "
                "educational engagement. Perfect for distance problems, map coordinates, "
                "data plotting, and spatial reasoning development exercises."
            ),
            "x_title": (
                "Optional descriptive title for the horizontal x-axis providing educational "
                "context and real-world meaning. Use titles that connect to student "
                "experiences and learning objectives (e.g., 'Time (hours)', 'Distance "
                "(miles)', 'Temperature (°F)', 'Number of Items'). Clear axis labels "
                "enhance mathematical comprehension and help students understand the "
                "practical applications of coordinate systems in various contexts."
            ),
            "y_title": (
                "Optional descriptive title for the vertical y-axis providing educational "
                "context and mathematical meaning. Use titles that represent measurable "
                "quantities and connect to curriculum objectives (e.g., 'Height (feet)', "
                "'Cost ($)', 'Speed (mph)', 'Population'). Strategic axis labeling "
                "supports student understanding of coordinate relationships and reinforces "
                "connections between abstract mathematical concepts and real-world data."
            )
        }
    )
    return spec, generate_coach_bot_coordinate_points_with_context_image


def generate_coach_bot_scatter_plot_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for scatter plot generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_scatter_plot_image",
        description=(
            "Generate educational scatter plots with custom axes and scaling for "
            "statistical analysis and correlation visualization. Creates professional "
            "scatter plots with configurable axis ranges, labels, and data point "
            "visualization perfect for teaching statistical relationships, correlation "
            "analysis, and data interpretation skills. Supports comprehensive data "
            "visualization for mathematics, science, and social studies curricula. "
            "Essential for teaching students to identify patterns, trends, and "
            "relationships in bivariate data through visual analysis. Perfect for "
            "worksheets, assessments, research projects, and statistical reasoning "
            "exercises that develop critical thinking and data literacy skills."
        ),
        pydantic_model=ScatterPlot,
        custom_descriptions={
            "title": (
                "Descriptive title for the scatter plot providing educational context "
                "and statistical purpose. Use titles that clearly communicate the "
                "relationship being investigated (e.g., 'Height vs Weight', 'Study Time "
                "vs Test Scores', 'Temperature vs Ice Cream Sales'). Effective titles "
                "help students understand the variables being analyzed and the purpose "
                "of the statistical visualization for enhanced data literacy development."
            ),
            "points": (
                "List of data points to plot for statistical analysis and correlation "
                "investigation. Each point contains x-coordinate and y-coordinate "
                "representing paired numerical data values. Use realistic data sets "
                "that demonstrate meaningful relationships for educational purposes. "
                "Perfect for teaching correlation concepts, trend identification, "
                "outlier detection, and statistical reasoning through visual data "
                "analysis and interpretation exercises."
            ),
            "x_axis": (
                "Horizontal axis configuration defining the independent variable scale "
                "and educational context. Specify descriptive label (e.g., 'Time (hours)', "
                "'Age (years)', 'Temperature (°F)'), minimum value, and maximum value "
                "for appropriate data visualization. Strategic axis configuration enhances "
                "student understanding of variable relationships and supports effective "
                "statistical analysis and data interpretation skills development."
            ),
            "y_axis": (
                "Vertical axis configuration defining the dependent variable scale and "
                "measurement context. Specify descriptive label (e.g., 'Height (inches)', "
                "'Score (%)', 'Sales ($)'), minimum value, and maximum value for optimal "
                "data representation. Clear axis labeling supports student comprehension "
                "of statistical relationships and enhances analytical thinking skills "
                "through effective data visualization and interpretation practice."
            )
        }
    )
    return spec, generate_coach_bot_scatter_plot_image


def generate_coach_bot_stats_scatter_plot_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for statistical scatter plot."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_stats_scatter_plot_image",
        description=(
            "Generate advanced statistical scatter plots with line of best fit for "
            "linear regression and correlation analysis education. Creates professional "
            "statistical visualizations that highlight data points lying exactly on "
            "the line of best fit in red, with other data points in black for clear "
            "mathematical distinction. CRITICAL CONSTRAINT: All point coordinates "
            "(x and y values) must be within the range of -15 to 15 for proper "
            "statistical visualization and analysis. Essential for teaching advanced "
            "statistical concepts including linear regression, correlation analysis, "
            "prediction modeling, and residual analysis. Supports comprehensive "
            "statistical education in mathematics, science, and data analysis curricula. "
            "Perfect for introducing students to predictive modeling, trend analysis, "
            "and the mathematical relationship between correlation and causation through "
            "visual statistical reasoning and analytical thinking development."
        ),
        pydantic_model=StatsScatterplot,
        custom_descriptions={
            "points": (
                "List of coordinate data points for advanced statistical analysis and "
                "linear regression modeling. Each point contains x-coordinate and "
                "y-coordinate representing paired numerical data for correlation "
                "analysis. CRITICAL CONSTRAINT: All coordinates (both x and y) must be "
                "within the range of -15 to 15 for proper visualization and statistical "
                "analysis. EDUCATIONAL FEATURES: Points lying exactly on the line of "
                "best fit are automatically highlighted in red for visual emphasis, "
                "while other points appear in black. Use realistic datasets that "
                "demonstrate meaningful linear relationships within the coordinate bounds "
                "for effective statistical education and regression analysis skill development."
            ),
            "line_of_best_fit": (
                "Mathematical specification for the line of best fit defining the "
                "linear regression model for statistical analysis. Contains slope "
                "(rate of change) and y-intercept (starting value) parameters that "
                "define the predictive linear relationship. Essential for teaching "
                "concepts of correlation strength, prediction accuracy, and mathematical "
                "modeling. The tool validates that the provided line closely matches "
                "the actual statistical best fit for educational integrity and accurate "
                "mathematical representation in classroom instruction."
            )
        }
    )
    return spec, generate_coach_bot_stats_scatter_plot_image
