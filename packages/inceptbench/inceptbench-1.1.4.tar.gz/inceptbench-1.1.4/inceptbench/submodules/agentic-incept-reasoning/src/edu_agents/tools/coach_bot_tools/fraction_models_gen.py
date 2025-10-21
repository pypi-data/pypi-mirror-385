from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.fraction_models import (  # noqa: E402, I001
    draw_fractional_models,
    draw_fractional_models_labeled,
    draw_fractional_models_no_shade,
    draw_fractional_models_full_shade,
    draw_fractional_models_unequal,
    draw_fractional_pair_models,
    draw_fractional_models_multiplication_units,
    draw_mixed_fractional_models,
    draw_whole_fractional_models,
    draw_fraction_strips,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.fraction import (  # noqa: E402, I001
    Fraction,
    FractionList,
    FractionPair,
    FractionPairList,
    FractionSet,
    FractionShape,
    DividedShape,
    DividedShapeList,
    UnequalFraction,
    UnequalFractionList,
    MixedFraction,
    MixedFractionList,
    WholeFractionalShapes,
    FractionStrips,
)

logger = logging.getLogger("coach_bot_tools.fraction_models")


def generate_coach_bot_fraction_models_image(
    fractions: List[Dict],
    labeled: bool = False
) -> str:
    """
    Generate fraction model visualizations with shapes divided and shaded.
    
    Args:
        fractions: List of fraction dictionaries with 'shape' and 'fraction' keys
        labeled: Whether to show fraction labels below each model
        
    Returns:
        str: URL to the uploaded fraction models image
    """
    logger.info(f"Generating fraction models for {len(fractions)} fractions")
    
    # Convert input to Pydantic models
    fraction_objects = []
    for frac in fractions:
        fraction_obj = Fraction(
            shape=FractionShape(frac["shape"]),
            fraction=frac["fraction"]
        )
        fraction_objects.append(fraction_obj)
    
    fraction_list = FractionList(root=fraction_objects)
    
    # Generate appropriate model based on labeling
    if labeled:
        image_file_path = draw_fractional_models_labeled(fraction_list)
    else:
        image_file_path = draw_fractional_models(fraction_list)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_fraction_pairs_image(
    fraction_pairs: List[Dict]
) -> str:
    """
    Generate fraction pair models with multiple fractions per shape.
    
    Args:
        fraction_pairs: List of dictionaries with 'shape' and 'fractions' keys
        
    Returns:
        str: URL to the uploaded fraction pairs image
    """
    logger.info(f"Generating fraction pairs for {len(fraction_pairs)} shapes")
    
    # Convert input to Pydantic models
    pair_objects = []
    for pair in fraction_pairs:
        pair_obj = FractionPair(
            shape=FractionShape(pair["shape"]),
            fractions=pair["fractions"]
        )
        pair_objects.append(pair_obj)
    
    pair_list = FractionPairList(root=pair_objects)
    image_file_path = draw_fractional_pair_models(pair_list)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_fraction_multiplication_units_image(
    fraction1: str,
    fraction2: str
) -> str:
    """
    Generate a rectangular grid visualization showing fraction multiplication product area.
    
    IMPORTANT: This tool shows only the final product area (yellow shading) in a grid,
    not the individual fraction representations or step-by-step visual process.
    The grid dimensions are determined by the denominators, and the yellow area
    represents the intersection/product of the two fractions.
    
    Args:
        fraction1: First fraction as string (e.g., "2/3") - denominator sets grid width
        fraction2: Second fraction as string (e.g., "3/4") - denominator sets grid height
        
    Returns:
        str: URL to the uploaded multiplication units grid image
    """
    logger.info(f"Generating fraction multiplication grid: {fraction1} × {fraction2}")
    
    fraction_set = FractionSet(fractions=[fraction1, fraction2])
    image_file_path = draw_fractional_models_multiplication_units(fraction_set)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_divided_shapes_image(
    shapes: List[Dict],
    shading_type: str = "no_shade"
) -> str:
    """
    Generate shapes divided into parts with various shading options.
    
    Args:
        shapes: List of shape dictionaries with 'shape' and 'denominator' keys
        shading_type: Type of shading ('no_shade', 'full_shade')
        
    Returns:
        str: URL to the uploaded divided shapes image
    """
    logger.info(f"Generating {shading_type} divided shapes for {len(shapes)} shapes")
    
    # Convert input to Pydantic models
    shape_objects = []
    for shape in shapes:
        shape_obj = DividedShape(
            shape=FractionShape(shape["shape"]),
            denominator=shape["denominator"]
        )
        shape_objects.append(shape_obj)
    
    shape_list = DividedShapeList(root=shape_objects)
    
    # Generate based on shading type
    if shading_type == "full_shade":
        image_file_path = draw_fractional_models_full_shade(shape_list)
    else:  # no_shade
        image_file_path = draw_fractional_models_no_shade(shape_list)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_unequal_fractions_image(
    shapes: List[Dict]
) -> str:
    """
    Generate shapes with equal or unequal divisions.
    
    Args:
        shapes: List with 'shape', 'divided_parts', 'equally_divided' keys
        
    Returns:
        str: URL to the uploaded unequal fractions image
    """
    logger.info(f"Generating unequal fractions for {len(shapes)} shapes")
    
    # Convert input to Pydantic models
    unequal_objects = []
    for shape in shapes:
        unequal_obj = UnequalFraction(
            shape=FractionShape(shape["shape"]),
            divided_parts=shape["divided_parts"],
            equally_divided=shape["equally_divided"]
        )
        unequal_objects.append(unequal_obj)
    
    unequal_list = UnequalFractionList(root=unequal_objects)
    image_file_path = draw_fractional_models_unequal(unequal_list)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_mixed_fractions_image(
    mixed_fractions: List[Dict]
) -> str:
    """
    Generate mixed number and improper fraction visualizations.
    
    Args:
        mixed_fractions: List with 'shape' and 'fraction' keys (fractions can be > 1)
        
    Returns:
        str: URL to the uploaded mixed fractions image
    """
    logger.info(f"Generating mixed fractions for {len(mixed_fractions)} fractions")
    
    # Convert input to Pydantic models
    mixed_objects = []
    for frac in mixed_fractions:
        mixed_obj = MixedFraction(
            shape=FractionShape(frac["shape"]),
            fraction=frac["fraction"]
        )
        mixed_objects.append(mixed_obj)
    
    mixed_list = MixedFractionList(root=mixed_objects)
    image_file_path = draw_mixed_fractional_models(mixed_list)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_whole_fractions_image(
    count: int,
    shape: str,
    divisions: int
) -> str:
    """
    Generate fully shaded shapes representing whole fractions.
    
    Args:
        count: Number of whole units (1-5 shapes)
        shape: Shape type ('circle' or 'rectangle')
        divisions: Number of equal parts each shape is divided into
        
    Returns:
        str: URL to the uploaded whole fractions image
    """
    logger.info(f"Generating {count} whole {shape}s with {divisions} divisions each")
    
    whole_fractions = WholeFractionalShapes(
        count=count,
        shape=FractionShape(shape),
        divisions=divisions
    )
    image_file_path = draw_whole_fractional_models(whole_fractions)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_fraction_strips_image(
    splits: int,
    first_division: int,
    second_division: Optional[int] = None
) -> str:
    """
    Generate stacked rectangles showing fraction decomposition.
    
    Creates 2-3 stacked rectangles demonstrating progressive fraction 
    subdivision from whole to unit fractions. Essential for teaching 
    fractional decomposition, unit fraction concepts, and visual 
    fraction representation.
    
    🚨 CRITICAL PARAMETER RULES:
    - When splits=2: Do NOT provide second_division (it will be ignored)
    - When splits=3: second_division is MANDATORY
    - splits must be exactly 2 or 3
    - first_division: 2-10 (always required)
    - second_division: 2-10 (only when splits=3)
    - Product constraint: first_division × second_division ≤ 21
    
    Parameters
    ----------
    splits : int
        Number of rectangle strips (2 or 3)
    first_division : int
        Parts to split the whole into for second rectangle (2-10)
    second_division : Optional[int]
        Parts to split unit fraction into for third rectangle (2-10).
        🚨 IMPORTANT: Only provide when splits=3. Ignored when splits=2.
        
    Returns
    -------
    str
        The URL of the uploaded fraction strips image
    """
    
    # Use centralized logging utility
    log_tool_generation(
        "generate_coach_bot_fraction_strips_image",
        splits=splits,
        first_division=first_division,
        second_division=second_division
    )
    
    # 🔧 CONDITIONAL PARAMETER HANDLING:
    # Remove second_division when splits=2 to prevent validation errors
    kwargs = {
        "splits": splits,
        "first_division": first_division
    }
    
    # Only include second_division when splits=3
    if splits == 3:
        if second_division is None:
            raise ValueError(
                "second_division is required when splits=3. Please provide a value between 2-10."
            )
        kwargs["second_division"] = second_division
    elif splits == 2 and second_division is not None:
        # Log warning but proceed (ignore the parameter)
        logger.warning(
            f"second_division={second_division} provided when splits=2. "
            "This parameter is ignored for 2-level fraction strips."
        )
        # Don't include second_division in kwargs - it will remain None
    
    # Create FractionStrips using Pydantic validation with conditional parameters
    fraction_strips = FractionStrips(**kwargs)
    
    # Generate the image using the fraction strips function
    image_file_path = draw_fraction_strips(fraction_strips)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_fraction_models_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for fraction models."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_fraction_models_image",
        "description": (
            "Generate comprehensive visual fraction models using circles or rectangles with "
            "proportional shading to demonstrate fraction concepts, part-whole relationships, "
            "and mathematical fraction representation. Essential for elementary mathematics "
            "education, fraction comprehension instruction, and visual fraction learning. "
            "Supports both unlabeled models for exploration and labeled models with fraction "
            "notation for assessment and reinforcement. Perfect for teaching fraction basics, "
            "equivalent fractions, fraction comparison, and mathematical reasoning development "
            "with clear, educationally-appropriate visual representations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "fractions": {
                    "type": "array",
                    "description": (
                        "List of fractions to visualize with visual fraction models. Each "
                        "fraction dictionary must contain 'shape' (circle or rectangle) and "
                        "'fraction' (numerator/denominator format) keys. Supports multiple "
                        "fractions for comparison exercises, fraction sequences, and educational "
                        "demonstrations. Maximum denominator of 25 ensures clear visual division. "
                        "Circles show segments starting at 12 o'clock going counterclockwise. "
                        "Rectangles show vertical divisions with shading from left to right."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "shape": {
                                "type": "string",
                                "enum": ["circle", "rectangle"],
                                "description": (
                                    "Shape type for the fraction visualization. Choose 'circle' "
                                    "for pie chart-style representation with wedge segments, or "
                                    "'rectangle' for bar model-style representation with vertical "
                                    "divisions. Both provide clear visual fraction demonstration "
                                    "appropriate for different learning styles and educational "
                                    "contexts."
                                )
                            },
                            "fraction": {
                                "type": "string",
                                "pattern": "^\\d+/\\d+$",
                                "description": (
                                    "Fraction in standard numerator/denominator format (e.g., "
                                    "'3/4', '2/8', '7/12'). The numerator represents shaded parts, "
                                    "denominator represents total equal parts. Maximum denominator "
                                    "of 25 ensures clear visual division and educational "
                                    "appropriateness. Supports proper fractions for fundamental "
                                    "fraction concept instruction."
                                )
                            }
                        },
                        "required": ["shape", "fraction"],
                        "additionalProperties": False
                    },
                    "minItems": 1,
                    "maxItems": 8
                },
                "labeled": {
                    "type": "boolean",
                    "description": (
                        "Whether to display mathematical fraction notation (e.g., ³⁄₄) below each "
                        "visual model for reinforcement and assessment. Choose true for exercises "
                        "requiring explicit fraction identification, false for exploration and "
                        "visual fraction discovery activities. Labels use proper mathematical "
                        "formatting with superscript numerators and subscript denominators."
                    ),
                    "default": False
                }
            },
            "required": ["fractions"],
            "additionalProperties": False
        }
    }
    return spec, generate_coach_bot_fraction_models_image


def generate_coach_bot_fraction_pairs_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for fraction pairs."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_fraction_pairs_image",
        description=(
            "Generate advanced fraction pair models showing multiple fractions within the same "
            "shape using distinct color coding for comprehensive fraction addition, subtraction, "
            "and comparison instruction. Creates visual representations where multiple fractions "
            "share the same denominator and are displayed with different colors (blue, green, "
            "etc.) to demonstrate fraction relationships, equivalent fractions, and "
            "part-part-whole concepts. Essential for intermediate fraction education, fraction "
            "operations instruction, and visual fraction relationship analysis with clear "
            "mathematical accuracy."
        ),
        pydantic_model=FractionPairList,
        parameter_wrapper_name="fraction_pairs",
        custom_descriptions={
            "fraction_pairs": (
                "List of fraction pair models for advanced fraction visualization and comparison. "
                "Each model contains a shape (circle or rectangle) and multiple fractions with "
                "the same denominator, automatically colored with distinct colors (first fraction "
                "blue, second fraction green, additional fractions with random colors). Perfect "
                "for teaching fraction addition (3/8 + 2/8 = 5/8), fraction comparison, and "
                "part-part-whole relationships in a single visual model. All fractions must "
                "share the same denominator and their sum cannot exceed the denominator value."
            )
        }
    )
    return spec, generate_coach_bot_fraction_pairs_image


def generate_coach_bot_fraction_multiplication_units_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for fraction multiplication units."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_fraction_multiplication_units_image",
        "description": (
            "Generate rectangular grid visualization for fraction multiplication showing the "
            "product area using area model approach for mathematical reasoning. Creates a "
            "grid divided by the denominators of two fractions with the intersection area "
            "(representing the product) shaded in yellow. The grid shows the total possible "
            "area units and highlights the specific area that represents the multiplication "
            "result. IMPORTANT LIMITATION: This tool shows only the final product area, not "
            "the individual fraction representations or the step-by-step visual process. "
            "Best for demonstrating the final result of fraction multiplication using area "
            "model concepts, grid-based multiplication understanding, and mathematical reasoning "
            "about fractional products with clear grid structure and proportional accuracy."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "fraction1": {
                    "type": "string",
                    "pattern": "^\\d+/\\d+$",
                    "description": (
                        "First fraction in the multiplication expression (e.g., '2/3', '3/4', "
                        "'1/2'). The denominator determines the width of the rectangular grid "
                        "(number of columns), and the numerator determines how many columns are "
                        "included in the yellow product area. For example, '2/3' creates a "
                        "3-column grid where the product area spans 2 columns. Maximum denominator "
                        "of 25 ensures clear visual grid structure and educational appropriateness "
                        "for area model instruction."
                    )
                },
                "fraction2": {
                    "type": "string",
                    "pattern": "^\\d+/\\d+$",
                    "description": (
                        "Second fraction in the multiplication expression (e.g., '3/4', '2/5', "
                        "'4/7'). The denominator determines the height of the rectangular grid "
                        "(number of rows), and the numerator determines how many rows are included "
                        "in the yellow product area. For example, '3/4' creates a 4-row grid where "
                        "the product area spans 3 rows. Combined with fraction1, the intersection "
                        "creates the final product area visualization (fraction1_num × "
                        "fraction2_num yellow cells)."
                    )
                }
            },
            "required": ["fraction1", "fraction2"],
            "additionalProperties": False
        }
    }
    return spec, generate_coach_bot_fraction_multiplication_units_image


def generate_coach_bot_divided_shapes_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for divided shapes."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_divided_shapes_image",
        "description": (
            "Generate fundamental fraction shapes divided into equal parts with flexible "
            "shading options for comprehensive fraction concept instruction and visual "
            "fraction representation. Creates clear geometric shapes (circles or rectangles) "
            "divided into precise equal segments without any shading (for exploration and "
            "discovery activities) or with complete shading (for whole number fraction "
            "concepts and visual comparison). Essential for foundational fraction education, "
            "part-whole relationship instruction, and visual fraction comprehension development "
            "with mathematically accurate division patterns and educational clarity."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "shapes": {
                    "type": "array",
                    "description": (
                        "List of shapes to divide into equal parts for fraction concept "
                        "instruction. Each shape dictionary must contain 'shape' (circle or "
                        "rectangle) and 'denominator' (number of equal parts) keys. Supports "
                        "multiple shapes for comparison exercises, fraction sequences, and "
                        "educational demonstrations. Circles are divided with radial lines from "
                        "center, rectangles are divided with vertical lines for consistent visual "
                        "representation and clear mathematical accuracy appropriate for all "
                        "educational levels."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "shape": {
                                "type": "string",
                                "enum": ["circle", "rectangle"],
                                "description": (
                                    "Shape type for the divided fraction visualization. Choose "
                                    "'circle' for pie chart-style representation with radial "
                                    "segment divisions, or 'rectangle' for bar model-style "
                                    "representation with vertical section divisions. Both provide "
                                    "clear visual fraction demonstration of equal parts concepts "
                                    "appropriate for foundational fraction education and "
                                    "mathematical understanding development."
                                )
                            },
                            "denominator": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 25,
                                "description": (
                                    "Number of equal parts to divide the shape into (1-25). "
                                    "Represents the denominator in fraction concepts and "
                                    "determines the visual division pattern. Higher values provide "
                                    "more complex fraction visualization while maintaining "
                                    "educational clarity. Choose values appropriate for student "
                                    "developmental level and learning objectives in fraction "
                                    "comprehension and mathematical reasoning instruction."
                                )
                            }
                        },
                        "required": ["shape", "denominator"],
                        "additionalProperties": False
                    },
                    "minItems": 1,
                    "maxItems": 8
                },
                "shading_type": {
                    "type": "string",
                    "enum": ["no_shade", "full_shade"],
                    "description": (
                        "Visual shading option for educational flexibility and instructional "
                        "variety. Choose 'no_shade' for blank shapes with division lines only "
                        "(perfect for exploration activities, student practice, and discovery "
                        "learning where students identify or shade their own parts). Choose "
                        "'full_shade' for completely shaded shapes (ideal for demonstrating whole "
                        "number concepts, comparison activities, and visual reinforcement of "
                        "complete fraction units)."
                    ),
                    "default": "no_shade"
                }
            },
            "required": ["shapes"],
            "additionalProperties": False
        }
    }
    return spec, generate_coach_bot_divided_shapes_image


def generate_coach_bot_unequal_fractions_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for unequal fractions."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_unequal_fractions_image",
        description=(
            "Generate comprehensive visual representations of shapes divided into equal "
            "or unequal parts to demonstrate critical fraction foundation concepts and "
            "mathematical reasoning about part-whole relationships. Creates educational "
            "visualizations showing the difference between equal division (true fractions) "
            "and unequal division (non-fractional parts) using circles and rectangles. "
            "Essential for foundational fraction education, spatial reasoning instruction, "
            "and visual discrimination skills development. Perfect for teaching why fractions "
            "require equal parts, comparative analysis activities, and mathematical precision "
            "understanding with clear visual accuracy and educational effectiveness."
        ),
        pydantic_model=UnequalFractionList,
        parameter_wrapper_name="shapes",
        custom_descriptions={
            "shapes": (
                "List of shapes to divide into equal or unequal parts for fraction concept "
                "instruction and comparative analysis. Each shape contains specifications for "
                "'shape' (circle or rectangle), 'divided_parts' (2-25 parts), and "
                "'equally_divided' (true for equal parts, false for deliberately unequal parts). "
                "Perfect for teaching the fundamental concept that fractions require equal parts, "
                "visual discrimination between equal and unequal divisions, and mathematical "
                "precision understanding. All shapes are fully shaded to emphasize the division "
                "patterns rather than fraction values, making this ideal for foundational "
                "part-whole relationship instruction and spatial reasoning development."
            )
        }
    )
    return spec, generate_coach_bot_unequal_fractions_image


def generate_coach_bot_mixed_fractions_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for mixed fractions."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_mixed_fractions_image",
        description=(
            "Generate comprehensive mixed number and improper fraction visualizations using "
            "multiple coordinated shapes to demonstrate advanced fraction concepts beyond one "
            "whole unit. Creates educational displays showing how fractions greater than 1 "
            "(improper fractions) can be represented visually and conceptually converted to "
            "mixed numbers with whole units plus fractional parts. Essential for intermediate "
            "fraction education, improper fraction understanding, and mixed number concept "
            "instruction. Perfect for teaching fraction magnitude, whole-part relationships, "
            "and advanced fraction representation with clear visual accuracy and mathematical "
            "precision for enhanced fraction comprehension and reasoning development."
        ),
        pydantic_model=MixedFractionList,
        parameter_wrapper_name="mixed_fractions",
        custom_descriptions={
            "mixed_fractions": (
                "List of mixed number and improper fraction models for advanced fraction "
                "visualization and mathematical reasoning. Each model contains 'shape' (circle "
                "or rectangle) and 'fraction' (can be greater than 1 for improper fractions "
                "like '7/4', '11/3', '5/2'). The system automatically creates multiple shapes "
                "when fractions exceed 1, with complete shapes representing whole units and "
                "partial shapes representing fractional remainders. Perfect for teaching "
                "improper fraction concepts, mixed number conversion, fraction magnitude "
                "comparison, and visual fraction comprehension beyond single unit representation. "
                "Supports 1-4 models displayed in flexible grid layout for educational clarity."
            )
        }
    )
    return spec, generate_coach_bot_mixed_fractions_image


def generate_coach_bot_whole_fractions_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for whole fractions."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_whole_fractions_image",
        description=(
            "Generate comprehensive whole fraction visualizations using multiple fully shaded "
            "shapes to demonstrate complete fraction units and mathematical whole number "
            "relationships. Creates educational displays showing 1-5 identical shapes, each "
            "divided into equal parts with complete shading to represent whole fractions like "
            "3/3, 6/6, 4/4, etc. Essential for foundational fraction education, whole unit "
            "concept instruction, and visual fraction comprehension. Perfect for teaching that "
            "fractions can represent whole numbers, fraction equivalence to 1, and mathematical "
            "reasoning about complete fraction units with clear visual accuracy and educational "
            "effectiveness for enhanced fraction understanding and conceptual development."
        ),
        pydantic_model=WholeFractionalShapes,
        custom_descriptions={
            "count": (
                "Number of whole fraction units (shapes) to display in the visualization (1-5). "
                "Each shape represents one complete whole unit divided into equal parts with "
                "full shading. Perfect for demonstrating fraction concepts where the numerator "
                "equals the denominator (3/3 = 1, 4/4 = 1, etc.). Multiple shapes help teach "
                "fraction multiplication, equivalent whole numbers, and visual reinforcement "
                "of complete fraction units for foundational mathematical understanding."
            ),
            "shape": (
                "Type of geometric shape to use for whole fraction representation. Choose "
                "'circle' for pie chart-style visualization with radial divisions and complete "
                "shading, or 'rectangle' for bar model-style representation with vertical "
                "divisions and full shading. Both shapes provide clear visual demonstration "
                "of complete fraction units appropriate for whole number fraction instruction "
                "and mathematical reasoning development with consistent educational effectiveness."
            ),
            "divisions": (
                "Number of equal parts each shape is divided into, representing the common "
                "denominator (1-14). All shapes use the same division pattern for consistency "
                "and comparison. Each part is fully shaded to show complete fraction units. "
                "Lower values (2-6) are ideal for introductory concepts, higher values (7-14) "
                "for advanced fraction understanding. Choose values appropriate for student "
                "developmental level and educational objectives in whole fraction instruction."
            )
        }
    )
    return spec, generate_coach_bot_whole_fractions_image


def generate_coach_bot_fraction_strips_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for fraction strips."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_fraction_strips_image",
        description=(
            "Generate stacked rectangles showing fraction decomposition for comprehensive "
            "fraction education and visual fraction representation. Creates 2-3 progressive "
            "levels demonstrating how whole numbers decompose into unit fractions and further "
            "subdivisions. Essential for teaching fractional decomposition concepts, unit "
            "fraction understanding, and visual fraction relationships. Perfect for elementary "
            "mathematics education, fraction literacy instruction, and mathematical reasoning "
            "development. 🚨 CRITICAL PARAMETER RULES: When splits=2, do NOT provide "
            "second_division parameter at all. When splits=3, second_division is MANDATORY. "
            "These rules prevent validation errors and ensure proper fraction strip visualization."
        ),
        pydantic_model=FractionStrips,
        custom_descriptions={
            "splits": (
                "Number of rectangle strips to draw in the decomposition visualization. "
                "Choose 2 for basic whole-to-unit fraction demonstration (second_division "
                "must NOT be provided), or 3 for advanced multi-level decomposition showing "
                "further subdivision of unit fractions (second_division is MANDATORY). "
                "🚨 CRITICAL: This choice determines whether second_division parameter should "
                "be included or omitted entirely to prevent validation errors. For splits=2, "
                "only provide splits and first_division parameters."
            ),
            "first_division": (
                "Number of equal parts to split the whole into for the second rectangle "
                "strip (range 2-10). Represents the denominator of the unit fractions "
                "created from the whole. Critical for teaching unit fraction concepts, "
                "equal partitioning, and foundational fraction comprehension. Always "
                "required regardless of splits value. Choose values appropriate for "
                "student developmental level and learning objectives."
            ),
            "second_division": (
                "Number of equal parts to split one unit fraction into for the third "
                "rectangle strip (range 2-10). 🚨 CONDITIONAL USAGE: ONLY provide this "
                "parameter when splits=3. When splits=2, do NOT include this parameter "
                "at all or it will be ignored. When splits=3, this parameter is "
                "MANDATORY. Demonstrates advanced fractional decomposition by further "
                "subdividing unit fractions. Essential for teaching complex fraction "
                "relationships and multiplicative fraction concepts. CONSTRAINT: Product "
                "of first_division × second_division must not exceed 21 to ensure smallest "
                "fraction remains educationally appropriate."
            )
        }
    )
    return spec, generate_coach_bot_fraction_strips_image
