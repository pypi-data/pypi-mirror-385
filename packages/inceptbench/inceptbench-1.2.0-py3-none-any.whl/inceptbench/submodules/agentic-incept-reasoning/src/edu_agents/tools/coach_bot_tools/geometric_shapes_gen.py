from __future__ import annotations

import logging
from typing import Callable, Dict, List

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.geometric_shapes import (  # noqa: E402, E501
    draw_geometric_shapes,
    draw_geometric_shapes_no_indicators,
    draw_geometric_shapes_no_indicators_with_rotation,
    draw_geometric_shapes_with_angles,
    draw_geometric_shapes_with_rotation,
    draw_shape_with_right_angles,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.geometric_shapes import (  # noqa: E402, E501
    GeometricShape,
    GeometricShapeList,
    GeometricShapeListWithRotation,
    GeometricShapeWithAngle,
    GeometricShapeWithAngleList,
    ShapeWithRightAngles,
    ValidGeometricShape,
)

logger = logging.getLogger("coach_bot_tools.geometric_shapes")


def generate_coach_bot_geometric_shapes_image(
    shapes: List[Dict],
    show_indicators: bool = True,
    with_rotation: bool = False
) -> str:
    """
    Generate geometric shapes with various options for indicators and rotation.
    
    Perfect tool for comprehensive geometry education, shape recognition, and spatial
    reasoning development. Creates versatile educational visualizations with customizable
    features for diverse teaching contexts and skill levels.
    
    Args:
        shapes: List of shape dictionaries with 'shape', 'color', and 'label' keys
        show_indicators: Whether to show dimension indicators (tick marks, etc.)
        with_rotation: Whether to apply random rotation to shapes
        
    Returns:
        str: URL to the uploaded geometric shapes image
    """
    log_tool_generation("generate_coach_bot_geometric_shapes_image", 
                       shapes=f"{len(shapes)} shapes", 
                       show_indicators=show_indicators, 
                       with_rotation=with_rotation)
    
    # Convert input to Pydantic models
    shape_objects = []
    for shape_data in shapes:
        shape_obj = GeometricShape(
            shape=ValidGeometricShape(shape_data["shape"]),
            color=shape_data.get("color", "blue"),
            label=shape_data.get("label")
        )
        shape_objects.append(shape_obj)
    
    if with_rotation:
        # Use rotation-enabled version
        shape_list = GeometricShapeListWithRotation(
            shapes=shape_objects,
            rotate=True
        )
        if show_indicators:
            image_file_path = draw_geometric_shapes_with_rotation(shape_list)
        else:
            image_file_path = draw_geometric_shapes_no_indicators_with_rotation(shape_list)
    else:
        # Use standard version
        shape_list = GeometricShapeList(root=shape_objects)
        if show_indicators:
            image_file_path = draw_geometric_shapes(shape_list)
        else:
            image_file_path = draw_geometric_shapes_no_indicators(shape_list)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_shapes_with_angles_image(
    shapes: List[Dict]
) -> str:
    """
    Generate geometric shapes with specific angle markers.
    
    Essential tool for advanced angle instruction, classification, and assessment.
    Creates educational visualizations that highlight specific angle types (acute, obtuse, 
    right) within geometric shapes for enhanced understanding and analysis.
    
    Args:
        shapes: List with 'shape', 'angle_type', 'color', and 'label' keys
        
    Returns:
        str: URL to the uploaded shapes with angles image
    """
    log_tool_generation("generate_coach_bot_shapes_with_angles_image", 
                       shapes=f"{len(shapes)} shapes with angle markers")
    
    # Convert input to Pydantic models
    shape_objects = []
    for shape_data in shapes:
        shape_obj = GeometricShapeWithAngle(
            shape=ValidGeometricShape(shape_data["shape"]),
            angle_type=shape_data["angle_type"],
            color=shape_data.get("color", "blue"),
            label=shape_data.get("label")
        )
        shape_objects.append(shape_obj)
    
    shape_list = GeometricShapeWithAngleList(root=shape_objects)
    image_file_path = draw_geometric_shapes_with_angles(shape_list)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_shape_with_right_angles_image(
    num_right_angles: int
) -> str:
    """
    Generate a random shape with a specified number of right angles.
    
    Perfect tool for teaching angle recognition, classification, and geometric properties.
    Creates educational visualizations that highlight right angle markers for clear 
    identification of 90-degree angles in various geometric contexts.
    
    Args:
        num_right_angles: Number of right angles (0-4)
        
    Returns:
        str: URL to the uploaded shape with right angles image
    """
    log_tool_generation("generate_coach_bot_shape_with_right_angles_image", 
                       num_right_angles=num_right_angles)
    
    shape_data = ShapeWithRightAngles(num_right_angles=num_right_angles)
    image_file_path = draw_shape_with_right_angles(shape_data)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_geometric_shapes_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for geometric shapes."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_geometric_shapes_image",
        "description": (
            "Generate comprehensive geometric shapes (triangles, quadrilaterals, "
            "polygons, circles) with customizable dimension indicators and rotation "
            "effects. Perfect educational tool for geometry instruction, shape "
            "recognition, spatial reasoning development, and mathematical "
            "visualization. Supports diverse teaching contexts from basic shape "
            "identification to advanced geometric analysis and classification exercises."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "shapes": {
                    "type": "array",
                    "description": (
                        "List of geometric shapes to generate for educational "
                        "visualization. Each shape supports comprehensive customization "
                        "for diverse instructional needs."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "shape": {
                                "type": "string",
                                "enum": [
                                    "square", "rectangle", "triangle", "circle", "pentagon",
                                    "hexagon", "heptagon", "octagon", "rhombus", "trapezoid",
                                    "isosceles trapezoid", "right trapezoid", "isosceles triangle",
                                    "right triangle", "scalene triangle", "regular triangle",
                                    "equilateral triangle", "regular quadrilateral",
                                    "quadrilateral", "regular pentagon", "regular hexagon",
                                    "regular heptagon", "regular octagon", "obtuse triangle",
                                    "acute triangle", "parallelogram", "kite"
                                ],
                                "description": (
                                    "Type of geometric shape for educational instruction. "
                                    "Supports comprehensive range from basic shapes (triangle, "
                                    "square, circle) to advanced polygons (hexagon, heptagon, "
                                    "octagon) and specialized quadrilaterals (rhombus, kite, "
                                    "parallelogram) for diverse geometric education."
                                )
                            },
                            "color": {
                                "type": "string",
                                "description": (
                                    "Fill and outline color of the shape for visual "
                                    "distinction and educational categorization. Supports "
                                    "standard color names and enhances shape recognition exercises."
                                ),
                                "default": "blue"
                            },
                            "label": {
                                "type": "string",
                                "description": (
                                    "Optional educational label for shape identification "
                                    "(e.g., 'Figure A', 'Shape 1'). Auto-generated based on "
                                    "shape name if not provided. Essential for selection "
                                    "problems and comparative analysis."
                                )
                            }
                        },
                        "required": ["shape"]
                    },
                    "minItems": 1,
                    "maxItems": 9
                },
                "show_indicators": {
                    "type": "boolean",
                    "description": (
                        "Whether to display dimension indicators, tick marks, and "
                        "measurement aids. Essential for geometric analysis, measurement "
                        "instruction, and spatial reasoning development. Enhances "
                        "educational value for assessment activities."
                    ),
                    "default": True
                },
                "with_rotation": {
                    "type": "boolean",
                    "description": (
                        "Whether to apply random rotation to shapes for advanced spatial "
                        "reasoning. Challenges students to recognize shapes in different "
                        "orientations, developing geometric intuition and shape recognition "
                        "skills independent of position."
                    ),
                    "default": False
                }
            },
            "required": ["shapes"]
        }
    }
    return spec, generate_coach_bot_geometric_shapes_image


def generate_coach_bot_shapes_with_angles_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for shapes with angle markers."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_shapes_with_angles_image",
        "description": (
            "Generate geometric shapes with specific angle markers to highlight "
            "acute, obtuse, or right angles within the shapes. Essential educational "
            "tool for advanced angle instruction, classification, assessment, and "
            "geometric analysis. Creates comprehensive visualizations for angle "
            "recognition, measurement understanding, and spatial reasoning development."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "shapes": {
                    "type": "array",
                    "description": (
                        "List of shapes with specific angle type markers for educational "
                        "instruction. Each shape highlights a particular angle type "
                        "(acute, obtuse, right) for enhanced geometric understanding "
                        "and assessment activities."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "shape": {
                                "type": "string",
                                "enum": [
                                    "square", "rectangle", "triangle", "circle", "pentagon",
                                    "hexagon", "heptagon", "octagon", "rhombus", "trapezoid",
                                    "isosceles trapezoid", "right trapezoid", "isosceles triangle",
                                    "right triangle", "scalene triangle", "regular triangle",
                                    "equilateral triangle", "regular quadrilateral",
                                    "quadrilateral", "regular pentagon", "regular hexagon",
                                    "regular heptagon", "regular octagon", "obtuse triangle",
                                    "acute triangle", "parallelogram", "kite"
                                ],
                                "description": (
                                    "Type of geometric shape for angle marker instruction. "
                                    "Supports comprehensive range of polygons and quadrilaterals, "
                                    "each providing different angle measurement opportunities "
                                    "for diverse educational contexts."
                                )
                            },
                            "angle_type": {
                                "type": "string",
                                "enum": ["acute", "obtuse", "right"],
                                "description": (
                                    "Type of angle to highlight with visual markers: 'acute' "
                                    "(< 90°), 'obtuse' (> 90°), or 'right' (= 90°). System "
                                    "automatically finds the first vertex with the requested "
                                    "angle type for educational clarity and assessment purposes."
                                )
                            },
                            "color": {
                                "type": "string",
                                "description": (
                                    "Fill and outline color of the shape for visual distinction "
                                    "in angle classification exercises. Enhances recognition "
                                    "and categorization activities for comprehensive "
                                    "geometric instruction."
                                ),
                                "default": "blue"
                            },
                            "label": {
                                "type": "string",
                                "description": (
                                    "Optional educational label for shape identification in "
                                    "angle assessment activities (e.g., 'Figure A', 'Triangle 1'). "
                                    "Auto-generated based on shape name if not provided. "
                                    "Essential for comparative angle analysis."
                                )
                            }
                        },
                        "required": ["shape", "angle_type"]
                    },
                    "minItems": 1,
                    "maxItems": 9
                }
            },
            "required": ["shapes"]
        }
    }
    return spec, generate_coach_bot_shapes_with_angles_image


def generate_coach_bot_shape_with_right_angles_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for shapes with right angles."""
    return create_dynamic_tool_spec(
        name="generate_coach_bot_shape_with_right_angles_image",
        description=(
            "Generate a random shape with a specific number of right angles, "
            "with right angle markers to clearly indicate 90-degree angles. "
            "Perfect educational tool for angle recognition, classification, and "
            "geometric property analysis. Creates comprehensive visualizations for "
            "geometry instruction, spatial reasoning development, and assessment."
        ),
        pydantic_model=ShapeWithRightAngles,
        custom_descriptions={
            "num_right_angles": (
                "Number of right angles the shape should have (0-4). Educational examples:\n"
                "• 0: Circle, equilateral triangle, pentagon, hexagon (no right angles)\n"
                "• 1: Right triangle or right angle kite shape\n"
                "• 2: Pentagon with 2 right angles at base or right trapezoid\n"
                "• 3: File icon shape (triangle + rectangle composite)\n"
                "• 4: Rectangle or square (all corners are right angles)\n"
                "Each shape includes clear right angle markers for educational clarity."
            )
        }
    ), generate_coach_bot_shape_with_right_angles_image
