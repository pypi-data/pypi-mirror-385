from __future__ import annotations

import io
import logging
from typing import Callable, Optional
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
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

def generate_clock_image(
    hour: Optional[int] = None, 
    minute: Optional[int] = None, 
    second: Optional[int] = None,
    background_color: Optional[str] = 'transparent'
) -> str:
    """
    Generate an image of a clock with optional hour, minute, and second hands.
    
    Parameters
    ----------
    hour : Optional[int], default None
        The hour (0-23), if None, hour hand won't be shown
    minute : Optional[int], default None
        The minute (0-59), if None, minute hand won't be shown
    second : Optional[int], default None
        The second (0-59), if None, second hand won't be shown
    background_color : Optional[str], default 'transparent'
        The background color behind the clock. Use 'transparent' for transparent background,
        or any valid matplotlib color name or hex code. The clock face itself remains white.
        
    Returns
    -------
    str
        The URL of the generated clock image
    """
    logger.info(f"Generating clock image for time: {hour}:{minute}:{second} with background: {background_color}")
    hour = None if hour is None or hour < 0 else hour
    minute = None if minute is None or minute < 0 else minute
    second = None if second is None or second < 0 else second
    
    # Convert to 12-hour format if hour is provided
    hour_12 = None
    if hour is not None:
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12
    
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
    
    # Draw clock face with adjusted radius to avoid cropping - always white
    face = Circle((0.5, 0.5), 0.4, fill=True, facecolor='white', edgecolor='black', linewidth=10)
    ax.add_patch(face)
    
    # Draw minute ticks first
    for i in range(60):
        angle = i * 6  # 6 degrees per minute
        rad = np.radians(angle)
        
        if i % 5 == 0:  # 5-minute/hour ticks - thicker and shorter
            tick_outer_x = 0.5 + 0.4 * np.sin(rad)
            tick_outer_y = 0.5 + 0.4 * np.cos(rad)
            tick_inner_x = 0.5 + 0.35 * np.sin(rad)
            tick_inner_y = 0.5 + 0.35 * np.cos(rad)
            ax.plot([tick_inner_x, tick_outer_x], [tick_inner_y, tick_outer_y], 'k-', linewidth=4)  # Twice as thick
        else:  # 1-minute ticks
            tick_outer_x = 0.5 + 0.4 * np.sin(rad) 
            tick_outer_y = 0.5 + 0.4 * np.cos(rad)
            tick_inner_x = 0.5 + 0.37 * np.sin(rad)
            tick_inner_y = 0.5 + 0.37 * np.cos(rad)
            ax.plot([tick_inner_x, tick_outer_x], [tick_inner_y, tick_outer_y], 'k-', linewidth=1)
    
    bold_font = FontProperties(weight='bold')

    # Draw hour numbers, properly inset and with larger font
    for i in range(12):
        hour_num = i if i != 0 else 12  # 12 at the top (i=0), then 1-11 clockwise
        angle = i * 30  # 30 degrees per hour
        rad = np.radians(angle)
        
        if hour_num < 10:
            radius_factor = 0.314
        else:
            radius_factor = 0.295

        x = 0.5 + radius_factor * np.sin(rad)
        y = 0.5 + radius_factor * np.cos(rad)
        
        text = ax.text(x, y, str(hour_num), fontsize=48, ha='center', va='center', 
                     fontproperties=bold_font)
        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    
    # Calculate hand angles and draw hands only if parameters are provided
    
    # Draw hour hand (shorter and thicker) only if hour is provided
    if hour is not None:
        # Use minute value for gradual movement, default to 0 if not provided
        minute_for_hour = minute if minute is not None else 0
        hour_angle = 90 - (hour_12 * 30 + minute_for_hour / 2)  # 30 degrees per hour, plus gradual movement
        hour_length = 0.2
        hour_rad = np.radians(hour_angle)
        hour_x = 0.5 + hour_length * np.cos(hour_rad)
        hour_y = 0.5 + hour_length * np.sin(hour_rad)
        ax.plot([0.5, hour_x], [0.5, hour_y], 'k-', linewidth=10)
    
    # Draw minute hand (longer and thinner) only if minute is provided
    if minute is not None:
        minute_angle = 90 - (minute * 6)  # 6 degrees per minute
        minute_length = 0.26
        minute_rad = np.radians(minute_angle)
        minute_x = 0.5 + minute_length * np.cos(minute_rad)
        minute_y = 0.5 + minute_length * np.sin(minute_rad)
        ax.plot([0.5, minute_x], [0.5, minute_y], 'k-', linewidth=5)
    
    # Draw second hand if seconds are provided (thin and red)
    if second is not None:
        second_angle = 90 - (second * 6)  # 6 degrees per second
        second_length = 0.27
        second_rad = np.radians(second_angle)
        second_x = 0.5 + second_length * np.cos(second_rad)
        second_y = 0.5 + second_length * np.sin(second_rad)
        ax.plot([0.5, second_x], [0.5, second_y], 'r-', linewidth=2)
    
    # Draw center dot
    center = Circle((0.5, 0.5), 0.02, fill=True, facecolor='black')
    ax.add_patch(center)
    
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

def generate_clock_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_clock_image",
        "description": "Generate an image of a clock displaying a specific time. Any time parameter set to None will not have a hand drawn for that time component.",
        "parameters": {
            "type": "object",
            "properties": {
                "hour": {
                    "type": "integer",
                    "description": "The hour (0-23). Set this to None or a negative number if the content does not specify an hour to display."
                },
                "minute": {
                    "type": "integer",
                    "description": "The minute (0-59). Set this to None or a negative number if the content does not specify a minute to display."
                },
                "second": {
                    "type": "integer",
                    "description": "The second (0-59). Set this to None or a negative number if the content does not specify a second to display."
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the clock. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code. The clock face itself remains white. Defaults to 'transparent'."
                }
            },
            "required": ["hour", "minute", "second", "background_color"]
        }
    }
    return spec, generate_clock_image