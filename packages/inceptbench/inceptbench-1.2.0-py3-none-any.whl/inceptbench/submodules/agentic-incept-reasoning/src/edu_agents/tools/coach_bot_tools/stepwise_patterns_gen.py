from __future__ import annotations

import logging
from typing import Callable, Dict, List

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.stepwise_dot_pattern import (  # noqa: E402, E501
    draw_stepwise_shape_pattern,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.stepwise_dot_pattern import (  # noqa: E402, E501
    StepwiseShapePattern,
    StepwiseShapePatternStep,
)

logger = logging.getLogger("coach_bot_tools.stepwise_patterns")


def generate_coach_bot_stepwise_pattern_image(
    steps: List[Dict[str, any]],
    shape_size: float = 1.0,
    spacing: float = 0.5
) -> str:
    """
    Generate stepwise shape pattern diagrams for sequence and pattern recognition.
    
    Creates visual patterns showing step-by-step progression of shapes arranged in 
    rows and columns. Useful for teaching mathematical patterns, sequences, algebraic 
    thinking, and visual pattern recognition. Supports circles, squares, and triangles
    with customizable colors and arrangements.
    
    Parameters
    ----------
    steps : List[Dict[str, any]]
        List of step specifications, each containing:
        - rows: Number of rows of shapes (1-10)
        - columns: Number of columns of shapes (1-10)  
        - shape: Shape type - 'circle', 'square', or 'triangle'
        - color: Color of shapes (hex code like '#e78be7' or named color)
        - rotation: Rotation in degrees (only for triangles, optional)
        - label: Optional label for the step (required if more than 3 steps total)
    shape_size : float
        Relative size of the shapes (0.5-2.0, default 1.0)
    spacing : float  
        Horizontal spacing between steps (0.1-1.0, default 0.5)
        
    Returns
    -------
    str
        The URL of the generated stepwise pattern image
    """
    
    # Use standardized logging
    log_tool_generation("stepwise_pattern_image", step_count=len(steps),
                       shape_size=shape_size, spacing=spacing)
    
    # Convert List[Dict] to List[StepwiseShapePatternStep] for Pydantic model
    # This handles interface flattening: simple Dict → complex StepwiseShapePatternStep objects
    step_objects = []
    for step_data in steps:
        # Create StepwiseShapePatternStep Pydantic objects with automatic defaults
        # Pydantic handles all field validation and type conversion
        step_obj = StepwiseShapePatternStep(
            rows=step_data['rows'],
            columns=step_data['columns'],
            shape=step_data['shape'],
            color=step_data.get('color', '#e78be7'),
            rotation=step_data.get('rotation', 0.0),
            label=step_data.get('label')
        )
        step_objects.append(step_obj)
    
    # Create and validate the StepwiseShapePattern using Pydantic
    # This handles all validation: step count (1-9), shape_size (0.5-2.0), 
    # spacing (0.1-1.0), label requirements (>3 steps), and shape enum validation
    pattern_stimulus = StepwiseShapePattern(
        steps=step_objects,
        shape_size=shape_size,
        spacing=spacing
    )
    
    # Generate the image using the stepwise pattern function
    image_file_path = draw_stepwise_shape_pattern(pattern_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_stepwise_pattern_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for stepwise pattern generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_stepwise_pattern_image",
        description=(
            "Generate stepwise shape pattern visualizations for mathematics education "
            "focused on pattern recognition, sequence analysis, and algebraic thinking "
            "development. Creates step-by-step visual progressions of geometric shapes "
            "arranged in structured rows and columns for teaching mathematical patterns, "
            "sequential reasoning, and visual-spatial relationships. Supports circles, "
            "squares, and triangles with customizable colors, sizes, and arrangements "
            "for comprehensive pattern education. Perfect for elementary and middle "
            "school mathematics lessons covering number patterns, geometric sequences, "
            "algebraic thinking, and problem-solving strategies. Displays 1-9 steps "
            "in organized layouts with optional labeling for complex multi-step "
            "patterns. Excellent for worksheets, assessments, interactive learning "
            "activities, and mathematical reasoning exercises that develop students' "
            "ability to identify, extend, and analyze visual patterns through "
            "systematic observation and logical thinking skills."
        ),
        pydantic_model=StepwiseShapePattern,
        custom_descriptions={
            "steps": (
                "Comprehensive list of pattern step specifications for mathematical "
                "sequence visualization and educational pattern analysis (1-9 steps "
                "maximum for optimal learning clarity). Each step represents one "
                "stage in the mathematical progression, demonstrating relationships "
                "between consecutive terms or visual elements. CRITICAL EDUCATIONAL "
                "REQUIREMENT: When pattern contains more than 3 steps, ALL steps "
                "must include labels for proper visual organization and student "
                "comprehension. Each step contains: rows (1-10 shape rows for pattern "
                "complexity), columns (1-10 shape columns for width relationships), "
                "shape ('circle' for smooth patterns, 'square' for grid-based thinking, "
                "'triangle' for angular distinctive forms), color (hex codes like "
                "'#e78be7' or named colors for visual distinction), rotation (degrees "
                "for triangles only, enables transformation sequences), and optional "
                "label (required for >3 steps, use 'Step 1', 'Term n', mathematical "
                "notation). Strategic step progression creates learning opportunities "
                "for pattern recognition, algebraic thinking, and mathematical reasoning."
            ),
            "shape_size": (
                "Relative size of shapes for optimal educational visualization (0.5-2.0 "
                "scale, default 1.0). Shape size affects visual clarity, pattern "
                "recognition, and student engagement with mathematical concepts. "
                "Smaller values (0.5-0.8) work well for complex multi-step patterns "
                "with many shapes. Larger values (1.2-2.0) enhance visibility for "
                "simple patterns and younger students. Strategic sizing improves "
                "pattern comprehension and mathematical reasoning accessibility."
            ),
            "spacing": (
                "Horizontal spacing between pattern steps for optimal educational "
                "visualization (0.1-1.0 scale, default 0.5). Spacing affects "
                "visual organization, pattern clarity, and mathematical progression "
                "comprehension. Tighter spacing (0.1-0.3) emphasizes sequence "
                "continuity and pattern flow. Wider spacing (0.6-1.0) provides "
                "clear step distinction and individual analysis opportunities. "
                "Strategic spacing enhances pattern recognition and supports "
                "diverse learning preferences for mathematical sequence analysis."
            )
        }
    )
    return spec, generate_coach_bot_stepwise_pattern_image
