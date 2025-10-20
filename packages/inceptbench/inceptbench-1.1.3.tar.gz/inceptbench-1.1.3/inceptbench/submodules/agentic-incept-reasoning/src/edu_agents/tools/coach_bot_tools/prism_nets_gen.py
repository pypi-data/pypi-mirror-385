from __future__ import annotations

import logging
from typing import Callable

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.prism_nets import (  # noqa: E402
    draw_dual_nets,
    draw_pyramid_net,
    draw_rectangular_prism_net,
    draw_triangular_prism_net,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.prism_net import (  # noqa: E402
    CubePrismNet,
    DualNetsShapeType,
    DualPrismNets,
    Position,
    RectangularPyramidPrismNet,
    RegularRectangularPrismNet,
    SquarePyramidPrismNet,
    TriangularPrismNet,
)

logger = logging.getLogger("coach_bot_tools.prism_nets_gen")


def generate_coach_bot_rectangular_prism_net_image(
    height: int,
    width: int,
    length: int,
    unit_label: str,
    label_all_sides: bool = False,
    blank_net: bool = False
) -> str:
    """
    Generate a rectangular prism (cuboid) net diagram.
    
    Creates an unfolded 2D representation of a rectangular prism showing all six faces.
    Useful for teaching 3D geometry concepts, surface area calculations, and 
    spatial visualization skills.
    
    Parameters
    ----------
    height : int
        Height of the prism (must be positive)
    width : int
        Width of the prism (must be positive)
    length : int
        Length of the prism (must be positive)
    unit_label : str
        Unit of measurement (e.g., 'cm', 'in', 'units')
    label_all_sides : bool
        Whether to label all edges with dimensions (default: False)
    blank_net : bool
        Whether to show dimensions or create a blank net (default: False)
        
    Returns
    -------
    str
        The URL of the generated rectangular prism net image
    """
    
    log_tool_generation("generate_coach_bot_rectangular_prism_net_image", 
                        height=height, width=width, length=length, 
                        unit_label=unit_label, label_all_sides=label_all_sides, 
                        blank_net=blank_net)
    
    # Create the RegularRectangularPrismNet stimulus (Pydantic handles validation automatically)
    # Note: net_type is automatically set to EPrismType.RECTANGULAR by the Pydantic model
    prism_net = RegularRectangularPrismNet(
        height=height,
        width=width,
        length=length,
        unit_label=unit_label,
        label_all_sides=label_all_sides,
        blank_net=blank_net
    )
    
    # Generate the image using the rectangular prism net function
    image_file_path = draw_rectangular_prism_net(prism_net)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_cube_net_image(
    side_length: int,
    unit_label: str,
    label_all_sides: bool = False,
    blank_net: bool = False
) -> str:
    """
    Generate a cube net diagram.
    
    Creates an unfolded 2D representation of a cube showing all six identical faces.
    Useful for teaching 3D geometry concepts, surface area calculations, and 
    spatial visualization skills.
    
    Parameters
    ----------
    side_length : int
        Length of each side of the cube (must be positive)
    unit_label : str
        Unit of measurement (e.g., 'cm', 'in', 'units')
    label_all_sides : bool
        Whether to label all edges with dimensions (default: False)
    blank_net : bool
        Whether to show dimensions or create a blank net (default: False)
        
    Returns
    -------
    str
        The URL of the generated cube net image
    """
    
    log_tool_generation("generate_coach_bot_cube_net_image", 
                        side_length=side_length, unit_label=unit_label, 
                        label_all_sides=label_all_sides, blank_net=blank_net)
    
    # Create the CubePrismNet stimulus (all dimensions equal)
    cube_net = CubePrismNet(
        height=side_length,
        width=side_length,
        length=side_length,
        unit_label=unit_label,
        label_all_sides=label_all_sides,
        blank_net=blank_net
    )
    
    # Generate the image using the rectangular prism net function (cubes use the same function)
    image_file_path = draw_rectangular_prism_net(cube_net)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_triangular_prism_net_image(
    height: int,
    width: int,
    length: int,
    unit_label: str,
    label_all_sides: bool = False,
    blank_net: bool = False
) -> str:
    """
    Generate a triangular prism net diagram.
    
    Creates an unfolded 2D representation of a triangular prism showing three rectangular
    faces and two triangular faces. Useful for teaching 3D geometry concepts, surface 
    area calculations, and spatial visualization skills.
    
    Parameters
    ----------
    height : int
        Height of the triangular cross-section (must be positive)
    width : int
        Base width of the triangular cross-section (must be positive)
    length : int
        Length of the prism (must be positive)
    unit_label : str
        Unit of measurement (e.g., 'cm', 'in', 'units')
    label_all_sides : bool
        Whether to label all edges with dimensions (default: False)
    blank_net : bool
        Whether to show dimensions or create a blank net (default: False)
        
    Returns
    -------
    str
        The URL of the generated triangular prism net image
    """
    
    log_tool_generation("generate_coach_bot_triangular_prism_net_image", 
                        height=height, width=width, length=length, 
                        unit_label=unit_label, label_all_sides=label_all_sides, 
                        blank_net=blank_net)
    
    # Create the TriangularPrismNet stimulus (Pydantic handles validation automatically)
    # Note: net_type is automatically set to EPrismType.TRIANGULAR by the Pydantic model
    prism_net = TriangularPrismNet(
        height=height,
        width=width,
        length=length,
        unit_label=unit_label,
        label_all_sides=label_all_sides,
        blank_net=blank_net
    )
            
    # Generate the image using the triangular prism net function
    image_file_path = draw_triangular_prism_net(prism_net)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_square_pyramid_net_image(
    height: int,
    base_side_length: int,
    unit_label: str,
    label_all_sides: bool = False,
    blank_net: bool = False
) -> str:
    """
    Generate a square pyramid net diagram.
    
    Creates an unfolded 2D representation of a square pyramid showing one square base
    and four triangular faces. Useful for teaching 3D geometry concepts, surface area
    calculations, and spatial visualization skills.
    
    Parameters
    ----------
    height : int
        Height of the pyramid (must be positive)
    base_side_length : int
        Side length of the square base (must be positive)
    unit_label : str
        Unit of measurement (e.g., 'cm', 'in', 'units')
    label_all_sides : bool
        Whether to label all edges with dimensions (default: False)
    blank_net : bool
        Whether to show dimensions or create a blank net (default: False)
        
    Returns
    -------
    str
        The URL of the generated square pyramid net image
    """
    
    log_tool_generation("generate_coach_bot_square_pyramid_net_image", 
                        height=height, base_side_length=base_side_length, 
                        unit_label=unit_label, label_all_sides=label_all_sides, 
                        blank_net=blank_net)
    
    # Create the SquarePyramidPrismNet stimulus (width = length for square base)
    pyramid_net = SquarePyramidPrismNet(
        height=height,
        width=base_side_length,
        length=base_side_length,
        unit_label=unit_label,
        label_all_sides=label_all_sides,
        blank_net=blank_net
    )
    
    # Generate the image using the pyramid net function
    image_file_path = draw_pyramid_net(pyramid_net)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_rectangular_pyramid_net_image(
    height: int,
    base_width: int,
    base_length: int,
    unit_label: str,
    label_all_sides: bool = False,
    blank_net: bool = False
) -> str:
    """
    Generate a rectangular pyramid net diagram.
    
    Creates an unfolded 2D representation of a rectangular pyramid showing one rectangular
    base and four triangular faces. Useful for teaching 3D geometry concepts, surface area
    calculations, and spatial visualization skills.
    
    Parameters
    ----------
    height : int
        Height of the pyramid (must be positive)
    base_width : int
        Width of the rectangular base (must be positive)
    base_length : int
        Length of the rectangular base (must be positive)
    unit_label : str
        Unit of measurement (e.g., 'cm', 'in', 'units')
    label_all_sides : bool
        Whether to label all edges with dimensions (default: False)
    blank_net : bool
        Whether to show dimensions or create a blank net (default: False)
        
    Returns
    -------
    str
        The URL of the generated rectangular pyramid net image
    """
    
    log_tool_generation("generate_coach_bot_rectangular_pyramid_net_image", 
                        height=height, base_width=base_width, base_length=base_length, 
                        unit_label=unit_label, label_all_sides=label_all_sides, 
                        blank_net=blank_net)
    
    # Create the RectangularPyramidPrismNet stimulus
    pyramid_net = RectangularPyramidPrismNet(
        height=height,
        width=base_width,
        length=base_length,
        unit_label=unit_label,
        label_all_sides=label_all_sides,
        blank_net=blank_net
    )
    
    # Generate the image using the pyramid net function
    image_file_path = draw_pyramid_net(pyramid_net)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_dual_prism_nets_image(
    correct_shape_type: str,
    incorrect_shape_type: str,
    correct_shape_position: str
) -> str:
    """
    Generate a comparison image showing two 3D shape nets side by side.
    
    Creates a visual comparison of two different 3D shape nets for assessment purposes.
    Shows two nets labeled as "Figure 1" and "Figure 2" where one is correct for the 
    question and one is incorrect. Useful for teaching shape identification and 
    spatial reasoning skills.
    
    Parameters
    ----------
    correct_shape_type : str
        Type of 3D shape that is the correct answer. Must be one of:
        'cube', 'rectangular_prism', 'triangular_prism', 'square_pyramid', 'rectangular_pyramid'
    incorrect_shape_type : str
        Type of 3D shape to use as the incorrect option. Must be one of:
        'cube', 'rectangular_prism', 'triangular_prism', 'square_pyramid', 'rectangular_pyramid'
    correct_shape_position : str
        Whether to show the correct shape in 'left' (Figure 1) or 'right' (Figure 2) position
        
    Returns
    -------
    str
        The URL of the generated dual nets comparison image
    """
    
    log_tool_generation("generate_coach_bot_dual_prism_nets_image", 
                        correct_shape_type=correct_shape_type, 
                        incorrect_shape_type=incorrect_shape_type, 
                        correct_shape_position=correct_shape_position)
    
    # Validate shape types
    valid_shapes = ["cube", "rectangular_prism", "triangular_prism", "square_pyramid",
                    "rectangular_pyramid"]
    if correct_shape_type not in valid_shapes:
        raise ValueError(f"correct_shape_type must be one of {valid_shapes}")
    if incorrect_shape_type not in valid_shapes:
        raise ValueError(f"incorrect_shape_type must be one of {valid_shapes}")
    if correct_shape_type == incorrect_shape_type:
        raise ValueError("correct_shape_type and incorrect_shape_type must be different")
    
    # Validate position
    if correct_shape_position not in ["left", "right"]:
        raise ValueError("correct_shape_position must be 'left' or 'right'")
    
    # Convert string values to enum values
    correct_enum = DualNetsShapeType(correct_shape_type)
    incorrect_enum = DualNetsShapeType(incorrect_shape_type)
    position_enum = Position(correct_shape_position)
    
    # Create the DualPrismNets stimulus
    dual_nets = DualPrismNets(
        correct_shape_type=correct_enum,
        incorrect_shape_type=incorrect_enum,
        correct_shape_position=position_enum
    )
    
    # Generate the image using the dual nets function
    image_file_path = draw_dual_nets(dual_nets)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


# Tool specifications
def generate_coach_bot_rectangular_prism_net_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for rectangular prism net generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_rectangular_prism_net_image",
        "description": (
            "Generate rectangular prism (cuboid) net diagrams for 3D geometry education. "
            "Creates unfolded 2D representations showing all six faces with dimensional labels "
            "and measurement units. Perfect for teaching surface area calculations, spatial "
            "visualization, and 3D-to-2D transformations. Supports educational customization with "
            "optional labeling and blank net modes for assessment and interactive learning "
            "exercises."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "height": {
                    "type": "integer",
                    "minimum": 1,
                    "description": (
                        "Height dimension of the rectangular prism in specified units (positive "
                        "integer). Determines the vertical extent of the 3D shape and affects "
                        "surface area calculations for mathematical education and spatial "
                        "reasoning instruction."
                    )
                },
                "width": {
                    "type": "integer",
                    "minimum": 1,
                    "description": (
                        "Width dimension of the rectangular prism in specified units (positive "
                        "integer). Defines the horizontal extent of the base and contributes to "
                        "volume and surface area computations for geometric analysis and STEM "
                        "education."
                    )
                },
                "length": {
                    "type": "integer",
                    "minimum": 1,
                    "description": (
                        "Length dimension of the rectangular prism in specified units (positive "
                        "integer). Establishes the depth of the 3D shape for comprehensive "
                        "geometric understanding and mathematical modeling in educational contexts."
                    )
                },
                "unit_label": {
                    "type": "string",
                    "description": (
                        "Unit of measurement for all dimensions (e.g., 'cm', 'inches', 'feet', "
                        "'units'). Essential for dimensional analysis, real-world applications, "
                        "and mathematical communication skills in geometry and measurement "
                        "instruction."
                    )
                },
                "label_all_sides": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Whether to display dimensional labels on all edges of the net (default: "
                        "False). When True, provides comprehensive labeling for detailed analysis. "
                        "When False, offers cleaner visualization for introductory concepts and "
                        "assessment materials."
                    )
                },
                "blank_net": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Whether to create a blank net without dimensional markings (default: "
                        "False). Useful for assessment, student practice exercises, and "
                        "interactive geometry activities where students fill in measurements or "
                        "identify shapes."
                    )
                }
            },
            "required": ["height", "width", "length", "unit_label"]
        }
    }
    return spec, generate_coach_bot_rectangular_prism_net_image


def generate_coach_bot_cube_net_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for cube net generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_cube_net_image",
        "description": (
            "Generate cube net diagrams for foundational 3D geometry education. Creates "
            "unfolded 2D representations showing all six identical square faces with "
            "dimensional labels and measurement units. Perfect for teaching surface area "
            "calculations, spatial visualization, and understanding regular polyhedra. "
            "Supports educational customization with optional labeling and blank modes "
            "for comprehensive geometric instruction and assessment materials."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "side_length": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Side length of the cube in specified units (positive integer). "
                                   "Determines all dimensions since cubes have equal edges. "
                                   "Essential for surface area calculations and spatial reasoning "
                                   "instruction."
                },
                "unit_label": {
                    "type": "string",
                    "description": "Unit of measurement (e.g., 'cm', 'in', 'units')"
                },
                "label_all_sides": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to label all edges with dimensions"
                },
                "blank_net": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to create a blank net without dimensions"
                }
            },
            "required": ["side_length", "unit_label"]
        }
    }
    return spec, generate_coach_bot_cube_net_image


def generate_coach_bot_triangular_prism_net_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for triangular prism net generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_triangular_prism_net_image",
        "description": (
            "Generate triangular prism net diagrams for advanced 3D geometry education. "
            "Creates unfolded 2D representations showing three rectangular faces and two "
            "triangular faces with dimensional labels and measurement units. Perfect for "
            "teaching complex surface area calculations, spatial visualization, and advanced "
            "geometric transformations. Supports educational customization for comprehensive "
            "STEM instruction and mathematical modeling exercises."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "height": {
                    "type": "integer",
                    "minimum": 1,
                    "description": (
                        "Height dimension of the triangular cross-section in specified units "
                        "(positive integer). Determines the vertical extent of the triangular "
                        "faces and affects surface area calculations for advanced geometric "
                        "education and engineering applications."
                    )
                },
                "width": {
                    "type": "integer",
                    "minimum": 1,
                    "description": (
                        "Base width of the triangular cross-section in specified units (positive "
                        "integer). Defines the horizontal extent of the triangular base and "
                        "contributes to volume and surface area computations for complex geometric "
                        "analysis."
                    )
                },
                "length": {
                    "type": "integer",
                    "minimum": 1,
                    "description": (
                        "Length dimension of the triangular prism in specified units (positive "
                        "integer). Establishes the depth of the prism and determines the "
                        "dimensions of rectangular faces for comprehensive 3D geometric "
                        "understanding and spatial reasoning."
                    )
                },
                "unit_label": {
                    "type": "string",
                    "description": (
                        "Unit of measurement for all dimensions (e.g., 'cm', 'inches', 'meters', "
                        "'units'). Critical for dimensional analysis, engineering applications,"
                        "and mathematical precision in advanced geometry and measurement "
                        "instruction."
                    )
                },
                "label_all_sides": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Whether to display dimensional labels on all edges of the net (default: "
                        "False). When True, provides comprehensive labeling for detailed "
                        "mathematical analysis. When False, offers cleaner visualization for "
                        "conceptual introduction."
                    )
                },
                "blank_net": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Whether to create a blank net without dimensional markings (default: "
                        "False). Useful for advanced assessment, student construction exercises, "
                        "and interactive geometry activities requiring measurement and calculation "
                        "skills."
                    )
                }
            },
            "required": ["height", "width", "length", "unit_label"]
        }
    }
    return spec, generate_coach_bot_triangular_prism_net_image


def generate_coach_bot_square_pyramid_net_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for square pyramid net generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_square_pyramid_net_image",
        "description": (
            "Generate a square pyramid net diagram. Creates an unfolded 2D representation "
            "showing one square base and four triangular faces for teaching 3D geometry "
            "concepts and surface area calculations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "height": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Height of the pyramid"
                },
                "base_side_length": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Side length of the square base"
                },
                "unit_label": {
                    "type": "string",
                    "description": "Unit of measurement (e.g., 'cm', 'in', 'units')"
                },
                "label_all_sides": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to label all edges with dimensions"
                },
                "blank_net": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to create a blank net without dimensions"
                }
            },
            "required": ["height", "base_side_length", "unit_label"]
        }
    }
    return spec, generate_coach_bot_square_pyramid_net_image


def generate_coach_bot_rectangular_pyramid_net_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for rectangular pyramid net generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_rectangular_pyramid_net_image",
        "description": (
            "Generate a rectangular pyramid net diagram. Creates an unfolded 2D representation "
            "showing one rectangular base and four triangular faces for teaching 3D geometry "
            "concepts and surface area calculations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "height": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Height of the pyramid"
                },
                "base_width": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Width of the rectangular base"
                },
                "base_length": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Length of the rectangular base"
                },
                "unit_label": {
                    "type": "string",
                    "description": "Unit of measurement (e.g., 'cm', 'in', 'units')"
                },
                "label_all_sides": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to label all edges with dimensions"
                },
                "blank_net": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to create a blank net without dimensions"
                }
            },
            "required": ["height", "base_width", "base_length", "unit_label"]
        }
    }
    return spec, generate_coach_bot_rectangular_pyramid_net_image


def generate_coach_bot_dual_prism_nets_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for dual prism nets comparison generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_dual_prism_nets_image",
        "description": (
            "Generate a comparison image showing two 3D shape nets side by side. Creates "
            "a visual comparison for assessment purposes with one correct and one incorrect "
            "net labeled as Figure 1 and Figure 2."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "correct_shape_type": {
                    "type": "string",
                    "enum": ["cube", "rectangular_prism", "triangular_prism", "square_pyramid",
                            "rectangular_pyramid"],
                    "description": "Type of 3D shape that is the correct answer"
                },
                "incorrect_shape_type": {
                    "type": "string",
                    "enum": ["cube", "rectangular_prism", "triangular_prism", "square_pyramid",
                            "rectangular_pyramid"],
                    "description": "Type of 3D shape to use as the incorrect option"
                },
                "correct_shape_position": {
                    "type": "string",
                    "enum": ["left", "right"],
                    "description": "Whether to show the correct shape in left (Figure 1) or right "
                                   "(Figure 2) position"
                }
            },
            "required": ["correct_shape_type", "incorrect_shape_type", "correct_shape_position"]
        }
    }
    return spec, generate_coach_bot_dual_prism_nets_image
