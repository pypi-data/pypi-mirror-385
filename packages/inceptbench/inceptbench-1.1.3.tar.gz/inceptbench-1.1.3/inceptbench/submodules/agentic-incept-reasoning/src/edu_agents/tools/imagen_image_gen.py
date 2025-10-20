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

async def _generate_single_image_imagen(prompt: str, aspect_ratio: str, model: str, image_index: int) -> str:
    """
    Generate a single image using Imagen models.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the image from
    aspect_ratio : str
        The aspect ratio of the image
    model : str
        The Imagen model to use
    image_index : int
        Index of this image in the batch for logging
        
    Returns
    -------
    str
        The URL of the generated image
    """
    try:
        logger.info(f"Generating image {image_index + 1} with Imagen model {model} using prompt: {prompt}")
        
        # Initialize Gemini client (same client handles Imagen)
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Generate single image using Imagen API
        response = await asyncio.to_thread(
            client.models.generate_images,
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio
            )
        )
        
        # Extract image data from response
        if not response.generated_images:
            raise ValueError("No images generated in Imagen response")
            
        generated_image = response.generated_images[0]
        image_bytes = generated_image.image.image_bytes
        
        # Create a unique filename for this image
        image_number = _get_next_image_number()
        
        # Upload the image to Supabase
        public_url = upload_image_to_supabase(
            image_bytes=image_bytes,
            content_type="image/png",
            bucket_name="incept-images"
        )
        
        logger.info(f"Successfully generated image {image_index + 1} with Imagen: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Error generating image {image_index + 1} with Imagen: {e}")
        raise

async def generate_image_imagen(prompt: str, aspect_ratio: str = "1:1", num_images: int = 3, image_quality: str = "standard") -> str:
    """
    Generate image(s) using Google's Imagen models.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the images from
    aspect_ratio : str, default "1:1"
        The aspect ratio of the images. Must be one of: '1:1', '3:4', '4:3', '9:16', '16:9'.
    num_images : int, default 3
        The number of images to generate in parallel
    image_quality : str, default "standard"
        The quality level for image generation. Options: 'fast', 'standard', 'ultra'
        
    Returns
    -------
    str
        JSON string containing the list of generated image URLs
    """
    try:
        logger.info(f"Generating {num_images} images with Imagen quality '{image_quality}' using prompt: {prompt}")
        
        # Map image quality to model names
        model_mapping = {
            "fast": "imagen-4.0-fast-generate-001",
            "standard": "imagen-4.0-generate-001", 
            "ultra": "imagen-4.0-ultra-generate-001"
        }
        
        model = model_mapping.get(image_quality, model_mapping["standard"])
        if image_quality not in model_mapping:
            logger.warning(f"Invalid image quality: {image_quality}. Defaulting to standard.")
            image_quality = "standard"
            model = model_mapping["standard"]
        
        # Validate aspect ratio
        valid_ratios = ["1:1", "3:4", "4:3", "9:16", "16:9"]
        if aspect_ratio not in valid_ratios:
            logger.warning(f"Invalid aspect ratio: {aspect_ratio}. Defaulting to 1:1.")
            aspect_ratio = "1:1"
        
        # Generate all images in parallel using asyncio.gather
        try:
            # Create tasks for all images
            tasks = [
                _generate_single_image_imagen(prompt, aspect_ratio, model, i)
                for i in range(num_images)
            ]
            
            # Run all tasks concurrently
            image_urls = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for exceptions
            for i, result in enumerate(image_urls):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate image {i + 1} with Imagen: {result}")
                    raise result
        except Exception as e:
            logger.error(f"Error during parallel image generation with Imagen: {e}")
            raise
        
        # Filter out any None values (failed generations)
        successful_urls = [url for url in image_urls if url is not None]
        
        if not successful_urls:
            logger.error("Failed to generate any images with Imagen")
            return json.dumps({"image_urls": [], "status": "failed"})
        
        logger.info(f"Successfully generated {len(successful_urls)} out of {num_images} images with Imagen")
        
        # Return the URLs as a JSON string
        result = {
            "image_urls": successful_urls,
            "status": "success",
            "count": len(successful_urls)
        }
        
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error generating images with Imagen: {e}")
        return json.dumps({"image_urls": [], "status": "failed", "error": str(e)})

def generate_image_imagen_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_image_imagen",
        "description": "Generate image(s) using Google's Imagen models (specialized high-fidelity image generation). Returns a JSON string containing the list of generated image URLs. Use the quality checker to select the best image from the list. Best for photorealism, artistic detail, and specific styles.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Prompt for generating images. Imagen excels at photorealistic images, artistic styles, and high-quality detailed imagery. Maximum 480 tokens."
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "The aspect ratio of the images. Must be one of: '1:1', '3:4', '4:3', '9:16', '16:9'. Imagen has precise aspect ratio control.",
                    "enum": ["1:1", "3:4", "4:3", "9:16", "16:9"],
                    "default": "1:1"
                },
                "num_images": {
                    "type": "integer",
                    "description": "The number of images to generate in parallel. Default is 3.",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 5
                },
                "image_quality": {
                    "type": "string",
                    "description": "Quality level for image generation. 'fast' (quick simple images), 'standard' (typical quality), 'ultra' (high-quality photorealistic).",
                    "enum": ["fast", "standard", "ultra"],
                    "default": "standard"
                }
            },
            "required": ["prompt"]
        }
    }
    return spec, generate_image_imagen 