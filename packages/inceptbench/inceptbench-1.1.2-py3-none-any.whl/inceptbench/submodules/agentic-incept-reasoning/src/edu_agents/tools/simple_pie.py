import io
import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import logging
from typing import Optional, Dict, Any, Callable, List
from PIL import Image
from utils.supabase_utils import upload_image_to_supabase
from .color_utils import validate_color_list

# Set matplotlib to use a non-interactive backend
matplotlib.use('Agg')

# Configure matplotlib to prevent memory leaks and limit figure accumulation
matplotlib.rcParams['figure.max_open_warning'] = 5  # Warn much earlier
matplotlib.rcParams['figure.raise_window'] = False   # Don't raise GUI windows

logger = logging.getLogger(__name__)


def plot_pie(
    sizes: List[float],
    labels: List[str],
    *,
    colors: Optional[List[str]] = None,
    autopct: bool = False,
    pct_format: str = "{:.1f}%",
    startangle: float = 0,
    explode: Optional[List[float]] = None,
    title: Optional[str] = None,
    legend: bool = True,
    background_color: str = 'transparent'
) -> str:
    """
    Draw a pie chart of categorical data.

    Parameters
    ----------
    sizes : List[float]
        List containing the numeric sizes of each slice.
    labels : List[str]
        List containing the name of each slice (same length as sizes).
    colors : List[str]
        List containing fill colors for each slice.
    autopct : bool
        If True, label slices with their percentage of the total.
    pct_format : str
        Format string for percentages (only if autopct=True).
    startangle : float
        Rotation angle (in degrees) to start the first slice.
    explode : List[float]
        List containing fractional offset for each slice (e.g., [0.1, 0, 0] to "pop out" the first slice).
    title : str
        Plot title.
    legend : bool
        If True, draw a legend to the side.
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
        
        # sizes and labels are now already lists, no need to parse JSON
        sizes_data = sizes
        labels_data = labels
        
        print("Pie chart parameters:")
        print(f"Number of slices: {len(sizes_data)}")
        print(f"Sizes: {sizes_data}")
        print(f"Labels: {labels_data}")
        print(f"Colors: {colors}")
        print(f"Autopct: {autopct}")
        print(f"Pct_format: {pct_format}")
        print(f"Startangle: {startangle}")
        print(f"Explode: {explode}")
        print(f"Title: {title}")
        print(f"Legend: {legend}")
        print(f"Background color: {background_color}")
        
        # Validate data
        if len(sizes_data) != len(labels_data):
            raise ValueError(f"Sizes ({len(sizes_data)}) and labels ({len(labels_data)}) must have the same length")
        
        # colors and explode are now already lists or None, no need to parse JSON
        if colors:
            colors_data = validate_color_list(colors, default='blue')
            if len(colors_data) != len(sizes_data):
                raise ValueError(f"Colors ({len(colors_data)}) must have the same length as sizes ({len(sizes_data)})")
        else:
            colors_data = None
        
        explode_data = explode
        if explode_data and len(explode_data) != len(sizes_data):
            raise ValueError(f"Explode ({len(explode_data)}) must have the same length as sizes ({len(sizes_data)})")
        
        # Create inner figure with white background
        if legend:
            inner_fig = plt.figure(figsize=(10, 6))
        else:
            inner_fig = plt.figure(figsize=(8, 8))
            
        inner_fig.patch.set_facecolor('white')
        ax = inner_fig.add_subplot(111)
        ax.set_facecolor('white')
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes_data,
            labels=labels_data if not legend else None,
            colors=colors_data,
            autopct=(lambda pct: pct_format.format(pct) if autopct else None),
            startangle=startangle,
            explode=explode_data,
            textprops=dict(va="center", fontsize=18, bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1)),
            wedgeprops=dict(edgecolor='black', linewidth=0.5)  # Add black edges for better definition
        )

        # Ensure pie is drawn as a circle
        ax.axis("equal")

        # Set title with white background
        if title:
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20, bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))

        # Add legend if requested with white background
        if legend:
            ax.legend(wedges, labels_data, title="Categories", 
                     loc="center left", bbox_to_anchor=(1, 0.5),
                     fontsize=18, title_fontsize=18,
                     facecolor='white', framealpha=0.8)

        # Improve text readability for percentage labels
        if autopct and autotexts:
            for autotext in autotexts:
                autotext.set_color('black')  # Changed from 'white' to 'black'
                autotext.set_fontweight('bold')
                autotext.set_fontsize(18)
                # Add white background to percentage labels
                autotext.set_bbox(dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))

        # Save inner figure with white background and inner padding
        inner_buf = io.BytesIO()
        if legend:
            plt.subplots_adjust(left=0.1, right=0.75)
        inner_fig.savefig(inner_buf, format='png', dpi=300, bbox_inches='tight',
                         pad_inches=0.15, facecolor='white')
        inner_buf.seek(0)
        plt.close(inner_fig)

        # Create outer figure with specified background color
        if legend:
            outer_fig = plt.figure(figsize=(10.5, 6.5))
        else:
            outer_fig = plt.figure(figsize=(8.5, 8.5))
            
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
        error_message = f"Error generating pie chart: {str(e)}"
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


def generate_simple_pie_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the simple pie chart tool specification and function."""
    
    spec = {
        "type": "function",
        "name": "plot_pie",
        "description": "Create pie charts to show proportions and percentages of categorical data. Each slice represents a category's share of the total.",
        "parameters": {
            "type": "object",
            "properties": {
                "sizes": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    },
                    "description": "List containing numeric sizes of each slice. Example: '[30, 25, 20, 15, 10]'"
                },
                "labels": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List containing names for each slice (same length as sizes). Example: '[\"Category A\", \"Category B\", \"Category C\", \"Category D\", \"Category E\"]'"
                },
                "colors": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List containing fill colors for each slice. Can use color names or hex codes. Example: '[\"red\", \"blue\", \"green\", \"orange\", \"purple\"]' or '[\"#FF6B6B\", \"#4ECDC4\", \"#45B7D1\"]'"
                },
                "autopct": {
                    "type": "boolean",
                    "description": "Whether to label slices with their percentage of the total."
                },
                "pct_format": {
                    "type": "string",
                    "description": "Format string for percentages (only used if autopct=true). Examples: '{:.1f}%' (1 decimal), '{:.0f}%' (whole numbers)."
                },
                "startangle": {
                    "type": "number",
                    "description": "Rotation angle (in degrees) to start the first slice. 0 starts at 3 o'clock, 90 starts at 12 o'clock."
                },
                "explode": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    },
                    "description": "List containing fractional offset for each slice to 'pop out' certain slices. Example: '[0.1, 0, 0, 0, 0]' to explode the first slice. Values typically between 0 and 0.3."
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "legend": {
                    "type": "boolean",
                    "description": "Whether to show a legend to the side listing all categories."
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the chart. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code.",
                    "default": "transparent"
                }
            },
            "required": [
                "sizes",
                "labels",
                "colors",
                "autopct",
                "pct_format",
                "startangle",
                "explode",
                "title",
                "legend",
                "background_color"
            ]
        }
    }
    
    return spec, plot_pie 