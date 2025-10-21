import io
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import logging
from typing import Optional, Dict, Any, Callable, List
import matplotlib.patheffects as path_effects
from PIL import Image
from utils.supabase_utils import upload_image_to_supabase
from fractions import Fraction
from .color_utils import validate_color_list
from .chart_utils import (
    fraction_to_latex,
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


def calculate_point_label_position(
    x: float,
    y: float,
    connected_points: List[tuple[float, float]],
    bounds: tuple[float, float, float, float]
) -> tuple[float, float]:
    """
    Calculate the optimal position for a point label based on connected points.
    
    Parameters
    ----------
    x, y : float
        Coordinates of the point being labeled
    connected_points : List[tuple[float, float]]
        List of coordinates of points connected to this point
    bounds : tuple[float, float, float, float]
        (min_x, max_x, min_y, max_y) bounds of the plot
        
    Returns
    -------
    tuple[float, float]
        (x, y) coordinates for label placement
    """
    if not connected_points:
        # If no connected points, use a default offset
        label_distance = np.sqrt((bounds[1] - bounds[0])**2 + (bounds[3] - bounds[2])**2) * 0.05
        return x + label_distance, y + label_distance
        
    # Calculate angles to all connected points
    angles = []
    for px, py in connected_points:
        angle = np.arctan2(py - y, px - x)
        if angle < 0:
            angle += 2 * np.pi
        angles.append(angle)
    
    # Sort angles
    angles.sort()
    
    # Find largest gap between angles
    n = len(angles)
    max_gap = 0
    gap_mid_angle = 0
    
    # Add the first angle again at the end to check gap between last and first
    angles.append(angles[0] + 2 * np.pi)
    
    for i in range(n):
        gap = angles[i + 1] - angles[i]
        if gap > max_gap:
            max_gap = gap
            gap_mid_angle = angles[i] + gap / 2
            if gap_mid_angle >= 2 * np.pi:
                gap_mid_angle -= 2 * np.pi
    
    # Calculate label position in direction of gap bisector
    label_distance = np.sqrt((bounds[1] - bounds[0])**2 + (bounds[3] - bounds[2])**2) * 0.05
    label_x = x + label_distance * np.cos(gap_mid_angle) / 1.25
    label_y = y + label_distance * np.sin(gap_mid_angle)
    
    return label_x, label_y

def plot_line(
    series: List[Dict[str, Any]],
    *,
    linestyle: str = "-",
    marker: Optional[str] = None,
    markersize: float = 6,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    legend: bool = True,
    grid: bool = False,
    xlim: Optional[Dict[str, float]] = None,
    ylim: Optional[Dict[str, float]] = None,
    x_axis_interval: Optional[float] = None,
    y_axis_interval: Optional[float] = None,
    x_axis_show_fractions: bool = False,
    x_axis_fraction_denominator: Optional[int] = None,
    y_axis_show_fractions: bool = False,
    y_axis_fraction_denominator: Optional[int] = None,
    background_color: str = 'transparent'
) -> str:
    """
    Draw one or more line‐series on the same axes.

    Parameters
    ----------
    series : List[Dict[str, Any]]
        List of series dictionaries. Each dict must have:
          - 'x': list of x-coordinates
          - 'y': list of y-coordinates
          - 'label': string name for the series (shown in legend)
          - 'color': string line color (e.g. 'red', 'blue', '#FF5733')
          - 'point_labels': optional list of labels for points
    linestyle : str
        Line style (e.g. '-', '--', '-.', ':').
    marker : str or None
        Marker symbol at each data point (e.g. 'o', 's', '^'), or None for no markers.
    markersize : float
        Size of the marker symbols.
    title : str
        Plot title.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis.
    legend : bool
        Whether to show a legend.
    grid : bool
        Whether to draw gridlines.
    xlim : dict
        X-axis limits as dict with 'min' and 'max' keys (e.g. {'min': 0, 'max': 10}).
    ylim : dict
        Y-axis limits as dict with 'min' and 'max' keys (e.g. {'min': 0, 'max': 100}).
    x_axis_interval : float
        Interval for x-axis ticks and gridlines (e.g. 0.25 for ticks at 0, 0.25, 0.5, 0.75...).
    y_axis_interval : float
        Interval for y-axis ticks and gridlines (e.g. 10 for ticks at 0, 10, 20, 30...).
    x_axis_show_fractions : bool
        Whether to display x-axis tick labels as fractions instead of decimals.
    x_axis_fraction_denominator : int
        Denominator to use for x-axis fractions (e.g. 4 for quarters: 1/4, 1/2, 3/4).
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
        print("Line chart parameters:")
        print(f"Number of series: {len(series_data)}")
        print(f"Linestyle: {linestyle}")
        print(f"Marker: {marker}")
        print(f"Markersize: {markersize}")
        print(f"Title: {title}")
        print(f"Xlabel: {xlabel}")
        print(f"Ylabel: {ylabel}")
        print(f"Legend: {legend}")
        print(f"Grid: {grid}")
        print(f"Xlim: {xlim}")
        print(f"Ylim: {ylim}")
        print(f"X-axis interval: {x_axis_interval}")
        print(f"Y-axis interval: {y_axis_interval}")
        print(f"X-axis show fractions: {x_axis_show_fractions}")
        print(f"X-axis fraction denominator: {x_axis_fraction_denominator}")
        print(f"Y-axis show fractions: {y_axis_show_fractions}")
        print(f"Y-axis fraction denominator: {y_axis_fraction_denominator}")
        print(f"Background color: {background_color}")
        
        # Parse axis limits if provided
        xlim_tuple = None
        ylim_tuple = None
        if xlim:
            xlim_tuple = (xlim['min'], xlim['max'])
        if ylim:
            ylim_tuple = (ylim['min'], ylim['max'])
        
        # Create inner figure with white background
        inner_fig = plt.figure(figsize=(10, 6))
        inner_fig.patch.set_facecolor('white')
        ax = inner_fig.add_subplot(111)
        ax.set_facecolor('white')
        
        # Enable LaTeX rendering for mathematical notation
        plt.rcParams['text.usetex'] = False  # Use matplotlib's built-in math renderer
        plt.rcParams['mathtext.default'] = 'regular'  # Use regular font for math
        
        # Plot each series and collect point information for label placement
        all_points = []  # List to store all points for bounds calculation
        series_points = []  # List to store points for each series
        
        for i, s in enumerate(series_data):
            # Validate required fields
            if 'x' not in s or 'y' not in s:
                raise ValueError(f"Series {i} missing required 'x' or 'y' field")
            
            # Get series properties with defaults
            x_data = s['x']
            y_data = s['y']
            label = s.get('label', f'Series {i+1}')
            color = validate_color_list(s.get('color', f'C{i}'), default=f'C{i}')  # Use matplotlib's default color cycle
            
            # Store points for this series
            points = list(zip(x_data, y_data))
            series_points.append(points)
            all_points.extend(points)
            
            # Plot the line
            ax.plot(
                x_data, y_data,
                linestyle=linestyle,
                marker=marker,
                markersize=markersize,
                color=color,
                label=label,
                linewidth=2,
                markeredgecolor='black' if marker else None,
                markeredgewidth=0.5 if marker else None
            )

        # Calculate bounds for label positioning
        if all_points:
            x_coords, y_coords = zip(*all_points)
            bounds = (min(x_coords), max(x_coords), min(y_coords), max(y_coords))
        else:
            bounds = (0, 1, 0, 1)

        # Add point labels if provided
        for i, s in enumerate(series_data):
            if 'point_labels' in s and s['point_labels']:
                points = series_points[i]
                for j, (x, y) in enumerate(points):
                    if j < len(s['point_labels']) and s['point_labels'][j]:
                        # Get connected points (previous and next points in series)
                        connected = []
                        if j > 0:
                            connected.append(points[j-1])
                        if j < len(points) - 1:
                            connected.append(points[j+1])
                        
                        # Calculate label position
                        label_x, label_y = calculate_point_label_position(x, y, connected, bounds)
                        
                        # Add label with white outline
                        text = ax.text(label_x, label_y, s['point_labels'][j],
                                     color=s.get('color', f'C{i}'),
                                     ha='center', va='center',
                                     fontsize=18, weight='bold',
                                     zorder=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))
                        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])

        # Set labels and title with white background boxes
        if title:
            ax.set_title(title, fontsize=18, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=18, bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=18, bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))

        # Set axis limits
        if xlim_tuple:
            ax.set_xlim(xlim_tuple)
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

        # Add grid if requested
        if grid:
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_axisbelow(True)

        # Add legend if requested and there are multiple series or labels
        if legend and (len(series_data) > 1 or any('label' in s for s in series_data)):
            ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=min(4, len(series_data)),
                     facecolor='white', framealpha=0.8)

        # Set adaptive font sizing for non-fraction axes
        if not x_axis_show_fractions:
            x_ticks = len(ax.get_xticks())
            # Check if we should rotate x-axis labels
            should_rotate = should_rotate_x_labels(x_ticks, is_fractions=False)
            x_adaptive_size = calculate_adaptive_font_size(x_ticks, use_rotation=should_rotate)
            ax.tick_params(axis='x', which='major', labelsize=x_adaptive_size)
            
            # Rotate x-axis labels if needed
            if should_rotate:
                ax.tick_params(axis='x', rotation=45)
            
        if not y_axis_show_fractions:
            y_ticks = len(ax.get_yticks())
            y_adaptive_size = calculate_adaptive_font_size(y_ticks)
            ax.tick_params(axis='y', which='major', labelsize=y_adaptive_size)

        # Improve appearance
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Save inner figure with white background and inner padding
        inner_buf = io.BytesIO()
        if legend and (len(series_data) > 1 or any('label' in s for s in series_data)):
            plt.subplots_adjust(bottom=0.2)
        inner_fig.savefig(inner_buf, format='png', dpi=300, bbox_inches='tight',
                         pad_inches=0.15, facecolor='white')
        inner_buf.seek(0)
        plt.close(inner_fig)

        # Create outer figure with specified background color
        outer_fig = plt.figure(figsize=(10.5, 6.5))
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
        
        # Save final figure with outer padding
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
        error_message = f"Error generating line chart: {str(e)}"
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


def generate_simple_line_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the simple line chart tool specification and function."""
    
    spec = {
        "type": "function",
        "name": "plot_line",
        "description": "Create line charts to show trends and relationships over continuous data. Can plot multiple series on the same axes. CRITICAL: Within each series, x and y arrays MUST have exactly the same length. If point_labels are used, they must also match the x/y length.\n\nEXAMPLES:\n- Single series: [{\"x\":[1,2,3], \"y\":[4,5,6], \"label\":\"Line1\", \"color\":\"red\"}] ✓\n- Multiple series: [{\"x\":[1,2], \"y\":[3,4], \"label\":\"A\", \"color\":\"red\"}, {\"x\":[1,2], \"y\":[5,6], \"label\":\"B\", \"color\":\"blue\"}] ✓\n- With point labels: [{\"x\":[1,2], \"y\":[3,4], \"label\":\"Line\", \"color\":\"red\", \"point_labels\":[\"P1\",\"P2\"]}] ✓\n- WRONG: [{\"x\":[1,2,3], \"y\":[4,5], \"label\":\"Line\", \"color\":\"red\"}] ✗ (length mismatch)",
        "parameters": {
            "type": "object",
            "properties": {
                "series": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "array",
                                "items": {
                                    "type": "number"
                                },
                                "description": "REQUIRED: Array of x-coordinates for this series. MUST have exactly the same length as the y array for this series. Should contain the INDEPENDENT VARIABLE for the plot, which is the unmeasured variable (e.g., time, sample number, etc.)."
                            },
                            "y": {
                                "type": "array",
                                "items": {
                                    "type": "number"
                                },
                                "description": "REQUIRED: Array of y-coordinates for this series. MUST have exactly the same length as the x array for this series. Should contain the DEPENDENT VARIABLE for the plot, which is the measured variable (e.g., temperature, weight, length, etc.)."
                            },
                            "label": {
                                "type": "string",
                                "description": "REQUIRED: Name for this series (shown in legend)."
                            },
                            "color": {
                                "type": "string",
                                "description": "REQUIRED: Color for this series line (e.g. 'red', 'blue', '#FF5733')."
                            },
                            "point_labels": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "OPTIONAL: List of labels for points in this series. CRITICAL: If provided, MUST have exactly the same length as x and y arrays for this series. Each label corresponds to a point at the same index."
                            }
                        },
                        "required": ["x", "y", "label", "color"]
                    },
                    "description": "REQUIRED: List of series dictionaries. CRITICAL: Within each series, x and y arrays MUST have exactly the same length. Each dict must have 'x' (list of numbers), 'y' (list of numbers), 'label' (string), 'color' (string), and optionally 'point_labels' (list of strings matching x/y length)."
                },
                "linestyle": {
                    "type": "string",
                    "description": "Line style. Options: '-' (solid), '--' (dashed), '-.' (dash-dot), ':' (dotted)."
                },
                "marker": {
                    "type": "string",
                    "description": "Marker symbol at each data point. Options: 'o' (circle), 's' (square), '^' (triangle), 'D' (diamond), '*' (star), '+' (plus), 'x' (x), or None for no markers."
                },
                "markersize": {
                    "type": "number",
                    "description": "Size of the marker symbols."
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "xlabel": {
                    "type": "string",
                    "description": "Label for x-axis"
                },
                "ylabel": {
                    "type": "string",
                    "description": "Label for y-axis"
                },
                "legend": {
                    "type": "boolean",
                    "description": "Whether to show a legend."
                },
                "grid": {
                    "type": "boolean",
                    "description": "Whether to draw gridlines."
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
                "x_axis_interval": {
                    "type": "number",
                    "description": "Interval for x-axis ticks and gridlines (e.g. 0.25 for ticks at 0, 0.25, 0.5, 0.75..., 1.5 for ticks at 0, 1.5, 3, 4.5, etc.)"
                },
                "y_axis_interval": {
                    "type": "number",
                    "description": "Interval for y-axis ticks and gridlines (e.g. 10 for ticks at 0, 10, 20, 30...)"
                },
                "x_axis_show_fractions": {
                    "type": "boolean",
                    "description": "Whether to display x-axis tick labels as mathematical fractions instead of decimals (e.g. properly formatted '1/4' instead of '0.25'). Uses LaTeX rendering for beautiful mathematical notation that works with any fraction. If x_axis_fraction_denominator is not provided, will auto-detect from x_axis_interval. When creating a plot for content that uses fractions rather than decimals, ALWAYS set this to True."
                },
                "x_axis_fraction_denominator": {
                    "type": ["integer", "null"],
                    "description": "Optional denominator to use for x-axis fractions (e.g. 4 for quarters: 1/4, 2/4, 3/4, 4/4, 5/4, etc.). If not provided, will auto-detect from x_axis_interval and simplify fractions. If provided, maintains the denominator without simplifying."
                },
                "y_axis_show_fractions": {
                    "type": "boolean",
                    "description": "Whether to display y-axis tick labels as mathematical fractions instead of decimals (e.g. properly formatted '1/4' instead of '0.25'). Uses LaTeX rendering for beautiful mathematical notation that works with any fraction. If y_axis_fraction_denominator is not provided, will auto-detect from y_axis_interval. When creating a plot for content that uses fractions rather than decimals, ALWAYS set this to True."
                },
                "y_axis_fraction_denominator": {
                    "type": ["integer", "null"],
                    "description": "Optional denominator to use for y-axis fractions (e.g. 4 for quarters: 1/4, 2/4, 3/4, 4/4, 5/4, etc.). If not provided, will auto-detect from y_axis_interval and simplify fractions. If provided, maintains the denominator without simplifying."
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the chart. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code.",
                    "default": "transparent"
                }
            },
            "required": ["series", "linestyle", "marker", "markersize", "title", "xlabel", "ylabel", "legend", "grid", "xlim", "ylim", "x_axis_interval", "y_axis_interval", "x_axis_show_fractions", "x_axis_fraction_denominator", "y_axis_show_fractions", "y_axis_fraction_denominator", "background_color"]
        }
    }
    
    return spec, plot_line 