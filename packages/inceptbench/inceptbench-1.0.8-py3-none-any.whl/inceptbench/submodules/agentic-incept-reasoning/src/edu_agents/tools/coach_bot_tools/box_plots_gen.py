from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.box_plots import (  # noqa: E402
    draw_box_plots,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.box_plots import (  # noqa: E402
    BoxPlotData,
    BoxPlotDescription,
)

logger = logging.getLogger("coach_bot_tools.box_plots")


def generate_coach_bot_box_plots_image(
    data: List[Dict[str, Any]],
    title: Optional[str] = None
) -> str:
    """
    Generate a box plot diagram for statistical data visualization.
    
    Creates box plots showing the five-number summary (minimum, Q1, median, Q3, maximum)
    for one or more datasets. Useful for comparing distributions and identifying outliers.
    
    Parameters
    ----------
    data : List[Dict[str, any]]
        List of dataset specifications, each containing:
        - class_name: Name of the dataset (optional)
        - min_value: Minimum value in the dataset
        - q1: First quartile (25th percentile)
        - median: Median value (50th percentile) 
        - q3: Third quartile (75th percentile)
        - max_value: Maximum value in the dataset
    title : Optional[str]
        Title for the box plot diagram
        
    Returns
    -------
    str
        The URL of the generated box plot image
    """
    
    # Use standardized logging
    log_tool_generation("box_plots_image", dataset_count=len(data), title=title or "untitled")
    
    # Enforce box plot validation rules before creating Pydantic objects
    is_single_plot = len(data) == 1
    
    if is_single_plot:
        # Single box plots: class_name must be None, title is optional
        if "class_name" in data[0]:
            # Remove class_name if provided (not allowed for single plots)
            data[0] = {k: v for k, v in data[0].items() if k != "class_name"}
    else:
        # Multiple box plots: title and class_name are required
        if title is None:
            raise ValueError("Title is required when comparing multiple box plots")
        for i, dataset in enumerate(data):
            if "class_name" not in dataset or dataset["class_name"] is None:
                raise ValueError(
                    f"class_name is required for dataset {i+1} when creating multiple box plots"
                )
    
    # Create and validate BoxPlotData objects from the cleaned input data
    box_plot_data_objects = []
    for dataset in data:
        box_plot_obj = BoxPlotData(
            class_name=dataset.get("class_name"),  # None for single plots, required for multiple
            min_value=dataset["min_value"],
            q1=dataset["q1"],
            median=dataset["median"],
            q3=dataset["q3"],
            max_value=dataset["max_value"]
        )
        box_plot_data_objects.append(box_plot_obj)
    
    # Create and validate the BoxPlotDescription using Pydantic
    # This validates complex rules: ascending order, title/class_name requirements
    box_plot_description = BoxPlotDescription(
        title=title,
        data=box_plot_data_objects
    )
    
    # Generate the image using the box plot function
    image_file_path = draw_box_plots(box_plot_description)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_box_plots_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for box plots generation."""
    # Note: This uses an enhanced static spec because the wrapper interface is flattened
    # (takes List[Dict]) while the Pydantic model uses nested BoxPlotData objects
    spec = {
        "type": "function",
        "name": "generate_coach_bot_box_plots_image",
        "description": (
            "Generate a box plot diagram for statistical data visualization. Creates box plots "
            "showing the five-number summary (minimum, Q1, median, Q3, maximum) for one or more "
            "datasets. Useful for comparing distributions, identifying outliers, and teaching "
            "statistical concepts like quartiles, range, and data spread."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "class_name": {
                                "type": "string",
                                "description": (
                                    "Name/label for this dataset. REQUIRED for multiple box plots "
                                    "to distinguish between datasets. Should be omitted for single "
                                    "box plots."
                                )
                            },
                            "min_value": {
                                "type": "number",
                                "description": (
                                    "Minimum value in the dataset (leftmost whisker). "
                                    "Must be less than all other values in ascending order."
                                )
                            },
                            "q1": {
                                "type": "number",
                                "description": (
                                    "First quartile (25th percentile) - left edge of the box. "
                                    "Must be greater than min_value and less than median."
                                )
                            },
                            "median": {
                                "type": "number",
                                "description": (
                                    "Median value (50th percentile) - line inside the box. "
                                    "Must be between Q1 and Q3."
                                )
                            },
                            "q3": {
                                "type": "number",
                                "description": (
                                    "Third quartile (75th percentile) - right edge of the box. "
                                    "Must be greater than median and less than max_value."
                                )
                            },
                            "max_value": {
                                "type": "number",
                                "description": (
                                    "Maximum value in the dataset (rightmost whisker). "
                                    "Must be greater than all other values in the five-number "
                                    "summary."
                                )
                            }
                        },
                        "required": ["min_value", "q1", "median", "q3", "max_value"]
                    },
                    "description": (
                        "List of datasets to create box plots for. Each dataset must have values "
                        "in strict ascending order: min_value < q1 < median < q3 < max_value. "
                        "Maximum of 2 datasets can be compared side-by-side."
                    ),
                    "minItems": 1,
                    "maxItems": 2
                },
                "title": {
                    "type": "string",
                    "description": (
                        "Title for the box plot diagram. REQUIRED when comparing multiple "
                        "datasets. Optional for single box plots (will default to 'Data "
                        "Distribution')."
                    )
                }
            },
            "required": ["data"]
        }
    }
    return spec, generate_coach_bot_box_plots_image
