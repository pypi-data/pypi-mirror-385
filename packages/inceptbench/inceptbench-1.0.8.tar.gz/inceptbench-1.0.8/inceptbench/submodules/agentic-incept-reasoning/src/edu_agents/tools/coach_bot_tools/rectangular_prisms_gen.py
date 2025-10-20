from __future__ import annotations  # noqa: I001

import logging  # noqa: E402
from typing import Callable

# Coach-bot imports setup handled by setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.rectangular_prisms import (  # noqa: E501
    draw_multiple_rectangular_prisms,
    draw_multiple_base_area_rectangular_prisms,
    draw_unit_cube_figure,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.rectangular_prisms import (  # noqa: E501
    RectangularPrismList,
    BaseAreaRectangularPrismList,
    UnitCubeFigure,
    RectangularPrismShape,
    CustomCubeShape,
    Point3d,
)

from .coach_bot_utils import (
    setup_coach_bot_imports,
    create_dynamic_tool_spec,
    log_tool_generation,
    upload_coach_bot_image
)

# Setup coach-bot imports
setup_coach_bot_imports()  # noqa: E402

logger = logging.getLogger("coach_bot_tools.rectangular_prisms")


def generate_coach_bot_rectangular_prisms_image(**kwargs) -> str:
    """
    Generate visualization of one or more rectangular prisms with measurements.
    
    Creates 3D visualizations showing rectangular prisms with customizable fill states
    (empty, partial, bottom layer, or full of unit cubes) and dimensional labels.
    Perfect for teaching volume, surface area, and 3D geometry concepts through
    visual representation of spatial relationships and dimensional analysis.
    
    Educational applications include volume calculations, surface area exploration,
    3D geometry understanding, spatial reasoning development, and unit cube
    counting exercises. Supports various fill states to demonstrate different
    levels of completion and measurement visibility for comprehensive
    mathematical instruction.
    
    Note: Layout warnings may occur with multiple prisms but don't affect quality.
    
    Returns
    -------
    str
        The URL of the generated rectangular prisms image
    """
    
    log_tool_generation("generate_coach_bot_rectangular_prisms_image", **kwargs)
    
    # Create and validate using Pydantic model (handles all validation automatically)
    prism_list = RectangularPrismList(**kwargs)
    
    # Generate the image using the prisms drawing function
    image_file_path = draw_multiple_rectangular_prisms(prism_list)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_base_area_prisms_image(**kwargs) -> str:
    """
    Generate controlled comparison visualization of rectangular prisms by base area.
    
    🚨 CRITICAL CONSTRAINT: When using 2+ prisms, ALL must have SAME height for 
    valid educational comparison. This enables controlled experiments where height 
    is constant and only base area varies, clearly demonstrating the direct 
    relationship between base area changes and volume changes.
    
    Creates 3D visualizations where prisms are specified by their base area rather
    than individual width and length dimensions. Perfect for teaching volume formula
    V = base area × height through controlled mathematical experiments.
    
    Educational applications include volume formula understanding, base area effect
    isolation, controlled variable analysis, and multiplicative reasoning through
    area-height relationships. Supports measurement visibility for focused learning.
    
    Returns
    -------
    str
        The URL of the generated base area prisms image
    """
    
    log_tool_generation("generate_coach_bot_base_area_prisms_image", **kwargs)
    
    # Create and validate using Pydantic model (handles all validation automatically)
    prism_list = BaseAreaRectangularPrismList(**kwargs)
    
    # Generate the image using the base area prisms function
    image_file_path = draw_multiple_base_area_rectangular_prisms(prism_list)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_unit_cube_figure_image(
    title: str,
    shape_type: str,
    **shape_params
) -> str:
    """
    Generate a unit cube figure (rectangular prism or custom shape).
    
    Creates visualizations of unit cube arrangements, either as regular rectangular
    prisms or custom single-layer connected shapes. Perfect for teaching volume 
    concepts, spatial reasoning with unit cubes, and 3D geometry understanding.
    
    🚨 CRITICAL CONSTRAINT for Custom Shapes: ALL cubes must have the SAME 
    y-coordinate (exactly one cube thick). This creates single-layer arrangements 
    that are face-connected and ideal for transitional 2D-to-3D understanding.
    
    Educational applications include volume calculations through counting,
    spatial visualization development, single-layer pattern construction, unit cube
    concept reinforcement, and hands-on geometry learning through controlled
    manipulatives that enhance mathematical reasoning and problem-solving skills.
    
    Parameters
    ----------
    title : str
        Title for the figure
    shape_type : str
        Type of shape - 'rectangular' or 'custom'
    **shape_params
        For rectangular: length, width, height (integers 1-10)
        For custom: cubes (list of {x, y, z} coordinates with same y-value)
        
    Returns
    -------
    str
        The URL of the generated unit cube figure image
    """
    
    log_tool_generation("generate_coach_bot_unit_cube_figure_image", 
                        title=title, shape_type=shape_type, **shape_params)
    
    # Create shape object based on type (Pydantic handles validation automatically)
    if shape_type == 'rectangular':
        shape = RectangularPrismShape(
            kind='rectangular',
            length=shape_params['length'],
            width=shape_params['width'],
            height=shape_params['height']
        )
        
    elif shape_type == 'custom':
        # Create Point3d objects for custom cubes (Pydantic validates coordinates)
        cube_points = [Point3d(**cube) for cube in shape_params['cubes']]
        shape = CustomCubeShape(
            kind='custom',
            cubes=cube_points
        )
        
    else:
        raise ValueError(f"Invalid shape_type '{shape_type}'. Must be 'rectangular' or 'custom'")
    
    # Create the UnitCubeFigure (Pydantic validates title and shape)
    figure = UnitCubeFigure(
        title=title,
        shape=shape
    )
    
    # Generate the image using the unit cube figure function
    image_file_path = draw_unit_cube_figure(figure)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_rectangular_prisms_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for rectangular prisms generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_rectangular_prisms_image",
        description=(
            "Generate visualization of rectangular prisms with customizable fill states and "
            "dimensional labels. Perfect for teaching volume, surface area, and 3D geometry "
            "concepts through visual representation of spatial relationships and dimensional "
            "analysis. Supports empty, partial, bottom layer, or full unit cube fill states "
            "with measurement labels for comprehensive educational instruction in geometry, "
            "spatial reasoning, and mathematical visualization. Note: Layout warnings may "
            "occur with multiple prisms but don't affect image quality."
        ),
        pydantic_model=RectangularPrismList,
        custom_descriptions={
            "root": (
                "List of rectangular prism specifications (1+ prisms). Each prism supports "
                "customizable dimensions (1-40 units), fill states (empty/partial/bottom/full), "
                "optional unit labels, and measurement visibility controls. Essential for "
                "teaching volume calculations, 3D geometry concepts, spatial reasoning, and "
                "unit cube counting through interactive visual mathematical representation."
            )
        }
    )
    return spec, generate_coach_bot_rectangular_prisms_image


def generate_coach_bot_base_area_prisms_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for base area prisms generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_base_area_prisms_image",
        description=(
            "Generate controlled comparison visualization of rectangular prisms defined by "
            "base area and height. 🚨 CRITICAL: When using 2+ prisms, ALL must have SAME "
            "height for valid comparison. Perfect for teaching volume formula V = base area × "
            "height through controlled experiments where height is constant and only base area "
            "varies. Enables students to see direct relationship between base area changes and "
            "volume changes. Supports customizable measurement visibility and unit labeling for "
            "focused learning objectives in 3D geometry and multiplicative reasoning instruction."
        ),
        pydantic_model=BaseAreaRectangularPrismList,
        custom_descriptions={
            "root": (
                "List of base area prism specifications (1-4 prisms). 🚨 CRITICAL CONSTRAINT: "
                "When using 2+ prisms, ALL prisms MUST have the SAME height for valid comparison. "
                "Each prism defined by base area (1-100 square units) and height (1-10 units) "
                "with optional unit labels and measurement visibility controls. Essential for "
                "teaching volume formula V = base area × height through controlled comparison "
                "where height remains constant and only base area varies."
            )
        }
    )
    return spec, generate_coach_bot_base_area_prisms_image


def generate_coach_bot_unit_cube_figure_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for unit cube figure generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_unit_cube_figure_image",
        "description": (
            "Generate unit cube figure visualizations (rectangular prism or custom shape). "
            "Creates manipulative-style arrangements perfect for teaching volume concepts, "
            "spatial reasoning, and 3D geometry understanding through digital unit cubes. "
            "Supports both regular rectangular prisms for structured volume calculation "
            "and custom single-layer shapes. 🚨 CRITICAL: Custom shapes must be exactly "
            "one cube thick (all cubes same y-coordinate) and face-connected. Essential "
            "for hands-on geometry learning, mathematical visualization, and developing "
            "spatial intelligence through controlled unit cube modeling and construction."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": (
                        "Educational title for the unit cube figure. Should clearly describe "
                        "the mathematical concept or learning objective being demonstrated "
                        "through the visualization for instructional clarity and context."
                    )
                },
                "shape_type": {
                    "type": "string",
                    "enum": ["rectangular", "custom"],
                    "description": (
                        "Type of unit cube arrangement: 'rectangular' for regular prisms "
                        "(requires length, width, height) perfect for volume calculations "
                        "and structured learning, or 'custom' for connected cube arrangements "
                        "(requires cubes coordinates) ideal for spatial creativity and exploration."
                    )
                },
                "length": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": (
                        "Length dimension in unit cubes for rectangular prism (1-10 units). "
                        "REQUIRED when shape_type='rectangular'. Essential for teaching "
                        "volume calculation as length × width × height and developing "
                        "understanding of 3D measurement and spatial relationships."
                    )
                },
                "width": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": (
                        "Width dimension in unit cubes for rectangular prism (1-10 units). "
                        "REQUIRED when shape_type='rectangular'. Essential for teaching "
                        "volume calculation and understanding spatial dimensions in 3D "
                        "geometric visualization and mathematical reasoning development."
                    )
                },
                "height": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": (
                        "Height dimension in unit cubes for rectangular prism (1-10 units). "
                        "REQUIRED when shape_type='rectangular'. Essential for teaching "
                        "volume calculation and developing 3D spatial understanding through "
                        "layered construction and dimensional analysis concepts."
                    )
                },
                "cubes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 10,
                                "description": (
                                    "X coordinate position of individual unit cube (0-10)"
                                )
                            },
                            "y": {
                                "type": "integer",
                                "minimum": 0, 
                                "maximum": 10,
                                "description": (
                                    "Y coordinate position of individual unit cube (0-10)"
                                )
                            },
                            "z": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 10,
                                "description": (
                                    "Z coordinate position of individual unit cube (0-10)"
                                )
                            }
                        },
                        "required": ["x", "y", "z"]
                    },
                    "description": (
                        "List of 3D coordinates for custom unit cube arrangement. REQUIRED "
                        "when shape_type='custom'. 🚨 CRITICAL CONSTRAINT: ALL cubes must have "
                        "the SAME y-coordinate (single layer thickness). Each cube specified by "
                        "{x, y, z} coordinates within 0-10 range. Cubes must be face-connected. "
                        "Creates single-layer arrangements for spatial reasoning, pattern "
                        "exploration, and 2D-to-3D transitional understanding in mathematics."
                    )
                }
            },
            "required": ["title", "shape_type"]
        }
    }
    return spec, generate_coach_bot_unit_cube_figure_image
