from __future__ import annotations

import logging
from typing import Callable, Dict, List, Union

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.line_graph import (  # noqa: E402
    create_line_graph,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.line_graph_description import (  # noqa: E402, E501
    LineDataPoint,
    LineGraph,
    LineGraphList,
    LineGraphSeries,
)

logger = logging.getLogger("coach_bot_tools.line_graph")


def generate_coach_bot_line_graph_image(
    title: str,
    x_axis_label: str,
    y_axis_label: str,
    data_series: List[Dict[str, Union[str, List[Dict[str, float]]]]]
) -> str:
    """
    Generate a multi-series line graph with customizable styling.
    
    Creates line graphs with multiple data series (lines) on the same chart. Each series
    can have its own color and label. Useful for comparing trends, showing relationships
    between variables, or displaying multiple datasets on the same axes.
    
    Note: For statistical line plots with specialized formatting, use the line plot tools instead.
    
    Parameters
    ----------
    title : str
        The main title of the line graph
    x_axis_label : str
        Label for the x-axis
    y_axis_label : str
        Label for the y-axis
    data_series : List[Dict[str, Union[str, List[Dict[str, float]]]]]
        List of data series to plot, each containing:
        - label: Display name for the series (optional, for legend)
        - color: Color for the line (optional, e.g., 'blue', 'red', '#FF5733')
        - data_points: List of coordinate points, each with 'x' and 'y' values
        
    Returns
    -------
    str
        The URL of the generated line graph image
    """
    
    # Use standardized logging
    total_points = sum(len(series.get("data_points", [])) for series in data_series)
    log_tool_generation("line_graph_image", title=title, series_count=len(data_series), 
                       total_data_points=total_points)
    
    # Convert and validate input data to nested Pydantic models
    # Structure: LineGraphList → LineGraph → LineGraphSeries → LineDataPoint
    series_objects = []
    for series_data in data_series:
        # Create LineDataPoint objects
        data_points = []
        for point_data in series_data["data_points"]:
            point_obj = LineDataPoint(
                x=point_data["x"],
                y=point_data["y"]
            )
            data_points.append(point_obj)
        
        # Create the series object
        series_obj = LineGraphSeries(
            data_points=data_points,
            label=series_data.get("label"),
            color=series_data.get("color")
        )
        series_objects.append(series_obj)
    
    # Create and validate the complete LineGraph using Pydantic
    # This validates axis labels, data series constraints, and coordinate values
    line_graph = LineGraph(
        title=title,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        data_series=series_objects
    )
    
    # Create the LineGraphList (required by the drawing function)
    line_graph_list = LineGraphList(root=[line_graph])
    
    # Generate the image using the line graph function
    image_file_path = create_line_graph(line_graph_list)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_line_graph_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for line graph generation."""
    # Note: This uses an enhanced static spec because the wrapper interface is flattened
    # (takes nested List[Dict] structures) while the Pydantic models use 4-layer nested objects
    spec = {
        "type": "function",
        "name": "generate_coach_bot_line_graph_image",
        "description": (
            "Generate multi-series line graphs for trend analysis, data comparison, and "
            "mathematical function visualization. Creates professional line charts with multiple "
            "data series (lines) on the same axes, each with customizable colors and labels. "
            "Perfect for showing relationships between variables, comparing datasets over time, or "
            "displaying mathematical functions. Supports legends, axis labeling, and clean "
            "educational formatting."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": (
                        "The main title displayed at the top of the line graph. Should clearly "
                        "describe what the graph shows (e.g., 'Temperature vs Time', 'Student "
                        "Performance Comparison')."
                    ),
                    "maxLength": 100
                },
                "x_axis_label": {
                    "type": "string",
                    "description": (
                        "Label for the horizontal x-axis describing the independent variable "
                        "(e.g., 'Time (hours)', 'Temperature (°C)', 'Week Number')."
                    ),
                    "maxLength": 50
                },
                "y_axis_label": {
                    "type": "string",
                    "description": (
                        "Label for the vertical y-axis describing the dependent variable "
                        "(e.g., 'Score (%)', 'Distance (km)', 'Population')."
                    ),
                    "maxLength": 50
                },
                "data_series": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": (
                                    "Display name for this data series shown in the legend "
                                    "(e.g., 'Class A', 'Before Treatment', 'Linear Function'). "
                                    "Optional for single-series graphs."
                                ),
                                "maxLength": 30
                            },
                            "color": {
                                "type": "string",
                                "description": (
                                    "Color for the line using standard color names (e.g., 'blue', "
                                    "'red', 'green') or hex codes (e.g., '#FF5733', '#3498DB'). If "
                                    "omitted, colors are assigned automatically."
                                )
                            },
                            "data_points": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "x": {
                                            "type": "number",
                                            "description": (
                                                "X-coordinate (horizontal position) of the data "
                                                "point. Represents the independent variable value."
                                            )
                                        },
                                        "y": {
                                            "type": "number",
                                            "description": (
                                                "Y-coordinate (vertical position) of the data "
                                                "point. Represents the dependent variable value."
                                            )
                                        }
                                    },
                                    "required": ["x", "y"]
                                },
                                "description": (
                                    "Array of (x, y) coordinate points that form this line. Points "
                                    "should be in logical order (typically ascending x-values) for "
                                    "proper line connection. Minimum 2 points required to form a "
                                    "line."
                                ),
                                "minItems": 2,
                                "maxItems": 50
                            }
                        },
                        "required": ["data_points"]
                    },
                    "description": (
                        "Array of data series (lines) to plot on the same graph. Each series "
                        "represents a different dataset, group, or function. Use multiple series "
                        "to compare trends, show before/after scenarios, or display related "
                        "variables."
                    ),
                    "minItems": 1,
                    "maxItems": 5
                }
            },
            "required": ["title", "x_axis_label", "y_axis_label", "data_series"]
        }
    }
    return spec, generate_coach_bot_line_graph_image
