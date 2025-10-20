import io
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import logging
from typing import Optional, Dict, Any, Callable, List
from PIL import Image
from utils.supabase_utils import upload_image_to_supabase
from .color_utils import validate_color_list
from .chart_utils import (
    auto_detect_denominator,
    decimal_to_fraction_string,
    should_rotate_x_labels,
    calculate_adaptive_font_size
)

# Set matplotlib to use a non-interactive backend
matplotlib.use('Agg')

logger = logging.getLogger(__name__)


def plot_histogram(
    values: List[float],
    *,
    bins: int = 10,
    xlim: Optional[Dict[str, float]] = None,
    ylim: Optional[Dict[str, float]] = None,
    color: str = "blue",
    label: Optional[str] = None,
    legend: bool = False,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    x_axis_interval: Optional[float] = None,
    x_axis_show_fractions: bool = False,
    x_axis_fraction_denominator: Optional[int] = None,
    y_axis_interval: Optional[float] = None,
    y_axis_show_fractions: bool = False,
    y_axis_fraction_denominator: Optional[int] = None,
    background_color: str = 'transparent'
) -> str:
    """
    Draw a histogram of a single data series.

    Parameters
    ----------
    values : List[float]
        List of numeric data to bin and plot.
    bins : int
        Number of bins.
    xlim : dict
        X-axis limits as dict with 'min' and 'max' keys (e.g. {'min': 0, 'max': 100}).
    ylim : dict
        Y-axis limits as dict with 'min' and 'max' keys (e.g. {'min': 0, 'max': 50}).
    color : str
        Fill color for the bars (e.g., 'blue', 'red', 'green', '#FF5733').
    label : str
        Name for this series (shown in a legend if legend=True).
    legend : bool
        Whether to show a legend.
    title : str
        Plot title.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis.
    x_axis_interval : float
        Interval for x-axis ticks and gridlines (e.g. 0.25 for ticks at 0, 0.25, 0.5, 0.75...).
    x_axis_show_fractions : bool
        Whether to display x-axis tick labels as fractions instead of decimals.
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
        # values is now already a list, no need to parse JSON
        values_array = values
        print("Histogram parameters:")
        print(f"Values count: {len(values_array)}")
        print(f"Bins: {bins}")
        print(f"Xlim: {xlim}")
        print(f"Ylim: {ylim}")
        print(f"Color: {color}")
        print(f"Label: {label}")
        print(f"Legend: {legend}")
        print(f"Title: {title}")
        print(f"Xlabel: {xlabel}")
        print(f"Ylabel: {ylabel}")
        print(f"X-axis interval: {x_axis_interval}")
        print(f"X-axis show fractions: {x_axis_show_fractions}")
        print(f"X-axis fraction denominator: {x_axis_fraction_denominator}")
        print(f"Y-axis interval: {y_axis_interval}")
        print(f"Y-axis show fractions: {y_axis_show_fractions}")
        print(f"Y-axis fraction denominator: {y_axis_fraction_denominator}")
        print(f"Background color: {background_color}")
        
        # Parse range if provided
        xlim_tuple = None
        if xlim:
            xlim_tuple = (xlim['min'], xlim['max'])
        
        ylim_tuple = None
        if ylim:
            ylim_tuple = (ylim['min'], ylim['max'])
        
        # Create inner figure with white background
        inner_fig = plt.figure(figsize=(8, 6))
        inner_fig.patch.set_facecolor('white')
        ax = inner_fig.add_subplot(111)
        ax.set_facecolor('white')
        
        # Enable LaTeX rendering for mathematical notation
        plt.rcParams['text.usetex'] = False  # Use matplotlib's built-in math renderer
        plt.rcParams['mathtext.default'] = 'regular'  # Use regular font for math
        
        # Validate and normalize color
        validated_color = validate_color_list(color, default='blue')
        
        # Create histogram
        n, bins_edges, patches = ax.hist(
            values_array,
            bins=bins,
            range=xlim_tuple,
            color=validated_color,
            label=label,
            alpha=0.7,
            edgecolor='black',
            linewidth=0.5
        )

        # Set labels and title with white background boxes
        if title:
            ax.set_title(title, fontsize=18, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=18, bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=18, bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        else:
            # Default y-label for histograms
            ax.set_ylabel('Frequency', fontsize=18, bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))

        # Set axis limits if provided
        if ylim_tuple:
            ax.set_ylim(ylim_tuple)
        
        # Set x-axis interval if provided
        if x_axis_interval is not None:
            # Get current x-axis limits
            xmin, xmax = ax.get_xlim()
            
            # Create ticks at the specified interval
            # Start from the first multiple of interval >= xmin
            start_tick = np.ceil(xmin / x_axis_interval) * x_axis_interval
            # End at the last multiple of interval <= xmax
            end_tick = np.floor(xmax / x_axis_interval) * x_axis_interval
            
            # Generate tick positions
            xticks = np.arange(start_tick, end_tick + x_axis_interval, x_axis_interval)
            ax.set_xticks(xticks)
            
            # Set fraction labels if requested
            if x_axis_show_fractions:
                # Auto-detect denominator if not provided
                denominator = x_axis_fraction_denominator
                if denominator is None:
                    denominator = auto_detect_denominator(x_axis_interval)
                
                if denominator is not None:
                    # Only simplify if denominator was auto-detected
                    simplify_fractions = (x_axis_fraction_denominator is None)
                    fraction_labels = [decimal_to_fraction_string(tick, denominator, simplify_fractions, use_latex=True) for tick in xticks]
                    ax.set_xticklabels(fraction_labels)
                    
                    # Check if we should rotate x-axis labels
                    should_rotate = should_rotate_x_labels(len(xticks), is_fractions=True)
                    
                    # Apply adaptive font sizing for x-axis with rotation consideration
                    x_font_size = calculate_adaptive_font_size(len(xticks), use_rotation=should_rotate)
                    ax.tick_params(axis='x', labelsize=x_font_size)
                    
                    # Rotate labels if needed
                    if should_rotate:
                        ax.tick_params(axis='x', rotation=45)
                else:
                    print(f"Warning: Could not auto-detect denominator for x_axis_interval {x_axis_interval}. Using decimal labels.")

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
                    fraction_labels = [decimal_to_fraction_string(tick, denominator, simplify_fractions, use_latex=True) for tick in yticks]
                    ax.set_yticklabels(fraction_labels)
                    
                    # Apply adaptive font sizing for y-axis
                    y_font_size = calculate_adaptive_font_size(len(yticks))
                    ax.tick_params(axis='y', labelsize=y_font_size)
                else:
                    print(f"Warning: Could not auto-detect denominator for y_axis_interval {y_axis_interval}. Using decimal labels.")

        # Add legend if requested and label is provided
        if legend and label:
            ax.legend(facecolor='white', framealpha=0.8)

        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_axisbelow(True)

        # Apply adaptive font sizing for non-fraction axes
        if not x_axis_show_fractions:
            x_ticks = len(ax.get_xticks())
            # Check if we should rotate x-axis labels
            should_rotate = should_rotate_x_labels(x_ticks, is_fractions=False)
            x_font_size = calculate_adaptive_font_size(x_ticks, use_rotation=should_rotate)
            ax.tick_params(axis='x', labelsize=x_font_size)
            
            # Rotate x-axis labels if needed
            if should_rotate:
                ax.tick_params(axis='x', rotation=45)
                
        if not y_axis_show_fractions:
            y_ticks = len(ax.get_yticks())
            y_font_size = calculate_adaptive_font_size(y_ticks)
            ax.tick_params(axis='y', labelsize=y_font_size)
        
        # Improve appearance
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add some statistics as text if there's space
        if len(values_array) > 0:
            mean_val = np.mean(values_array)
            std_val = np.std(values_array)
            stats_text = f'Mean: {mean_val:.2f}\nStd: {std_val:.2f}\nN: {len(values_array)}'
            
            # Position the text box in the upper right with white background
            ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
                   verticalalignment='top', horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                   fontsize=18)

        # Save inner figure to bytes buffer with inner padding
        inner_buf = io.BytesIO()
        inner_fig.savefig(inner_buf, format='png', dpi=300, bbox_inches='tight', 
                         pad_inches=0.15, facecolor='white')
        inner_buf.seek(0)
        plt.close(inner_fig)

        # Create outer figure with specified background color
        outer_fig = plt.figure(figsize=(8.5, 6.5))
        if background_color == 'transparent':
            outer_fig.patch.set_alpha(0)
        else:
            outer_fig.patch.set_facecolor(background_color)

        # Display inner figure on outer figure
        inner_img = Image.open(inner_buf)
        # Convert PIL Image to numpy array for matplotlib
        inner_img_array = np.array(inner_img)
        outer_ax = outer_fig.add_subplot(111)
        outer_ax.imshow(inner_img_array)
        outer_ax.axis('off')
        
        # Save final figure to bytes buffer with outer padding
        final_buf = io.BytesIO()
        if background_color == 'transparent':
            outer_fig.savefig(final_buf, format='png', dpi=300, bbox_inches='tight',
                            pad_inches=0.25, transparent=True)
        else:
            outer_fig.savefig(final_buf, format='png', dpi=300, bbox_inches='tight',
                            pad_inches=0.25, facecolor=background_color)
        final_buf.seek(0)
        
        # Upload to Supabase
        public_url = upload_image_to_supabase(
            image_bytes=final_buf.getvalue(),
            content_type="image/png",
            bucket_name="incept-images",
            file_extension=".png"
        )
        
        # Thread-safe cleanup - close specific figures only
        # (inner_fig was already closed after saving to buffer)
        plt.close(outer_fig)
        inner_buf.close()
        final_buf.close()
        
        return public_url
        
    except Exception as e:
        error_message = f"Error generating histogram: {str(e)}"
        logger.error(error_message)
        # Ensure cleanup on error - close any figures we may have created
        try:
            if 'inner_fig' in locals():
                plt.close(inner_fig)
        except Exception:
            pass
        try:
            if 'outer_fig' in locals():
                plt.close(outer_fig)
        except Exception:
            pass
        raise RuntimeError(error_message)


def generate_simple_histogram_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the simple histogram tool specification and function."""
    
    spec = {
        "type": "function",
        "name": "plot_histogram",
        "description": "Create a histogram to show the distribution of numeric data. Displays frequency of values in bins.",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": "array",
                    "description": "List of numeric data to bin and plot",
                    "items": {"type": "number"}
                },
                "bins": {
                    "type": "integer",
                    "description": "Number of bins to divide the data into."
                },
                "xlim": {
                    "type": "object",
                    "description": "X-axis limits",
                    "properties": {
                        "min": {
                            "type": "number",
                            "description": "Minimum x-axis value to include in plot area"
                        },
                        "max": {
                            "type": "number",
                            "description": "Maximum x-axis value to include in plot area"
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
                "color": {
                    "type": "string",
                    "description": "Fill color for the bars. Valid colors: 'red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'lightcoral', 'lightblue', 'lightgreen', or hex codes like '#FF5733'. AVOID: 'lightred' (use 'lightcoral' instead)."
                },
                "label": {
                    "type": "string",
                    "description": "Name for this data series (shown in legend if legend=true)"
                },
                "legend": {
                    "type": "boolean",
                    "description": "Whether to show a legend (only useful if label is provided)."
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "xlabel": {
                    "type": "string",
                    "description": "Label for x-axis (values)"
                },
                "ylabel": {
                    "type": "string",
                    "description": "Label for y-axis."
                },
                "x_axis_interval": {
                    "type": "number",
                    "description": "Interval for x-axis ticks and gridlines (e.g. 0.25 for ticks at 0, 0.25, 0.5, 0.75..., 1.5 for ticks at 0, 1.5, 3, 4.5, etc.)"
                },
                "x_axis_show_fractions": {
                    "type": "boolean",
                    "description": "Whether to display x-axis tick labels as mathematical fractions instead of decimals (e.g. properly formatted '1/4' instead of '0.25'). When creating a plot for content that uses fractions rather than decimals, set this to True."
                },
                "x_axis_fraction_denominator": {
                    "type": ["integer", "null"],
                    "description": "Optional denominator to use for ALL x-axis fractions without simplifying (e.g. 4 for quarters: 1/4, 2/4, 3/4, 4/4, 5/4, etc.). If set to null, will auto-detect appropriate denominators and display simplified fractions. If provided, maintains the denominator without simplifying."
                },
                "y_axis_interval": {
                    "type": "number",
                    "description": "Interval for y-axis ticks and gridlines (e.g. 10 for ticks at 0, 10, 20, 30...)"
                },
                "y_axis_show_fractions": {
                    "type": "boolean",
                    "description": "Whether to display y-axis tick labels as mathematical fractions instead of decimals (e.g. properly formatted '1/4' instead of '0.25'). When creating a plot for content that uses fractions rather than decimals, set this to True."
                },
                "y_axis_fraction_denominator": {
                    "type": ["integer", "null"],
                    "description": "Optional denominator to use for ALL y-axis fractions without simplifying (e.g. 4 for quarters: 1/4, 2/4, 3/4, 4/4, 5/4, etc.). If set to null, will auto-detect appropriate denominators and display simplified fractions. If provided, maintains the denominator without simplifying."
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color for the plot. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code.",
                    "default": "transparent"
                }
            },
            "required": ["values", "bins", "xlim", "ylim", "color", "label", "legend", "title", "xlabel", "ylabel", "x_axis_interval", "x_axis_show_fractions", "x_axis_fraction_denominator", "y_axis_interval", "y_axis_show_fractions", "y_axis_fraction_denominator", "background_color"]
        }
    }
    
    return spec, plot_histogram 