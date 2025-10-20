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

from content_generators.additional_content.stimulus_image.drawing_functions.base_ten_blocks import (  # noqa: E402
    draw_base_ten_blocks,
    draw_base_ten_blocks_grid,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.base_ten_block import (  # noqa: E402, E501
    BaseTenBlock,
    BaseTenBlockGridStimulus,
    BaseTenBlockStimulus,
)

logger = logging.getLogger("coach_bot_tools.base_ten_blocks")


def generate_coach_bot_base_ten_blocks_image(
    blocks: List[Dict[str, Union[int, bool]]],
    operation: Optional[str] = None
) -> str:
    """
    Generate a base ten blocks image for representing numbers in 3D.
    
    Creates a visual representation using hundreds (flat squares), tens (rods), 
    and ones (unit cubes) arranged in 3D space.
    
    Parameters
    ----------
    blocks : List[Dict[str, Union[int, bool]]]
        List of block specifications, each containing:
        - value: The numerical value to represent (0-999)
        - display_as_decimal: Whether to show as decimal (optional, default False)
    operation : Optional[str]
        The operation being performed (e.g., "addition", "subtraction")
        
    Returns
    -------
    str
        The URL of the generated base ten blocks image
    """
    
    # Use standardized logging
    log_tool_generation("base_ten_blocks_image", block_count=len(blocks),
                        operation=operation or "addition")
    
    # Create BaseTenBlock objects from the input data
    block_objects = []
    for block_data in blocks:
        block_obj = BaseTenBlock(
            value=block_data["value"],
            display_as_decimal=block_data.get("display_as_decimal", False)
        )
        block_objects.append(block_obj)
    
    # Create the BaseTenBlockStimulus
    stimulus_data = BaseTenBlockStimulus(
        blocks=block_objects,
        operation=operation or "addition"
    )
    
    # Generate the image using the base ten blocks function
    image_file_path = draw_base_ten_blocks(stimulus_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_base_ten_blocks_grid_image(
    block_value: int,
    count: int,
    display_as_decimal: bool = False
) -> str:
    """
    Generate a grid of identical base ten blocks.
    
    Creates a 2-column grid layout of identical base ten block representations,
    useful for division and grouping problems.
    
    Parameters
    ----------
    block_value : int
        The value each block represents (0-999)
    count : int
        Number of blocks to display (maximum 6)
    display_as_decimal : bool
        Whether to display the value as a decimal
        
    Returns
    -------
    str
        The URL of the generated base ten blocks grid image
    """
    
    # Use standardized logging
    log_tool_generation("base_ten_blocks_grid_image", block_value=block_value, count=count,
                        display_as_decimal=display_as_decimal)
    
    # Create and validate the BaseTenBlockGridStimulus using Pydantic
    stimulus_data = BaseTenBlockGridStimulus(
        block_value=block_value,
        count=count,
        display_as_decimal=display_as_decimal
    )
    
    # Generate the image using the grid function
    image_file_path = draw_base_ten_blocks_grid(stimulus_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_base_ten_blocks_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for base ten blocks generation."""
    # Note: This uses an enhanced static spec because the wrapper interface is flattened
    # (takes List[Dict]) while the Pydantic model uses nested BaseTenBlock objects
    spec = {
        "type": "function",
        "name": "generate_coach_bot_base_ten_blocks_image",
        "description": (
            "Generate a 3D base ten blocks image for representing numbers. Creates a visual "
            "representation using hundreds (cyan flat squares), tens (green rods), and ones "
            "(orange unit cubes) arranged in 3D space. Useful for teaching place value, "
            "addition, subtraction, and number decomposition. Supports 1-2 block sets with "
            "optional operation symbols between them."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "blocks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "integer",
                                "description": "The numerical value to represent with base ten "
                                               "blocks (1-1000)",
                                "minimum": 1,
                                "maximum": 1000
                            },
                            "display_as_decimal": {
                                "type": "boolean",
                                "description": (
                                    "Whether to display as decimal format where hundreds=1.0, "
                                    "tens=0.1, ones=0.01. All blocks in the stimulus must use the "
                                    "same display mode."
                                ),
                                "default": False
                            }
                        },
                        "required": ["value"]
                    },
                    "description": (
                        "List of block specifications representing different number values. "
                        "Maximum of 2 blocks for optimal visual clarity. Each block is decomposed "
                        "into hundreds (cyan), tens (green), and ones (orange) components."
                    ),
                    "minItems": 1,
                    "maxItems": 2
                },
                "operation": {
                    "type": "string",
                    "description": (
                        "The mathematical operation being performed between the blocks. "
                        "When specified, values are shown as labels separated by the operation "
                        "symbol. If omitted, blocks are displayed as a vertical stack without "
                        "labels."
                    ),
                    "enum": ["addition", "subtraction", "divide", "multiply"]
                }
            },
            "required": ["blocks"]
        }
    }
    return spec, generate_coach_bot_base_ten_blocks_image


def generate_coach_bot_base_ten_blocks_grid_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for base ten blocks grid generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_base_ten_blocks_grid_image",
        description=(
            "Generate a grid of identical base ten blocks arranged in 2 columns. Creates "
            "multiple identical base ten block representations useful for division and "
            "grouping problems. Maximum of 6 blocks (3 rows x 2 columns). The hundreds "
            "are shown in cyan, tens in green, and ones in orange."
        ),
        pydantic_model=BaseTenBlockGridStimulus,
        custom_descriptions={
            "block_value": (
                "The numerical value represented by each base 10 block in the grid. "
                "Must be between 1-1000 for optimal visual clarity. Decomposed into "
                "hundreds (cyan flats), tens (green rods), and ones (orange cubes)."
            ),
            "count": (
                "The number of identical base 10 blocks to display in the 2-column grid. "
                "Maximum of 6 blocks (3 rows × 2 columns) for optimal layout."
            ),
            "display_as_decimal": (
                "Whether to display the value as a decimal where hundreds=1.0, tens=0.1, "
                "ones=0.01. Useful for teaching decimal place value concepts."
            )
        }
    )
    return spec, generate_coach_bot_base_ten_blocks_grid_image
