from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.histogram import (  # noqa: E402
    draw_histogram,
    draw_histogram_pair,
    draw_histogram_with_dotted_bin,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.histograms import (  # noqa: E402
    HistogramBin,
    HistogramDescription,
    HistogramWithDottedBinDescription,
    MultiHistogramDescription,
)

logger = logging.getLogger("coach_bot_tools.histogram_gen")


def generate_coach_bot_histogram_image(
    bins: List[Dict[str, any]],
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: str = "Frequency"
) -> str:
    """
    Generate a single histogram for data visualization.
    
    Creates a histogram with contiguous bins of equal width, useful for displaying
    frequency distributions and teaching statistical concepts.
    
    IMPORTANT: All bins must have identical width calculated as (end - start + 1).
    Valid widths are 5, 10, or 20. Bins must be contiguous with no gaps.
    Example: bins 0-4, 5-9, 10-14 all have width 5 and are contiguous.
    
    Parameters
    ----------
    bins : List[Dict[str, any]]
        List of histogram bins, each containing:
        - start: Starting value of the bin (inclusive)
        - end: Ending value of the bin (inclusive)
        - frequency: Count of occurrences in this bin
        - label: Optional custom label for the bin
    title : Optional[str]
        Title for the histogram
    x_label : Optional[str]
        Label for the x-axis
    y_label : str
        Label for the y-axis (default: "Frequency")
        
    Returns
    -------
    str
        The URL of the generated histogram image
    """
    
    log_tool_generation("generate_coach_bot_histogram_image", bins=bins, title=title,
                        x_label=x_label, y_label=y_label)
    
    # Create HistogramBin objects from the input data
    bin_objects = []
    for bin_data in bins:
        bin_obj = HistogramBin(
            start=bin_data["start"],
            end=bin_data["end"],
            frequency=bin_data["frequency"],
            label=bin_data.get("label")
        )
        bin_objects.append(bin_obj)
    
    # Create and validate the HistogramDescription
    histogram_description = HistogramDescription(
        title=title,
        x_label=x_label,
        y_label=y_label,
        bins=bin_objects
    )
    
    # Generate the image using the histogram function
    image_file_path = draw_histogram(histogram_description)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_histogram_pair_image(
    histograms: List[Dict[str, any]],
    title: Optional[str] = None,
    y_label: str = "Frequency"
) -> str:
    """
    Generate side-by-side histograms for comparison.
    
    Creates two histograms displayed side-by-side for comparing distributions.
    Both histograms must have IDENTICAL bin structure for fair comparison.
    
    IMPORTANT: Both histograms must have the same start/end values for all bins,
    equal widths (5, 10, or 20), and be contiguous with no gaps.
    
    Parameters
    ----------
    histograms : List[Dict[str, any]]
        List of exactly 2 histogram specifications, each containing:
        - title: Title for this histogram
        - x_label: X-axis label for this histogram
        - y_label: Y-axis label for this histogram
        - bins: List of bin objects (same structure as single histogram)
    title : Optional[str]
        Overall title for the comparison
    y_label : str
        Shared y-axis label (default: "Frequency")
        
    Returns
    -------
    str
        The URL of the generated histogram pair image
    """
    
    log_tool_generation("generate_coach_bot_histogram_pair_image", histograms=histograms,
                        title=title, y_label=y_label)
    
    # Create HistogramDescription objects for each histogram
    histogram_objects = []
    for hist_data in histograms:
        bin_objects = []
        for bin_data in hist_data["bins"]:
            bin_obj = HistogramBin(
                start=bin_data["start"],
                end=bin_data["end"],
                frequency=bin_data["frequency"],
                label=bin_data.get("label")
            )
            bin_objects.append(bin_obj)
        
        histogram_obj = HistogramDescription(
            title=hist_data["title"],
            x_label=hist_data.get("x_label"),
            y_label=hist_data.get("y_label", "Frequency"),
            bins=bin_objects
        )
        histogram_objects.append(histogram_obj)
    
    # Create and validate the MultiHistogramDescription with random positioning
    multi_histogram = MultiHistogramDescription.with_random_position(
        title=title,
        y_label=y_label,
        histograms=histogram_objects
    )
    
    # Generate the image using the histogram pair function
    image_file_path = draw_histogram_pair(multi_histogram)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_histogram_with_dotted_bin_image(
    bins: List[Dict[str, any]],
    dotted_bin_index: int,
    raw_data: List[int],
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: str = "Frequency"
) -> str:
    """
    Generate a static histogram image with one bin shown as a dotted outline.
    
    Creates a histogram where one bin is shown as a dotted outline,
    typically used for educational exercises where students need to determine the missing frequency.
    
    IMPORTANT: All bins must have identical width calculated as (end - start + 1).
    Valid widths are 5, 10, or 20. Bins must be contiguous with no gaps.
    
    Parameters
    ----------
    bins : List[Dict[str, any]]
        List of histogram bins (same structure as single histogram)
    dotted_bin_index : int
        Index (0-based) of the bin to show as dotted outline
    raw_data : List[int]
        Raw data points used to validate bin frequencies
    title : Optional[str]
        Title for the histogram
    x_label : Optional[str]
        Label for the x-axis
    y_label : str
        Label for the y-axis (default: "Frequency")
        
    Returns
    -------
    str
        The URL of the generated histogram with dotted bin image
    """
    
    log_tool_generation("generate_coach_bot_histogram_with_dotted_bin_image", 
                       bins=bins, dotted_bin_index=dotted_bin_index, raw_data=raw_data, 
                       title=title, x_label=x_label, y_label=y_label)
    
    # Create HistogramBin objects from the input data
    bin_objects = []
    for bin_data in bins:
        bin_obj = HistogramBin(
            start=bin_data["start"],
            end=bin_data["end"],
            frequency=bin_data["frequency"],
            label=bin_data.get("label")
        )
        bin_objects.append(bin_obj)
    
    # Create and validate the HistogramWithDottedBinDescription
    histogram_description = HistogramWithDottedBinDescription(
        title=title,
        x_label=x_label,
        y_label=y_label,
        bins=bin_objects,
        dotted_bin_index=dotted_bin_index,
        raw_data=raw_data
    )
    
    # Generate the image using the dotted histogram function
    image_file_path = draw_histogram_with_dotted_bin(histogram_description)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_histogram_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for single histogram generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_histogram_image",
        description=(
            "Generate a histogram for statistical data visualization and frequency distribution "
            "analysis. Creates educational histograms with contiguous bins of equal width "
            "(5, 10, or 20 units) for teaching data analysis, statistics, and probability "
            "concepts. Perfect for elementary through high school mathematics education, showing "
            "how data is distributed across different ranges. All bins must be contiguous (no "
            "gaps), have identical width calculated as (end - start + 1), and fall within 0-100 "
            "range. Supports customizable titles and axis labels for various educational contexts "
            "including test scores, survey data, measurement analysis, and statistical "
            "problem-solving exercises."
        ),
        pydantic_model=HistogramDescription,
        custom_descriptions={
            "bins": (
                "List of histogram bins for frequency distribution (5-10 bins recommended). "
                "Each bin contains start (integer 0-100), end (integer 0-100), frequency "
                "(non-negative integer), and optional label (string). CRITICAL EDUCATIONAL "
                "REQUIREMENTS: All bins must have identical width where width = (end - start + 1). "
                "Valid educational widths are 5, 10, or 20 units. Bins must be contiguous with no "
                "gaps for proper statistical representation. Example: test score bins 60-69, "
                "70-79, 80-89, 90-99 all have width 10."
            ),
            "title": (
                "Educational title for the histogram that describes the data being analyzed. "
                "Should be descriptive and appropriate for the target grade level. Examples: "
                "'Test Score Distribution', 'Student Heights', 'Daily Temperature Readings'."
            ),
            "x_label": (
                "Label for the x-axis describing what categories or ranges are being measured. "
                "Should clearly indicate the units and context. Examples: 'Score Range', "
                "'Height (inches)', 'Temperature (°F)', 'Age Groups'."
            ),
            "y_label": (
                "Label for the y-axis indicating what is being counted. Default is 'Frequency' "
                "which counts occurrences. Other examples: 'Number of Students', 'Count', "
                "'Number of Observations' depending on educational context."
            )
        }
    )
    return spec, generate_coach_bot_histogram_image


def generate_coach_bot_histogram_pair_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for histogram pair generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_histogram_pair_image",
        "description": (
            "Generate side-by-side histograms for comparative statistical analysis and data "
            "comparison exercises. Creates two histograms displayed side-by-side to help students "
            "compare different data sets, analyze distributions, and identify patterns or "
            "differences. Perfect for educational scenarios like comparing test scores between "
            "classes, before/after studies, gender comparisons, seasonal data analysis, or any "
            "situation requiring direct comparison of frequency distributions. Both histograms "
            "must have IDENTICAL bin structure (same start/end values, equal widths of 5, 10, or "
            "20 units) for fair and meaningful comparison. Supports educational analysis of "
            "central tendency, spread, shape, and outliers across different datasets."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "histograms": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": (
                                    "Individual title for this histogram in the comparison. Should "
                                    "clearly identify what dataset this represents. Examples: "
                                    "'Class A', 'Before', 'Males', 'Summer', 'Control Group' for "
                                    "meaningful comparison context."
                                )
                            },
                            "x_label": {
                                "type": "string",
                                "description": (
                                    "X-axis label for this specific histogram. Should describe the "
                                    "categories or measurement ranges. Usually identical between "
                                    "both histograms for fair comparison. Examples: 'Test Scores', "
                                    "'Height (cm)', 'Age Range'."
                                )
                            },
                            "y_label": {
                                "type": "string",
                                "description": (
                                    "Y-axis label for this specific histogram indicating what is "
                                    "being counted. Examples: 'Number of Students', 'Frequency', "
                                    "'Count of Responses'."
                                )
                            },
                            "bins": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "start": {
                                            "type": "integer",
                                            "minimum": 0,
                                            "maximum": 100,
                                            "description": (
                                                "Starting value of the bin range (inclusive). MUST "
                                                "be identical across both histograms for "
                                                "meaningful comparison. Educational requirement "
                                                "for valid statistical analysis."
                                            )
                                        },
                                        "end": {
                                            "type": "integer",
                                            "minimum": 0,
                                            "maximum": 100,
                                            "description": (
                                                "Ending value of the bin range (inclusive). MUST "
                                                "be identical across both histograms for fair "
                                                "comparison. Bin width must match between "
                                                "histograms for educational validity."
                                            )
                                        },
                                        "frequency": {
                                            "type": "integer",
                                            "minimum": 0,
                                            "description": (
                                                "Count of data points in this bin for this "
                                                "specific dataset. This is where the histograms "
                                                "will differ, showing the comparison between "
                                                "different groups or conditions being analyzed."
                                            )
                                        },
                                        "label": {
                                            "type": "string",
                                            "description": (
                                                "Optional custom label for this bin range. Should "
                                                "be identical between both histograms if used. "
                                                "Examples: 'A Grade', 'Tall', 'Excellent' for "
                                                "educational category names."
                                            )
                                        }
                                    },
                                    "required": ["start", "end", "frequency"]
                                },
                                "minItems": 5,
                                "maxItems": 10
                            }
                        },
                        "required": ["title", "bins"]
                    },
                    "description": (
                        "Exactly 2 histograms for side-by-side comparison with IDENTICAL bin "
                        "structure. Both histograms must have the same start/end values for all "
                        "bins, equal widths (5, 10, or 20 units), and be contiguous for valid "
                        "educational comparison. Only the frequency values should differ between "
                        "the two datasets being compared."
                    ),
                    "minItems": 2,
                    "maxItems": 2
                },
                "title": {
                    "type": "string",
                    "description": (
                        "Overall title for the histogram comparison that describes what is being "
                        "analyzed. Should indicate the nature of the comparison. Examples: 'Test "
                        "Score Comparison: Class A vs Class B', 'Before vs After Training "
                        "Results', 'Height Distribution by Gender'."
                    )
                },
                "y_label": {
                    "type": "string",
                    "description": (
                        "Shared y-axis label for both histograms indicating what is being counted. "
                        "Should be consistent across both charts for clear comparison. Examples: "
                        "'Number of Students', 'Frequency', 'Count of Observations'."
                    ),
                    "default": "Frequency"
                }
            },
            "required": ["histograms"]
        }
    }
    return spec, generate_coach_bot_histogram_pair_image


def generate_coach_bot_histogram_with_dotted_bin_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for histogram with dotted bin."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_histogram_with_dotted_bin_image",
        description=(
            "Generate a static histogram image with one bin shown as a dotted outline for "
            "educational problem-solving and data analysis exercises. Creates histograms where "
            "one bin is intentionally left incomplete (shown as dotted outline) for students "
            "to calculate the missing frequency based on provided raw data. Perfect for teaching "
            "data interpretation, frequency calculation, statistical reasoning, and critical "
            "thinking skills. Students analyze the raw data to determine how many values "
            "fall within the dotted bin range. Excellent for assessment questions, worksheets, "
            "and educational activities that engage students with statistical concepts. "
            "All bins must have equal width (5, 10, or 20 units) and be contiguous for educational "
            "validity."
        ),
        pydantic_model=HistogramWithDottedBinDescription,
        custom_descriptions={
            "bins": (
                "List of histogram bins for the educational exercise. MANDATORY: Must have exactly "
                "5-10 bins (not 4 or less). Each bin contains start (integer 0-100), end (integer "
                "0-100), frequency (non-negative integer), and optional label (string). CRITICAL "
                "EDUCATIONAL REQUIREMENTS: "
                "1) All bins must have identical width where width = (end - start + 1). Valid "
                "educational widths are 5, 10, or 20 units. "
                "2) Bins must be contiguous with no gaps (next bin start = previous bin end + 1). "
                "3) FREQUENCY VALIDATION: Each bin's frequency must EXACTLY match the count of "
                "raw_data values in that range, "
                "EXCEPT for the dotted bin which can have any frequency since it's shown as "
                "incomplete. "
                "Example: If bin is 70-79 with frequency=8, there must be exactly 8 values in "
                "raw_data between 70-79."
            ),
            "dotted_bin_index": (
                "Index (0-based) of the bin to show as dotted outline for student calculation. "
                "This bin will appear incomplete, requiring students to analyze the raw data "
                "to determine the correct frequency. The frequency for this bin can be any value "
                "since it will be visually incomplete. Choose strategically for educational impact "
                "- middle bins often work well for engaging problem-solving exercises."
            ),
            "raw_data": (
                "Raw data points that students will analyze to calculate the missing frequency. "
                "CRITICAL: Must contain at least 10 values. The frequency of each NON-DOTTED bin "
                "must EXACTLY match the count of raw_data values that fall within that bin's "
                "range. Example: If you have bins 60-69, 70-79, 80-89, 90-99 and "
                "dotted_bin_index=1, then: "
                "- Count values in raw_data from 60-69 must equal frequency for bin 0 "
                "- Count values in raw_data from 80-89 must equal frequency for bin 2 "
                "- Count values in raw_data from 90-99 must equal frequency for bin 3 "
                "- Bin 1 (70-79) is dotted so its frequency can be anything (students calculate it)"
            ),
            "title": (
                "Educational title for the histogram that indicates this is a problem-solving "
                "exercise. Examples: 'Complete the Histogram', 'Find the Missing Frequency', "
                "'Data Analysis Challenge', 'Calculate the Missing Bar'."
            ),
            "x_label": (
                "Label for the x-axis describing what categories or ranges are being measured. "
                "Should guide students in understanding what the data represents. Examples: "
                "'Test Scores', 'Height (cm)', 'Age Groups', 'Daily Sales'."
            ),
            "y_label": (
                "Label for the y-axis indicating what students need to count or calculate. "
                "Should clearly communicate the task. Examples: 'Frequency', 'Number of Students', "
                "'Count of Observations', 'How Many?'."
            )
        }
    )
    return spec, generate_coach_bot_histogram_with_dotted_bin_image
