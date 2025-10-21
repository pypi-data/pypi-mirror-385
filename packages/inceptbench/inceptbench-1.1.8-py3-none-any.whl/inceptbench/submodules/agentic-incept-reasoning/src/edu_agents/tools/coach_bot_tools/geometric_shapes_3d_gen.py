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
setup_coach_bot_imports()  # noqa: E402, I001

# Import drawing functions  # noqa: E402, I001
from content_generators.additional_content.stimulus_image.drawing_functions.geometric_shapes_3d import (  # noqa
    draw_cross_section_question,
    draw_multiple_3d_objects,
    draw_right_prisms,
)

# Import Pydantic models  # noqa: E402, I001
from content_generators.additional_content.stimulus_image.stimulus_descriptions.right_prisms import (  # noqa
    RightPrismsList,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.three_dimensional_objects import (  # noqa
    CrossSectionQuestion,
    ThreeDimensionalObjectsList,
)

logger = logging.getLogger("coach_bot_tools.geometric_shapes_3d")


def generate_coach_bot_3d_objects_image(
    shapes: List[Dict],
    units: str = "units"
) -> str:
    """
    Generate comprehensive 3D geometric objects visualization with dimensional labels.
    
    Creates educational grid layout of 3D shapes including spheres, pyramids, cubes,
    rectangular prisms, cones, and cylinders with accurate dimensional measurements.
    Essential for spatial reasoning instruction, geometric visualization education,
    and 3D shape identification. Supports mathematics curricula for geometry
    concepts, volume calculations, and solid figure recognition.
    
    EDUCATIONAL APPLICATIONS:
    - 3D shape identification and classification
    - Spatial reasoning and visualization skills  
    - Geometric property analysis and comparison
    - Volume and surface area concept development
    - Mathematical modeling with dimensional constraints
    - STEM education for engineering and architecture concepts
    
    Args:
        shapes: List of 3D shape dictionaries with 'shape', 'label' and dimension keys
        units: Unit of measurement for dimensions (e.g., 'cm', 'm', 'units')
        
    Returns:
        str: URL to the uploaded 3D objects visualization image
    """
    log_tool_generation("generate_coach_bot_3d_objects_image", shapes=shapes, units=units)
    
    # Create ThreeDimensionalObjectsList with automatic Pydantic validation
    objects_list = ThreeDimensionalObjectsList(shapes=shapes, units=units)
    image_file_path = draw_multiple_3d_objects(objects_list)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_cross_section_image(
    shape: Dict,
    correct_cross_section: str,
    correct_letter: str
) -> str:
    """
    Generate comprehensive 3D cross-section analysis with educational multiple choice assessment.
    
    Creates sophisticated geometry visualization showing a 3D shape intersected by a cutting
    plane with multiple choice options for the resulting 2D cross-section. Essential for
    advanced spatial reasoning instruction, geometric analysis education, and critical
    thinking development. Supports advanced mathematics curricula for spatial geometry,
    cross-sectional analysis, and geometric reasoning assessment.
    
    EDUCATIONAL APPLICATIONS:
    - Advanced spatial reasoning and 3D visualization skills
    - Cross-sectional geometry analysis and interpretation  
    - Geometric reasoning assessment and evaluation
    - Solid geometry concepts and plane intersection theory
    - Mathematical problem solving and critical thinking
    - Engineering and architectural spatial analysis preparation
    - Advanced mathematics assessment and standardized test preparation
    
    Args:
        shape: Dictionary describing the 3D shape with dimensions and properties
        correct_cross_section: The correct 2D cross-section shape result
        correct_letter: Letter (a, b, c, d) indicating correct answer position
        
    Returns:
        str: URL to the uploaded cross-section question visualization
    """
    log_tool_generation("generate_coach_bot_cross_section_image", 
                       shape=shape, 
                       correct_cross_section=correct_cross_section, 
                       correct_letter=correct_letter)
    
    # Create CrossSectionQuestion with automatic Pydantic validation
    question = CrossSectionQuestion(
        shape=shape,
        correct_cross_section=correct_cross_section,
        correct_letter=correct_letter
    )
    image_file_path = draw_cross_section_question(question)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_right_prisms_image(
    prisms: List[Dict],
    units: str = "units",
    show_height: bool = True,
    show_base_area: bool = True
) -> str:
    """
    Generate comprehensive right prisms visualization with diverse polygonal base shapes.
    
    Creates advanced geometric visualization of right prisms including triangular, 
    rectangular, pentagonal, hexagonal, octagonal, trapezoidal, and irregular bases.
    Essential for advanced geometry instruction, volume calculation education, and
    3D geometric analysis. Supports mathematics curricula for solid geometry concepts,
    surface area calculations, and architectural design principles.
    
    EDUCATIONAL APPLICATIONS:
    - Advanced 3D geometric shape analysis and classification
    - Volume and surface area calculation instruction
    - Polygonal base shape recognition and properties
    - Architectural and engineering design concepts
    - Mathematical modeling with complex geometric constraints
    - STEM education for construction and design principles
    - Advanced spatial reasoning and geometric visualization
    
    CRITICAL VALIDATION CONSTRAINTS:
    - Regular polygonal prisms (octagonal/hexagonal/pentagonal): side_length 2-8
                - Cube: side_length 3-10 OR base_area 9-100 (not both)
                - Rectangular: width+length 2-8 OR base_area 4-64 (not both)
                - Triangular: side_a, side_b, side_c 1-40
                - Trapezoidal: top_base, bottom_base, trapezoid_height 2-8
    
    Args:
        prisms: List of prism dictionaries with type-specific dimensional parameters
        units: Unit of measurement for dimensions (e.g., 'cm', 'm', 'units')
        show_height: Whether to display height dimensional labels
        show_base_area: Whether to display base area calculation labels
        
    Returns:
        str: URL to the uploaded right prisms visualization
    """
    log_tool_generation("generate_coach_bot_right_prisms_image", 
                       prisms=prisms, 
                       units=units, 
                       show_height=show_height, 
                       show_base_area=show_base_area)
    
    # Create RightPrismsList with automatic Pydantic validation
    prisms_list = RightPrismsList(
        prisms=prisms,
        units=units,
        show_height=show_height,
        show_base_area=show_base_area
    )
    image_file_path = draw_right_prisms(prisms_list)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_3d_objects_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for 3D objects."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_3d_objects_image",
        description=(
            "Generate comprehensive 3D geometric objects visualization with dimensional "
            "accuracy for advanced spatial reasoning education. Creates educational grid "
            "layout of diverse 3D shapes including spheres, pyramids, cubes, rectangular "
            "prisms, cones, and cylinders with precise dimensional measurements. Essential "
            "for geometry instruction, mathematical visualization, spatial reasoning "
            "development, and STEM education applications."
        ),
        pydantic_model=ThreeDimensionalObjectsList,
        custom_descriptions={
            "shapes": (
                "List of 3D geometric shapes for comprehensive spatial visualization. "
                "🚨 CRITICAL FIELD REQUIREMENTS: Each shape dictionary MUST include:\n"
                "• 'shape': EXACT literal value (see below)\n"
                "• 'label': Text label for educational identification (e.g., 'Ball', 'Dice')\n"
                "• Dimensional parameters: specific to each shape type\n\n"
                "📋 EXACT SHAPE VALUES & REQUIRED PARAMETERS:\n"
                "• Sphere: {'shape': 'sphere', 'label': 'Ball', 'radius': 4} "
                "⚠️ radius: 3-10\n"
                "• Cube: {'shape': 'cube', 'label': 'Dice', 'height': 5, 'width': 5, "
                "'length': 5} ⚠️ all dimensions: 3-10\n"
                "• Rectangular Prism: {'shape': 'rectangular prism', 'label': 'Box', "
                "'width': 6, 'length': 8, 'height': 4} ⚠️ width/length/height: 3-10\n"
                "• Pyramid: {'shape': 'pyramid', 'label': 'Pyramid', 'side': 5, "
                "'height': 7} ⚠️ side/height: 3-10\n"
                "• Cone: {'shape': 'cone', 'label': 'Cone', 'radius': 3, 'height': 6} "
                "⚠️ radius/height: 3-10\n"
                "• Cylinder: {'shape': 'cylinder', 'label': 'Can', 'radius': 4, "
                "'height': 8} ⚠️ radius/height: 3-10\n\n"
                "🚨 CRITICAL CONSTRAINTS: ALL dimensions MUST be 3-10 (inclusive). "
                "Examples: radius=2❌, radius=3✅, length=12❌, length=10✅. "
                "Use 'label' not 'title'."
            ),
            "units": (
                "Unit of measurement for all dimensional labels and calculations "
                "(e.g., 'cm', 'm', 'inches', 'feet', 'units'). Enhances mathematical "
                "accuracy and real-world application understanding for measurement "
                "concepts and dimensional analysis instruction."
            )
        }
    )
    return spec, generate_coach_bot_3d_objects_image


def generate_coach_bot_cross_section_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for cross-section questions."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_cross_section_image",
        description=(
            "Generate advanced 3D cross-sectional analysis with educational multiple choice "
            "assessment for sophisticated geometry instruction. Creates comprehensive "
            "visualization showing a 3D shape intersected by cutting plane with multiple "
            "choice options for the resulting 2D cross-section. Essential for advanced "
            "spatial reasoning education, geometric analysis assessment, critical thinking "
            "development, and standardized test preparation."
        ),
        pydantic_model=CrossSectionQuestion,
        custom_descriptions={
            "shape": (
                "🚨 MUST BE COMPLETE DICTIONARY (not string) with ALL required fields! "
                "3D geometric shape dictionary for cross-sectional analysis.\n\n"
                "❌ WRONG: 'cone' (string)\n"
                "❌ WRONG: {'shape': 'cone', 'radius': 4, 'height': 8} (missing label)\n"
                "✅ CORRECT: {'shape': 'cone', 'radius': 4, 'height': 8, "
                "'label': 'Traffic Cone'}\n\n"
                "🚨 CRITICAL REQUIREMENTS: Dictionary MUST include:\n"
                "• 'shape': EXACT literal value (e.g., 'sphere', 'cube', "
                "'rectangular prism', 'pyramid', 'cone', 'cylinder')\n"
                "• 'label': Text label for educational context (e.g., 'Ball', 'Dice', 'Box')\n"
                "• Dimensional parameters: shape-specific (radius, height, width, length, side)\n\n"
                "📋 COMPLETE VALID EXAMPLES:\n"
                "• {'shape': 'sphere', 'label': 'Ball', 'radius': 5} ⚠️ radius: 3-10\n"
                "• {'shape': 'cube', 'label': 'Dice', 'height': 6, 'width': 6, "
                "'length': 6} ⚠️ all dimensions: 3-10\n"
                "• {'shape': 'cone', 'label': 'Traffic Cone', 'radius': 4, 'height': 8}\n"
                "• {'shape': 'rectangular prism', 'label': 'Box', "
                "'width': 4, 'length': 7, 'height': 5} ⚠️ width/length/height: 3-10\n"
                "🚨 CRITICAL: ALL dimensions MUST be 3-10 range. "
                "NO exceptions (radius=2❌, length=12❌). Use 'label' not 'title'."
            ),
            "correct_cross_section": (
                "The mathematically correct 2D cross-section shape resulting from the "
                "plane intersection: 'circle' (spheres/cylinders/cones), 'triangle' (pyramids), "
                "'rectangle' (rectangular prisms), 'square' (cubes). Critical for developing "
                "advanced spatial reasoning and geometric analysis skills."
            ),
            "correct_letter": (
                "Assessment answer key position (a, b, c, d) indicating which multiple "
                "choice option is correct. Essential for educational assessment creation, "
                "standardized test preparation, and systematic evaluation of student "
                "understanding in advanced 3D geometry concepts."
            )
        }
    )
    return spec, generate_coach_bot_cross_section_image


def generate_coach_bot_right_prisms_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for right prisms."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_right_prisms_image",
        description=(
            "Generate comprehensive right prisms visualization with diverse polygonal "
            "base shapes for advanced geometry instruction. Creates sophisticated "
            "educational visualization of triangular, rectangular, pentagonal, hexagonal, "
            "octagonal, trapezoidal, and irregular right prisms with precise dimensional "
            "constraints and validation. Essential for advanced 3D geometry education, "
            "volume calculation instruction, architectural design concepts, and STEM "
            "engineering applications."
        ),
        pydantic_model=RightPrismsList,
        custom_descriptions={
            "prisms": (
                "List of advanced right prism dictionaries with diverse polygonal bases. "
                "🚨 CRITICAL FIELD REQUIREMENTS: Each prism dictionary MUST include:\n"
                "• 'shape': EXACT enum value (see below)\n"
                "• 'height': Prism height (1-40 range)\n"
                "• 'label': Educational label for identification\n"
                "• Type-specific dimensional parameters\n\n"
                "📋 EXACT SHAPE VALUES & REQUIRED PARAMETERS:\n"
                "• Cube: {'shape': 'cube', 'height': 8, 'side_length': 6, "
                "'label': 'Cube Prism'} ⚠️ height: 1-40, side_length: 3-10\n"
                "• Octagonal: {'shape': 'octagonal prism', 'height': 12, "
                "'side_length': 4, 'label': 'Octagon'} ⚠️ height: 1-40, side_length: 2-8\n"
                "• Pentagonal: {'shape': 'pentagonal prism', 'height': 15, "
                "'side_length': 7, 'label': 'Pentagon'} ⚠️ height: 1-40, side_length: 2-8\n"
                "• Hexagonal: {'shape': 'hexagonal prism', 'height': 10, "
                "'side_length': 5, 'label': 'Hexagon'} ⚠️ height: 1-40, side_length: 2-8\n"
                "• Triangular: {'shape': 'triangular prism', 'height': 8, "
                "'side_a': 3, 'side_b': 4, 'side_c': 5, 'label': 'Triangle'} "
                "⚠️ height: 1-40, sides: 1-40\n"
                "• Rectangular: {'shape': 'rectangular prism', 'height': 6, "
                "'width': 4, 'length': 7, 'label': 'Rectangle'} "
                "⚠️ height: 1-40, width/length: 2-8\n"
                "• Trapezoidal: {'shape': 'trapezoidal prism', 'height': 9, "
                "'top_base': 3, 'bottom_base': 7, 'trapezoid_height': 4, 'label': 'Trapezoid'} "
                "⚠️ height: 1-40, bases/trapezoid_height: 2-8\n\n"
                "🚨 CRITICAL: Different constraints per type! Use 'shape' not 'prism_type'."
            ),
            "units": (
                "Unit of measurement for all dimensional labels (e.g., 'cm', 'm', 'inches'). "
                "Enhances mathematical precision and real-world application understanding "
                "for engineering and architectural measurement concepts."
            ),
            "show_height": (
                "Whether to display height dimensional labels on each prism. Critical for "
                "volume calculation instruction and dimensional analysis education."
            ),
            "show_base_area": (
                "Whether to display base area calculation labels when appropriate. "
                "Essential for surface area instruction and geometric property analysis."
            )
        }
    )
    return spec, generate_coach_bot_right_prisms_image
