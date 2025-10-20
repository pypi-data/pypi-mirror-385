from __future__ import annotations

import asyncio
import base64
import json
import logging
from threading import Lock
from typing import Callable

from dotenv import find_dotenv, load_dotenv

from edu_agents.core.api_key_manager import get_async_openai_client
from utils.supabase_utils import upload_image_to_supabase

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)

# Thread-safe counter for unique image naming
_image_counter = 0
_counter_lock = Lock()

def _get_next_image_number():
    """Get the next image number in a thread-safe way."""
    global _image_counter
    with _counter_lock:
        _image_counter += 1
        return _image_counter

async def _generate_single_image(prompt: str, size: str, image_index: int,
transparent_background: bool = False) -> str:
    """
    Generate a single image using DALL-E 3.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the image from
    size : str
        The size of the image
    image_index : int
        Index of this image in the batch for logging
    transparent_background : bool, default False
        If True, requests a transparent background using PNG format
        
    Returns
    -------
    str
        The URL of the generated image
    """
    try:
        logger.info(f"Generating image {image_index + 1} with prompt: {prompt}")
        
        # Base parameters for the API call
        params = {
            "model": "gpt-image-1",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "output_format": "png"
        }
        
        # Add transparency parameters if requested
        if transparent_background:
            params["background"] = "transparent"
        
        # Get OpenAI client with API key rotation
        client = get_async_openai_client(timeout=300.0)  # 5 minutes timeout for image generation
        response = await client.images.generate(**params)

        # Decode the base64-encoded image returned by the API
        b64_data = response.data[0].b64_json
        image_bytes = base64.b64decode(b64_data)
        
        # Upload the image to Supabase using the utility function
        public_url = upload_image_to_supabase(
            image_bytes=image_bytes,
            content_type="image/png",
            bucket_name="incept-images"
        )

        logger.info(f"Successfully generated image {image_index + 1}: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Error generating image {image_index + 1}: {e}")
        raise

async def generate_image(prompt: str, aspect_ratio: str = "1:1", num_images: int = 3,
use_transparent_background: bool = False) -> str:
    """
    Generate image(s) using DALL-E 3.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the images from
    aspect_ratio : str, default "1:1"
        The aspect ratio of the images. Must be one of: '1:1', '16:9', '9:16'.
    num_images : int, default 3
        The number of images to generate in parallel
    use_transparent_background : bool, default False
        If True, requests images with transparent backgrounds in PNG format
        
    Returns
    -------
    str
        JSON string containing the list of generated image URLs
    """
    logger.info(f"Generating {num_images} images with prompt: {prompt}")
    
    # Determine image size based on aspect ratio
    if aspect_ratio == "1:1":
        size = "1024x1024"
    elif aspect_ratio == "16:9" or aspect_ratio == "4:3":
        size = "1536x1024"
    elif aspect_ratio == "9:16" or aspect_ratio == "3:4":
        size = "1024x1536"
    else:
        logger.warning(f"Invalid aspect ratio: {aspect_ratio}. Defaulting to 1:1.")
        size = "1024x1024"
    
    # Generate all images in parallel using asyncio.gather
    try:
        # Create tasks for all images
        tasks = [
            _generate_single_image(prompt, size, i, use_transparent_background)
            for i in range(num_images)
        ]
        
        # Run all tasks concurrently
        image_urls = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions
        for i, result in enumerate(image_urls):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate image {i + 1}: {result}")
                raise result
    except Exception as e:
        logger.error(f"Error during parallel image generation: {e}")
        raise
    
    # Filter out any None values (failed generations)
    successful_urls = [url for url in image_urls if url is not None]
    
    if not successful_urls:
        logger.error("Failed to generate any images")
        return json.dumps({"image_urls": [], "status": "failed"})
    
    logger.info(f"Successfully generated {len(successful_urls)} out of {num_images} images")
    
    # Return the URLs as a JSON string
    result = {
        "image_urls": successful_urls,
        "status": "success",
        "count": len(successful_urls)
    }
    
    return json.dumps(result)

def generate_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_image",
        "description": (
            "Generate images of real-world objects, or other images that are not covered by other "
            "tools or that createsimple schematic diagrams. Returns a JSON string containing the "
            "list of generated image URLs. Use the quality checker to select the best image from "
            "the list."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": (
                        "Prompt for generating images, especially for images that depict objects "
                        "a student could see in real life."
                    )
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": (
                        "The aspect ratio of the images. MUST be one of: '1:1', '16:9', '9:16' "
                        ". Any other aspect ratio will be rejected."
                    )
                },
                "num_images": {
                    "type": "integer",
                    "description": (
                        "The number of images to generate in parallel. Default is 3. All images "
                        "will be returned for quality checking."
                    ),
                    "default": 3,
                    "minimum": 1,
                    "maximum": 5
                },
                "use_transparent_background": {
                    "type": "boolean",
                    "description": (
                        "If True, attempts to request a transparent background. Note that DALL-E "
                        "may generate a simulated transparent background rather than true "
                        "transparency."
                    ),
                    "default": False
                }
            },
            "required": ["prompt", "aspect_ratio"]
        }
    }
    return spec, generate_image