from __future__ import annotations

import io
import logging
from typing import Callable
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties

from utils.supabase_utils import upload_image_to_supabase
import matplotlib

# Set matplotlib to use a non-interactive backend
matplotlib.use('Agg')

# Configure matplotlib to prevent memory leaks and limit figure accumulation
matplotlib.rcParams['figure.max_open_warning'] = 5  # Warn much earlier
matplotlib.rcParams['figure.raise_window'] = False   # Don't raise GUI windows

logger = logging.getLogger(__name__)

def generate_latex_equation_image(latex_string: str, font_size: int = 24, background_color: str = 'transparent') -> str:
    """
    Generate an image of a mathematical equation from a LaTeX string.
    
    Parameters
    ----------
    latex_string : str
        The LaTeX string to render (e.g., "x^2 + y^2 = r^2")
    font_size : int, default 24
        Font size for the equation
    background_color : str, default 'white'
        The background color behind the equation. Use 'transparent' for transparent background,
        or any valid matplotlib color name or hex code.
        
    Returns
    -------
    str
        The URL of the generated equation image
    """
    logger.info(f"Generating LaTeX equation image for: {latex_string} with background: {background_color}")
    
    # Create a minimal figure to measure text size
    fig_temp = plt.figure(figsize=(1, 1), dpi=150)
    if background_color == 'transparent':
        fig_temp.patch.set_alpha(0)
    else:
        fig_temp.patch.set_facecolor(background_color)
    ax_temp = fig_temp.add_subplot(111)
    ax_temp.axis('off')
    
    # Set axes background to match figure
    if background_color == 'transparent':
        ax_temp.patch.set_alpha(0)
    else:
        ax_temp.patch.set_facecolor(background_color)
    
    # Set up the equation rendering
    try:
        # Use matplotlib's mathtext parser for LaTeX rendering
        # Wrap the LaTeX in $ symbols for math mode
        if not latex_string.startswith('$'):
            latex_string = f'${latex_string}$'
        
        # Render the text to measure its size
        text_temp = ax_temp.text(0, 0, latex_string, 
                                fontsize=font_size, 
                                ha='left', va='bottom')
        
        # Force a draw to get the text extent
        fig_temp.canvas.draw()
        
        # Get the bounding box of the text in pixels
        bbox = text_temp.get_window_extent(renderer=fig_temp.canvas.get_renderer())
        
        # Convert to inches (matplotlib uses inches for figure size)
        dpi = 150
        width_inches = bbox.width / dpi
        height_inches = bbox.height / dpi
        
        # Add padding in inches
        padding_inches = 0.5
        total_width = width_inches + 2 * padding_inches
        total_height = height_inches + 2 * padding_inches
        
        # Close the temporary figure
        plt.close(fig_temp)
        
        # Create the final figure with the calculated size
        fig = plt.figure(figsize=(total_width, total_height), dpi=150)
        if background_color == 'transparent':
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(background_color)
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Set axes background to match figure
        if background_color == 'transparent':
            ax.patch.set_alpha(0)
        else:
            ax.patch.set_facecolor(background_color)
        
        # Render the text centered in the properly sized figure
        text = ax.text(0.5, 0.5, latex_string, 
                      fontsize=font_size, 
                      ha='center', va='center',
                      transform=ax.transAxes)
        
    except Exception as e:
        logger.error(f"Error rendering LaTeX: {e}")
        # Close temporary figure if it exists
        if 'fig_temp' in locals():
            plt.close(fig_temp)
        
        # Fallback: create a standard sized figure and render as plain text
        fig = plt.figure(figsize=(6, 2), dpi=150)
        if background_color == 'transparent':
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(background_color)
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Set axes background to match figure
        if background_color == 'transparent':
            ax.patch.set_alpha(0)
        else:
            ax.patch.set_facecolor(background_color)
        
        ax.text(0.5, 0.5, latex_string.replace('$', ''), 
               fontsize=font_size, 
               ha='center', va='center',
               transform=ax.transAxes)
    
    # Save to a bytes buffer with minimal padding
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
               pad_inches=0.05, transparent=(background_color == 'transparent'))
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

def generate_latex_equation_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_latex_equation_image",
        "description": "Generate an image of a mathematical equation from a LaTeX string. The equation will be rendered with proper mathematical formatting. Use this whenever you need to display any visually complex mathematical equation (e.g., square roots, exponents, etc.).",
        "parameters": {
            "type": "object",
            "properties": {
                "latex_string": {
                    "type": "string",
                    "description": "The LaTeX string to render as an equation (e.g., 'x^2 + y^2 = r^2', '\\frac{a}{b} + c', '\\sqrt{x + 1}')"
                },
                "font_size": {
                    "type": "integer",
                    "description": "Font size for the equation (default: 24)",
                    "default": 24
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the equation. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code. Defaults to 'transparent'."
                }
            },
            "required": ["latex_string", "background_color"]
        }
    }
    return spec, generate_latex_equation_image 