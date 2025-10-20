import io
import logging
from typing import Any, Callable, Dict, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from utils.supabase_utils import upload_image_to_supabase

from .chart_utils import (
    auto_detect_denominator,
    calculate_adaptive_font_size,
    decimal_to_fraction_string,
    should_rotate_x_labels,
)
from .color_utils import validate_color_list

# Set matplotlib to use a non-interactive backend
matplotlib.use('Agg')

# Configure matplotlib to prevent memory leaks and limit figure accumulation
matplotlib.rcParams['figure.max_open_warning'] = 5  # Warn much earlier
matplotlib.rcParams['figure.raise_window'] = False   # Don't raise GUI windows

logger = logging.getLogger(__name__)


def plot_bar(
    series: list,
    *,
    width: float = 0.8,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    xlim: Optional[Dict[str, float]] = None,
    ylim: Optional[Dict[str, float]] = None,
    legend: bool = True,
    xtick_rotation: float = 0,
    x_axis_show_fractions: bool = False,
    x_axis_fraction_denominator: Optional[int] = None,
    y_axis_interval: Optional[float] = None,
    y_axis_show_fractions: bool = False,
    y_axis_fraction_denominator: Optional[int] = None,
    background_color: str = 'transparent'
) -> str:
    """
    Draw one or more bar series on the same axes.

    Parameters
    ----------
    series : list
        List of series dictionaries. Each series must have:
          - 'categories': list of category names
          - 'values': list of heights for each category
          - 'label': string name for the series (shown in legend)
          - 'color': string color for bars (e.g. 'red', 'blue', '#FF5733')
    width : float
        Total width allocated per category for each series (bars get split if multiple series).
    title : str
        Plot title.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis.
    xlim : dict
        X-axis limits as dict with 'min' and 'max' keys (e.g. {'min': 0, 'max': 10}).
    ylim : dict
        Y-axis limits as dict with 'min' and 'max' keys (e.g. {'min': 0, 'max': 100}).
    legend : bool
        Whether to show a legend (only needed if more than one series).
    xtick_rotation : float
        Rotation (in degrees) of the category labels on the x-axis.
    x_axis_show_fractions : bool
        Whether to convert numeric x-axis categories to fraction labels (e.g. 3.25 -> 3¼).
    x_axis_fraction_denominator : int
        Denominator to use for x-axis fractions (e.g. 4 for quarters: 1/4, 1/2, 3/4).
    y_axis_interval : float
        Interval for y-axis ticks and gridlines (e.g. 10 for ticks at 0, 10, 20, 30...).
    y_axis_show_fractions : bool
        Whether to display y-axis tick labels as fractions instead of decimals.
    y_axis_fraction_denominator : int
        Denominator to use for y-axis fractions (e.g. 4 for quarters: 1/4, 1/2, 3/4).
    background_color : str, default 'white'
        The background color behind the chart. Use 'transparent' for transparent background,
        or any valid matplotlib color name or hex code.
        
    Returns
    -------
    str
        URL of the generated image
    """
    try:
        # Thread-safe figure creation - each thread gets its own figure
        # Don't use plt.close('all') as it affects other threads
        
        # series is now already a list of dicts, no need to parse JSON
        series_data = series
        print("Bar chart parameters:")
        print(f"Series data: {series_data}")
        print(f"Width: {width}")
        print(f"Title: {title}")
        print(f"Xlabel: {xlabel}")
        print(f"Ylabel: {ylabel}")
        print(f"Xlim: {xlim}")
        print(f"Ylim: {ylim}")
        print(f"Legend: {legend}")
        print(f"Xtick rotation: {xtick_rotation}")
        print(f"X-axis show fractions: {x_axis_show_fractions}")
        print(f"X-axis fraction denominator: {x_axis_fraction_denominator}")
        print(f"Y-axis interval: {y_axis_interval}")
        print(f"Y-axis show fractions: {y_axis_show_fractions}")
        print(f"Y-axis fraction denominator: {y_axis_fraction_denominator}")
        print(f"Background color: {background_color}")
        
        # Create figure with white background for the chart
        fig = plt.figure(figsize=(8, 6), facecolor='white')
        ax = fig.add_subplot(111, facecolor='white')
        
        # Create a white background patch that covers the entire chart area
        fig.patch.set_facecolor('white')
        
        # Enable LaTeX rendering for mathematical notation
        plt.rcParams['text.usetex'] = False  # Use matplotlib's built-in math renderer
        plt.rcParams['mathtext.default'] = 'regular'  # Use regular font for math
        
        n_series = len(series_data)
        categories = series_data[0]['categories']
        
        # Determine if categories are numeric for positioning
        numeric_categories = []
        are_numeric = True
        for cat in categories:
            try:
                numeric_categories.append(float(cat))
            except (ValueError, TypeError):
                are_numeric = False
                break
        
        # Set up positioning - use actual values for numeric categories, indices for strings
        if are_numeric:
            # For numeric categories, position bars at their actual values
            positions = np.array(numeric_categories)
            # Calculate appropriate bar width based on minimum spacing
            min_spacing = min(np.diff(sorted(positions))) if len(positions) > 1 else 1.0
            bar_width = min(width * min_spacing * 0.8, min_spacing * 0.8) / n_series
        else:
            # For string categories, use integer indices
            positions = np.arange(len(categories))
            bar_width = width / n_series
        
        # Convert categories to fraction labels if requested
        display_categories = categories.copy()
        if x_axis_show_fractions and are_numeric:
            fraction_categories = []
            all_denominators_detected = True
            
            for cat_value in numeric_categories:
                # Auto-detect denominator if not provided
                denominator = x_axis_fraction_denominator
                if denominator is None:
                    # Use the chart_utils function to auto-detect denominator
                    denominator = auto_detect_denominator(cat_value)
                    if denominator is None:
                        all_denominators_detected = False
                        break
                
                # Only simplify if denominator was auto-detected
                simplify_fractions = (x_axis_fraction_denominator is None)
                fraction_label = decimal_to_fraction_string(cat_value, denominator,
                                 simplify_fractions, use_latex=True)
                fraction_categories.append(fraction_label)
            
            if all_denominators_detected:
                display_categories = fraction_categories
            else:
                print("Warning: Could not auto-detect denominators for some x-axis categories " + \
                      f"{numeric_categories}. Using decimal labels.")
                # Keep original string categories as decimal labels
                display_categories = [str(cat) for cat in categories]

        # Plot each series
        for i, s in enumerate(series_data):
            # Validate and normalize color
            validated_color = validate_color_list(s['color'], default=f'C{i}')
            
            # Calculate bar positions for this series
            if n_series > 1:
                # Multiple series: offset bars within each group
                series_positions = positions + (i - (n_series - 1) / 2) * bar_width
            else:
                # Single series: center bars at positions
                series_positions = positions
            
            ax.bar(
                series_positions,
                s['values'],
                bar_width,
                label=s['label'],
                color=validated_color,
                edgecolor='black',
                linewidth=1
            )

        # Set x-axis ticks and labels
        ax.set_xticks(positions)
        ax.set_xticklabels(display_categories, rotation=xtick_rotation)
        
        # Apply adaptive font sizing for x-axis labels if many categories
        x_ticks = len(display_categories)
        should_rotate_x = should_rotate_x_labels(x_ticks, is_fractions=x_axis_show_fractions)
        x_font_size = calculate_adaptive_font_size(x_ticks,
                        use_rotation=(xtick_rotation != 0 or should_rotate_x))
        ax.tick_params(axis='x', labelsize=x_font_size)
        
        # Auto-rotate x-axis labels if needed and not manually specified
        if xtick_rotation == 0 and should_rotate_x:
            ax.tick_params(axis='x', rotation=45)
        
        # Apply adaptive font sizing for y-axis if not using fractions
        if not y_axis_show_fractions:
            y_ticks = len(ax.get_yticks())
            y_font_size = calculate_adaptive_font_size(y_ticks)
            ax.tick_params(axis='y', labelsize=y_font_size)
        
        # Set labels and title
        if title:
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=18)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=18)
        
        # Set x-axis limits if provided
        if xlim:
            ax.set_xlim(xlim['min'], xlim['max'])
        
        # Set y-axis limits if provided
        if ylim:
            ax.set_ylim(ylim['min'], ylim['max'])
        
        # Set y-axis interval if provided
        if y_axis_interval is not None:
            # Get current y-axis limits
            ymin, ymax = ax.get_ylim()
            
            # Create ticks at the specified interval
            # Start from the first multiple of interval >= ymin
            start_tick = np.ceil(ymin / y_axis_interval) * y_axis_interval
            # End at the last multiple of interval <= ymax
            end_tick = np.floor(ymax / y_axis_interval) * y_axis_interval
            
            # Generate tick positions
            yticks = np.arange(start_tick, end_tick + y_axis_interval, y_axis_interval)
            ax.set_yticks(yticks)
            
            # Set fraction labels if requested
            if y_axis_show_fractions:
                # Auto-detect denominator if not provided
                denominator = y_axis_fraction_denominator
                if denominator is None:
                    denominator = auto_detect_denominator(y_axis_interval)
                
                if denominator is not None:
                    # Only simplify if denominator was auto-detected
                    simplify_fractions = (y_axis_fraction_denominator is None)
                    fraction_labels = [decimal_to_fraction_string(tick, denominator,
                                       simplify_fractions, use_latex=True) for tick in yticks]
                    ax.set_yticklabels(fraction_labels)
                    
                    # Apply adaptive font sizing for y-axis
                    y_font_size = calculate_adaptive_font_size(len(yticks))
                    ax.tick_params(axis='y', labelsize=y_font_size)
                else:
                    print("Warning: Could not auto-detect denominator for y_axis_interval " + \
                          f"{y_axis_interval}. Using decimal labels.")
        
        # Add legend if requested and there are multiple series
        if legend and n_series > 1:
            legend = ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center',
                        ncol=min(n_series, 4))
            # Set white background for legend
            if legend:
                legend.get_frame().set_facecolor('white')
                legend.get_frame().set_alpha(1.0)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3, axis='y')
        
        # Ensure all spines are visible against any background
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('black')
        
        # Adjust layout to accommodate legend
        plt.tight_layout()
        if legend and n_series > 1:
            plt.subplots_adjust(bottom=0.2)  # Add extra space at bottom for legend
        
        # Create a new figure with the specified background color for padding
        inner_pad_inches = 0.15  # White padding around the chart
        outer_pad_inches = 0.25  # Colored padding around the white padding
        
        # Save with white background and inner padding
        buf_white = io.BytesIO()
        fig.savefig(buf_white, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none',
                   pad_inches=inner_pad_inches)
        
        # Create new figure with specified background
        fig_with_bg = plt.figure(figsize=(8, 6))
        if background_color == 'transparent':
            fig_with_bg.patch.set_alpha(0)
        else:
            fig_with_bg.patch.set_facecolor(background_color)
        
        # Display the white-background image on this figure
        buf_white.seek(0)
        img = Image.open(buf_white)
        # Convert PIL Image to numpy array for matplotlib
        img_array = np.array(img)
        plt.imshow(img_array)
        plt.axis('off')
        
        # Save final version with outer padding
        buf_final = io.BytesIO()
        fig_with_bg.savefig(buf_final, format='png', dpi=300, bbox_inches='tight',
                   transparent=(background_color == 'transparent'),
                   pad_inches=outer_pad_inches)
        buf_final.seek(0)
        
        # Clean up the first buffer
        buf_white.close()
        
        # Upload to Supabase
        public_url = upload_image_to_supabase(
            image_bytes=buf_final.getvalue(),
            content_type="image/png",
            bucket_name="incept-images",
            file_extension=".png"
        )
        
        # Thread-safe cleanup - close specific figures only
        plt.close(fig)
        plt.close(fig_with_bg)
        buf_final.close()
        
        return public_url
        
    except Exception as e:
        error_message = f"Error generating bar chart: {str(e)}"
        logger.error(error_message)
        # Ensure cleanup on error - close any figures we may have created
        try:
            if 'fig' in locals():
                plt.close(fig)
        except Exception:
            pass
        try:
            if 'fig_with_bg' in locals():
                plt.close(fig_with_bg)
        except Exception:
            pass
        raise RuntimeError(error_message) from e


def generate_simple_bar_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the simple bar chart tool specification and function."""
    
    spec = {
        "type": "function",
        "name": "plot_bar",
        "description": "Create a bar chart to compare values across different categories. Each bar "
                       "represents one category's value.\n\nCRITICAL REQUIREMENTS:\n- All series "
                       "must have the same length for 'categories' and 'values' arrays\n- Values "
                       "must be numeric (not strings or null)\n- Each series must have at least "
                       "one data point\n- Categories and values arrays cannot be empty\n- All "
                       "series should have the same categories in the same order for proper "
                       "comparison\n- Colors must be valid matplotlib colors: use 'red', 'blue', "
                       "'green', 'lightcoral' (NOT 'lightred'), or hex codes like '#FF0000'",
        "parameters": {
            "type": "object",
            "properties": {
                "series": {
                    "type": "array",
                    "description": "List of data series to plot as bars",
                    "items": {
                        "type": "object",
                        "properties": {
                            "categories": {
                                "type": "array",
                                "items": {"type": ["string", "number"]},
                                "description": "List of category names for the x-axis. MUST have "
                                               "same length as 'values' array. Cannot be empty. "
                                               "Can be strings (e.g. ['A', 'B', 'C']) or numbers/"
                                               "numeric strings (e.g. [3.0, 3.25, 3.5] or ['3.0', "
                                               "'3.25', '3.5']). If numeric and "
                                               "x_axis_show_fractions=true, will be converted to "
                                               "numerical fraction labels. Use numeric values with "
                                               "x_axis_show_fractions=true whenever creating a "
                                               "plot for content that uses fractions rather than "
                                               "decimals (rather than using strings containing "
                                               "fractions). If the x-axis categories represent "
                                               "numerical quantities (even when those quantities "
                                               "include a unit), supply them as numbers (e.g., 2, "
                                               "2.5, 3, 3.5) and set x_axis_show_fractions to "
                                               "true. Put the unit in xlabel rather than inside "
                                               "each category label. Reserve string categories for "
                                               "labels that are genuinely non-numeric (e.g., "
                                               "“Red,” “Blue,” “Yellow”). Don't worry about the "
                                               "sort order or formatting of the categories when "
                                               "deciding whether to use numeric or string "
                                               "categories. The tool has been heavily tested to "
                                               "properly handle all these cases.",
                                "minItems": 1
                            },
                            "values": {
                                "type": "array", 
                                "items": {"type": "number"},
                                "description": "List of numeric values for each category. MUST "
                                               "have same length as 'categories' array. Cannot be "
                                               "empty. All values must be valid numbers. The "
                                               "values array should contain a number for every "
                                               "category listed in the categories array.",
                                "minItems": 1
                            },
                            "label": {
                                "type": "string",
                                "description": "Name for this data series (shown in legend)"
                            },
                            "color": {
                                "type": "string",
                                "description": "Color for the bars. Valid colors: 'red', 'blue', "
                                               "'green', 'orange', 'purple', 'brown', 'pink', "
                                               "'gray', 'lightcoral', 'lightblue', 'lightgreen', "
                                               "or hex codes like '#FF5733'. AVOID: 'lightred' "
                                               "(use 'lightcoral' instead)."
                            }
                        },
                        "required": ["categories", "values", "label", "color"]
                    }
                },
                "width": {
                    "type": "number",
                    "description": "Total width allocated per category. Use 0.8 (normal), 0.6 "
                                   "(narrower), 1.0 (wider)"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "xlabel": {
                    "type": "string",
                    "description": "Label for x-axis (categories)"
                },
                "ylabel": {
                    "type": "string",
                    "description": "Label for y-axis (values)"
                },
                "xlim": {
                    "type": "object",
                    "description": "X-axis limits",
                    "properties": {
                        "min": {
                            "type": "number",
                            "description": "When using numeric x-axis values, minimum x-axis "
                                           "numeric value to include in plot area. Ensure this is "
                                           "smaller than the smallest value in the values array by"
                                           "enough to show a gap on the left side of the chart "
                                           "(left gap should be the same width as the right gap)."
                        },
                        "max": {
                            "type": "number", 
                            "description": "When using numeric x-axis values, maximum x-axis "
                                           "numeric value to include in plot area. Ensure this is "
                                           "larger than the largest value in the values array by "
                                           "enough to show a gap on the right side of the chart "
                                           "(right gap should be the same width as the left gap)."
                        }
                    },
                    "required": ["min", "max"]
                },
                "ylim": {
                    "type": "object",
                    "description": "Y-axis limits",
                    "properties": {
                        "min": {
                            "type": "number",
                            "description": "Minimum y-axis value to include in plot area"
                        },
                        "max": {
                            "type": "number",
                            "description": "Maximum y-axis value to include in plot area"
                        }
                    },
                    "required": ["min", "max"]
                },
                "legend": {
                    "type": "boolean",
                    "description": "Whether to show legend (only needed for multiple series)."
                },
                "xtick_rotation": {
                    "type": "number",
                    "description": "Rotation angle for category labels in degrees. Use 0 "
                                   "(horizontal), 45 (diagonal), 90 (vertical)."
                },
                "x_axis_show_fractions": {
                    "type": "boolean",
                    "description": "Whether to convert numeric x-axis categories to fraction "
                                   "labels (e.g. 3.25 -> 3¼). Only applies if categories can be "
                                   "converted to numbers. Allows users to provide decimal values "
                                   "like ['3.0', '3.25', '3.5'] and have them displayed as "
                                   "fractions."
                },
                "x_axis_fraction_denominator": {
                    "type": ["integer", "null"],
                    "description": "Optional denominator to use for ALL x-axis fractions without "
                                   "simplifying (e.g. 4 for quarters: 1/4, 2/4, 3/4, 4/4, 5/4, "
                                   "etc.). If set to null, will auto-detect appropriate "
                                   "denominators and display simplified fractions. If provided, "
                                   "maintains the denominator without simplifying."
                },
                "y_axis_interval": {
                    "type": "number",
                    "description": "Interval for y-axis ticks and gridlines (e.g. 10 for ticks at "
                                   "0, 10, 20, 30...)"
                },
                "y_axis_show_fractions": {
                    "type": "boolean",
                    "description": "Whether to display y-axis tick labels as mathematical "
                                   "fractions instead of decimals (e.g. properly formatted '1/4' "
                                   "instead of '0.25'). When creating a plot for content that uses "
                                   "fractions rather than decimals, set this to True."
                },
                "y_axis_fraction_denominator": {
                    "type": ["integer", "null"],
                    "description": "Optional denominator to use for ALL y-axis fractions without "
                                   "simplifying (e.g. 4 for quarters: 1/4, 2/4, 3/4, 4/4, 5/4, "
                                   "etc.). If set to null, will auto-detect appropriate "
                                   "denominators and display simplified fractions. If provided, "
                                   "maintains the denominator without simplifying."
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the chart. Use 'transparent' for "
                                   "transparent background, or any valid matplotlib color name or "
                                   "hex code. Defaults to 'transparent'."
                }
            },
            "required": ["series", "width", "title", "xlabel", "ylabel", "xlim", "ylim", "legend",
                        "xtick_rotation", "x_axis_show_fractions", "x_axis_fraction_denominator",
                        "y_axis_interval", "y_axis_show_fractions", "y_axis_fraction_denominator",
                        "background_color"]
        }
    }
    
    return spec, plot_bar 