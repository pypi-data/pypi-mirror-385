from __future__ import annotations

import io
import logging
from typing import Callable, Optional
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
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

def generate_ruler_image(length: int = 12, tick_precision: float = 0.25, background_color: str = 'transparent') -> str:
    """
    Generate an image of a ruler with specified length and tick precision.
    
    Parameters
    ----------
    length : int, default 12
        The length of the ruler in some unit (e.g., 6, 12, 18, 30)
    tick_precision : float, default 0.25
        The interval between ticks as a fraction of a unit (e.g., 0.25 for quarter-unit ticks, 0.1 for tenth-unit ticks)
    background_color : str, default 'white'
        The background color behind the ruler. Use 'transparent' for transparent background,
        or any valid matplotlib color name or hex code. The ruler itself remains wheat-colored.
        
    Returns
    -------
    str
        The URL of the generated ruler image
    """
    logger.info(f"Generating ruler image with length: {length} inches, precision: {tick_precision}, background: {background_color}")
    
    # Validate inputs
    if length <= 0:
        length = 12
    if tick_precision <= 0 or tick_precision > 1:
        tick_precision = 0.25
    
    # Create figure - adjust size based on ruler length for better readability
    fig_width = max(14, length * 0.8)  # Scale width with ruler length
    fig = plt.figure(figsize=(fig_width, 4), dpi=100)
    
    # Set figure and axes background
    if background_color == 'transparent':
        fig.patch.set_alpha(0)
    else:
        fig.patch.set_facecolor(background_color)
    
    fig.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.15)
    ax = fig.add_subplot(111)
    
    # Set equal aspect ratio and remove axes
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Set axes background to match figure
    if background_color == 'transparent':
        ax.patch.set_alpha(0)
    else:
        ax.patch.set_facecolor(background_color)
    
    # Define ruler dimensions in the coordinate system
    ruler_width = 10.0  # Fixed visual width regardless of actual length
    ruler_height = 0.8
    ruler_x = 0.5
    ruler_y = 0.5
    
    # Draw ruler body
    ruler_body = Rectangle((ruler_x, ruler_y), ruler_width, ruler_height, 
                          fill=True, facecolor='wheat', edgecolor='black', linewidth=2)
    ax.add_patch(ruler_body)
    
    # Calculate tick positions and heights
    def get_tick_height(position: float) -> float:
        """Calculate tick height based on position and precision hierarchy."""
        # Convert position to a fraction for easier calculation
        pos_frac = position % 1
        
        # Define tick heights (relative to ruler height)
        base_height = ruler_height * 0.55  # Base tick height for integers
        
        # Integer positions always get the tallest ticks
        if abs(pos_frac) < 1e-10 or abs(pos_frac - 1) < 1e-10:
            return base_height
        
        # Handle all fractional cases with proper hierarchy
        if abs(pos_frac - 0.5) < 1e-10:  # Half-unit
            return base_height * 0.7
        elif abs(pos_frac - 0.25) < 1e-10 or abs(pos_frac - 0.75) < 1e-10:  # Quarter-unit
            return base_height * 0.5
        elif abs(pos_frac - 0.125) < 1e-10 or abs(pos_frac - 0.375) < 1e-10 or \
             abs(pos_frac - 0.625) < 1e-10 or abs(pos_frac - 0.875) < 1e-10:  # Eighth-unit
            return base_height * 0.35
        elif abs(pos_frac - 0.0625) < 1e-10 or abs(pos_frac - 0.1875) < 1e-10 or \
             abs(pos_frac - 0.3125) < 1e-10 or abs(pos_frac - 0.4375) < 1e-10 or \
             abs(pos_frac - 0.5625) < 1e-10 or abs(pos_frac - 0.6875) < 1e-10 or \
             abs(pos_frac - 0.8125) < 1e-10 or abs(pos_frac - 0.9375) < 1e-10:  # Sixteenth-unit
            return base_height * 0.25
        
        # Handle decimal intervals for metric rulers
        elif tick_precision == 0.1:
            if abs(pos_frac - 0.5) < 1e-10:  # 0.5 gets medium height
                return base_height * 0.7
            else:  # Other tenths get small height
                return base_height * 0.4
        elif abs(tick_precision - 1/3) < 1e-10:  # Third intervals
            if abs(pos_frac - 1/3) < 1e-10 or abs(pos_frac - 2/3) < 1e-10:
                return base_height * 0.7
        
        # Default small tick
        return base_height * 0.4
    
    # Generate tick positions
    tick_positions = []
    current_pos = 0
    while current_pos <= length:
        tick_positions.append(current_pos)
        current_pos += tick_precision
    
    # Draw ticks and labels
    bold_font = FontProperties(weight='bold')
    
    for pos in tick_positions:
        if pos > length:
            break
            
        # Calculate tick position on ruler
        tick_x = ruler_x + (pos / length) * ruler_width
        tick_height = get_tick_height(pos)
        
        # Draw tick line with width based on height
        if tick_height >= ruler_height * 0.35:  # Larger ticks
            line_width = 2
        else:  # Smaller ticks
            line_width = 1
        
        ax.plot([tick_x, tick_x], [ruler_y, ruler_y + tick_height], 'k-', linewidth=line_width)
        
        # Add labels for every integer position (except 0 and end) - SUPER SIMPLE
        # Use better floating point comparison to handle precision errors
        rounded_pos = round(pos)
        if abs(pos - rounded_pos) < 1e-6 and rounded_pos != 0 and rounded_pos != length:  # Integer position, not at edges
            label = str(int(rounded_pos))
            
            # Use appropriate font size based on ruler length (14pt minimum)
            if length <= 24:
                fontsize = 20
            else:
                fontsize = 26
            
            # Place the label ON the ruler body
            label_y = ruler_y + ruler_height * 0.7  # 70% up from the bottom of the ruler
            
            text = ax.text(tick_x, label_y, label, 
                   fontsize=fontsize, ha='center', va='center', fontproperties=bold_font,
                   color='black', weight='bold', clip_on=False)
    

    
    # Set figure limits based on ruler dimensions
    margin = 0.2
    ax.set_xlim(ruler_x - margin, ruler_x + ruler_width + margin)
    ax.set_ylim(ruler_y - margin, ruler_y + ruler_height + margin)  # Normal spacing since labels are on ruler
    
    # Save to a bytes buffer
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0.1,
                transparent=(background_color == 'transparent'))
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

def generate_ruler_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_ruler_image",
        "description": "Generate an image of a ruler with specified length and tick precision. The ruler will show appropriate tick marks and labels based on the precision setting.",
        "parameters": {
            "type": "object",
            "properties": {
                "length": {
                    "type": "integer",
                    "description": "The length of the ruler (e.g., 6, 12, 18, 30). The unit need not be specified. Default is 12."
                },
                "tick_precision": {
                    "type": "number",
                    "description": "The interval between ticks as a fraction of the length a unit (e.g., 0.25 for quarter-interval ticks, 0.125 for eighth-interval ticks, 0.1 for tenth-interval ticks). Must be between 0.0 and 1.0. Default is 0.25."
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the ruler. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code. The ruler itself remains wheat-colored. Defaults to 'transparent'."
                }
            },
            "required": ["length", "tick_precision", "background_color"]
        }
    }
    return spec, generate_ruler_image 