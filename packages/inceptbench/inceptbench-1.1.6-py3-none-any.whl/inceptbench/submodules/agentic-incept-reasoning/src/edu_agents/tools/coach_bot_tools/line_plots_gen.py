from __future__ import annotations

import logging
from typing import Callable, Dict, List, Union

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.line_plots import (  # noqa: E402
    generate_double_line_plot,
    generate_single_line_plot,
    generate_stacked_line_plots,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.double_line_plot import (  # noqa: E402, E501
    DoubleLinePlot,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.line_plots import (  # noqa: E402
    DataPoint,
    LinePlot,
    LinePlotList,
    SingleLinePlot,
)

logger = logging.getLogger("coach_bot_tools.line_plots")


def generate_coach_bot_single_line_plot_image(
    title: str,
    x_axis_label: str,
    data_points: List[Dict[str, Union[str, int]]]
) -> str:
    """
    Generate a single line plot for data visualization.
    
    Creates a line plot showing frequency data with X marks stacked vertically
    above each value. Useful for displaying small datasets and teaching basic
    data analysis concepts.
    
    Parameters
    ----------
    title : str
        Title for the line plot
    x_axis_label : str
        Label for the x-axis
    data_points : List[Dict[str, Union[str, int]]]
        List of data points, each containing:
        - value: The x-axis value (string, number, or fraction)
        - frequency: Number of occurrences (0-8)
        
    Returns
    -------
    str
        The URL of the generated line plot image
    """
    
    log_tool_generation(
        "generate_coach_bot_single_line_plot_image",
        title=title,
        x_axis_label=x_axis_label,
        data_points=data_points
    )
    
    # Create DataPoint objects from the input data
    data_point_objects = []
    for point_data in data_points:
        data_point_obj = DataPoint(
            value=str(point_data["value"]),
            frequency=point_data["frequency"]
        )
        data_point_objects.append(data_point_obj)
    
    # Create the SingleLinePlot stimulus
    line_plot_stimulus = SingleLinePlot(
        title=title,
        x_axis_label=x_axis_label,
        data_points=data_point_objects
    )
    
    # Generate the image using the single line plot function
    image_file_path = generate_single_line_plot(line_plot_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_stacked_line_plots_image(
    line_plots: List[Dict[str, any]]
) -> str:
    """
    Generate multiple line plots arranged in a grid layout.
    
    Creates 2-4 line plots arranged in a grid for comparison. Each plot shows
    frequency data with X marks stacked vertically. Useful for comparing
    multiple datasets or showing different scenarios.
    
    Parameters
    ----------
    line_plots : List[Dict[str, any]]
        List of 2-4 line plot specifications, each containing:
        - title: Title for this line plot
        - x_axis_label: X-axis label for this line plot
        - data_points: List of data point objects
        
    Returns
    -------
    str
        The URL of the generated stacked line plots image
    """
    
    log_tool_generation(
        "generate_coach_bot_stacked_line_plots_image",
        line_plots=line_plots
    )
    
    # Create LinePlot objects from the input data
    line_plot_objects = []
    for plot_data in line_plots:
        data_point_objects = []
        for point_data in plot_data["data_points"]:
            data_point_obj = DataPoint(
                value=str(point_data["value"]),
                frequency=point_data["frequency"]
            )
            data_point_objects.append(data_point_obj)
        
        line_plot_obj = LinePlot(
            title=plot_data["title"],
            x_axis_label=plot_data["x_axis_label"],
            data_points=data_point_objects
        )
        line_plot_objects.append(line_plot_obj)
    
    # Create the LinePlotList stimulus
    line_plot_list = LinePlotList(root=line_plot_objects)
    
    # Generate the image using the stacked line plots function
    image_file_path = generate_stacked_line_plots(line_plot_list)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_double_line_plot_image(
    x_axis_label: str,
    datasets: List[Dict[str, any]]
) -> str:
    """
    Generate a double line plot for comparing two datasets.
    
    Creates a specialized line plot that displays two datasets on opposite sides
    of a horizontal axis. Useful for comparing two groups or showing before/after
    data in educational contexts.
    
    Parameters
    ----------
    x_axis_label : str
        Label for the x-axis
    datasets : List[Dict[str, any]]
        List of exactly 2 dataset specifications, each containing:
        - title: Title for this dataset
        - data_points: List of data point objects with value and frequency
        
    Returns
    -------
    str
        The URL of the generated double line plot image
    """
    
    log_tool_generation(
        "generate_coach_bot_double_line_plot_image",
        x_axis_label=x_axis_label,
        datasets=datasets
    )
    
    # Prepare raw dictionary data for DoubleLinePlot
    # The model validator expects raw dict data, not Pydantic objects
    datasets_raw = []
    for dataset_data in datasets:
        data_points_raw = []
        for point_data in dataset_data["data_points"]:
            data_points_raw.append({
                "value": point_data["value"],
                "frequency": point_data["frequency"]
            })
        
        datasets_raw.append({
            "title": dataset_data["title"],
            "data_points": data_points_raw
        })
    
    # Create the DoubleLinePlot stimulus with raw dictionary data
    # This allows the @model_validator(mode="before") to work properly
    double_line_plot_stimulus = DoubleLinePlot(
        x_axis_label=x_axis_label,
        datasets=datasets_raw
    )
    
    # Generate the image using the double line plot function
    image_file_path = generate_double_line_plot(double_line_plot_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_single_line_plot_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for single line plot generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_single_line_plot_image",
        description=(
            "Generate a single line plot for data visualization. Creates a line plot "
            "showing frequency data with X marks stacked vertically above each value. "
            "Useful for displaying small datasets and teaching basic data analysis concepts. "
            "Data points can include string values, numbers, or fractions like '2 1/2'."
        ),
        pydantic_model=SingleLinePlot,
        custom_descriptions={
            "data_points": (
                "Data points for the line plot. Each data point contains a value "
                "(string, number, or fraction like '2 1/2') and frequency (0-8 occurrences). "
                "Maximum 8 data points per plot."
            )
        }
    )
    return spec, generate_coach_bot_single_line_plot_image


def generate_coach_bot_stacked_line_plots_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for stacked line plots generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_stacked_line_plots_image",
        "description": (
            "Generate multiple line plots arranged in a grid layout for comparative data analysis. "
            "Creates 2-4 line plots arranged in a grid format, allowing students to compare "
            "different datasets, time periods, or experimental conditions side-by-side. Each plot "
            "displays frequency data with X marks stacked vertically above each value. Excellent "
            "for teaching data comparison, pattern recognition, and statistical analysis skills. "
            "Supports string values, numbers, and fractions for x-axis data points."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "line_plots": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title for this individual line plot that clearly "
                                               "identifies the dataset or condition being "
                                               "displayed (e.g., 'Class A Test Scores', 'Before "
                                               "Training', 'Group 1 Results')"
                            },
                            "x_axis_label": {
                                "type": "string",
                                "description": "Label for the x-axis that describes what the data "
                                               "represents (e.g., 'Score Range', 'Time Period', "
                                               "'Categories', 'Number of Items')"
                            },
                            "data_points": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "value": {
                                            "type": ["string", "number"],
                                            "description": "The x-axis value (string, number, or "
                                                           "fraction like '2 1/2'). Can represent "
                                                           "categories, time periods, "
                                                           "measurements, or any data "
                                                           "classification"
                                        },
                                        "frequency": {
                                            "type": "integer",
                                            "minimum": 0,
                                            "maximum": 8,
                                            "description": "Number of occurrences or frequency "
                                                           "count at this value. Each frequency "
                                                           "unit is represented by an X mark "
                                                           "stacked vertically"
                                        }
                                    },
                                    "required": ["value", "frequency"]
                                },
                                "minItems": 1,
                                "maxItems": 8
                            }
                        },
                        "required": ["title", "x_axis_label", "data_points"]
                    },
                    "description": "List of 2-4 line plots to display in a grid layout for "
                                   "side-by-side comparison. Each plot should represent a "
                                   "different dataset, condition, or time period for "
                                   "effective comparative analysis",
                    "minItems": 2,
                    "maxItems": 4
                }
            },
            "required": ["line_plots"]
        }
    }
    return spec, generate_coach_bot_stacked_line_plots_image


def generate_coach_bot_double_line_plot_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for double line plot generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_double_line_plot_image",
        "description": (
            "Generate a double line plot for comparing two datasets. Creates a "
            "specialized line plot that displays two datasets on opposite sides "
            "of a horizontal axis. Useful for comparing two groups or showing "
            "before/after data in educational contexts. IMPORTANT: X-axis range "
            "is automatically calculated and missing values are filled with frequency 0. "
            "Range constraints: single-digit values allow range up to 20, multi-digit values allow "
            "range up to 12."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "x_axis_label": {
                    "type": "string",
                    "description": "Label for the x-axis that describes what the data represents "
                                   "(e.g., 'Age', 'Score', 'Time Period')"
                },
                "datasets": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title for this dataset that clearly identifies "
                                               "what group or condition it represents"
                            },
                            "data_points": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "value": {
                                            "type": "integer",
                                            "minimum": -999,
                                            "maximum": 999,
                                            "description": "The x-axis value (integer). Range "
                                                           "constraints: single-digit values allow "
                                                           "range up to 20, multi-digit values "
                                                           "allow range up to 12."
                                        },
                                        "frequency": {
                                            "type": "integer",
                                            "minimum": 0,
                                            "maximum": 8,
                                            "description": "Number of occurrences at this value. "
                                                           "Each frequency unit is represented by "
                                                           "an X mark"
                                        }
                                    },
                                    "required": ["value", "frequency"]
                                },
                                "description": "Data points for this dataset. Missing values in "
                                               "the range will be automatically filled with "
                                               "frequency 0."
                            }
                        },
                        "required": ["title", "data_points"]
                    },
                    "description": "Exactly 2 datasets to compare. Data points are automatically "
                                   "sorted by value and missing values in the range are filled "
                                   "with frequency 0.",
                    "minItems": 2,
                    "maxItems": 2
                }
            },
            "required": ["x_axis_label", "datasets"]
        }
    }
    return spec, generate_coach_bot_double_line_plot_image
