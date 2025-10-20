from __future__ import annotations

import logging
from typing import Callable, List, Union

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.area_models import (  # noqa: E402
    create_area_model,
    unit_square_decomposition,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.area_model import (  # noqa: E402
    AreaModel,
    Dimensions,
    Headers,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.unit_squares import (  # noqa: E402, E501
    UnitSquareDecomposition,
)

logger = logging.getLogger("coach_bot_tools.area_models")


def generate_coach_bot_area_model_image(
    columns: int,
    rows: int,
    column_headers: List[Union[str, int, float]],
    row_headers: List[Union[str, int, float]],
    data: List[List[Union[str, int, float]]]
) -> str:
    """
    Generate an area model table for multiplication/division.
    
    Creates a table-style area model with headers and data cells, commonly used 
    for teaching multiplication algorithms or division methods.
    
    Parameters
    ----------
    columns : int
        Number of columns in the area model
    rows : int
        Number of rows in the area model
    column_headers : List[Union[str, int, float]]
        Headers for each column (can be numbers, letters, fractions, decimals)
    row_headers : List[Union[str, int, float]]
        Headers for each row (can be numbers, letters, fractions, decimals)
    data : List[List[Union[str, int, float]]]
        2D array of cell contents, left to right, top to bottom.
        Can be letters (A, AC, BD), numbers (12, 6), fractions (6/5, 9/4),
        decimals (1.5, 2.75), or question marks (?) for unknowns.
        
    Returns
    -------
    str
        The URL of the generated area model image
    """
    
    # Use standardized logging
    log_tool_generation("area_model_image", columns=columns, rows=rows, 
                       column_headers_count=len(column_headers), row_headers_count=len(row_headers),
                       data_cells=len(data) * len(data[0]) if data else 0)
    
    # Create and validate the AreaModel stimulus using Pydantic
    area_model_data = AreaModel(
        dimensions=Dimensions(columns=columns, rows=rows),
        headers=Headers(columns=column_headers, rows=row_headers),
        data=data
    )
    
    # Generate the image using the area model function
    image_file_path = create_area_model(area_model_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_unit_square_decomposition_image(
    size: int,
    filled_count: int
) -> str:
    """
    Generate a unit square decomposition grid with filled squares.
    
    Creates a square grid divided into unit squares with some squares filled in
    to form a perfect rectangle. The rectangle dimensions are randomly chosen
    from all possible factorizations that fit. Always leaves 2 rows at the
    bottom and 2 columns at the right empty.
    
    Parameters
    ----------
    size : int
        Size of the square grid (e.g., 6 creates a 6x6 grid). Must be 1-10.
    filled_count : int
        Number of squares to fill in the grid. Cannot exceed the fillable
        area (size-2)^2 since 2 rows/columns are left empty.
        
    Returns
    -------
    str
        The URL of the generated unit square decomposition image
    """
    
    # Use standardized logging
    log_tool_generation("unit_square_decomposition_image", size=size, filled_count=filled_count)
    
    # Create and validate the UnitSquareDecomposition stimulus using Pydantic
    unit_square_data = UnitSquareDecomposition(
        size=size,
        filled_count=filled_count
    )
    
    # Generate the image using the area model function
    image_file_path = unit_square_decomposition(unit_square_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_area_model_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for area model generation."""
    # Note: This uses a static spec because the wrapper interface is flattened 
    # while the Pydantic model uses nested structures (Dimensions, Headers)
    spec = {
        "type": "function",
        "name": "generate_coach_bot_area_model_image",
        "description": (
            "Generate an area model table for multiplication/division. Creates a table-style "
            "area model with headers and data cells, commonly used for teaching "
            "multiplication algorithms or division methods. The area model helps visualize "
            "the decomposition of products or dividends into their constituent parts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "columns": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Number of columns in the area model (1-10 for optimal clarity)"
                },
                "rows": {
                    "type": "integer", 
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Number of rows in the area model (1-10 for optimal clarity)"
                },
                "column_headers": {
                    "type": "array",
                    "items": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "integer"},
                            {"type": "number"}
                        ]
                    },
                    "description": (
                        "Headers for each column representing decomposition pieces. "
                        "Can be single letters (A, B), numbers (4, 2), fractions (2/5, 3/4), "
                        "decimals (1.5, 2.75), or question marks (?) for unknown values. "
                        "Length must match the number of columns."
                    )
                },
                "row_headers": {
                    "type": "array",
                    "items": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "integer"},
                            {"type": "number"}
                        ]
                    },
                    "description": (
                        "Headers for each row representing decomposition pieces. "
                        "Can be single letters (A, B), numbers (4, 2), fractions (2/5, 3/4), "
                        "decimals (1.5, 2.75), or question marks (?) for unknown values. "
                        "Length must match the number of rows."
                    )
                },
                "data": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "anyOf": [
                                {"type": "string"},
                                {"type": "integer"},
                                {"type": "number"}
                            ]
                        }
                    },
                    "description": (
                        "2D array of cell contents representing partial products or quotients, "
                        "organized left to right, top to bottom. Can be single/double letters "
                        "(A, AC, BD), numbers (12, 6), fractions (6/5, 9/4), decimals (1.5, 2.75), "
                        "or question marks (?) for unknown values. Dimensions must match rows × "
                        "columns."
                    )
                }
            },
            "required": ["columns", "rows", "column_headers", "row_headers", "data"]
        }
    }
    return spec, generate_coach_bot_area_model_image


def generate_coach_bot_unit_square_decomposition_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for unit square decomposition generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_unit_square_decomposition_image",
        description=(
            "Generate a unit square decomposition grid with filled squares. Creates a "
            "square grid divided into unit squares with some squares filled in to form "
            "a perfect rectangle. The rectangle dimensions are randomly chosen from all "
            "possible factorizations that fit. Always leaves 2 rows at the bottom and 2 "
            "columns at the right empty."
        ),
        pydantic_model=UnitSquareDecomposition,
        custom_descriptions={
            "size": (
                "Size of the square grid (e.g., 6 creates a 6x6 grid). "
                "Must be between 1 and 10 for optimal visual clarity."
            ),
            "filled_count": (
                "Number of squares to fill in the grid. Cannot exceed the fillable "
                "area (size-2)² since 2 rows/columns are left empty for labeling. "
                "The filled squares will form a perfect rectangle."
            )
        }
    )
    return spec, generate_coach_bot_unit_square_decomposition_image
