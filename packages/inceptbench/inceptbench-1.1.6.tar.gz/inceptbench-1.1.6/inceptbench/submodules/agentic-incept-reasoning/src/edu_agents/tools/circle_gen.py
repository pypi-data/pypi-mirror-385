from __future__ import annotations

import io
import logging
from typing import Callable, Optional, List, Dict, Any
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch
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

def generate_circle_image(elements: List[Dict[str, Any]]) -> str:
    """
    Generate an image of a circle with radii or diameters drawn on it.
    
    Parameters
    ----------
    elements : List[Dict[str, Any]]
        List of elements to draw on the circle. Each element should have:
        - type: "radius" or "diameter"
        - theta: angle in degrees (0 = right, 90 = top, 180 = left, 270 = bottom)
        - color: color of the line (e.g., "red", "blue", "#FF0000")
        - label: optional text label to place by the element, or None
        
    Returns
    -------
    str
        The URL of the generated circle image
    """
    logger.info(f"Generating circle image with {len(elements)} elements")
    
    # Create figure and axes with tight layout
    fig = plt.figure(figsize=(10, 10), dpi=100)
    fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    ax = fig.add_subplot(111)
    
    # Set equal aspect ratio and remove axes
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Circle center and radius
    center_x, center_y = 0.5, 0.5
    circle_radius = 0.35
    
    # Draw circle outline
    circle = Circle((center_x, center_y), circle_radius, fill=False, edgecolor='black', linewidth=8)
    ax.add_patch(circle)
    
    # Process each element
    for element in elements:
        element_type = element.get('type', 'radius').lower()
        theta = element.get('theta', 0)
        color = element.get('color', 'blue')
        label = element.get('label', None)
        
        # Convert theta to radians
        theta_rad = np.radians(theta)
        
        # Calculate endpoint coordinates
        end_x = center_x + circle_radius * np.cos(theta_rad)
        end_y = center_y + circle_radius * np.sin(theta_rad)
        
        if element_type == 'radius':
            # Draw radius from center to edge with arrowhead at the end
            arrow = FancyArrowPatch(
                (center_x, center_y), (end_x, end_y),
                color=color,
                linewidth=6,
                arrowstyle='-|>',
                mutation_scale=40
            )
            ax.add_patch(arrow)
            
            # Place label at the midpoint of the radius, slightly offset
            if label:
                label_x = center_x + (circle_radius * 0.6) * np.cos(theta_rad)
                label_y = center_y + (circle_radius * 0.6) * np.sin(theta_rad)
                
                # Offset label perpendicular to the radius
                offset_x = -0.06 * np.sin(theta_rad)
                offset_y = 0.06 * np.cos(theta_rad)
                
                text = ax.text(label_x + offset_x, label_y + offset_y, label, 
                             fontsize=28, ha='center', va='center', 
                             color=color, weight='bold')
                text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
        
        elif element_type == 'diameter':
            # Calculate opposite endpoint
            opposite_x = center_x - circle_radius * np.cos(theta_rad)
            opposite_y = center_y - circle_radius * np.sin(theta_rad)
            
            # Draw diameter line slightly shorter to avoid overlapping with circle edge
            line_radius = circle_radius - 0.02  # Slightly shorter than full radius
            line_opposite_x = center_x - line_radius * np.cos(theta_rad)
            line_opposite_y = center_y - line_radius * np.sin(theta_rad)
            line_end_x = center_x + line_radius * np.cos(theta_rad)
            line_end_y = center_y + line_radius * np.sin(theta_rad)
            
            ax.plot([line_opposite_x, line_end_x], [line_opposite_y, line_end_y], color=color, linewidth=6)
            
            # Add arrowheads at both ends
            arrow1 = FancyArrowPatch(
                (center_x + 0.9 * (opposite_x - center_x), center_y + 0.9 * (opposite_y - center_y)),
                (opposite_x, opposite_y),
                color=color,
                linewidth=6,
                arrowstyle='-|>',
                mutation_scale=40
            )
            
            arrow2 = FancyArrowPatch(
                (center_x + 0.9 * (end_x - center_x), center_y + 0.9 * (end_y - center_y)),
                (end_x, end_y),
                color=color,
                linewidth=6,
                arrowstyle='-|>',
                mutation_scale=40
            )
            
            ax.add_patch(arrow1)
            ax.add_patch(arrow2)
            
            # Place label near the center of the circle, slightly offset from the diameter line
            if label:
                # Position label very close to center with small perpendicular offset
                offset_x = -0.06 * np.sin(theta_rad)
                offset_y = 0.06 * np.cos(theta_rad)
                
                text = ax.text(center_x + offset_x, center_y + offset_y, label, 
                             fontsize=28, ha='center', va='center', 
                             color=color, weight='bold')
                text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])

    # Draw center dot on top of everything
    center_dot = Circle((center_x, center_y), 0.01, fill=True, facecolor='black', zorder=10)
    ax.add_patch(center_dot)

    # Set figure limits with padding to avoid cropping
    ax.set_xlim(0.05, 0.95)
    ax.set_ylim(0.05, 0.95)
    
    # Save to a bytes buffer with tight layout
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0.1)
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

def generate_circle_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_circle_image",
        "description": "Generate an image of a circle with radii or diameters drawn on it. Each element can be a radius (from center to edge) or diameter (across the full circle), with customizable colors and labels.",
        "parameters": {
            "type": "object",
            "properties": {
                "elements": {
                    "type": "array",
                    "description": "List of elements to draw on the circle",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["radius", "diameter"],
                                "description": "Whether to draw a radius (from center to edge) or diameter (across the full circle)"
                            },
                            "theta": {
                                "type": "number",
                                "description": "Angle in degrees to place the element (0 = right, 90 = top, 180 = left, 270 = bottom)"
                            },
                            "color": {
                                "type": "string",
                                "description": "Color of the line (e.g., 'red', 'blue', '#FF0000')"
                            },
                            "label": {
                                "type": ["string", "null"],
                                "description": "Optional text label to place by the element, or null for no label"
                            }
                        },
                        "required": ["type", "theta", "color"]
                    }
                }
            },
            "required": ["elements"]
        }
    }
    return spec, generate_circle_image 