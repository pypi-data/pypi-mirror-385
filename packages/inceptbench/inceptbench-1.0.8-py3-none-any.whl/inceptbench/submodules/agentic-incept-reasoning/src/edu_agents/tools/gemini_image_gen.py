from __future__ import annotations

import asyncio
import json
import logging
import os
from threading import Lock
from typing import Callable

from dotenv import find_dotenv, load_dotenv
from google import genai
from google.genai import types

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

async def _generate_single_image_gemini(prompt: str, image_index: int) -> str:
    """
    Generate a single image using Gemini 2.0 Flash.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the image from
    image_index : int
        Index of this image in the batch for logging
        
    Returns
    -------
    str
        The URL of the generated image
    """
    try:
        logger.info(f"Generating image {image_index + 1} with Gemini using prompt: {prompt}")
        
        # Initialize Gemini client
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Generate content with both text and image modalities
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        # Extract image data from response parts
        image_data = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # The image data is already base64 decoded bytes
                image_data = part.inline_data.data
                break
        
        if image_data is None:
            raise ValueError("No image data found in Gemini response")
        
        # Upload the image to Supabase using the utility function
        public_url = upload_image_to_supabase(
            image_bytes=image_data,
            content_type="image/png",
            bucket_name="incept-images"
        )

        logger.info(f"Successfully generated image {image_index + 1} with Gemini: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Error generating image {image_index + 1} with Gemini: {e}")
        raise

async def generate_image_gemini(prompt: str, aspect_ratio: str = "1:1", num_images: int = 3) -> str:
    """
    Generate image(s) using Gemini 2.0 Flash.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the images from
    aspect_ratio : str, default "1:1"
        The aspect ratio preference (note: Gemini may not strictly follow this)
    num_images : int, default 3
        The number of images to generate in parallel
        
    Returns
    -------
    str
        JSON string containing the list of generated image URLs
    """
    logger.info(f"Generating {num_images} images with Gemini using prompt: {prompt}")
    
    # Enhance prompt with aspect ratio preference if not square
    enhanced_prompt = prompt
    if aspect_ratio == "16:9":
        enhanced_prompt = f"{prompt} (wide landscape format, 16:9 aspect ratio)"
    elif aspect_ratio == "9:16":
        enhanced_prompt = f"{prompt} (tall portrait format, 9:16 aspect ratio)"
    elif aspect_ratio == "4:3":
        enhanced_prompt = f"{prompt} (landscape format, 4:3 aspect ratio)"
    elif aspect_ratio == "3:4":
        enhanced_prompt = f"{prompt} (portrait format, 3:4 aspect ratio)"
    
    # Generate all images in parallel using asyncio.gather
    try:
        # Create tasks for all images
        tasks = [
            _generate_single_image_gemini(enhanced_prompt, i)
            for i in range(num_images)
        ]
        
        # Run all tasks concurrently
        image_urls = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions
        for i, result in enumerate(image_urls):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate image {i + 1} with Gemini: {result}")
                raise result
    except Exception as e:
        logger.error(f"Error during parallel image generation with Gemini: {e}")
        raise
    
    # Filter out any None values (failed generations)
    successful_urls = [url for url in image_urls if url is not None]
    
    if not successful_urls:
        logger.error("Failed to generate any images with Gemini")
        return json.dumps({"image_urls": [], "status": "failed"})
    
    logger.info(
        f"Successfully generated {len(successful_urls)} out of {num_images} images with Gemini"
    )
    
    # Return the URLs as a JSON string
    result = {
        "image_urls": successful_urls,
        "status": "success",
        "count": len(successful_urls)
    }
    
    return json.dumps(result)

def generate_image_gemini_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_image_gemini",
        "description": (
            "Generate image(s) using Google's Gemini 2.0 Flash image generation model. Returns a "
            "JSON string containing the list of generated image URLs. Use the quality checker to "
            "select the best image from the list."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": (
                        "Prompt for generating images. Gemini excels at creating contextually "
                        "relevant images that leverage world knowledge and reasoning."
                    )
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": (
                        "Preferred aspect ratio of the images. Options: '1:1', '16:9', '9:16', "
                        "'4:3', '3:4'. Note: Gemini may not strictly follow aspect ratios but will "
                        "attempt to match the preference."
                    ),
                    "default": "1:1"
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
                }
            },
            "required": ["prompt"]
        }
    }
    return spec, generate_image_gemini 