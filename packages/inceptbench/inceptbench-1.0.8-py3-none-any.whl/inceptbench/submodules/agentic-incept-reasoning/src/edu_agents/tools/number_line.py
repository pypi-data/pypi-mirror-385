import io
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import logging
from typing import Optional, Dict, Any, Callable, List
from utils.supabase_utils import upload_image_to_supabase

# Set matplotlib to use a non-interactive backend
matplotlib.use('Agg')

# Configure matplotlib to prevent memory leaks and limit figure accumulation
matplotlib.rcParams['figure.max_open_warning'] = 5  # Warn much earlier
matplotlib.rcParams['figure.raise_window'] = False   # Don't raise GUI windows

logger = logging.getLogger(__name__)


def plot_number_line(
    ticks: List[str],
    highlight_ranges: Optional[List[Dict[str, Any]]] = None,
    highlight_points: Optional[List[Dict[str, Any]]] = None,
    background_color: str = 'transparent',
    left_arrow: bool = False,
    left_arrow_color: str = 'black',
    right_arrow: bool = False,
    right_arrow_color: str = 'black'
) -> str:
    """
    Draw a number line with ticks, labels, highlight ranges, and highlight points.

    Parameters
    ----------
    ticks : List[str]
        Labels for the ticks to show on the number line. The first label is for the start,
        the last label is for the end, and any labels in between are evenly spaced.
        Empty strings indicate intentionally unlabeled ticks.
    highlight_ranges : Optional[List[Dict[str, Any]]]
        List of highlight range dictionaries with properties:
        - start_tick: float - index of starting tick (decimals supported)
        - end_tick: float - index of ending tick (decimals supported)  
        - color: str - color for the highlight range
    highlight_points : Optional[List[Dict[str, Any]]]
        List of highlight point dictionaries with properties:
        - tick: float - index of tick to highlight (decimals supported)
        - color: str - color for the highlight point
    background_color : str, default 'transparent'
        The background color behind the number line. Use 'transparent' for transparent background,
        or any valid matplotlib color name or hex code.
    left_arrow : bool, default False
        Whether to draw an arrow pointing left at the start of the number line.
        Useful for representing ranges that extend to negative infinity.
    left_arrow_color : str, default 'black'
        Color for the left arrow (e.g. 'red', 'blue', '#FF5733').
    right_arrow : bool, default False
        Whether to draw an arrow pointing right at the end of the number line.
        Useful for representing ranges that extend to positive infinity.
    right_arrow_color : str, default 'black'
        Color for the right arrow (e.g. 'red', 'blue', '#FF5733').
        
    Returns
    -------
    str
        URL of the generated image
    """
    try:
        print("Number line parameters:")
        print(f"Ticks: {ticks}")
        print(f"Highlight ranges: {highlight_ranges}")
        print(f"Highlight points: {highlight_points}")
        print(f"Background color: {background_color}")
        print(f"Left arrow: {left_arrow}, color: {left_arrow_color}")
        print(f"Right arrow: {right_arrow}, color: {right_arrow_color}")
        
        if len(ticks) < 2:
            raise ValueError("Ticks must have at least 2 elements (start and end)")
        
        # Create figure with 16:9 aspect ratio (1920x1080 at 100 DPI)
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        
        # Set figure and axes background
        if background_color == 'transparent':
            fig.patch.set_alpha(0)
            ax.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(background_color)
            ax.patch.set_facecolor(background_color)
        
        # Number of tick positions
        n_ticks = len(ticks)
        
        # Set up coordinate system - number line will be horizontal in the middle
        # Use wider coordinate system to match 16:9 aspect ratio
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 9)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Number line parameters - make everything much larger
        line_y = 4.5  # Vertical center
        line_start_x = 2
        line_end_x = 14
        line_length = line_end_x - line_start_x
        tick_height = 1.0  # Much taller ticks
        highlight_height = 0.6  # Taller highlight ranges
        
        # Draw the main number line with thicker line (lowest z-order)
        ax.plot([line_start_x, line_end_x], [line_y, line_y], 'k-', linewidth=8, zorder=1)
        
        # Draw arrows if requested (just above the main line)
        arrow_size = tick_height # Size of arrow heads
        arrow_width = tick_height * 0.5  # Width of arrow heads
        
        if left_arrow and left_arrow_color is not None and left_arrow_color != 'none' and left_arrow_color != '' and left_arrow_color != 'transparent':
            # Draw left-pointing arrow at the start of the line
            arrow_tip_x = line_start_x - arrow_size
            arrow_base_x = line_start_x
            arrow_points = np.array([
                [arrow_tip_x, line_y],  # Arrow tip
                [arrow_base_x, line_y + arrow_width],  # Top of arrow base
                [arrow_base_x, line_y - arrow_width]   # Bottom of arrow base
            ])
            arrow_patch = plt.Polygon(arrow_points, facecolor=left_arrow_color, 
                                    edgecolor='none', zorder=1.5)
            ax.add_patch(arrow_patch)
        
        if right_arrow and right_arrow_color is not None and right_arrow_color != 'none' and right_arrow_color != '' and right_arrow_color != 'transparent':
            # Draw right-pointing arrow at the end of the line
            arrow_tip_x = line_end_x + arrow_size
            arrow_base_x = line_end_x
            arrow_points = np.array([
                [arrow_tip_x, line_y],  # Arrow tip
                [arrow_base_x, line_y + arrow_width],  # Top of arrow base
                [arrow_base_x, line_y - arrow_width]   # Bottom of arrow base
            ])
            arrow_patch = plt.Polygon(arrow_points, facecolor=right_arrow_color, 
                                    edgecolor='none', zorder=1.5)
            ax.add_patch(arrow_patch)
        
        # Calculate tick positions
        if n_ticks == 2:
            tick_positions = [line_start_x, line_end_x]
        else:
            tick_positions = np.linspace(line_start_x, line_end_x, n_ticks)
        
        # Draw ticks first (low z-order so they appear behind highlight ranges and points)
        for i, tick_pos in enumerate(tick_positions):
            # Draw tick mark with thicker line
            ax.plot([tick_pos, tick_pos], [line_y - tick_height/2, line_y + tick_height/2], 
                   'k-', linewidth=6, zorder=2)
        
        # Draw highlight ranges second (medium z-order, on top of line and ticks)
        if highlight_ranges:
            for highlight_range in highlight_ranges:
                start_tick = highlight_range['start_tick']
                end_tick = highlight_range['end_tick']
                color = highlight_range['color']
                
                # Calculate x positions for start and end
                if n_ticks == 2:
                    # Special case for 2 ticks
                    start_x = line_start_x + start_tick * line_length
                    end_x = line_start_x + end_tick * line_length
                else:
                    start_x = line_start_x + (start_tick / (n_ticks - 1)) * line_length
                    end_x = line_start_x + (end_tick / (n_ticks - 1)) * line_length
                
                # Draw rectangle
                rect_y = line_y - highlight_height / 2
                rect_width = end_x - start_x
                rect = plt.Rectangle((start_x, rect_y), rect_width, highlight_height, 
                                   facecolor=color, edgecolor='none', alpha=0.8, zorder=3)
                ax.add_patch(rect)
        
        # Draw highlight points third (high z-order, on top of everything except labels)
        if highlight_points:
            point_radius = highlight_height / 2
            for highlight_point in highlight_points:
                tick = highlight_point['tick']
                color = highlight_point['color']
                
                # Calculate x position
                if n_ticks == 2:
                    # Special case for 2 ticks
                    point_x = line_start_x + tick * line_length
                else:
                    point_x = line_start_x + (tick / (n_ticks - 1)) * line_length
                
                # Draw circle
                circle = plt.Circle((point_x, line_y), point_radius, 
                                  facecolor=color, edgecolor='none', zorder=4)
                ax.add_patch(circle)
        
        # Draw labels last with smart spacing to prevent overlap (highest z-order)
        labels_to_show = _calculate_label_spacing(ticks, tick_positions, line_length)
        
        for i, (tick_pos, label, show_label) in enumerate(zip(tick_positions, ticks, labels_to_show)):
            # Draw label if not empty and should be shown
            if label.strip() and show_label:
                ax.text(tick_pos, line_y - tick_height/2 - 0.8, label, 
                       ha='center', va='top', fontsize=32, fontweight='bold', zorder=5)
        
        # Save figure to bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                   transparent=(background_color == 'transparent'), pad_inches=0.1)
        buf.seek(0)
        
        # Upload to Supabase
        public_url = upload_image_to_supabase(
            image_bytes=buf.getvalue(),
            content_type="image/png",
            bucket_name="incept-images",
            file_extension=".png"
        )
        
        # Clean up
        plt.close(fig)
        
        return public_url
        
    except Exception as e:
        error_message = f"Error generating number line: {str(e)}"
        logger.error(error_message)
        # Ensure cleanup on error - close any figures we may have created
        try:
            if 'fig' in locals():
                plt.close(fig)
        except Exception:
            pass
        raise RuntimeError(error_message)


def generate_number_line_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the number line tool specification and function."""
    
    spec = {
        "type": "function",
        "name": "plot_number_line",
        "description": "Create a number line image with ticks, labels, highlight ranges, and highlight points.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels for the ticks on the number line. First label is at start, last at end, others evenly spaced. Empty strings create intentionally unlabeled ticks; the tool will auto-space labels to prevent overlap so do not include empty ticks for this purpose. Must have at least 2 elements."
                },
                "highlight_ranges": {
                    "type": "array",
                    "description": "Optional highlight ranges to draw on the number line",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start_tick": {
                                "type": "number",
                                "description": "Zero-based starting tick index. Decimals are supported for positions between ticks, for example, 0.5 means halfway between the first and second ticks."
                            },
                            "end_tick": {
                                "type": "number", 
                                "description": "Zero-based ending tick index. Decimals are supported for positions between ticks, for example, 0.5 means halfway between the first and second ticks."
                            },
                            "color": {
                                "type": "string",
                                "description": "Color for the highlight range (e.g. 'red', 'blue', '#FF5733')"
                            }
                        },
                        "required": ["start_tick", "end_tick", "color"]
                    }
                },
                "highlight_points": {
                    "type": "array",
                    "description": "Optional highlight points to draw on the number line",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tick": {
                                "type": "number",
                                "description": "Zero-based tick index to highlight. Decimals are supported for positions between ticks, for example, 0.5 means halfway between the first and second ticks."
                            },
                            "color": {
                                "type": "string",
                                "description": "Color for the highlight point (e.g. 'red', 'blue', '#FF5733')"
                            }
                        },
                        "required": ["tick", "color"]
                    }
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the number line. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code. Defaults to 'transparent'."
                },
                "left_arrow": {
                    "type": "boolean",
                    "description": "Whether to draw an arrow pointing left at the start of the number line. Useful for representing ranges that extend to negative infinity. Defaults to false."
                },
                "left_arrow_color": {
                    "type": "string",
                    "description": "Color for the left arrow (e.g. 'red', 'blue', '#FF5733', or any valid matplotlib color name or hex code). Defaults to 'black'. If specifying a range extends to negative infinity, the color should match the color of the range."
                },
                "right_arrow": {
                    "type": "boolean",
                    "description": "Whether to draw an arrow pointing right at the end of the number line. Useful for representing ranges that extend to positive infinity. Defaults to false."
                },
                "right_arrow_color": {
                    "type": "string",
                    "description": "Color for the right arrow (e.g. 'red', 'blue', '#FF5733', or any valid matplotlib color name or hex code). Defaults to 'black'. If specifying a range extends to positive infinity, the color should match the color of the range."
                }
            },
            "required": ["ticks"]
        }
    }
    
    return spec, plot_number_line 

def _calculate_label_spacing(ticks: List[str], tick_positions: List[float], line_length: float) -> List[bool]:
    """
    Calculate which labels to show to prevent overlap.
    Always show first and last labels, intelligently distribute middle ones evenly.
    """
    n_ticks = len(ticks)
    labels_to_show = [False] * n_ticks
    
    # Always show first and last labels if they exist
    if n_ticks >= 1:
        labels_to_show[0] = True
    if n_ticks >= 2:
        labels_to_show[-1] = True
    
    # If only 2 ticks, we're done
    if n_ticks <= 2:
        return labels_to_show
    
    # Estimate label width based on average label length
    avg_label_length = sum(len(label) for label in ticks if label.strip()) / n_ticks
    # Rough estimate: spacing is 40% of the average label length
    min_spacing = avg_label_length * 0.4
    
    # Calculate actual spacing between adjacent ticks
    if n_ticks > 2:
        tick_spacing = line_length / (n_ticks - 1)
    else:
        tick_spacing = line_length
    
    # If tick spacing is sufficient, show all labels
    if tick_spacing >= min_spacing:
        return [True] * n_ticks
    
    # Calculate how many intermediate labels we can fit
    # We need at least min_spacing between any two shown labels
    available_space = line_length - 2 * min_spacing  # Space between first/last and their neighbors
    max_intermediate_labels = int(available_space / min_spacing)
    
    # If we can't fit any intermediate labels, just show first and last
    if max_intermediate_labels <= 0:
        return labels_to_show
    
    # Choose the best intermediate labels to show
    # Strategy: distribute them as evenly as possible across the middle section
    middle_indices = list(range(1, n_ticks - 1))  # Indices of middle ticks
    
    if len(middle_indices) <= max_intermediate_labels:
        # We can show all middle labels
        for i in middle_indices:
            labels_to_show[i] = True
    else:
        # We need to select a subset of middle labels
        # Use even distribution, preferring positions closer to the center when there are ties
        selected_indices = _select_evenly_distributed_indices(
            middle_indices, max_intermediate_labels, n_ticks
        )
        for i in selected_indices:
            labels_to_show[i] = True
    
    return labels_to_show


def _select_evenly_distributed_indices(middle_indices: List[int], max_count: int, total_ticks: int) -> List[int]:
    """
    Select evenly distributed indices from the middle indices.
    When there are multiple options for similar spacing, prefer positions closer to center.
    """
    if max_count >= len(middle_indices):
        return middle_indices
    
    if max_count == 1:
        # For a single label, prefer the one closest to the center
        center_index = (total_ticks - 1) / 2
        closest_to_center = min(middle_indices, key=lambda x: abs(x - center_index))
        return [closest_to_center]
    
    # For multiple labels, distribute them evenly
    # Calculate ideal positions in the middle section
    middle_start = 1
    middle_end = total_ticks - 2
    middle_length = middle_end - middle_start
    
    selected = []
    for i in range(max_count):
        # Calculate ideal position for this label in the middle section
        ideal_pos = middle_start + (i + 1) * middle_length / (max_count + 1)
        # Find the actual tick index closest to this ideal position
        closest_index = min(middle_indices, key=lambda x: abs(x - ideal_pos))
        
        # Avoid duplicates (though this shouldn't happen with proper spacing)
        if closest_index not in selected:
            selected.append(closest_index)
    
    return sorted(selected) 