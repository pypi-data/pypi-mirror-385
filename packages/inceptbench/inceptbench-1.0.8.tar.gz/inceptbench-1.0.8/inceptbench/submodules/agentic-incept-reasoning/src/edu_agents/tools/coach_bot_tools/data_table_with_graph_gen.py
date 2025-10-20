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

from content_generators.additional_content.stimulus_image.drawing_functions.data_table_with_graph import (  # noqa: E402, E501, I001
    draw_table_and_graph,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.table_with_graph import (  # noqa: E402, E501, I001
    DrawTableAndGraph,
    MultiBarChart,
    LineGraphs,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.table import (  # noqa: E402, I001
    DataTable,
)

logger = logging.getLogger("coach_bot_tools.data_table_with_graph")


def generate_coach_bot_data_table_with_graph_image(
    table_data: Dict[str, Union[str, List[str], List[List[str]]]],
    graph_type: str,
    graph_config: Dict[str, Union[str, List, Dict]]
) -> str:
    """
    Generate a combined data table and graph visualization.
    
    Creates a side-by-side display of a data table and either a bar chart or
    line graph.
    The table shows structured data while the graph provides a visual representation.
    
    Parameters
    ----------
    table_data : Dict[str, Union[str, List[str], List[List[str]]]]
        Table specification containing:
        - headers: List of column header strings
        - data: List of rows, each row is a list of cell values
        - title: Optional title for the table
        - metadata: Optional footer/metadata text
    graph_type : str
        Type of graph to generate ('bar_graph' or 'line_graph')
    graph_config : Dict[str, Union[str, List, Dict]]
        Graph configuration containing:
        For bar_graph:
        - title: Title for the graph
        - x_label: X-axis label
        - y_label: Y-axis label
        - data: List of data dictionaries with group, condition, value,
          error fields
        For line_graph:
        - title: Title for the graph
        - x_axis: Dict with label and optional range
        - y_axis: Dict with label and optional range
        - data_series: List of series dictionaries with x_values, y_values,
          label, marker
        
    Returns
    -------
    str
        The URL of the generated combined table and graph image
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_data_table_with_graph_image",
        table_data=table_data,
        graph_type=graph_type,
        graph_config=graph_config
    )
    
    # Create the DataTable using Pydantic validation
    data_table = DataTable(
        headers=table_data["headers"],
        data=table_data["data"],
        title=table_data.get("title"),
        metadata=table_data.get("metadata")
    )
    
    # Create the appropriate graph object
    if graph_type == "bar_graph":
        graph = MultiBarChart(
            graph_type="bar_graph",
            title=graph_config["title"],
            x_label=graph_config["x_label"],
            y_label=graph_config["y_label"],
            data=graph_config["data"]
        )
    elif graph_type == "line_graph":
        graph = LineGraphs(
            graph_type="line_graph",
            title=graph_config["title"],
            x_axis=graph_config["x_axis"],
            y_axis=graph_config["y_axis"],
            data_series=graph_config["data_series"]
        )
    else:
        raise ValueError(
            f"Unsupported graph type: {graph_type}. Must be 'bar_graph' or 'line_graph'"
        )
    
    # Create the DrawTableAndGraph stimulus using Pydantic validation
    table_and_graph = DrawTableAndGraph(
        data_table=data_table,
        graph=graph
    )
    
    # Generate the image using the table and graph function
    image_file_path = draw_table_and_graph(table_and_graph)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_data_table_with_graph_image_tool() -> tuple[
    dict, Callable
]:
    """Generate the tool specification and callable for data table with
    graph generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_data_table_with_graph_image",
        "description": (
            "Generate combined data table and graph visualizations for comprehensive data "
            "analysis and educational comparison exercises. Creates professional side-by-side "
            "displays combining structured data tables with visual graphs (bar charts or line "
            "graphs) to demonstrate relationships between numerical information and visual "
            "representations. Essential for teaching data literacy, statistical reasoning, "
            "graphical interpretation, and comparative analysis skills. Perfect for mathematics "
            "education, science data presentation, social studies statistics, and cross-curricular "
            "STEM applications where students need to analyze, interpret, and compare tabular "
            "versus visual data formats. Supports comprehensive data analysis instruction "
            "including reading tables, understanding axes, interpreting trends, making predictions, "  # noqa: E501
            "and developing critical thinking about data representation and communication."  # noqa: E501
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "table_data": {
                    "type": "object",
                    "description": (
                        "Structured data table specification for educational data presentation "
                        "and analysis. Supports comprehensive data organization with headers, "
                        "rows, and optional contextual information for effective data literacy "
                        "instruction and statistical reasoning development."
                    ),
                    "properties": {
                        "headers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Column header labels for data organization and interpretation. "
                                "Use clear, descriptive headers that help students understand "
                                "data categories and relationships. Essential for teaching table "
                                "reading skills and data categorization concepts."
                            ),
                            "minItems": 1,
                            "maxItems": 8
                        },
                        "data": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "description": (
                                "Tabular data rows for educational analysis and comparison with "
                                "visual graph representation. Each row contains cell values "
                                "corresponding to the column headers. Use realistic, educational "
                                "data that supports learning objectives and statistical reasoning."
                            ),
                            "minItems": 2,
                            "maxItems": 15
                        },
                        "title": {
                            "type": "string",
                            "description": (
                                "Optional descriptive title for the table providing educational "
                                "context and helping students understand the data's purpose and "
                                "significance (maximum 40 characters)."
                            )
                        },
                        "metadata": {
                            "type": "string",
                            "description": (
                                "Optional footer or additional metadata providing contextual "
                                "information such as data source, units, or collection details "
                                "for comprehensive data literacy education (maximum 40 characters)."
                            )
                        }
                    },
                    "required": ["headers", "data"]
                },
                "graph_type": {
                    "type": "string",
                    "enum": ["bar_graph", "line_graph"],
                    "description": (
                        "Type of visual graph to generate alongside the data table for "
                        "comprehensive data analysis education. Choose 'bar_graph' for "
                        "categorical comparisons, frequency distributions, and discrete "
                        "data visualization. Choose 'line_graph' for trend analysis, "
                        "continuous data relationships, and time-series visualization. "
                        "Essential for teaching appropriate graph selection based on data type."
                    )
                },
                "graph_config": {
                    "type": "object",
                    "description": (
                        "Graph configuration parameters that vary by graph_type. Contains "
                        "specific settings for either bar_graph or line_graph visualization "
                        "including titles, axis labels, and data specifications. Critical "
                        "for creating educationally appropriate and properly labeled graphs "
                        "for data literacy instruction and statistical reasoning development."
                    ),
                    "oneOf": [
                        {
                            "properties": {
                                "title": {
                                    "type": "string", 
                                    "description": (
                                        "Descriptive title for the bar graph providing clear "
                                        "educational context and helping students understand "
                                        "the purpose and significance of the data visualization."
                                    )
                                },
                                "x_label": {
                                    "type": "string", 
                                    "description": (
                                        "X-axis label describing the categorical variable or "
                                        "grouping factor being compared. Essential for teaching "
                                        "axis interpretation and graph reading skills."
                                    )
                                },
                                "y_label": {
                                    "type": "string", 
                                    "description": (
                                        "Y-axis label describing the quantitative variable or "
                                        "measurement being displayed. Include units when "
                                        "appropriate for comprehensive data literacy instruction."
                                    )
                                },
                                "data": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "group": {
                                                "type": "string", 
                                                "description": (
                                                    "Group or category name for data organization. "
                                                    "Use clear, educational labels that support "
                                                    "learning objectives and data comparison skills."  # noqa: E501
                                                )
                                            },
                                            "condition": {
                                                "type": "string", 
                                                "description": (
                                                    "Condition or subcategory name for detailed "
                                                    "data breakdown and comparative analysis. "
                                                    "Supports multi-variable data interpretation."
                                                )
                                            },
                                            "value": {
                                                "type": "number", 
                                                "description": (
                                                    "Numerical data value for bar height representation. "  # noqa: E501
                                                    "Use realistic values appropriate for educational "  # noqa: E501
                                                    "context and student comprehension level."
                                                )
                                            },
                                            "error": {
                                                "type": "number", 
                                                "description": (
                                                    "Optional error bar value for uncertainty visualization "  # noqa: E501
                                                    "and advanced statistical concept instruction. Useful "  # noqa: E501
                                                    "for science education and data analysis skills."  # noqa: E501
                                                )
                                            }
                                        },
                                        "required": ["group", "condition", "value"]
                                    },
                                    "description": (
                                        "Multi-bar chart data for categorical comparison and "  # noqa: E501
                                        "frequency analysis. Supports grouped data visualization "  # noqa: E501
                                        "for educational comparison exercises and statistical reasoning."  # noqa: E501
                                    )
                                }
                            },
                            "required": ["title", "x_label", "y_label", "data"]
                        },
                        {
                            "properties": {
                                "title": {
                                    "type": "string", 
                                    "description": (
                                        "Descriptive title for the line graph providing clear "
                                        "educational context and helping students understand "
                                        "trends, relationships, and data patterns over time or variables."  # noqa: E501
                                    )
                                },
                                "x_axis": {
                                    "type": "object",
                                    "description": (
                                        "X-axis configuration for horizontal scale and labeling. "  # noqa: E501
                                        "Essential for teaching coordinate systems and data interpretation."  # noqa: E501
                                    ),
                                    "properties": {
                                        "label": {
                                            "type": "string", 
                                            "description": (
                                                "X-axis label describing the independent variable or "  # noqa: E501
                                                "input factor being analyzed. Include units when "  # noqa: E501
                                                "appropriate for comprehensive data literacy instruction."  # noqa: E501
                                            )
                                        },
                                        "range": {
                                            "type": "array",
                                            "items": {"type": "number"},
                                            "minItems": 2,
                                            "maxItems": 2,
                                            "description": (
                                                "Optional [minimum, maximum] range for x-axis scaling "  # noqa: E501
                                                "to focus on specific data regions and enhance "  # noqa: E501
                                                "educational clarity and trend visibility."  # noqa: E501
                                            )
                                        }
                                    },
                                    "required": ["label"]
                                },
                                "y_axis": {
                                    "type": "object",
                                    "description": (
                                        "Y-axis configuration for vertical scale and labeling. "  # noqa: E501
                                        "Critical for teaching data measurement and trend analysis."
                                    ),
                                    "properties": {
                                        "label": {
                                            "type": "string", 
                                            "description": (
                                                "Y-axis label describing the dependent variable or "
                                                "output measurement being tracked. Include units when "  # noqa: E501
                                                "appropriate for comprehensive statistical education."  # noqa: E501
                                            )
                                        },
                                        "range": {
                                            "type": "array",
                                            "items": {"type": "number"},
                                            "minItems": 2,
                                            "maxItems": 2,
                                            "description": (
                                                "Optional [minimum, maximum] range for y-axis scaling "  # noqa: E501
                                                "to optimize data visualization and enhance pattern "  # noqa: E501
                                                "recognition for educational analysis."  # noqa: E501
                                            )
                                        }
                                    },
                                    "required": ["label"]
                                },
                                "data_series": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "x_values": {
                                                "type": "array",
                                                "items": {"type": "number"},
                                                "description": (
                                                    "X-coordinate values for data point positioning. "  # noqa: E501
                                                    "Use realistic, educational values that demonstrate "  # noqa: E501
                                                    "meaningful relationships and support learning objectives."  # noqa: E501
                                                )
                                            },
                                            "y_values": {
                                                "type": "array",
                                                "items": {"type": "number"},
                                                "description": (
                                                    "Y-coordinate values for data point positioning. "  # noqa: E501
                                                    "Should correspond to x_values to create meaningful "  # noqa: E501
                                                    "trends for statistical analysis and pattern recognition."  # noqa: E501
                                                )
                                            },
                                            "label": {
                                                "type": "string", 
                                                "description": (
                                                    "Optional descriptive label for this data series to "  # noqa: E501
                                                    "support multi-series comparison and legend interpretation "  # noqa: E501
                                                    "skills in advanced data analysis instruction."
                                                )
                                            },
                                            "marker": {
                                                "type": "string", 
                                                "description": (
                                                    "Optional marker style for data points (e.g., 'o' for "  # noqa: E501
                                                    "circles, 's' for squares, '^' for triangles) to enhance "  # noqa: E501
                                                    "visual distinction in multi-series comparisons."  # noqa: E501
                                                )
                                            }
                                        },
                                        "required": ["x_values", "y_values"]
                                    },
                                    "description": (
                                        "Data series collection for line graph visualization supporting "  # noqa: E501
                                        "trend analysis, time-series exploration, and continuous "  # noqa: E501
                                        "variable relationship investigation for comprehensive data education."  # noqa: E501
                                    )
                                }
                            },
                            "required": ["title", "x_axis", "y_axis", "data_series"]
                        }
                    ]
                }
            },
            "required": ["table_data", "graph_type", "graph_config"]
        }
    }
    return spec, generate_coach_bot_data_table_with_graph_image
