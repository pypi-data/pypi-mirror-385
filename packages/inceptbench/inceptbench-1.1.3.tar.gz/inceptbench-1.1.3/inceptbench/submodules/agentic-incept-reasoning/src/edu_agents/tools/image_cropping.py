"""
Image cropping utilities for automatic whitespace removal and content-aware cropping.

This module provides reusable cropping functionality that can be integrated into
various image generation workflows to automatically remove excess whitespace
and focus on the main content of generated images.
"""

import io
import logging
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageChops

logger = logging.getLogger(__name__)


def auto_crop_whitespace(
    image_bytes: bytes,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    tolerance: int = 10,
    margin: int = 20
) -> bytes:
    """
    Automatically crop whitespace and background from an image.
    
    This function detects the bounding box of non-background content and crops
    the image to remove excess whitespace while maintaining a small margin.
    
    Parameters
    ----------
    image_bytes : bytes
        The input image data as bytes
    background_color : Tuple[int, int, int], default (255, 255, 255)
        The RGB color to consider as background (default is white)
    tolerance : int, default 10
        Color tolerance for background detection (0-255)
    margin : int, default 20
        Minimum margin to keep around the content in pixels
        
    Returns
    -------
    bytes
        The cropped image data as bytes
    """
    try:
        # Load image from bytes
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get the bounding box of non-background content
            bbox = _get_content_bbox(img, background_color, tolerance)
            
            if bbox is None:
                logger.warning("No content detected for cropping, returning original image")
                return image_bytes
            
            # Apply margin while staying within image bounds
            left, top, right, bottom = bbox
            width, height = img.size
            
            # Add margin but don't exceed image boundaries
            left = max(0, left - margin)
            top = max(0, top - margin)
            right = min(width, right + margin)
            bottom = min(height, bottom + margin)
            
            # Crop the image
            cropped_img = img.crop((left, top, right, bottom))
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            cropped_img.save(output_buffer, format='PNG')
            cropped_bytes = output_buffer.getvalue()
            
            # Log cropping statistics
            original_size = (width, height)
            cropped_size = (right - left, bottom - top)
            reduction_pct = (1 - (cropped_size[0] * cropped_size[1]) / (original_size[0] * original_size[1])) * 100
            
            logger.info(f"Auto-cropped image from {original_size} to {cropped_size} "
                       f"({reduction_pct:.1f}% size reduction)")
            
            return cropped_bytes
            
    except Exception as e:
        logger.error(f"Error during auto-cropping: {e}")
        # Return original image if cropping fails
        return image_bytes


def _get_content_bbox(
    img: Image.Image,
    background_color: Tuple[int, int, int],
    tolerance: int
) -> Optional[Tuple[int, int, int, int]]:
    """
    Get the bounding box of non-background content in an image.
    
    Parameters
    ----------
    img : Image.Image
        The PIL Image to analyze
    background_color : Tuple[int, int, int]
        The RGB color to consider as background
    tolerance : int
        Color tolerance for background detection
        
    Returns
    -------
    Optional[Tuple[int, int, int, int]]
        The bounding box as (left, top, right, bottom) or None if no content found
    """
    try:
        # Convert image to numpy array for efficient processing
        img_array = np.array(img)
        
        # Create mask for non-background pixels
        # Calculate color distance from background color
        color_diff = np.sqrt(np.sum((img_array - background_color) ** 2, axis=2))
        content_mask = color_diff > tolerance
        
        # Find coordinates of non-background pixels
        content_coords = np.where(content_mask)
        
        if len(content_coords[0]) == 0:
            # No content found
            return None
        
        # Get bounding box coordinates
        top = int(np.min(content_coords[0]))
        bottom = int(np.max(content_coords[0])) + 1
        left = int(np.min(content_coords[1]))
        right = int(np.max(content_coords[1])) + 1
        
        return (left, top, right, bottom)
        
    except Exception as e:
        logger.error(f"Error calculating content bounding box: {e}")
        return None


def smart_crop_to_content(
    image_bytes: bytes,
    target_aspect_ratio: Optional[str] = None,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    tolerance: int = 10,
    margin: int = 20
) -> bytes:
    """
    Intelligently crop an image to focus on content, optionally maintaining an aspect ratio.
    
    This function first removes whitespace, then optionally adjusts the crop to match
    a target aspect ratio while keeping as much content as possible.
    
    Parameters
    ----------
    image_bytes : bytes
        The input image data as bytes
    target_aspect_ratio : Optional[str], default None
        Target aspect ratio as "width:height" (e.g., "16:9", "1:1").
        If None, only removes whitespace without aspect ratio constraints.
    background_color : Tuple[int, int, int], default (255, 255, 255)
        The RGB color to consider as background
    tolerance : int, default 10
        Color tolerance for background detection
    margin : int, default 20
        Minimum margin to keep around content
        
    Returns
    -------
    bytes
        The cropped image data as bytes
    """
    try:
        # First, do basic whitespace cropping
        cropped_bytes = auto_crop_whitespace(image_bytes, background_color, tolerance, margin)
        
        # If no target aspect ratio specified, return the whitespace-cropped image
        if target_aspect_ratio is None:
            return cropped_bytes
        
        # Parse target aspect ratio
        try:
            width_ratio, height_ratio = map(float, target_aspect_ratio.split(':'))
            target_ratio = width_ratio / height_ratio
        except (ValueError, ZeroDivisionError):
            logger.warning(f"Invalid aspect ratio '{target_aspect_ratio}', skipping aspect ratio adjustment")
            return cropped_bytes
        
        # Load the cropped image to adjust aspect ratio
        with Image.open(io.BytesIO(cropped_bytes)) as img:
            width, height = img.size
            current_ratio = width / height
            
            # If already close to target ratio, return as-is
            if abs(current_ratio - target_ratio) < 0.05:
                return cropped_bytes
            
            # Calculate new dimensions to match target ratio
            if current_ratio > target_ratio:
                # Image is too wide, crop width
                new_width = int(height * target_ratio)
                new_height = height
                left = (width - new_width) // 2
                top = 0
                right = left + new_width
                bottom = height
            else:
                # Image is too tall, crop height
                new_width = width
                new_height = int(width / target_ratio)
                left = 0
                top = (height - new_height) // 2
                right = width
                bottom = top + new_height
            
            # Apply aspect ratio crop
            aspect_cropped_img = img.crop((left, top, right, bottom))
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            aspect_cropped_img.save(output_buffer, format='PNG')
            
            logger.info(f"Applied aspect ratio crop from {img.size} to {aspect_cropped_img.size} "
                       f"for target ratio {target_aspect_ratio}")
            
            return output_buffer.getvalue()
            
    except Exception as e:
        logger.error(f"Error during smart cropping: {e}")
        # Return basic whitespace-cropped image if aspect ratio adjustment fails
        return auto_crop_whitespace(image_bytes, background_color, tolerance, margin)


def crop_to_bbox(
    image_bytes: bytes,
    bbox: Tuple[int, int, int, int],
    margin: int = 0
) -> bytes:
    """
    Crop an image to a specific bounding box with optional margin.
    
    Parameters
    ----------
    image_bytes : bytes
        The input image data as bytes
    bbox : Tuple[int, int, int, int]
        The bounding box as (left, top, right, bottom)
    margin : int, default 0
        Additional margin to add around the bounding box
        
    Returns
    -------
    bytes
        The cropped image data as bytes
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            width, height = img.size
            left, top, right, bottom = bbox
            
            # Add margin while staying within image bounds
            left = max(0, left - margin)
            top = max(0, top - margin)
            right = min(width, right + margin)
            bottom = min(height, bottom + margin)
            
            # Crop the image
            cropped_img = img.crop((left, top, right, bottom))
            
            # Convert to bytes
            output_buffer = io.BytesIO()
            cropped_img.save(output_buffer, format='PNG')
            
            return output_buffer.getvalue()
            
    except Exception as e:
        logger.error(f"Error cropping to bounding box: {e}")
        return image_bytes
