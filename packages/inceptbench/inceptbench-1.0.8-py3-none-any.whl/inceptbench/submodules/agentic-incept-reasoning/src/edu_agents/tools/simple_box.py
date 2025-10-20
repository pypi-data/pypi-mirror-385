import io
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import logging
from typing import Optional, Dict, Any, Callable
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

# Configure matplotlib to prevent memory leaks and limit figure accumulation
matplotlib.rcParams['figure.max_open_warning'] = 5  # Warn much earlier
matplotlib.rcParams['figure.raise_window'] = False   # Don't raise GUI windows

logger = logging.getLogger(__name__)


def plot_box(
    series: list,
    *,
    notch: bool = False,
    show_means: bool = False,
    widths: float = 0.5,
    whisker_style: str = 'standard',
    legend: bool = True,  # Added parameter
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    xlim: Optional[Dict[str, float]] = None,
    ylim: Optional[Dict[str, float]] = None,
    xtick_rotation: float = 0,
    y_axis_interval: Optional[float] = None,
    y_axis_show_fractions: bool = False,
    y_axis_fraction_denominator: Optional[int] = None,
    background_color: str = 'transparent'
) -> str:
    """
    Draw one or more boxplots side by side.

    Parameters
    ----------
    series : list
        List of series dictionaries. Each series must have:
          - 'values': list of data points
          - 'label': string name for the group (shown on x-axis)
          - 'color': string fill color for the boxes (e.g. 'red', 'blue', '#FF5733')
    notch : bool
        If True, draw a notch (confidence interval) in each box.
    show_means : bool
        If True, mark the mean with a green triangle.
    widths : float
        Box width (as a fraction of the space allocated per box).
    whisker_style : str
        Style of whiskers to use:
          - 'standard': extends to 1.5 times the interquartile range (default)
          - 'full_range': extends to the full range of data (excluding outliers)
          - 'none': no whiskers shown
    legend : bool
        Whether to show a legend with box colors and labels.
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
    xtick_rotation : float
        Rotation (in degrees) of the group labels on the x-axis.
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
        # series is now already a list of dicts, no need to parse JSON
        series_data = series
        print("Boxplot parameters:")
        print(f"Series data: {series_data}")
        print(f"Notch: {notch}")
        print(f"Show means: {show_means}")
        print(f"Widths: {widths}")
        print(f"Whisker style: {whisker_style}")
        print(f"Legend: {legend}")  # Added print
        print(f"Title: {title}")
        print(f"Xlabel: {xlabel}")
        print(f"Ylabel: {ylabel}")
        print(f"Xlim: {xlim}")
        print(f"Ylim: {ylim}")
        print(f"Xtick rotation: {xtick_rotation}")
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
        
        labels = [s['label'] for s in series_data]
        data = [s['values'] for s in series_data]
        colors = [validate_color_list(s['color'], default=f'C{i}') for i, s in enumerate(series_data)]
        n_series = len(series_data)

        # Set whis parameter based on whisker_style
        if whisker_style == 'full_range':
            whis = 'range'  # Extends to full range
        elif whisker_style == 'none':
            whis = 0.0  # No whiskers
        else:  # 'standard'
            whis = 1.5  # Default 1.5 IQR

        # Create boxplot with whisker style
        bp = ax.boxplot(
            data,
            notch=notch,
            widths=widths,
            patch_artist=True,
            labels=labels,
            showmeans=show_means,
            whis=whis,
        )

        # Fill boxes with colors and add black outlines
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_edgecolor('black')
            patch.set_linewidth(1)

        # Add black outlines to other elements
        for element in ['whiskers', 'caps', 'medians']:
            for item in bp[element]:
                item.set_color('black')
                item.set_linewidth(1)
        
        # Style fliers (outliers)
        for flier in bp['fliers']:
            flier.set_markeredgecolor('black')
            flier.set_markerfacecolor('white')
            flier.set_markeredgewidth(1)

        # Create legend patches and labels
        if legend:
            legend_elements = []
            for color, label in zip(colors, labels):
                patch = plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor='black')
                legend_elements.append((patch, label))
            
            # Add mean marker to legend if means are shown
            if show_means:
                mean_marker = plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='green',
                                       markeredgecolor='black', markersize=10, label='Mean')
                legend_elements.append((mean_marker, 'Mean'))
            
            # Create legend
            legend = ax.legend(
                [item[0] for item in legend_elements],
                [item[1] for item in legend_elements],
                bbox_to_anchor=(0.5, -0.15),
                loc='upper center',
                ncol=min(n_series + (1 if show_means else 0), 4)
            )
            # Set white background for legend
            if legend:
                legend.get_frame().set_facecolor('white')
                legend.get_frame().set_alpha(1.0)

        # Set labels and title
        if title:
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20)  # Add some padding above title
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
                    fraction_labels = [decimal_to_fraction_string(tick, denominator, simplify_fractions, use_latex=True) for tick in yticks]
                    ax.set_yticklabels(fraction_labels)
                    
                    # Apply adaptive font sizing for y-axis
                    y_font_size = calculate_adaptive_font_size(len(yticks))
                    ax.tick_params(axis='y', labelsize=y_font_size)
                else:
                    print(f"Warning: Could not auto-detect denominator for y_axis_interval {y_axis_interval}. Using decimal labels.")

        # Set x-tick rotation and adaptive font sizing
        ax.tick_params(axis='x', rotation=xtick_rotation)
        
        # Apply adaptive font sizing for x-axis labels if many groups
        x_ticks = len(labels)
        should_rotate_x = should_rotate_x_labels(x_ticks, is_fractions=False)
        x_font_size = calculate_adaptive_font_size(x_ticks, use_rotation=(xtick_rotation != 0 or should_rotate_x))
        ax.tick_params(axis='x', labelsize=x_font_size)
        
        # Apply adaptive font sizing for y-axis if not using fractions
        if not y_axis_show_fractions:
            y_ticks = len(ax.get_yticks())
            y_font_size = calculate_adaptive_font_size(y_ticks)
            ax.tick_params(axis='y', labelsize=y_font_size)

        # Add grid for better readability
        ax.grid(True, alpha=0.3, axis='y')
        
        # Ensure all spines are visible against any background
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('black')
        
        # Adjust layout to accommodate legend
        plt.tight_layout()
        if legend:
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
        error_message = f"Error generating boxplot: {str(e)}"
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
        raise RuntimeError(error_message)


def generate_simple_box_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the simple boxplot tool specification and function."""
    
    spec = {
        "type": "function",
        "name": "plot_box",
        "description": "Create boxplots to show distribution statistics for different groups. Each box shows median, quartiles, and optional whiskers.",
        "parameters": {
            "type": "object",
            "properties": {
                "series": {
                    "type": "array",
                    "description": "List of data series to plot as boxplots",
                    "items": {
                        "type": "object",
                        "properties": {
                            "values": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "List of numeric data points for this group"
                            },
                            "label": {
                                "type": "string",
                                "description": "Name for this group (shown on x-axis and in legend)"
                            },
                            "color": {
                                "type": "string",
                                "description": "Fill color for the box (e.g. 'blue', 'red', '#FF5733')"
                            }
                        },
                        "required": ["values", "label", "color"]
                    }
                },
                "notch": {
                    "type": "boolean",
                    "description": "Whether to draw notches showing confidence interval around median."
                },
                "show_means": {
                    "type": "boolean",
                    "description": "Whether to mark the mean with green triangles."
                },
                "widths": {
                    "type": "number",
                    "description": "Box width as fraction of allocated space. Use 0.5 (normal), 0.3 (narrow), 0.8 (wide)"
                },
                "whisker_style": {
                    "type": "string",
                    "description": "Style of whiskers to use: 'standard' (1.5×IQR), 'full_range' (min/max), or 'none' (no whiskers)",
                    "enum": ["standard", "full_range", "none"]
                },
                "legend": {
                    "type": "boolean",
                    "description": "Whether to show a legend with box colors and labels."
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "xlabel": {
                    "type": "string",
                    "description": "Label for x-axis (groups)"
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
                "xtick_rotation": {
                    "type": "number",
                    "description": "Rotation angle for group labels in degrees. Use 0 (horizontal), 45 (diagonal), 90 (vertical)"
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
                    "description": "The background color behind the chart. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code. Defaults to 'transparent'."
                }
            },
            "required": ["series", "notch", "show_means", "widths", "whisker_style", "legend", "title", "xlabel", "ylabel", "xlim", "ylim", "xtick_rotation", "y_axis_interval", "y_axis_show_fractions", "y_axis_fraction_denominator", "background_color"]
        }
    }
    
    return spec, plot_box 