import asyncio
import json
import logging
import os
from enum import Enum
from time import sleep
from typing import Any, Callable, Dict, List, Optional, Union

import requests
from google import genai
from google.genai import types
from pydantic import BaseModel

from utils.supabase_utils import delete_files_from_supabase

logger = logging.getLogger(__name__)

class QualityRating(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NO_ACCESS = "NO_ACCESS"

class ImageQualityResult(BaseModel):
    rating: QualityRating
    description: str
    selected_image_url: Optional[str] = None  # For multi-image evaluation
    individual_image_ratings: Optional[Dict[str, str]] = None  # For multi-image: URL -> PASS/FAIL

class ImageQualityChecker:
    """Checks image quality and accuracy against expected descriptions using Gemini's vision
    capabilities."""
    
    SYSTEM_PROMPT = """You are an expert image quality assessor for educational content.
{task_description}

## Evaluation Criteria

- **Correctness**: Images are correct and free of logical errors.
- **Consistency**: Images included in the question are consistent with associated text.
- **Interpretability**: Images are not ambiguous or confusing. All text is legible.
- **Label Placement**: Labels in the image should be sufficiently placed on objects in the image to
enable students to understand any important details of the image. Labels should be placed logically,
for example centered on the object they are labeling or just outside the object they are labeling
(provided all labels are placed in the same way). Labels do not need to be placed precisely
according to the expected description, as long as they are placed unambiguously on visual
inspection.
- **Centroid Object Alignment**: Centroids of objects in the image should be aligned consistently
across the image. For example, if the expected description indicates a particular grid alignment or
the image is visually laid out in an implied grid, the image should show that alignment precisely
relative to the centroids of objects in the image. However, do not penalize slight alignment
differences that are not large enough to cause confusion.
- **Object Counts**: The number of each kind of object in the image should match the number of
objects in the expected description exactly and clearly. Carefully count the objects in the image
and verify that the counts match the Expected Description. VERIFYING OBJECT COUNTS IS CRITICAL - DO
IT VERY CAREFULLY!
- **Color Use**: Colors in the image should be reasonable for the educational content. They should
reasonably match the expected description, but do not need to be exact, especially if the color is
not relevant to the educational content.
- **Composition**:
    - The image is visually full, without excessive whitespace between elements.
    - The overall composition is precisely centered within the image.
    - Elements are spaced appropriately relative to the expected description.
- **No Cut-Off Elements**:
    - ALL essential elements in the image have a CLEAR, COMPLETE separation from the edge of the
    image to avoid cutting off elements.
    - Image cropping does not cut off any essential elements.
    - NO essential elements in the image are cut off IN ANY WAY by the edge of the image. If unsure,
    err on the side of rejecting images that contain possible cut-off elements.
- **Real-World Consistency**: If the image is depicting a real-world physical object, the object
should be reasonably recognizable as that object.
- **Educationally Appropriate**: The image should be appropriate for a typical student in the target
grade trying to learn the material.
- **Match Question Prompt**: If a question prompt is provided, the image should be accurately
reflect the content of the question prompt. **CRITICAL**: if the image is intended to depict a
certain number of objects in a question prompt, the image should show EXACTLY that number of
objects.
- **Allow Non-Disruptive Variations**: If details of the image differ from the expected description
in ways that are not disruptive to the learning experience, allow them.
    - Minor differences in the appearance of objects in the image are acceptable, as long as they
    would not be confusing in the context of the question prompt and educational content.
        - For example, if the expected description says the image contains four wicker baskets, but
        the baskets are plainly colored, allow it.
        - In another example, if the expected image says it contains rectangular baskets, but the
        baskets are actually square or round, AND the baskets being rectangular is not necessary to
        the educational content, allow it.
        - In another example, if the expected image would contain open-topped baskets, but the
        baskets are actually closed, allow it as long as this does not conflict with the question
        prompt and educational content.
        - However, note that on objects like bookshelves, the top of the bookshelf is not considered
        a shelf, so it does not count as a shelf for the purpose of counting shelves.
    - As long as colors specified in the expected description are not significantly different from
    the colors in the image, allow it. Don't penalize the image for using different shades of the
    specified color.
    - Unless the background of the image is relevant to the educational content, do not penalize the
    image for using a different background than the one specified in the expected description.
    - Unless they cause significant confusion, do not penalize the image for using decorative
    elements.
    - As long as an object can be reasonably identified as the object described in the expected
    description, allow it. For example, a trophy on a "pedestal" is acceptable if the description
    includes a trophy on an "award stand".
    - Background or scenic components of an image, such as tables, classrooms, fields, etc., are
    acceptable.
    - If several objects are described as "identical", they do not need to be literally identical,
    as long as they are easily identifiable as the same type of object.
- **Express Your Preferences through Selected URL, not Failing Other Good Images**: If you prefer a
particular image for some reason, indicate that by choosing it in the selected_image_url field,
rather than by rating other images that otherwise meet the Evaluation Criteria as a FAIL.

## Guidelines

- **Be Objective**: While the expected description tells you what the image should show, you should
be objective and strict in your evaluation. Even if the image reflects the expected description, if
it does not meet the Evaluation Criteria, rate it as FAIL.
- **QUALITY OVERALL**: The most important thing is that you hold a high bar for quality, and if the
quality bar is not met, you provide clear guidance on how to achieve the quality bar.

{rating_guidelines}

You must respond with a JSON object containing the following fields:
- "rating": either "PASS", "FAIL", or "NO_ACCESS"
- "description": detailed analysis and feedback
- "selected_image_url": (only for multi-image evaluation when rating is PASS) the exact URL of the
best image
- "individual_image_ratings": (for multi-image evaluation) object mapping each image URL to "PASS"
or "FAIL"
"""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    async def check_image_quality(self, image_urls: Union[str, List[str]],
    expected_description: str, educational_context: str, question_prompt: str = None,
    is_retry: bool = False, delete_failed_images: bool = True) -> str:
        """
        Check if image(s) match expected description and meet quality standards.
        
        Parameters
        ----------
        image_urls : Union[str, List[str]]
            Either a single image URL or a list of image URLs to analyze
        expected_description : str
            Description of what the image is supposed to depict
        educational_context : str
            The educational context of the image
        question_prompt : str, optional
            The prompt of the question that the image is associated with, if any. This will be used
            to verify the image is appropriate for the question.
        is_retry : bool, optional
            Whether this is a retry attempt
        delete_failed_images : bool, default True
            Whether to automatically delete failed or unselected images after evaluation
            
        Returns
        -------
        str
            JSON string with rating (PASS/FAIL) and description
        """
        try:
            # Handle both single URL and list of URLs for backward compatibility
            if isinstance(image_urls, str):
                image_urls = [image_urls]
            
            # For multiple images, evaluate all and select the best one
            if len(image_urls) > 1:
                return await self._evaluate_multiple_images(image_urls, expected_description,
                    educational_context, question_prompt, is_retry, delete_failed_images)
            else:
                # Single image evaluation (existing logic)
                return await self._evaluate_single_image(image_urls[0], expected_description,
                    educational_context, question_prompt, is_retry, delete_failed_images)
                
        except Exception as e:
            error_message = f"Error checking image quality: {str(e)}"
            logger.error(error_message)
            # Return a FAIL result with error details
            error_result = ImageQualityResult(
                rating=QualityRating.FAIL,
                description=f"Unable to analyze image due to technical error: {str(e)}"
            )
            return error_result.model_dump_json(indent=2)

    async def _evaluate_multiple_images(self, image_urls: List[str], expected_description: str,
    educational_context: str, question_prompt: str = None, is_retry: bool = False,
    delete_failed_images: bool = True) -> str:
        """Evaluate multiple images and return the best one or fail if none are good enough."""
        
        logger.info(f"Evaluating {len(image_urls)} images:")
        for i, url in enumerate(image_urls):
            logger.info(f"  Image {i+1}: {url}")
        
        system_prompt = self.SYSTEM_PROMPT.format(
            task_description="You are evaluating multiple images to select the best one that " + \
                "accurately depicts the expected content and meets quality standards.",
            rating_guidelines="""## Task: Select Best Image

Your task is to:
1. Evaluate all provided images against the expected description, educational context, question
prompt, and evaluation criteria
2. If at least one image meets all criteria, return PASS with the URL of the BEST image according to
all Evaluation Criteria. If multiple images meet the Evaluation Criteria, select the one that is the
most visually appealing and meets all Evaluation Criteria.
3. If no image meets the criteria, return FAIL with a summary of the main issues across all images

CRITICAL: You MUST select the URL exactly as provided in the list below. Do NOT modify, truncate, or
create new URLs.

For PASS ratings: You MUST provide the exact URL of the best image in the selected_image_url field
AND explain why it was selected. You must also provide individual PASS/FAIL ratings for each image
in the individual_image_ratings field.
For FAIL ratings: Provide a comprehensive summary of the main issues found across all images and
specific instructions on how to create a better image. You must also provide individual PASS/FAIL
ratings for each image in the individual_image_ratings field."""
        )

        try:
            # Create URL mapping for reference
            url_list = "\n".join([f"Image {i+1}: {url}" for i, url in enumerate(image_urls)])
            
            # Prepare the prompt
            user_prompt = f"""Please evaluate these {len(image_urls)} images against the expected
description within the specified educational context and question prompt:

Educational Context: {educational_context}

Question Prompt the image will be used in (if any): {question_prompt}

Expected Description: {expected_description}

IMAGE URL MAPPING:
{url_list}

IMPORTANT: You must select the URL exactly as listed above. Do not modify or create new URLs.

Select the best image that meets all criteria, or indicate if none are acceptable."""
            
            # Prepare content parts - start with text prompt
            content_parts = [system_prompt + "\n\n" + user_prompt]
            
            # Add all images
            for i, image_url in enumerate(image_urls):
                try:
                    if is_retry:
                        # Try downloading the image with delay
                        sleep(1)  # Small delay between requests
                        
                    # Download the image
                    image_response = requests.get(image_url)
                    image_response.raise_for_status()
                    image_bytes = image_response.content
                    
                    # Determine media type
                    content_type = image_response.headers.get('content-type', 'image/png')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        media_type = "image/jpeg"
                    elif 'webp' in content_type:
                        media_type = "image/webp"
                    else:
                        media_type = "image/png"
                    
                    # Create image part using proper types.Part.from_bytes (from official docs)
                    image_part = types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=media_type
                    )
                    content_parts.append(image_part)
                        
                except Exception as e:
                    logger.error(f"Error processing image {i+1}: {e}")
                    # Skip this image rather than failing the entire evaluation
                    continue

            logger.info(f"Evaluating {len(image_urls)} images for quality...")
            
            # Generate response with Gemini (simple format from official docs)
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-pro",
                contents=content_parts,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            response_text = response.text.strip()
            logger.info(f"Gemini multi-image response: {response_text}")
            
            try:
                response_data = json.loads(response_text)
                
                # Create the result object
                rating = QualityRating(response_data["rating"])
                selected_url = None
                
                if rating == QualityRating.PASS:
                    selected_url = response_data.get("selected_image_url")
                    
                    # Handle case where model returns PASS but no URL
                    if not selected_url:
                        logger.warning(
                            "Model returned PASS but no selected_image_url. Using first image."
                        )
                        selected_url = image_urls[0]
                    # Validate that the selected URL is from the provided list
                    elif selected_url not in image_urls:
                        logger.error(f"Model selected invalid URL: {selected_url}")
                        logger.error(f"Valid URLs were: {image_urls}")
                        logger.warning("Model hallucinated a URL. Falling back to first image.")
                        selected_url = image_urls[0]
                
                # Get individual image ratings
                individual_ratings = response_data.get("individual_image_ratings", {})
                
                result = ImageQualityResult(
                    rating=rating,
                    description=response_data["description"],
                    selected_image_url=selected_url,
                    individual_image_ratings=individual_ratings
                )
                
                if result.rating == QualityRating.PASS:
                    logger.info(
                        "Gemini multi-image quality check result: PASS - Selected: "
                        f"{result.selected_image_url}"
                    )
                    # Multi-image PASS: delete all unselected images
                    if delete_failed_images:
                        urls_to_delete = [url for url in image_urls \
                            if url != result.selected_image_url]
                        delete_files_from_supabase(urls_to_delete, delay_seconds=5.0)
                else:
                    logger.error(f"Gemini multi-image quality check result: {result}")
                    # Multi-image FAIL: delete all images since none were good enough
                    if delete_failed_images:
                        delete_files_from_supabase(image_urls, delay_seconds=5.0)
                    
                if result.rating == QualityRating.NO_ACCESS and not is_retry:
                    return self._evaluate_multiple_images(image_urls, expected_description,
                        educational_context, question_prompt, True, delete_failed_images)
                    
                return result.model_dump_json(indent=2)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini JSON response: {e}")
                logger.error(f"Raw response: {response_text}")
                # Fallback to a FAIL result
                result = ImageQualityResult(
                    rating=QualityRating.FAIL,
                    description=f"Unable to parse evaluation response: {response_text}",
                    individual_image_ratings={url: "FAIL" for url in image_urls}
                )
                # Multi-image FAIL: delete all images since none were good enough
                if delete_failed_images:
                    delete_files_from_supabase(image_urls, delay_seconds=5.0)
                return result.model_dump_json(indent=2)
            
        except Exception as e:
            logger.error(f"Error in multi-image evaluation: {e}")
            error_result = ImageQualityResult(
                rating=QualityRating.FAIL,
                description=f"Unable to evaluate images due to technical error: {str(e)}",
                individual_image_ratings={url: "FAIL" for url in image_urls}
            )
            # Multi-image FAIL: delete all images since none were good enough
            if delete_failed_images:
                delete_files_from_supabase(image_urls, delay_seconds=5.0)
            return error_result.model_dump_json(indent=2)

    async def _evaluate_single_image(self, image_url: str, expected_description: str,
    educational_context: str, question_prompt: str = None, is_retry: bool = False,
    delete_failed_images: bool = True) -> str:
        """Evaluate a single image."""
        
        system_prompt = self.SYSTEM_PROMPT.format(
            task_description="Your task is to evaluate whether an image accurately depicts " + \
                "what it's supposed to show and meets quality standards for educational use.",
            rating_guidelines="""## Rating the Image

Rate the image as:
- PASS: If the image accurately depicts the expected content and meets all Evaluation Criteria.
- FAIL: If there are significant issues with any Evaluation Criteria. All Evaluation Criteria must
be met for a PASS rating.
- NO_ACCESS: If the image is not accessible or cannot be reviewed.

For FAIL ratings, provide specific details about ALL Evaluation Criteria issues in ALL relevant
elements within the image. Include specific instructions on how to resolve the issues.
For PASS ratings, briefly confirm what the image shows correctly.
For NO_ACCESS ratings, provide a brief explanation of why the image is not accessible or cannot be
reviewed."""
        )

        user_prompt = f"""Please evaluate this image against the expected description within the
specified educational context and question prompt:

Educational Context: {educational_context}

Question Prompt the image will be used in (if any): {question_prompt}

Expected Description: {expected_description}

Analyze the image and determine if it accurately depicts what is described and meets all your
criteria."""

        try:
            # Download and prepare the image
            if is_retry:
                logger.info("Retrying image quality check in 3 seconds...")
                sleep(3)
                
            logger.info(f"Checking image quality for {image_url}")
            
            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            image_bytes = image_response.content

            # Determine media type
            content_type = image_response.headers.get('content-type', 'image/png')
            if 'jpeg' in content_type or 'jpg' in content_type:
                media_type = "image/jpeg"
            elif 'webp' in content_type:
                media_type = "image/webp"
            else:
                media_type = "image/png"
            
            # Create image part using proper types.Part.from_bytes (from official docs)
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=media_type
            )

            # Generate response with Gemini (simple format from official docs)
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-pro",
                contents=[
                    system_prompt + "\n\n" + user_prompt,
                    image_part
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            response_text = response.text.strip()
            logger.info(f"Gemini single image response: {response_text}")
            
            try:
                response_data = json.loads(response_text)
                
                # Create the result object
                rating = QualityRating(response_data["rating"])
                result = ImageQualityResult(
                    rating=rating,
                    description=response_data["description"]
                )
                
                if result.rating == QualityRating.PASS:
                    logger.info(f"Image quality check result: {result}")
                else:
                    logger.error(f"Image quality check result: {result}")
                    # Single image FAIL: delete the failed image
                    if delete_failed_images:
                        delete_files_from_supabase([image_url], delay_seconds=5.0)
                    
                if result.rating == QualityRating.NO_ACCESS and not is_retry:
                    return self._evaluate_single_image(image_url, expected_description,
                        educational_context, question_prompt, True, delete_failed_images)
                    
                return result.model_dump_json(indent=2)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini JSON response: {e}")
                logger.error(f"Raw response: {response_text}")
                # Fallback to a FAIL result
                result = ImageQualityResult(
                    rating=QualityRating.FAIL,
                    description=f"Unable to parse evaluation response: {response_text}"
                )
                # Single image FAIL: delete the failed image
                if delete_failed_images:
                    delete_files_from_supabase([image_url], delay_seconds=5.0)
                return result.model_dump_json(indent=2)
        
        except Exception as e:
            logger.error(f"Error evaluating single image: {e}")
            result = ImageQualityResult(
                rating=QualityRating.FAIL,
                description=f"Unable to evaluate image due to technical error: {str(e)}"
            )
            # Single image FAIL: delete the failed image
            if delete_failed_images:
                delete_files_from_supabase([image_url], delay_seconds=5.0)
            return result.model_dump_json(indent=2)


def generate_image_quality_checker_tool_gemini() -> tuple[Dict[str, Any], Callable]:
    """Generate the image quality checker tool specification and function."""
    
    checker = ImageQualityChecker()
    
    async def image_quality_check_function(image_urls: Union[str, List[str]],
    expected_description: str, educational_context: str, question_prompt: str = None,
    delete_failed_images: bool = True) -> str:
        """Check if image(s) accurately depict the expected content and meet quality standards."""
        return await checker.check_image_quality(image_urls, expected_description,
            educational_context, question_prompt=question_prompt,
            delete_failed_images=delete_failed_images)
    
    spec = {
        "type": "function",
        "name": "check_image_quality",
        "description": "Evaluate whether image(s) accurately depict expected content and meet " + \
            "quality standards for educational use. Can evaluate a single image or multiple " + \
            "images. For multiple images, returns the best one that meets standards or fails " + \
            "if none are acceptable.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_urls": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Either a single image URL (string) or a list of image URLs " + \
                        "to analyze and evaluate for quality and accuracy."
                },
                "expected_description": {
                    "type": "string", 
                    "description": "Description of what the image is supposed to depict or " + \
                        "show, focused on a precise description of all objects in the image " + \
                        "that a student may need to identify (including counts of these " + \
                        "objects). Don't include details that are not relevant to what the " + \
                        "student is supposed to observe in the image."
                },
                "educational_context": {
                    "type": "string",
                    "description": "The educational context of the image. This will be used " + \
                        "to verify the image is appropriate for a typical student in the " + \
                        "target grade trying to learn the material."
                },
                "question_prompt": {
                    "type": "string",
                    "description": "The prompt of the question that the image is associated " + \
                        "with, if any. This will be used to verify the image is appropriate " + \
                        "for the question."
                }
            },
            "required": ["image_urls", "expected_description", "educational_context",
                        "question_prompt"]
        }
    }
    
    return spec, image_quality_check_function
