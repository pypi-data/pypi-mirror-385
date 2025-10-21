from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional, Union

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.categorical_graphs import (  # noqa: E402, E501
    create_categorical_graph,
    create_multi_bar_graph,
    create_multi_picture_graph,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.categorical_graph import (  # noqa: E402, E501
    CategoricalGraph,
    CategoricalGraphList,
    DataPoint,
    MultiGraphList,
    PictureGraphConfig,
)

logger = logging.getLogger("coach_bot_tools.categorical_graphs")


def generate_coach_bot_categorical_graph_image(
    graph_type: str,
    title: str,
    x_axis_label: str,
    y_axis_label: str,
    data: List[Dict[str, Union[str, float]]],
    picture_graph_config: Optional[Dict[str, Union[int, str, bool]]] = None
) -> str:
    """
    Generate a categorical graph (bar graph, histogram, or picture graph).
    
    Creates various types of categorical data visualizations including bar graphs,
    histograms, and picture graphs with customizable styling and data representation.
    
    Parameters
    ----------
    graph_type : str
        Type of graph to create ("bar_graph", "histogram", or "picture_graph")
    title : str
        Title for the graph
    x_axis_label : str
        Label for the x-axis
    y_axis_label : str
        Label for the y-axis
    data : List[Dict[str, Union[str, float]]]
        List of data points, each containing:
        - category: The category name
        - frequency: The frequency/count for this category
    picture_graph_config : Optional[Dict[str, Union[int, str, bool]]]
        Configuration for picture graphs (required if graph_type is "picture_graph"):
        - star_value: Value each star represents
        - star_unit: Unit name for the stars
        - show_half_star_value: Whether to show half-star legend
        
    Returns
    -------
    str
        The URL of the generated categorical graph image
    """
    
    log_tool_generation(
        "generate_coach_bot_categorical_graph_image",
        graph_type=graph_type,
        title=title,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        data=data,
        picture_graph_config=picture_graph_config
    )
    
    # Create DataPoint objects from the input data
    data_point_objects = []
    for item in data:
        data_point_obj = DataPoint(
            category=item["category"],
            frequency=item["frequency"]
        )
        data_point_objects.append(data_point_obj)
    
    # Create picture config if provided
    pic_config = None
    if picture_graph_config:
        pic_config = PictureGraphConfig(
            star_value=picture_graph_config["star_value"],
            star_unit=picture_graph_config["star_unit"],
            show_half_star_value=picture_graph_config.get("show_half_star_value", False)
        )
    
    # Create and validate the CategoricalGraph
    categorical_graph = CategoricalGraph(
        graph_type=graph_type,
        title=title,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        data=data_point_objects,
        picture_graph_config=pic_config
    )
    
    # Create and validate the CategoricalGraphList (wrapper expects a list)
    graph_list = CategoricalGraphList(root=[categorical_graph])
    
    # Generate the image using the categorical graph function
    image_file_path = create_categorical_graph(graph_list)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_multi_bar_graph_image(
    graphs: List[Dict[str, any]]
) -> str:
    """
    Generate a 2x2 grid of bar graphs in a single image.
    
    Creates four bar graphs arranged in a 2x2 grid layout, useful for comparing
    multiple datasets or showing different views of related data.
    
    Parameters
    ----------
    graphs : List[Dict[str, any]]
        List of exactly 4 graph specifications, each containing:
        - title: Title for this graph
        - x_axis_label: Label for the x-axis
        - y_axis_label: Label for the y-axis  
        - data: List of data points with category and frequency
        
    Returns
    -------
    str
        The URL of the generated multi bar graph image
    """
    
    if len(graphs) != 4:
        raise ValueError("Multi bar graph requires exactly 4 graphs")
    
    log_tool_generation(
        "generate_coach_bot_multi_bar_graph_image",
        graphs=graphs
    )
    
    # Create CategoricalGraph objects from the input data
    graph_objects = []
    for graph_spec in graphs:
        data_point_objects = []
        for item in graph_spec["data"]:
            data_point_obj = DataPoint(
                category=item["category"],
                frequency=item["frequency"]
            )
            data_point_objects.append(data_point_obj)
        
        graph_obj = CategoricalGraph(
            graph_type="bar_graph",
            title=graph_spec["title"],
            x_axis_label=graph_spec["x_axis_label"],
            y_axis_label=graph_spec["y_axis_label"],
            data=data_point_objects
        )
        graph_objects.append(graph_obj)
    
    # Create and validate the MultiGraphList
    multi_graph_list = MultiGraphList(root=graph_objects)
    
    # Generate the image using the multi bar graph function
    image_file_path = create_multi_bar_graph(multi_graph_list)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_multi_picture_graph_image(
    graphs: List[Dict[str, any]]
) -> str:
    """
    Generate a 2x2 grid of picture graphs in a single image.
    
    Creates four picture graphs arranged in a 2x2 grid layout, useful for comparing
    multiple datasets using visual star representations.
    
    Parameters
    ----------
    graphs : List[Dict[str, any]]
        List of exactly 4 graph specifications, each containing:
        - title: Title for this graph
        - data: List of data points with category and frequency
        - picture_config: Configuration with star_value, star_unit, show_half_star_value
        
    Returns
    -------
    str
        The URL of the generated multi picture graph image
    """
    
    if len(graphs) != 4:
        raise ValueError("Multi picture graph requires exactly 4 graphs")
    
    log_tool_generation(
        "generate_coach_bot_multi_picture_graph_image",
        graphs=graphs
    )
    
    # Create CategoricalGraph objects from the input data
    graph_objects = []
    for graph_spec in graphs:
        data_point_objects = []
        for item in graph_spec["data"]:
            data_point_obj = DataPoint(
                category=item["category"],
                frequency=item["frequency"]
            )
            data_point_objects.append(data_point_obj)
        
        # Create picture config
        pic_config_data = graph_spec["picture_config"]
        pic_config = PictureGraphConfig(
            star_value=pic_config_data["star_value"],
            star_unit=pic_config_data["star_unit"],
            show_half_star_value=pic_config_data.get("show_half_star_value", False)
        )
        
        graph_obj = CategoricalGraph(
            graph_type="picture_graph",
            title=graph_spec["title"],
            x_axis_label="",  # Picture graphs typically don't have axis labels
            y_axis_label="",
            data=data_point_objects,
            picture_graph_config=pic_config
        )
        graph_objects.append(graph_obj)
    
    # Create and validate the MultiGraphList
    multi_graph_list = MultiGraphList(root=graph_objects)
    
    # Generate the image using the multi picture graph function
    image_file_path = create_multi_picture_graph(multi_graph_list)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_categorical_graph_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for categorical graph generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_categorical_graph_image",
        description=(
            "Generate a single categorical graph for data visualization and analysis. Creates "
            "bar graphs (vertical bars), histograms (for frequency distributions), or picture "
            "graphs (using star symbols). Ideal for elementary and middle school mathematics, "
            "statistics, and data analysis instruction. Features robust validation for educational "
            "accuracy and supports half-value representations for more precise data modeling. "
            "Picture graphs are limited to maximum frequency of 35 per category for visual clarity."
        ),
        pydantic_model=CategoricalGraph,
        custom_descriptions={
            "graph_type": (
                "Type of categorical graph to create: 'bar_graph' for standard vertical "
                "bar charts (ideal for comparing categories), 'histogram' for frequency "
                "distribution visualization (grouped data ranges), 'picture_graph' for "
                "star-based visual representations (engaging for younger students and "
                "visual learners)."
            ),
            "title": (
                "Descriptive title for the graph (e.g., 'Favorite Ice Cream Flavors', "
                "'Test Score Distribution', 'Books Read This Month'). Should clearly "
                "indicate what data is being displayed for educational context."
            ),
            "x_axis_label": (
                "Label for the horizontal axis describing the categories "
                "(e.g., 'Flavors', 'Score Ranges', 'Students', 'Months')."
            ),
            "y_axis_label": (
                "Label for the vertical axis describing the measured values "
                "(e.g., 'Number of Students', 'Frequency', 'Count', 'Votes')."
            ),
            "data": (
                "Array of 1-6 data points representing the categories and their values. "
                "Each data point contains a category (string) and frequency (number). "
                "Frequency can be whole numbers or half-values (e.g., 3.5 for picture graphs "
                "with half-stars). Keep category names concise for better visual readability."
            ),
            "picture_graph_config": (
                "Optional configuration for picture graphs. Required when graph_type is "
                "'picture_graph'. Defines star_value (what each star represents, min 1), star_unit "
                "(description like 'students' or 'books'), and show_half_star_value (boolean for "
                "half-star legend). Used to provide educational context and clarity for star-based "
                "visualizations."
            )
        },
    )
    return spec, generate_coach_bot_categorical_graph_image


def generate_coach_bot_multi_bar_graph_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for multi bar graph generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_multi_bar_graph_image",
        "description": (
            "Generate a 2x2 grid of bar graphs for comparative data analysis. Creates exactly "
            "four bar graphs arranged in a professional grid layout, ideal for comparing multiple "
            "datasets, time periods, groups, or different variables. Perfect for advanced "
            "elementary and middle school mathematics, statistics instruction, and scientific "
            "data comparison. Enables students to identify patterns, trends, and relationships "
            "across multiple data sets."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "graphs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title for this graph"
                            },
                            "x_axis_label": {
                                "type": "string",
                                "description": "Label for the x-axis"
                            },
                            "y_axis_label": {
                                "type": "string",
                                "description": "Label for the y-axis"
                            },
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "category": {
                                            "type": "string",
                                            "description": "The category name"
                                        },
                                        "frequency": {
                                            "type": "number",
                                            "description": "The frequency/count"
                                        }
                                    },
                                    "required": ["category", "frequency"]
                                },
                                "description": "Data points for this graph"
                            }
                        },
                        "required": ["title", "x_axis_label", "y_axis_label", "data"]
                    },
                    "description": "List of exactly 4 graph specifications",
                    "minItems": 4,
                    "maxItems": 4
                }
            },
            "required": ["graphs"]
        }
    }
    return spec, generate_coach_bot_multi_bar_graph_image


def generate_coach_bot_multi_picture_graph_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for multi picture graph generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_multi_picture_graph_image",
        "description": (
            "Generate a 2x2 grid of picture graphs for visual data comparison. Creates exactly "
            "four picture graphs using engaging star symbols, arranged in a professional grid "
            "layout. Ideal for elementary mathematics, visual learning, and making data accessible "
            "to younger students. Features consistent star scaling across all graphs for accurate "
            "comparison. Perfect for teaching data analysis concepts through visual, symbolic "
            "representation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "graphs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title for this graph"
                            },
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "category": {
                                            "type": "string",
                                            "description": "The category name"
                                        },
                                        "frequency": {
                                            "type": "number",
                                            "description": "The frequency/count"
                                        }
                                    },
                                    "required": ["category", "frequency"]
                                },
                                "description": "Data points for this graph"
                            },
                            "picture_config": {
                                "type": "object",
                                "properties": {
                                    "star_value": {
                                        "type": "integer",
                                        "description": "Value each star represents"
                                    },
                                    "star_unit": {
                                        "type": "string",
                                        "description": "Unit name for the stars"
                                    },
                                    "show_half_star_value": {
                                        "type": "boolean",
                                        "description": "Whether to show half-star legend"
                                    }
                                },
                                "required": ["star_value", "star_unit"]
                            }
                        },
                        "required": ["title", "data", "picture_config"]
                    },
                    "description": "List of exactly 4 graph specifications",
                    "minItems": 4,
                    "maxItems": 4
                }
            },
            "required": ["graphs"]
        }
    }
    return spec, generate_coach_bot_multi_picture_graph_image
