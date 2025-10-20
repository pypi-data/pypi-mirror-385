from __future__ import annotations

import logging
from decimal import Decimal
from typing import Callable, Dict, List

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.decimal_grid import (  # noqa: E402
    draw_decimal_comparison,
    draw_decimal_grid,
    draw_decimal_multiplication,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.decimal_grid import (  # noqa: E402, E501
    ComparisonLevel,
    DecimalComparison,
    DecimalComparisonList,
    DecimalGrid,
    DecimalMultiplication,
)

logger = logging.getLogger("coach_bot_tools.decimal_grid")


def generate_coach_bot_decimal_grid_image(
    division: int,
    shaded_squares: int
) -> str:
    """
    Generate a decimal grid visualization for teaching decimal concepts.
    
    Creates grids divided into equal parts (10 or 100) with specified squares shaded.
    When shaded squares exceed the division value, multiple grids are created side by side.
    
    Parameters
    ----------
    division : int
        Number of equal parts (10 for 1x10 grids, 100 for 10x10 grids)
    shaded_squares : int
        Number of squares to shade (can exceed division to create multiple grids)
        
    Returns
    -------
    str
        The URL of the generated decimal grid image
    """
    
    log_tool_generation(
        "generate_coach_bot_decimal_grid_image",
        division=division,
        shaded_squares=shaded_squares
    )
    
    # Create and validate the DecimalGrid stimulus description
    decimal_grid = DecimalGrid(
        division=division,
        shaded_squares=shaded_squares
    )
    
    # Generate the image using the decimal grid function
    image_file_path = draw_decimal_grid(decimal_grid)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_decimal_comparison_image(
    comparisons: List[Dict[str, any]]
) -> str:
    """
    Generate decimal comparison visualization with side-by-side grids.
    
    Creates visual models for comparing decimals with proper question format
    matching educational standards for decimal comparison.
    
    Parameters
    ----------
    comparisons : List[Dict[str, any]]
        List of comparison specifications, each containing:
        - decimal_1: First decimal value to compare
        - decimal_2: Second decimal value to compare 
        - complexity_level: "basic", "intermediate", or "advanced"
        - color_1: Optional color for first grid (default: "lightblue")
        - color_2: Optional color for second grid (default: "lightblue")
        
    Returns
    -------
    str
        The URL of the generated decimal comparison image
    """
    
    log_tool_generation(
        "generate_coach_bot_decimal_comparison_image",
        comparisons=comparisons
    )
    
    # Create DecimalComparison objects from the input data with precision fix
    comparison_objects = []
    for comp in comparisons:
        # Apply precision fix using Decimal class to avoid floating-point rounding errors
        # that cause 2.4 to display as 2.3 in grid visualization
        decimal_1 = float(Decimal(str(comp["decimal_1"])).quantize(Decimal('0.1')))
        decimal_2 = float(Decimal(str(comp["decimal_2"])).quantize(Decimal('0.1')))
        
        comparison_obj = DecimalComparison(
            decimal_1=decimal_1,
            decimal_2=decimal_2,
            complexity_level=ComparisonLevel(comp["complexity_level"]),
            color_1=comp.get("color_1", "lightblue"),
            color_2=comp.get("color_2", "lightblue")
        )
        comparison_objects.append(comparison_obj)
    
    # Create and validate the DecimalComparisonList
    comparison_list = DecimalComparisonList(
        comparisons=comparison_objects
    )
    
    # Generate the image using the decimal comparison function
    image_file_path = draw_decimal_comparison(comparison_list)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_decimal_multiplication_image(
    decimal_factors: List[float]
) -> str:
    """
    Generate decimal multiplication visualization using grid patterns.
    
    Uses 10×10 grids to show multiplication visually for products of the form 
    0.a × 0.b or 0.a × 1.b with shading and pattern overlays.
    
    Parameters
    ----------
    decimal_factors : List[float]
        Two decimal factors: first of form 0.a, second of form 0.b or 1.b 
        where a,b are single digits
        
    Returns
    -------
    str
        The URL of the generated decimal multiplication image
    """
    
    log_tool_generation(
        "generate_coach_bot_decimal_multiplication_image",
        decimal_factors=decimal_factors
    )
    
    # Create and validate the DecimalMultiplication stimulus description with precision fix
    # Apply precision fix using Decimal class to avoid floating-point rounding errors
    rounded_factors = [float(Decimal(str(factor)).quantize(Decimal('0.1'))) \
                        for factor in decimal_factors]
    
    decimal_mult = DecimalMultiplication(
        decimal_factors=rounded_factors
    )
    
    # Generate the image using the decimal multiplication function
    image_file_path = draw_decimal_multiplication(decimal_mult)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_decimal_grid_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for decimal grid generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_decimal_grid_image",
        description=(
            "Generate a decimal grid visualization for teaching decimal concepts and "
            "fraction-to-decimal conversion. Creates grids divided into equal parts (10 for "
            "tenths, 100 for hundredths) with specified squares shaded. When shaded squares exceed "
            "the division value, multiple grids are created side by side (maximum 5 grids). "
            "Perfect for elementary mathematics instruction, visual decimal representation, and "
            "building number sense."
        ),
        pydantic_model=DecimalGrid
    )
    return spec, generate_coach_bot_decimal_grid_image


def generate_coach_bot_decimal_comparison_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for decimal comparison generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_decimal_comparison_image",
        "description": (
            "Generate decimal comparison visualization with side-by-side grids for teaching "
            "decimal magnitude and comparison concepts. Creates visual models using 10x10 grids to "
            "represent decimal values with different complexity levels: BASIC (values < 1.0), "
            "INTERMEDIATE (matching whole number parts), ADVANCED (different whole number parts). "
            "Uses precise decimal arithmetic to ensure accurate grid shading (e.g., 2.4 shows "
            "exactly 4 shaded squares). Perfect for elementary mathematics instruction, decimal "
            "ordering, and magnitude comparison exercises."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "comparisons": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "decimal_1": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 9.99,
                                "description": (
                                    "First decimal value to compare (0-9.99). Should be "
                                    "appropriate for the selected complexity level. Automatically "
                                    "rounded to 2 decimal places for grid visualization accuracy."
                                )
                            },
                            "decimal_2": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 9.99,
                                "description": (
                                    "Second decimal value to compare (0-9.99). Should be "
                                    "appropriate for the selected complexity level. Automatically "
                                    "rounded to 2 decimal places for grid visualization accuracy."
                                )
                            },
                            "complexity_level": {
                                "type": "string",
                                "enum": ["basic", "intermediate", "advanced"],
                                "description": (
                                    "Educational complexity level: 'basic' for values < 1.0 only "
                                    "(pure decimal comparison), 'intermediate' for values with "
                                    "matching whole number parts (e.g., 2.3 vs 2.7), 'advanced' "
                                    "for values with different whole number parts (e.g., 1.8 vs "
                                    "3.2). Enforces appropriate educational progression."
                                )
                            },
                            "color_1": {
                                "type": "string",
                                "description": (
                                    "Color for the first decimal grid (e.g., 'lightblue', 'red', "
                                    "'#FF5733'). Use different colors for clear visual "
                                    "distinction. Defaults to 'lightblue'."
                                )
                            },
                            "color_2": {
                                "type": "string",
                                "description": (
                                    "Color for the second decimal grid (e.g., 'orange', 'green', "
                                    "'#33A1FF'). Should contrast with color_1 for educational "
                                    "clarity. Defaults to 'lightblue'."
                                )
                            }
                        },
                        "required": ["decimal_1", "decimal_2", "complexity_level"]
                    },
                    "description": (
                        "Array of 1+ decimal comparison pairs for side-by-side visualization. Each "
                        "pair creates a separate comparison exercise with two grids showing "
                        "relative decimal magnitudes. All pairs should use consistent complexity "
                        "levels for educational coherence."
                    ),
                    "minItems": 1
                }
            },
            "required": ["comparisons"]
        }
    }
    return spec, generate_coach_bot_decimal_comparison_image


def generate_coach_bot_decimal_multiplication_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for decimal multiplication generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_decimal_multiplication_image",
        description=(
            "Generate decimal multiplication visualization using grid patterns and area models. "
            "Uses 10×10 grids to show multiplication visually for products of the form 0.a × 0.b "
            "(single grid) or 0.a × 1.b (dual grid layout) with shading and pattern overlays. "
            "Perfect for teaching decimal multiplication concepts, area model understanding, "
            "and building conceptual foundation for decimal operations in elementary mathematics."
        ),
        pydantic_model=DecimalMultiplication
    )
    return spec, generate_coach_bot_decimal_multiplication_image
