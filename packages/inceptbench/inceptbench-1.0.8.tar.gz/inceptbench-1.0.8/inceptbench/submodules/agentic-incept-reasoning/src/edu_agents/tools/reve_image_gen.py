from __future__ import annotations

import base64
import concurrent.futures
import json
import logging
import os
import time
from threading import Lock
from typing import Callable

import requests
from dotenv import find_dotenv, load_dotenv

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

def _generate_single_image_reve(
    prompt: str, aspect_ratio: str, image_index: int, version: str = "latest"
) -> str:
    """
    Generate a single image using Reve API.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the image from
    aspect_ratio : str
        The aspect ratio of the image
    image_index : int
        Index of this image in the batch for logging
    version : str, default "latest"
        The specific model version to use
        
    Returns
    -------
    str
        The URL of the generated image
    """
    try:
        logger.info(f"Generating image {image_index + 1} with Reve API, prompt: {prompt}")
        
        # Get Reve API key from environment
        reve_api_key = os.getenv("REVE_KEY")
        
        if not reve_api_key:
            raise ValueError("REVE_KEY environment variable must be set")
        
        # Prepare the API request headers
        headers = {
            "Authorization": f"Bearer {reve_api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Prepare request data according to API specification
        data = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "version": version
        }
        
        # Make the API request to the correct endpoint
        response = requests.post(
            "https://api.reve.com/v1/image/create",
            headers=headers,
            json=data,
            timeout=300.0  # 5 minutes timeout for image generation
        )
        
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        # Check for content violation
        if result.get("content_violation", False):
            logger.warning(
                f"Image {image_index + 1} flagged for content violation. "
                f"Request ID: {result.get('request_id')}"
            )
            raise ValueError(f"Content policy violation detected for image {image_index + 1}")
        
        # Extract base64 image data
        b64_data = result.get("image")
        if not b64_data:
            raise ValueError(
                f"No image data in response for image {image_index + 1}. "
                f"Request ID: {result.get('request_id')}"
            )
        
        # Log API usage information
        logger.info(f"Reve API usage - Credits used: {result.get('credits_used')}, "
                   f"Credits remaining: {result.get('credits_remaining')}, "
                   f"Version: {result.get('version')}, "
                   f"Request ID: {result.get('request_id')}")
        
        # Decode the base64-encoded image
        image_bytes = base64.b64decode(b64_data)
        
        # Upload the image to Supabase using the utility function
        public_url = upload_image_to_supabase(
            image_bytes=image_bytes,
            content_type="image/png",
            bucket_name="incept-images"
        )
        
        logger.info(f"Successfully generated image {image_index + 1} with Reve API: {public_url}")
        return public_url
        
    except requests.RequestException as e:
        logger.error(f"Reve API request error for image {image_index + 1}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                logger.error(
                    f"API error details: {error_data.get('error_code')}, "
                    f"{error_data.get('message')}"
                )
            except json.JSONDecodeError:
                logger.error(f"API error response: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error generating image {image_index + 1} with Reve API: {e}")
        raise

def generate_image_reve(
    prompt: str, aspect_ratio: str = "3:2", num_images: int = 3, version: str = "latest"
) -> str:
    """
    Generate image(s) using Reve API.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the images from
    aspect_ratio : str, default "3:2"
        The aspect ratio of the images. Must be one of: 
        '16:9', '9:16', '3:2', '2:3', '4:3', '3:4', or '1:1'.
    num_images : int, default 3
        The number of images to generate in parallel
    version : str, default "latest"
        The specific model version to use
        
    Returns
    -------
    str
        JSON string containing the list of generated image URLs
    """
    logger.info(f"Generating {num_images} images with Reve API, prompt: {prompt}")
    
    # Validate aspect ratio
    valid_ratios = ["16:9", "9:16", "3:2", "2:3", "4:3", "3:4", "1:1"]
    if aspect_ratio not in valid_ratios:
        logger.warning(f"Invalid aspect ratio: {aspect_ratio}. Defaulting to 3:2.")
        aspect_ratio = "3:2"
    
    # Generate all images in parallel
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_images) as executor:
        # Submit all image generation tasks
        future_to_index = {
            executor.submit(_generate_single_image_reve, prompt, aspect_ratio, i, version): i 
            for i in range(num_images)
        }
        
        # Collect results as they complete
        image_urls = [None] * num_images
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                image_url = future.result()
                image_urls[index] = image_url
            except Exception as e:
                logger.error(f"Failed to generate image {index + 1} with Reve API: {e}")
                # Continue with other images, but this will result in a None in the list
                raise
    
    end_time = time.time()
    
    # Filter out any None values (failed generations)
    successful_urls = [url for url in image_urls if url is not None]
    
    if not successful_urls:
        logger.error("Failed to generate any images with Reve API")
        return json.dumps({"image_urls": [], "status": "failed"})
    
    logger.info(
        f"Successfully generated {len(successful_urls)} out of {num_images} images with Reve API " +
        f"in {end_time - start_time} seconds"
    )
    
    # Return the URLs as a JSON string
    result = {
        "image_urls": successful_urls,
        "status": "success",
        "count": len(successful_urls)
    }
    
    return json.dumps(result)

def generate_image_reve_tool() -> tuple[dict, Callable]:
    """
    Tool specification for Reve image generation.
    
    Returns
    -------
    tuple[dict, Callable]
        Tool specification dictionary and the callable function
    """
    spec = {
        "type": "function",
        "name": "generate_image_reve",
        "description": (
            "Generate images using the Reve API. Returns a JSON string containing the list of "
            "generated image URLs. Use the quality checker to select the best image from the list."
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
                        "The aspect ratio of the images. MUST be one of: '16:9', '9:16', '3:2', "
                        "'2:3', '4:3', '3:4', or '1:1'. Default is '3:2'."
                    ),
                    "default": "3:2"
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
            },
            "required": ["prompt"]
        }
    }
    return spec, generate_image_reve
