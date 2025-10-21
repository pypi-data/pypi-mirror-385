from __future__ import annotations

import io
import logging
from typing import Callable, Optional, List, Dict, Any
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Arc, Wedge
import matplotlib.patheffects as path_effects
from matplotlib.font_manager import FontProperties

from utils.supabase_utils import upload_image_to_supabase
import matplotlib

# Set matplotlib to use a non-interactive backend
matplotlib.use('Agg')

# Configure matplotlib to prevent memory leaks and limit figure accumulation
matplotlib.rcParams['figure.max_open_warning'] = 5  # Warn much earlier
matplotlib.rcParams['figure.raise_window'] = False   # Don't raise GUI windows

logger = logging.getLogger(__name__)

def generate_intersecting_lines_image(
    line_one_theta: float,
    line_two_theta: float,
    line_1_color: str = 'blue',
    line_2_color: str = 'red',
    angle_1_label: Optional[str] = None,
    angle_2_label: Optional[str] = None,
    angle_3_label: Optional[str] = None,
    angle_4_label: Optional[str] = None,
    angle_1_arc_color: Optional[str] = None,
    angle_2_arc_color: Optional[str] = None,
    angle_3_arc_color: Optional[str] = None,
    angle_4_arc_color: Optional[str] = None,
    background_color: str = 'transparent'
) -> str:
    """
    Generate an image of two intersecting lines with labeled angles.
    
    Parameters
    ----------
    line_one_theta : float
        Angle in degrees for the first line (0 = right, 90 = top, etc.)
    line_two_theta : float
        Angle in degrees for the second line (0 = right, 90 = top, etc.)
    line_1_color : str, default 'blue'
        Color for the first line
    line_2_color : str, default 'red'
        Color for the second line
    angle_1_label through angle_4_label : Optional[str]
        Labels for the angles, numbered clockwise from 12 o'clock
    angle_1_arc_color through angle_4_arc_color : Optional[str]
        Colors for angle arcs, or None for no arc
    background_color : str, default 'white'
        The background color behind the lines. Use 'transparent' for transparent background,
        or any valid matplotlib color name or hex code.
        
    Returns
    -------
    str
        The URL of the generated intersecting lines image
    """
    logger.info(f"Generating intersecting lines image: line1={line_one_theta}°, line2={line_two_theta}°, background={background_color}")
    
    # Create figure and axes with tight layout
    fig = plt.figure(figsize=(10, 10), dpi=100)
    if background_color == 'transparent':
        fig.patch.set_alpha(0)
    else:
        fig.patch.set_facecolor(background_color)
    
    fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    ax = fig.add_subplot(111)
    
    # Set equal aspect ratio and remove axes
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Set axes background to match figure
    if background_color == 'transparent':
        ax.patch.set_alpha(0)
    else:
        ax.patch.set_facecolor(background_color)
    
    # Center point
    center_x, center_y = 0.5, 0.5
    line_length = 0.4
    
    # Convert angles to radians
    line1_rad = np.radians(line_one_theta)
    line2_rad = np.radians(line_two_theta)
    
    # Calculate line endpoints
    line1_end1_x = center_x - line_length * np.cos(line1_rad)
    line1_end1_y = center_y - line_length * np.sin(line1_rad)
    line1_end2_x = center_x + line_length * np.cos(line1_rad)
    line1_end2_y = center_y + line_length * np.sin(line1_rad)
    
    line2_end1_x = center_x - line_length * np.cos(line2_rad)
    line2_end1_y = center_y - line_length * np.sin(line2_rad)
    line2_end2_x = center_x + line_length * np.cos(line2_rad)
    line2_end2_y = center_y + line_length * np.sin(line2_rad)
    
    # Draw the lines
    ax.plot([line1_end1_x, line1_end2_x], [line1_end1_y, line1_end2_y], 
            color=line_1_color, linewidth=6)
    ax.plot([line2_end1_x, line2_end2_x], [line2_end1_y, line2_end2_y], 
            color=line_2_color, linewidth=6)
    
    # Calculate the four line segments (rays) created by the two lines
    # Each line creates two rays in opposite directions
    line_segments = [
        line_one_theta,           # Line 1 positive direction
        line_one_theta + 180,     # Line 1 negative direction  
        line_two_theta,           # Line 2 positive direction
        line_two_theta + 180      # Line 2 negative direction
    ]
    
    # Normalize all angles to 0-360
    line_segments = [((a % 360) + 360) % 360 for a in line_segments]
    
    # Sort line segments by angle
    line_segments.sort()
    
    # Calculate angle pairs for the four regions
    # Each region is bounded by two adjacent line segments
    angle_pairs = []
    for i in range(4):
        start_angle = line_segments[i]
        end_angle = line_segments[(i + 1) % 4]
        angle_pairs.append((start_angle, end_angle))
    
    # Draw arcs and labels for each angle
    arc_radius = 0.05
    label_radius = 0.08
    
    labels = [angle_1_label, angle_2_label, angle_3_label, angle_4_label]
    arc_colors = [angle_1_arc_color, angle_2_arc_color, angle_3_arc_color, angle_4_arc_color]
    
    for i, (label, arc_color) in enumerate(zip(labels, arc_colors)):
        start_angle, end_angle = angle_pairs[i]
        
        # Calculate the middle angle for label positioning
        if end_angle < start_angle:
            end_angle += 360
        mid_angle = (start_angle + end_angle) / 2
        mid_angle_rad = np.radians(mid_angle)
        
        # Draw arc if color is specified
        if arc_color is not None:
            # Draw the arc from start_angle to end_angle (tangent to the lines)
            arc = Arc((center_x, center_y), 2 * arc_radius, 2 * arc_radius,
                     theta1=start_angle, theta2=end_angle, color=arc_color, linewidth=4)
            ax.add_patch(arc)
        
        # Draw label if specified
        if label is not None:
            label_x = center_x + label_radius * np.cos(mid_angle_rad)
            label_y = center_y + label_radius * np.sin(mid_angle_rad)
            
            # Use arc color for label if specified, otherwise black
            label_color = arc_color if arc_color is not None else 'black'
            
            text = ax.text(label_x, label_y, label, 
                         fontsize=28, ha='center', va='center', 
                         color=label_color, weight='bold')
            text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    
    # Set figure limits with padding to avoid cropping
    ax.set_xlim(0.05, 0.95)
    ax.set_ylim(0.05, 0.95)
    
    # Save to a bytes buffer with tight layout
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0.1,
                transparent=(background_color == 'transparent'))  # Enable transparency if requested
    buf.seek(0)
    plt.close(fig)
    
    # Upload the image to Supabase
    image_bytes = buf.getvalue()
    public_url = upload_image_to_supabase(
        image_bytes=image_bytes,
        content_type="image/png",
        bucket_name="incept-images"
    )
    
    return public_url

def generate_intersecting_lines_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_intersecting_lines_image",
        "description": "Generate an image of two intersecting lines with labeled angles. The angles are numbered clockwise from 12 o'clock position.",
        "parameters": {
            "type": "object",
            "properties": {
                "line_one_theta": {
                    "type": "number",
                    "description": "Angle in degrees for the first line (0 = right, 90 = top, 180 = left, 270 = bottom)"
                },
                "line_two_theta": {
                    "type": "number",
                    "description": "Angle in degrees for the second line (0 = right, 90 = top, 180 = left, 270 = bottom)"
                },
                "line_1_color": {
                    "type": "string",
                    "description": "Color for the first line (e.g., 'blue', 'red', '#FF0000')"
                },
                "line_2_color": {
                    "type": "string",
                    "description": "Color for the second line (e.g., 'blue', 'red', '#FF0000')"
                },
                "angle_1_label": {
                    "type": ["string", "null"],
                    "description": "Label for the first angle (clockwise from 12 o'clock), or null for no label"
                },
                "angle_2_label": {
                    "type": ["string", "null"],
                    "description": "Label for the second angle (clockwise from 12 o'clock), or null for no label"
                },
                "angle_3_label": {
                    "type": ["string", "null"],
                    "description": "Label for the third angle (clockwise from 12 o'clock), or null for no label"
                },
                "angle_4_label": {
                    "type": ["string", "null"],
                    "description": "Label for the fourth angle (clockwise from 12 o'clock), or null for no label"
                },
                "angle_1_arc_color": {
                    "type": ["string", "null"],
                    "description": "Color for arc showing angle 1, or null for no arc. If specified, the label will also be this color."
                },
                "angle_2_arc_color": {
                    "type": ["string", "null"],
                    "description": "Color for arc showing angle 2, or null for no arc. If specified, the label will also be this color."
                },
                "angle_3_arc_color": {
                    "type": ["string", "null"],
                    "description": "Color for arc showing angle 3, or null for no arc. If specified, the label will also be this color."
                },
                "angle_4_arc_color": {
                    "type": ["string", "null"],
                    "description": "Color for arc showing angle 4, or null for no arc. If specified, the label will also be this color."
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the lines. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code. Defaults to 'transparent'."
                }
            },
            "required": ["line_one_theta", "line_two_theta", "line_1_color", "line_2_color", "background_color"]
        }
    }
    return spec, generate_intersecting_lines_image 