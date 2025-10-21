from __future__ import annotations

import io
from typing import List, Dict, Any, Optional, Callable, Union
import matplotlib.pyplot as plt
import matplotlib
import logging
from PIL import Image
from utils.supabase_utils import upload_image_to_supabase
import numpy as np
from fractions import Fraction
from .color_utils import validate_color_list
from .chart_utils import (
    fraction_to_latex,
    auto_detect_denominator,
    decimal_to_fraction_string,
    should_rotate_x_labels,
    calculate_adaptive_font_size
)

logger = logging.getLogger(__name__)


# Set matplotlib to use a non-interactive backend
matplotlib.use('Agg')

# Configure matplotlib to prevent memory leaks and limit figure accumulation
matplotlib.rcParams['figure.max_open_warning'] = 5  # Warn much earlier
matplotlib.rcParams['figure.raise_window'] = False   # Don't raise GUI windows


def plot_scatter(
    x: List[float],
    y: List[float],
    *,
    s: float = 200,
    marker: str = "o",
    c: Optional[Union[str, List[str]]] = None,
    point_labels: Optional[List[Optional[str]]] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    xlim: Optional[Dict[str, float]] = None,
    ylim: Optional[Dict[str, float]] = None,
    x_axis_interval: Optional[float] = None,
    y_axis_interval: Optional[float] = None,
    x_axis_show_fractions: bool = False,
    x_axis_fraction_denominator: Optional[int] = None,
    y_axis_show_fractions: bool = False,
    y_axis_fraction_denominator: Optional[int] = None,
    background_color: str = 'transparent',
    linestyle: str = 'None',
    grid: bool = True,
) -> str:
    """
    Draw a scatter plot with points at the given coordinates.

    Parameters
    ----------
    x : List[float]
        List of x-coordinates for the points.
    y : List[float]
        List of y-coordinates for the points.
    s : float
        Marker size for all points (matplotlib standard name).
    marker : str
        Marker shape (e.g. 'o', 's', '^', '*', '+', 'x').
    c : str or List[str], optional
        Color(s) for the points. Can be:
        - Single color string (e.g. 'red', 'blue', '#FF5733') for all points
        - List of color strings for individual points (must match length of x/y)
        - None to use default blue color
    point_labels : List[Optional[str]], optional
        Array of labels for individual points. Points with non-null labels 
        will appear in the legend. Points with null labels won't have legend entries.
        If no points have labels or this is None, no legend is shown.
    title : str
        Plot title.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis.
    xlim : Dict[str, float]
        X-axis limits as dict with 'min' and 'max' keys (e.g. {'min': 0, 'max': 10}).
    ylim : Dict[str, float]
        Y-axis limits as dict with 'min' and 'max' keys (e.g. {'min': 0, 'max': 5}).
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
    background_color : str, default 'transparent'
        The background color behind the chart. Use 'transparent' for transparent background,
        or any valid matplotlib color name or hex code.
    linestyle : str, default 'None'
        Style of the line connecting points. Options: '-' (solid), '--' (dashed), ':' (dotted), 
        '-.' (dash-dot), 'None' (no lines drawn).
    grid : bool, default True
        Whether to show grid lines on the plot.
        
    Returns
    -------
    str
        URL of the generated image
    """
    try:
        print("Scatter plot parameters:")
        print(f"X data: {x}")
        print(f"Y data: {y}")
        print(f"Size (s): {s}")
        print(f"Marker: {marker}")
        print(f"Color (c): {c}")
        print(f"Point labels: {point_labels}")
        print(f"Title: {title}")
        print(f"Xlabel: {xlabel}")
        print(f"Ylabel: {ylabel}")
        print(f"Xlim: {xlim}")
        print(f"Ylim: {ylim}")
        print(f"X-axis interval: {x_axis_interval}")
        print(f"Y-axis interval: {y_axis_interval}")
        print(f"X-axis show fractions: {x_axis_show_fractions}")
        print(f"X-axis fraction denominator: {x_axis_fraction_denominator}")
        print(f"Y-axis show fractions: {y_axis_show_fractions}")
        print(f"Y-axis fraction denominator: {y_axis_fraction_denominator}")
        print(f"Background color: {background_color}")
        print(f"Linestyle: {linestyle}")
        print(f"Grid: {grid}")
        
        # Thread-safe figure creation - each thread gets its own figure
        # Don't use plt.close('all') as it affects other threads
        
        # Validate input lengths
        if len(x) != len(y):
            raise ValueError("x and y arrays must have the same length")
        
        if isinstance(c, list) and len(c) != len(x):
            raise ValueError("colors array must match length of x and y arrays")
            
        if point_labels and len(point_labels) != len(x):
            raise ValueError("point_labels array must match length of x and y arrays")
        
        # Create inner figure with white background
        inner_fig = plt.figure(figsize=(8, 6))
        inner_fig.patch.set_facecolor('white')
        ax = inner_fig.add_subplot(111)
        ax.set_facecolor('white')
        
        # Enable LaTeX rendering for mathematical notation
        plt.rcParams['text.usetex'] = False  # Use matplotlib's built-in math renderer
        plt.rcParams['mathtext.default'] = 'regular'  # Use regular font for math
        
        # Determine colors to use and validate them
        if c:
            point_colors = validate_color_list(c, default='blue')
        else:
            point_colors = 'blue'
        
        # Determine if we have meaningful labels
        has_labels = point_labels and any(label is not None and label != "None" and label != "" for label in point_labels)
        
        if has_labels:
            # Plot each point individually if we have labels
            for i, (px, py) in enumerate(zip(x, y)):
                point_color = point_colors[i] if isinstance(point_colors, list) else point_colors
                point_label = point_labels[i] if point_labels[i] is not None and point_labels[i] != "None" and point_labels[i] != "" else None
                
                ax.scatter([px], [py],
                          s=s,
                          marker=marker,
                          c=point_color,
                          label=point_label,
                          alpha=1.0,
                          edgecolors='black',
                          linewidths=1)
        else:
            # Plot all points as one group without individual labels
            ax.scatter(x, y,
                      s=s,
                      marker=marker,
                      c=point_colors,
                      alpha=1.0,
                      edgecolors='black',
                      linewidths=1)
        
        # Add connecting lines if linestyle is not 'None' (case-insensitive)
        if linestyle.lower() != 'none':
            line_color = c if c else (point_colors[0] if isinstance(point_colors, list) else point_colors)
            ax.plot(x, y,
                   color=line_color,
                   linestyle=linestyle,
                   alpha=0.7)
        
        # Set labels and title with white background boxes
        if title:
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20, 
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=18, 
                         bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=18, 
                         bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))
        
        # Add legend if requested and there are meaningful labels
        if has_labels:
            legend_obj = ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', 
                         ncol=min(len([l for l in point_labels if l and l != "None"]), 4), fontsize=18)
            # Set white background for legend
            if legend_obj:
                legend_obj.get_frame().set_facecolor('white')
                legend_obj.get_frame().set_alpha(1.0)
        
        # Set axis limits if provided
        if xlim:
            ax.set_xlim(xlim['min'], xlim['max'])
        if ylim:
            ax.set_ylim(ylim['min'], ylim['max'])
        
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
                    
                    # Apply adaptive font sizing for x-axis with fraction and rotation consideration
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
                    
                    # Apply adaptive font sizing for y-axis with fraction consideration 
                    y_font_size = calculate_adaptive_font_size(len(yticks))
                    ax.tick_params(axis='y', labelsize=y_font_size)
                else:
                    print(f"Warning: Could not auto-detect denominator for y_axis_interval {y_axis_interval}. Using decimal labels.")
        
        # Add grid for better readability
        if grid:
            ax.grid(True, alpha=0.3)
        
        # Ensure all spines are visible against any background
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('black')

        # Set tick label sizes (adaptive sizing for non-fraction axes)
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
        
        # Save inner figure with white background and inner padding
        inner_buf = io.BytesIO()
        if has_labels:
            plt.subplots_adjust(bottom=0.2)
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
        error_message = f"Error generating scatter plot: {str(e)}"
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


def generate_simple_scatter_tool() -> tuple[Dict[str, Any], Callable]:
    """Create the simple scatter plot tool specification and function."""
    
    spec = {
        "type": "function",
        "name": "plot_scatter",
        "description": "Create a scatter plot with points at given coordinates. Each point can have its own color and label. CRITICAL: All arrays (x, y, c if array, point_labels if array) MUST have exactly the same length.\n\nEXAMPLES:\n- Single color: x=[1,2,3], y=[4,5,6], c='red' ✓\n- Multiple colors: x=[1,2,3], y=[4,5,6], c=['red','blue','green'] ✓\n- With labels: x=[1,2], y=[3,4], c=['red','blue'], point_labels=['A','B'] ✓\n- WRONG: x=[1,2,3], y=[4,5,6], c=['red','blue'] ✗ (length mismatch)",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "REQUIRED: Array of x-coordinates for the points. MUST have same length as y array (and c/point_labels arrays if used). MUST contain the INDEPENDENT VARIABLE for the plot, which is the unmeasured variable (e.g., time, sample number, etc.)."
                },
                "y": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "REQUIRED: Array of y-coordinates for the points. MUST have same length as x array (and c/point_labels arrays if used). MUST contain the DEPENDENT VARIABLE for the plot, which is the measured variable (e.g., temperature, weight, length, etc.)."
                },
                "s": {
                    "type": "number",
                    "description": "Size of all markers. Use 100 (small), 200 (medium), 300 (large), 400 (very large)."
                },
                "marker": {
                    "type": "string", 
                    "description": "Shape of all markers. Options: 'o' (circle), 's' (square), '^' (triangle), '*' (star), '+' (plus), 'x' (x-mark), 'v' (triangle down), 'd' (diamond)."
                },
                "c": {
                    "type": ["string", "array", "null"],
                    "items": {"type": "string"},
                    "description": "REQUIRED: Color(s) for the points. CRITICAL: If using an array, it MUST have exactly the same length as x and y arrays. Options: (1) Single color string (e.g. 'red', 'blue', '#FF5733') - applies to all points, (2) Array of color strings - one per point, MUST match x/y length exactly, (3) null - uses default blue for all points."
                },
                "point_labels": {
                    "type": ["array", "null"],
                    "items": {"type": ["string", "null"]},
                    "description": "REQUIRED: Labels for individual points. CRITICAL: If using an array, it MUST have exactly the same length as x and y arrays. Options: (1) Array of strings/nulls - one per point, MUST match x/y length exactly. Use null for points without labels. (2) null - no labels for any points."
                },
                "title": {
                    "type": "string",
                    "description": "Title for the plot"
                },
                "xlabel": {
                    "type": "string",
                    "description": "Label for the x-axis"
                },
                "ylabel": {
                    "type": "string", 
                    "description": "Label for the y-axis"
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
                    "description": "Whether to display x-axis tick labels as mathematical fractions instead of decimals (e.g. properly formatted '1/4' instead of '0.25'). When creating a plot for content that uses fractions rather than decimals, YOU MUST ALWAYS set this to True."
                },
                "x_axis_fraction_denominator": {
                    "type": ["integer", "null"],
                    "description": "Optional denominator to use for ALL x-axis fractions without simplifying (e.g. 4 for quarters: 1/4, 2/4, 3/4, 4/4, 5/4, etc.). If set to null, will auto-detect appropriate denominators and display simplified fractions. If provided, maintains the denominator without simplifying."
                },
                "y_axis_show_fractions": {
                    "type": "boolean",
                    "description": "Whether to display y-axis tick labels as mathematical fractions instead of decimals (e.g. properly formatted '1/4' instead of '0.25'). When creating a plot for content that uses fractions rather than decimals, YOU MUST ALWAYS set this to True."
                },
                "y_axis_fraction_denominator": {
                    "type": ["integer", "null"],
                    "description": "Optional denominator to use for ALL y-axis fractions without simplifying (e.g. 4 for quarters: 1/4, 2/4, 3/4, 4/4, 5/4, etc.). If set to null, will auto-detect appropriate denominators and display simplified fractions. If provided, maintains the denominator without simplifying."
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the chart. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code.",
                    "default": "transparent"
                },
                "linestyle": {
                    "type": "string",
                    "description": "REQUIRED. Style of the line connecting points. Must be one of: '-' (solid), '--' (dashed), ':' (dotted), '-.' (dash-dot), or 'None' (no connecting lines). Use 'None' to draw only scatter points without connecting lines.",
                    "default": "None"
                },
                "grid": {
                    "type": "boolean",
                    "description": "Whether to show grid lines on the plot.",
                    "default": True
                }
            },
            "required": ["x", "y", "s", "marker", "c", "point_labels", "title", "xlabel", "ylabel", "xlim", "ylim", "x_axis_interval", "y_axis_interval", "x_axis_show_fractions", "x_axis_fraction_denominator", "y_axis_show_fractions", "y_axis_fraction_denominator", "background_color", "linestyle", "grid"]
        }
    }
    
    return spec, plot_scatter 