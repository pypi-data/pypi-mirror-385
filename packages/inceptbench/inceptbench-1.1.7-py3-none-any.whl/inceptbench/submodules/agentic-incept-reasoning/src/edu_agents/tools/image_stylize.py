from __future__ import annotations

import asyncio
import base64
import logging
import os
import tempfile
from typing import Callable

import requests
from dotenv import find_dotenv, load_dotenv

from edu_agents.core.api_key_manager import get_async_openai_client
from utils.supabase_utils import upload_image_to_supabase

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)

async def stylize_image(
    image_url: str,
    aspect_ratio: str,
    description_prompt: str
) -> str:
    """
    Stylize an existing image using OpenAI's image editing API and upload to Supabase.
    
    Parameters
    ----------
    image_url : str
        The URL of the image to stylize
    aspect_ratio : str
        The aspect ratio of the image. Must be one of: '1:1', '16:9', '9:16'.
    description_prompt : str
        The prompt to send to OpenAI to edit the image
        
    Returns
    -------
    str
        The URL of the stylized and uploaded image
    """
    logger.info(f"Stylizing image with prompt: {description_prompt}")
    try:
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
        
        # Download the image from the URL
        response = requests.get(image_url)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to download image from {image_url}")
        
        image_bytes = response.content
        
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(image_bytes)
            temp_file_path = temp_file.name
        
        # Call OpenAI API to stylize the image
        client = get_async_openai_client(timeout=300.0)  # 5 minutes timeout for image generation
        response = await client.images.edit(
            model="gpt-image-1",
            image=open(temp_file_path, "rb"),
            prompt=description_prompt,
            n=1,
            input_fidelity="high",
            size=size
        )
        
        # Delete the temp file
        os.remove(temp_file_path)
        
        # Get the edited image from the response
        edited_b64_data = response.data[0].b64_json
        edited_image_bytes = base64.b64decode(edited_b64_data)
        
        # Upload the edited image to Supabase
        public_url = upload_image_to_supabase(
            image_bytes=edited_image_bytes,
            content_type="image/png",
            bucket_name="incept-images",
            file_extension=".png"
        )
        return public_url
        
    except Exception as e:
        error_message = f"Error stylizing image: {str(e)}"
        logger.error(error_message)
        raise RuntimeError(error_message) from e

def stylize_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "stylize_image",
        "description": "Stylize an existing image and upload it.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL of the image to stylize."
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": (
                        "The aspect ratio of the image. MUST be one of: '1:1', '16:9', '9:16'. Any "
                        "other aspect ratio will be rejected."
                    )
                },
                "description_prompt": {
                    "type": "string",
                    "description": (
                        "Natural language prompt describing the desired appearance of the stylized "
                        "image, including all invariants, sandboxes, and constraints, and numbered "
                        "plan."
                    )
                }
            },
            "required": ["image_url", "aspect_ratio", "description_prompt"]
        }
    }
    return spec, stylize_image 