from __future__ import annotations

import base64
import asyncio
import io
import json
import logging
import os
import tempfile
import time
from threading import Lock
from typing import Callable

import cairosvg
from dotenv import find_dotenv, load_dotenv
from google import genai
from google.genai import types
from PIL import Image

from edu_agents.core.api_key_manager import get_async_openai_client
from edu_agents.tools.image_cropping import auto_crop_whitespace
from utils.supabase_utils import upload_image_to_supabase

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)

# Suppress verbose Google Genai logging
logging.getLogger("google_genai.models").setLevel(logging.WARNING)

# Thread-safe counter for unique image naming
_image_counter = 0
_counter_lock = Lock()

GPT_REFINEMENT_MODE = "gpt"
NANO_BANANA_REFINEMENT_MODE = "nano-banana"
REFINEMENT_MODE = NANO_BANANA_REFINEMENT_MODE

REFINEMENT_REQUIREMENTS = """Requirements:
- Keep the overall composition and layout from the sketch
- Make it more polished and professional looking
- Use appropriate colors that are educational and engaging
- Maintain clarity for educational purposes
- Keep it suitable for students
- Make sure all elements are clearly visible and well-defined
- **CRITICAL**: Do not change the counts of any objects in the sketch - maintain EXACT numerical
accuracy
  * If the sketch shows 5 plates, the refined image must show exactly 5 plates  
  * If the sketch shows 6 tables, the refined image must show exactly 6 tables
  * Count preservation is more important than visual improvements
- Enhance the sketch while preserving its core structure and elements
- Objects of the same type should be visually similar
- If you can confidently determine the perspective of the objects in the sketch, you may add
background elements in the same perspective to make the image more closely resemble the scene
described in the prompt, as long as the background elements have logical physical relationships
to the objects in the sketch (e.g., don't make it appear as if heavy objects are floating in
the air, don't make it appear as if objects are standing on end in an unbalanced or unnatural way)
  - Most images will either have a front perspective or a direct overhead perspective. Decide
  which perspective to use based on the prompt, the objects in the sketch, and the most natural
  direction gravity would be given the objects and prompt. If you create background elements,
  ensure they have the same perspective as the objects in the sketch with particular reference
  to gravity.
  - DO NOT add background elements that could be confused with objects in the sketch
  - If you cannot determine a way to illustrate the background that maintains a logical physical
  relationship with the objects in the sketch, with proper perspective, do NOT add background
  elements. It's better to be simple and clear than to be realistic yet confusing.
    - If you decide not to add background elements, choose an appropriate backround color for the
    image that makes the objects in the sketch visible and clear. Do not choose black or very dark
    colors for the background unless appropriate given the prompt and image context.
- While it's acceptable to add elements to make the image appear more realistic or
3D, do not obscure any objects in the sketch
- **ABSOLUTE REQUIREMENT**: Ensure that the resulting image shows EXACTLY the correct number of 
each object specified in the prompt, without any objects obscured by other objects
  * Count every object type in the final image to verify accuracy
  * If you must choose between visual appeal and numerical accuracy, ALWAYS prioritize numerical
  accuracy
  * If you must choose whether to follow the template or to present the correct number of objects,
  ALWAYS prioritize presenting the correct number of objects
- Ensure that all objects have physically logical placement in relation to each other. For example,
objects that are supposed to be contained within other objects should be clearly contained within
them. It is acceptable to modify regions outside of objects in the sketch to ensure this requirement
is met.
- Use a colorful, engaging cartoon style, but don't make it distracting"""

def _get_next_image_number():
    """Get the next image number in a thread-safe way."""
    global _image_counter
    with _counter_lock:
        _image_counter += 1
        return _image_counter

async def _generate_svg_sketch(prompt: str, size: tuple[int, int]) -> str:
    """
    Generate an SVG sketch based on the prompt.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the SVG sketch from
    size : tuple[int, int]
        The (width, height) of the SVG canvas
        
    Returns
    -------
    str
        The SVG content as a string
    """
    width, height = size
    
    # Use OpenAI to generate SVG code based on the prompt
    try:
        client = get_async_openai_client(timeout=60.0)
        
        svg_prompt = f"""Generate clean, simple SVG code for: {prompt}

Steps:
1. Review the prompt and determine the correct number of each object to create.
2. Review the Requirements and ensure you have a plan that will meet all of them.
3. Create the SVG code based on your plan.
4. CRITICAL VERIFICATION: Before returning the SVG, mentally count every object in your generated
code:
   - For each type of object mentioned in the prompt, enumerate every instance in your SVG
   - Verify the count matches exactly what was requested (not approximately)
   - If the count is wrong, revise the SVG to have the correct number
5. Only after verification, return the SVG code ONLY. No explanations.

Requirements:
- Create a sketch-like, simple line drawing style
- Use stroke-based drawing (outlines) rather than filled shapes where appropriate
- Keep it simple but recognizable
- Use a {width}x{height} viewBox, and ensure no objects extend beyond the viewBox
- Include proper SVG structure with xmlns
- Use black strokes on white/transparent background
- Make it educational and clear for students
- When positioning objects on top of platforms or inside containers, lay the objects out in
neat lines or grids, with the overall line or grid being centered on the platform or container
and ALL of the objects fully on top of the platform or inside the container
- **CRITICAL OBJECT COUNT REQUIREMENT**: Ensure you create EXACTLY the correct number of each 
object specified in the prompt, without any objects obscured by other objects
  * If prompt says "5 plates", create exactly 5 plates - not 4, not 6, not approximately 5
  * If prompt says "3 tables each with 4 cups", create exactly 3 tables with exactly 4 cups each
  * Every single object mentioned in the prompt with a specific count must be present and countable
- Sketch the image as if gravity is pulling the objects down towards the bottom of the image
such that the objects are in a stable, balanced position. For example, if making a stack of
6 marbles, the stack should have 3 on the bottom, 2 in the middle, and 1 on top"""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert at creating simple, educational "
                              "SVG illustrations. Generate clean SVG code based on user prompts."
                },
                {"role": "user", "content": svg_prompt}
            ],
            temperature=0.1,
        )
        
        # Defensive check: ensure content is not a coroutine
        response_content = response.choices[0].message.content
        if hasattr(response_content, '__await__'):
            response_content = await response_content
        svg_content = response_content.strip()
        
        # Clean up the response to extract just the SVG
        if "```svg" in svg_content:
            svg_content = svg_content.split("```svg")[1].split("```")[0].strip()
        elif "```" in svg_content:
            svg_content = svg_content.split("```")[1].split("```")[0].strip()
        
        # Ensure it starts with <svg and ends with </svg>
        if not svg_content.startswith("<svg"):
            # Look for SVG tag in the content
            svg_start = svg_content.find("<svg")
            if svg_start != -1:
                svg_content = svg_content[svg_start:]
        
        # Basic validation
        if not svg_content.startswith("<svg") or not svg_content.endswith("</svg>"):
            raise ValueError("Generated content is not valid SVG")
            
        return svg_content
        
    except Exception as e:
        logger.error(f"Error generating SVG sketch: {e}")
        # Fallback to a simple placeholder SVG
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" """\
               f"""width="{width}" height="{height}">
            <rect x="10" y="10" width="{width-20}" height="{height-20}" """\
               f"""fill="none" stroke="black" stroke-width="2"/>
            <text x="{width//2}" y="{height//2}" text-anchor="middle" """\
               f"""font-family="Arial" font-size="16" fill="black">
                Sketch: {prompt[:30]}...
            </text>
        </svg>"""

def _convert_svg_to_png(svg_content: str, output_size: tuple[int, int]) -> bytes:
    """
    Convert SVG content to PNG bytes.
    
    Parameters
    ----------
    svg_content : str
        The SVG content as a string
    output_size : tuple[int, int]
        The (width, height) for the output PNG
        
    Returns
    -------
    bytes
        The PNG image data as bytes
    """
    try:
        # Convert SVG to PNG using cairosvg
        png_bytes = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=output_size[0],
            output_height=output_size[1]
        )
        return png_bytes
        
    except Exception as e:
        logger.error(f"Error converting SVG to PNG: {e}")
        # Create a fallback PNG using PIL
        width, height = output_size
        img = Image.new('RGB', (width, height), 'white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

async def _refine_image_with_gpt(png_bytes: bytes, prompt: str, size: str) -> bytes:
    """
    Use GPT image editing to refine the PNG sketch into a more polished image.
    
    Parameters
    ----------
    png_bytes : bytes
        The PNG image data to refine
    prompt : str
        The original prompt for context
    size : str
        The size parameter for OpenAI API
        
    Returns
    -------
    bytes
        The refined PNG image data as bytes
    """
    try:
        # Save PNG to temporary file for OpenAI API
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(png_bytes)
            temp_file_path = temp_file.name
        
        # Create refinement prompt
        refinement_prompt = f"""Transform this sketch into a clean, educational 
illustration of: {prompt}

{REFINEMENT_REQUIREMENTS}"""

        # Call OpenAI API to refine the image
        client = get_async_openai_client(timeout=300.0)
        response = await client.images.edit(
            model="gpt-image-1",
            image=open(temp_file_path, "rb"),
            prompt=refinement_prompt,
            n=1,
            size=size,
            output_format="png"
        )
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        # Get the refined image from the response
        refined_b64_data = response.data[0].b64_json
        refined_image_bytes = base64.b64decode(refined_b64_data)
        
        return refined_image_bytes
        
    except Exception as e:
        logger.error(f"Error refining image with GPT: {e}")
        # Return original image if refinement fails
        return png_bytes

async def _refine_image_with_nano_banana(png_bytes: bytes, prompt: str) -> bytes:
    """
    Use Google's nano-banana (Gemini 2.5 Flash Image) to refine the PNG sketch 
    into a more polished image.
    
    Parameters
    ----------
    png_bytes : bytes
        The PNG image data to refine
    prompt : str
        The original prompt for context
        
    Returns
    -------
    bytes
        The refined PNG image data as bytes
    """
    try:
        # Create refinement prompt for nano-banana
        refinement_prompt = f"""Transform this sketch into a clean, educational 
illustration of: {prompt}

{REFINEMENT_REQUIREMENTS}"""

        # Initialize Gemini client for nano-banana
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Convert bytes to PIL Image for Gemini API
        pil_image = Image.open(io.BytesIO(png_bytes))
        
        # Use nano-banana to refine the image
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash-image",
            contents=[refinement_prompt, pil_image],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE']
            )
        )
        
        # Extract refined image data from response
        refined_image_data = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                refined_image_data = part.inline_data.data
                break
        
        if refined_image_data is None:
            raise ValueError("No refined image data found in nano-banana response")
        
        return refined_image_data
        
    except Exception as e:
        logger.error(f"Error refining image with nano-banana: {e}")
        # Return original image if refinement fails
        return png_bytes

async def _generate_single_svg_image(
    prompt: str, 
    size: str, 
    image_index: int, 
    transparent_background: bool = False
) -> str:
    """
    Generate a single image using SVG sketch + refinement workflow.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the image from
    size : str
        The size of the image (e.g., "1024x1024")
    image_index : int
        Index of this image in the batch for logging
    transparent_background : bool, default False
        If True, requests a transparent background (note: may not be fully supported)
        
    Returns
    -------
    str
        The URL of the generated image
    """
    try:
        logger.info(f"Generating SVG-based image {image_index + 1}")
        
        # Parse size
        width, height = map(int, size.split('x'))
        
        # Step 1: Generate SVG sketch
        svg_content = await _generate_svg_sketch(prompt, (width, height))
        
        # Step 2: Convert SVG to PNG
        png_bytes = _convert_svg_to_png(svg_content, (width, height))
        
        # Step 3: Refine with selected method
        if REFINEMENT_MODE == NANO_BANANA_REFINEMENT_MODE:
            refined_png_bytes = await _refine_image_with_nano_banana(png_bytes, prompt)
        else:  # Default to GPT
            refined_png_bytes = await _refine_image_with_gpt(png_bytes, prompt, size)
        
        # Step 4: Auto-crop whitespace from refined image
        cropped_png_bytes = auto_crop_whitespace(
            refined_png_bytes,
            background_color=(255, 255, 255),  # White background
            tolerance=15,  # Slightly higher tolerance for refined images
            margin=10  # Small margin around content
        )
        
        # Step 5: Upload to Supabase
        public_url = upload_image_to_supabase(
            image_bytes=cropped_png_bytes,
            content_type="image/png",
            bucket_name="incept-images"
        )

        logger.info(f"Successfully created refined and cropped image {image_index + 1} with "
                    f"{REFINEMENT_MODE} refinement: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Error creating refined and cropped image {image_index + 1} with " +
                     f"{REFINEMENT_MODE} refinement: {e}")
        raise

async def generate_svg_sketch_image(
    prompt: str, 
    aspect_ratio: str = "1:1", 
    num_images: int = 1
) -> str:
    """
    Generate image(s) using SVG sketch + refinement workflow.
    
    Parameters
    ----------
    prompt : str
        The prompt to generate the images from
    aspect_ratio : str, default "1:1"
        The aspect ratio of the images. Must be one of: '1:1', '16:9', '9:16'.
    num_images : int, default 1
        The number of images to generate in parallel
        
    Returns
    -------
    str
        JSON string containing the list of generated image URLs
    """
    logger.info(f"Generating {num_images} SVG-based images with prompt: {prompt}")
    
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
    start_time = time.time()
    try:
        # Create tasks for all images
        tasks = [
            _generate_single_svg_image(prompt, size, i)
            for i in range(num_images)
        ]
        
        # Run all tasks concurrently
        image_urls = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions
        for i, result in enumerate(image_urls):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate SVG-based image {i + 1}: {result}")
                raise result
    except Exception as e:
        logger.error(f"Error during parallel image generation: {e}")
        raise
    
    end_time = time.time()
    logger.info(f"Time taken to generate {num_images} SVG-based images using {REFINEMENT_MODE} " +
                f"refinement and auto-cropping: {end_time - start_time} seconds")
    
    # Filter out any None values (failed generations)
    successful_urls = [url for url in image_urls if url is not None]
    
    if not successful_urls:
        logger.error("Failed to generate any SVG-based images")
        return json.dumps({"image_url": None, "status": "failed"})
    
    logger.info(
        f"Successfully generated {len(successful_urls)} out of {num_images} SVG-based images "
        f"with auto-cropping"
    )
    
    # Return the URLs as a JSON string
    result = {
        "image_url": successful_urls[0],
        "status": "success"
    }
    
    return json.dumps(result)

def generate_svg_sketch_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_svg_sketch_image",
        "description": "Generate images of real-world objects that are appropriate for educational "
                       "use. Returns a JSON string containing the list of generated image URLs.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Prompt for generating images."
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "The aspect ratio of the images. MUST be one of: '1:1', "
                                  "'16:9', '9:16'. Any other aspect ratio will be rejected."
                },
            },
            "required": ["prompt", "aspect_ratio"]
        }
    }
    return spec, generate_svg_sketch_image
