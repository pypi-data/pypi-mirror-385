from __future__ import annotations

import logging
import re
import textwrap
import xml.etree.ElementTree as ET
from typing import Callable

from cairosvg import svg2png
from dotenv import find_dotenv, load_dotenv

from edu_agents.core.api_key_manager import get_async_openai_client
from edu_agents.tools.brainlift_files import ACCURATE_FIGURES_FILE_KEY, get_file_entry
from utils.supabase_utils import upload_image_to_supabase

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)

def clean_svg(raw: str) -> str:
    # 1. remove Markdown code fences
    raw = re.sub(r"```.*?```", "", raw, flags=re.S)
    # 2. drop anything before the first <svg
    raw = raw[raw.find("<svg"):]
    # 3. dedent and strip BOM / whitespace
    raw = textwrap.dedent(raw).lstrip("\ufeff \n\r\t")
    try:
        ET.fromstring(raw)
    except ET.ParseError as e:
        raise RuntimeError(f"Bad SVG from LLM: {e}") from e
    return raw

async def _generate_svg_code(description: str) -> str:
    """
    Generate SVG code based on a description using GPT-4.
    
    Parameters
    ----------
    description : str
        Description of the image to generate
        
    Returns
    -------
    str
        The generated SVG code
    """
    try:
        system_prompt = """You are an expert at creating SVG images with a focus on educational
        clarity and visual precision. Create clean, accurate SVG code based on the provided
        description. Follow guidance you have been given about Creating Accurate Figures to create
        the image. In particular:

        ## SVG CREATION PRINCIPLES

        1. Ensure the image is accurate, clear, logical, and would be easy for a student to
        understand.
        2. Ensure all components of the image are fully visible within the viewport.
        3. Ensure the sizes of all components of the image are appropriate for the content.
        4. Choose a viewing angle that is most natural for the content you are creating. For
        example, boxes and baskets should be viewed from the front, not the top.
        5. Pay careful attention to the relative positions and orientations of all components of
        the image to ensure the image is logically constructed. For example, when drawing a bag with
        handles, ensure the ends of the handles are exactly tangent to the bag.
        6. Use labels where appropriate to clarify the image.
        7. Do not include excessive empty space around the image. A 10% padding or margin around the
        main content of the image is sufficient.
        8. Do not give images a title. The only text in the image should be labels on objects, if
        needed.
        9. When creating images of real-world objects, sketch them so that they are clearly
        recognizable. You may use color, texture, perspective, and other visual elements to make the
        image more realistic.
            - As long as it will not be confusing given the content you are creating, use color and
            texture fills to make image more attractive and engaging.
        10. When creating mathematical content:
            - Use standard mathematical conventions
            - Choose appropriate scales that make content clearly visible
            - Verify that geometric relationships are mathematically correct
            - Place labels clearly without overlapping other elements

        ## TEXT AND LABELING

        1. **Text Placement**:
           - Position text to avoid overlapping with other elements
           - Use appropriate font families: Arial, Helvetica, or sans-serif
           - Ensure sufficient contrast between text and background
           - Consider text-anchor and dominant-baseline for proper alignment

        2. **Mathematical Notation**:
           - Use Unicode characters for mathematical symbols when possible
           - Keep fractions simple using / notation
           - Use consistent notation throughout the image
        
        ## FINALIZING THE IMAGE

        1. Ensure all components of the image are fully visible within the viewport.
        2. Ensure the image does not contain excessive padding, margins, or other empty space
        outside the main content of the image.
            - Reduce the height of the image such that the empty space is no more than 10% along the
            height.
            - Reduce the width of the image such that the empty space is no more than 10% along the
            width.
            - Be sure to remove from the top and bottom of the image equally to reduce height, and
            from the left and right of the image equally to reduce width.

        ## OUTPUT FORMAT

        - Provide only the SVG code, starting with <?xml version="1.0" encoding="UTF-8"?>
        - No markdown code blocks or additional text
        - Ensure the SVG is well-formed and valid
        - Include all necessary namespace declarations"""

        user_prompt = f"""Create an SVG image that illustrates: {description}

        Follow all the guidelines above to create an educational, accurate, and visually clear SVG
        image. Make sure the image effectively communicates the concept described."""

        # Get the guidance file for accurate figures
        files = [get_file_entry(ACCURATE_FIGURES_FILE_KEY)]
        
        # Build input content with files + user prompt (following conversation.py pattern)
        content = list(files) + [
            {
                "type": "input_text",
                "text": user_prompt,
            }
        ]
        
        # Build input for responses API
        input_items = [
            {
                "type": "message",
                "role": "developer",
                "content": system_prompt
            },
            {
                "type": "message", 
                "role": "user",
                "content": content
            }
        ]

        client = get_async_openai_client(timeout=180.0)
        response = await client.responses.create(
            model="o3",
            input=input_items
        )

        # Extract the assistant message from the response (following runnable_agent.py pattern)
        assistant_msg = next(
            (
                itm
                for itm in response.output
                if getattr(itm, "type", "") == "message"
                and getattr(itm, "role", "") == "assistant"
            ),
            None,
        )
        
        if assistant_msg is None:
            raise Exception("No assistant message found in response")
            
        # Extract the text content from the assistant message
        # Defensive check: ensure text parts are not coroutines
        text_parts = []
        for part in getattr(assistant_msg, "content", []):
            if hasattr(part, "text"):
                text_content = part.text
                if hasattr(text_content, '__await__'):
                    text_content = await text_content
                text_parts.append(text_content)
        svg_code = "".join(text_parts).strip()
        
        if not svg_code:
            raise Exception("Empty SVG code generated")
            
        logger.info("Successfully generated SVG code")
        return svg_code

    except Exception as e:
        logger.error(f"Error generating SVG: {e}")
        raise

async def generate_svg_image(
    description: str,
) -> str:
    """
    Generate an SVG image from a description and convert it to PNG.
    
    Parameters
    ----------
    description : str
        Description of the image to generate
        
    Returns
    -------
    str
        A JSON string containing the URL of the generated and uploaded image and the SVG code
    """
    logger.info(f"Generating SVG image from description: {description}")
    try:
        # Generate SVG code from description
        svg_code = await _generate_svg_code(description)
        
        # Clean up the SVG code
        svg_code = clean_svg(svg_code)

        # Convert SVG to PNG using CairoSVG
        png_bytes = svg2png(
            bytestring=svg_code.encode('utf-8')
        )
        
        # Upload the PNG
        public_url = upload_image_to_supabase(
            image_bytes=png_bytes,
            content_type="image/png",
            bucket_name="incept-images",
            file_extension=".png"
        )
        return f"{{'public_url': '{public_url}', 'svg_code': '{svg_code}'}}"
        
    except Exception as e:
        error_message = f"Error generating SVG image: {str(e)}"
        logger.error(error_message)
        return f"{{'error': 'Failed to generate SVG image: {error_message}'}}"

def generate_svg_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_svg_image",
        "description": "Generate simple schematic images from text descriptions. DO NOT USE if you "
                       "are creating images of real-world objects.",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Description of the image to generate. Be specific about the "
                                   "visual elements, layout, colors, labels, and educational "
                                   "purpose."
                },
            },
            "required": ["description"]
        }
    }
    return spec, generate_svg_image 
