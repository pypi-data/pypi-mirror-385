from __future__ import annotations

import logging
from typing import Callable  # noqa: I001

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()  # noqa: E402, I001

from content_generators.additional_content.stimulus_image.drawing_functions.table_and_multi_scatterplots import (  # noqa: E402, I001, E501
    create_table_and_multi_scatterplots,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.table_and_multi_scatterplots import (  # noqa: E402, I001, E501
    TableAndMultiScatterplots,
)

logger = logging.getLogger("coach_bot_tools.table_scatterplots")


def generate_coach_bot_table_and_scatterplots_image(**kwargs) -> str:
    """
    Generate combined table and multiple scatterplots for data analysis assessment.
    
    Creates comprehensive educational visualizations combining data tables with 
    multiple scatterplot options. Perfect for teaching scatter plot interpretation, 
    data analysis skills, and creating multiple-choice assessment questions where 
    students identify which scatterplot correctly represents tabular data.
    
    🚨 CRITICAL REQUIREMENTS:
    - Each scatterplot MUST include ALL 7 required fields: title, x_label, y_label, 
      x_min, x_max, y_min, y_max, data_points
    - data_points MUST be dictionaries: [{'x': value, 'y': value}] NOT lists
    - Table rows should be strings for consistent formatting
    
    Educational applications include comparing different scatterplot representations
    of the same dataset, identifying correct vs incorrect data interpretations, 
    teaching statistical literacy, and developing critical analysis skills for
    data visualization assessment and mathematical reasoning.
    
    Returns
    -------
    str
        The URL of the generated table and scatterplots image
    """
    
    log_tool_generation("generate_coach_bot_table_and_scatterplots_image", **kwargs)
    
    # Create and validate using Pydantic model (handles all validation automatically)
    table_scatter_stimulus = TableAndMultiScatterplots(**kwargs)
    
    # Generate the image using the table and scatterplots function
    image_file_path = create_table_and_multi_scatterplots(table_scatter_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_table_and_scatterplots_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for table and scatterplots generation."""
    
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_table_and_scatterplots_image",
        description=(
            "Generate combined table and multiple scatterplots for comprehensive data analysis "
            "assessment. Creates educational visualizations combining data tables with multiple "
            "scatterplot options, perfect for teaching scatter plot interpretation, data analysis "
            "skills, statistical literacy, and creating multiple-choice assessment questions where "
            "students identify which scatterplot correctly represents tabular data. Supports "
            "assessment scenarios with correct and incorrect scatterplot options for critical "
            "thinking development and data visualization comprehension. 🚨 CRITICAL: Each "
            "scatterplot requires ALL 7 fields (title, x_label, y_label, x_min, x_max, y_min, "
            "y_max, data_points) with data_points as dictionaries [{'x': value, 'y': value}]."
        ),
        pydantic_model=TableAndMultiScatterplots,
        custom_descriptions={
            "table": (
                "Data table specification for display alongside scatterplots. Essential for "
                "creating table-to-graph interpretation exercises and data literacy assessment. "
                "Contains headers (2-5 columns) and rows (1-20 rows) with consistent column "
                "structure for clear educational presentation and systematic data analysis "
                "instruction."
            ),
            "scatterplots": (
                "🚨 CRITICAL SCATTERPLOT REQUIREMENTS: List of scatterplot options (1-4 plots) "
                "for comparative analysis and assessment. EACH scatterplot MUST include ALL "
                "7 REQUIRED FIELDS: 'title', 'x_label', 'y_label', 'x_min', 'x_max', 'y_min', "
                "'y_max', 'data_points'. ✅ CORRECT data_points format: [{'x': 70, 'y': 25}, "
                "{'x': 75, 'y': 30}] with 'x' and 'y' dictionary keys. ❌ WRONG: [[70, 25], "
                "[75, 30]] as lists. Perfect for multiple-choice questions, data interpretation "
                "challenges, and statistical reasoning development where students analyze "
                "different representations of the same dataset for accuracy and mathematical "
                "understanding."
            ),
            "layout": (
                "Layout arrangement for optimal educational presentation: 'vertical' places table "
                "above scatterplots for sequential analysis, 'horizontal' places table beside "
                "plots for side-by-side comparison. Choose based on instructional focus: vertical "
                "for step-by-step data interpretation, horizontal for simultaneous table-graph "
                "analysis and comparative reasoning exercises."
            )
        }
    )
    
    return spec, generate_coach_bot_table_and_scatterplots_image
