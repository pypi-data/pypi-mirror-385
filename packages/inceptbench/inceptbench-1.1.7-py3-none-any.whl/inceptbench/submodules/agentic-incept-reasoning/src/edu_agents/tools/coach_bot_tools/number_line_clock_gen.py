from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.number_lines_clock import (  # noqa: E402, E501
    create_clock_number_line,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.number_line_clock_model import (  # noqa: E402, E501
    NumberLineClockStimulus,
    Range,
    TimePoint,
)

logger = logging.getLogger("coach_bot_tools.number_line_clock")


def generate_coach_bot_number_line_clock_image(
    range_min: int,
    range_max: int,
    time_points: List[Dict[str, Any]]
) -> str:
    """
    Generate a number line representing time periods for clock and time-related problems.
    
    Creates a horizontal number line showing hours with time points marked. Useful for teaching
    time concepts, elapsed time calculations, and time intervals. The number line shows hours
    with appropriate tick marks and can display 1-2 specific time points.
    
    Parameters
    ----------
    range_min : int
        The minimum hour value on the number line (1-12)
    range_max : int
        The maximum hour value on the number line (1-12)
        Range span must be less than 5 hours
    time_points : List[Dict[str, Any]]
        List of 1-2 time points to mark on the line, each containing:
        - label: Display label (e.g., "Start", "3:45 PM", "Start: 3:45 PM")
        - hour: Hour value (1-12)
        - minute: Minute value (0-59, must be multiple of 5)
        
    Returns
    -------
    str
        The URL of the generated number line clock image
    """
    
    # Use standardized logging
    log_tool_generation("number_line_clock_image", range_min=range_min, 
                       range_max=range_max, point_count=len(time_points))
    
    # Convert flattened parameters to nested Pydantic model structure
    # Create Range object from flattened range_min/range_max
    hour_range = Range(min=range_min, max=range_max)
    
    # Create TimePoint objects from List[Dict]
    points = []
    for point_data in time_points:
        time_point = TimePoint(
            label=point_data["label"],
            hour=point_data["hour"],
            minute=point_data["minute"]
        )
        points.append(time_point)
    
    # Create and validate the NumberLineClockStimulus using Pydantic
    # This validates all constraints: range (1-12, span < 5), points (1-2), 
    # hour/minute values, spacing
    clock_stimulus = NumberLineClockStimulus(
        range=hour_range,
        points=points
    )
    
    # Generate the image using the clock number line function
    image_file_path = create_clock_number_line(clock_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_number_line_clock_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for number line clock generation."""
    # Note: This uses enhanced static spec due to interface flattening
    # The wrapper handles the parameter transformation from flattened to nested structure
    spec = {
        "type": "function",
        "name": "generate_coach_bot_number_line_clock_image",
        "description": (
            "Generate number line representations for time concepts and clock-related educational "
            "exercises. Creates horizontal number lines showing hours (1-12) with marked time "
            "points for teaching elapsed time calculations, time intervals, and temporal "
            "relationships. Perfect for elementary mathematics education focused on time concepts, "
            "clock reading skills, and time-based problem solving. The number line displays hours "
            "with appropriate tick marks and can highlight 1-2 specific time points with "
            "educational labels."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "range_min": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 12,
                    "description": (
                        "Starting hour value for the number line range (1-12 hour format). "
                        "Represents the leftmost point on the horizontal time line. "
                        "Must be combined with range_max to create a span of less than 5 hours "
                        "for optimal educational visualization and readability."
                    )
                },
                "range_max": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 12,
                    "description": (
                        "Ending hour value for the number line range (1-12 hour format). "
                        "Represents the rightmost point on the horizontal time line. "
                        "Range span (range_max - range_min) must be less than 5 hours "
                        "considering 12-hour wrap-around for educational clarity."
                    )
                },
                "time_points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": (
                                    "Educational display label for the time point (e.g., 'Start "
                                    "Time', '3:45 PM', 'End: 4:30 PM', 'Lunch Break'). Use "
                                    "descriptive labels that help students understand the "
                                    "educational context and purpose of each marked time point on "
                                    "the number line."
                                ),
                                "maxLength": 20
                            },
                            "hour": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 12,
                                "description": (
                                    "Hour component of the time point (1-12 hour format). "
                                    "Must fall within the specified range_min to range_max span "
                                    "for proper visualization on the number line."
                                )
                            },
                            "minute": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 59,
                                "multipleOf": 5,
                                "description": (
                                    "Minute component of the time point (0-59). Must be a multiple "
                                    "of 5 (e.g., 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55) "
                                    "for clear educational representation and easier student "
                                    "comprehension of time intervals."
                                )
                            }
                        },
                        "required": ["label", "hour", "minute"]
                    },
                    "description": (
                        "List of 1-2 specific time points to mark and highlight on the number "
                        "line. Each point represents an important moment in time-based educational "
                        "scenarios (e.g., start/end times, event markers, calculation reference "
                        "points). When providing 2 points, they must be at least 30 minutes apart "
                        "for clear visual distinction and meaningful educational comparison."
                    ),
                    "minItems": 1,
                    "maxItems": 2
                }
            },
            "required": ["range_min", "range_max", "time_points"]
        }
    }
    return spec, generate_coach_bot_number_line_clock_image
