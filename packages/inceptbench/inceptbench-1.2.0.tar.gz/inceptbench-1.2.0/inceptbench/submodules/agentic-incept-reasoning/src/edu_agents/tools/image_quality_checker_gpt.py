import asyncio
import base64
import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import requests
from openai import APIConnectionError, APITimeoutError, BadRequestError
from pydantic import BaseModel

from edu_agents.core.api_key_manager import get_async_openai_client
from utils.supabase_utils import delete_files_from_supabase

logger = logging.getLogger(__name__)

class QualityRating(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NO_ACCESS = "NO_ACCESS"

class ObjectCountCheck(BaseModel):
    """
    Recursive data structure for tracking object counts in images.
    
    Can represent both simple counts (e.g., "4 baskets") and nested counts 
    (e.g., "4 baskets, each containing 6 apples").
    
    Multiple object types can be tracked by having multiple ObjectCountCheck 
    instances in the object_counts list of ImageQualityResult.
    """
    object_name: str
    expected_count: int
    observed_count: int
    is_count_mismatch: bool = False
    contained_objects: Optional[List['ObjectCountCheck']] = None

# Enable forward references for recursive model
ObjectCountCheck.model_rebuild()

class ImageQualityResult(BaseModel):
    rating: QualityRating
    description: str
    selected_image_url: Optional[str] = None  # For multi-image evaluation
    individual_image_ratings: Optional[Dict[str, str]] = None  # For multi-image: URL -> PASS/FAIL
    object_counts: Optional[List[ObjectCountCheck]] = None
    correctness_passed: bool
    consistency_passed: bool
    interpretability_passed: bool
    label_placement_passed: bool
    centroid_object_alignment_passed: bool
    object_counts_passed: bool
    color_use_passed: bool
    composition_passed: bool
    no_object_cut_off_passed: bool
    real_world_consistency_passed: bool
    educational_appropriateness_passed: bool
    match_question_prompt_passed: bool

class ImageQualityCheckerGPT:
    """Checks image quality and accuracy against expected descriptions using OpenAI's vision
    capabilities."""
    
    def __init__(self):
        # Increase timeout to 600 seconds (10 minutes) for image processing
        self.client = get_async_openai_client(timeout=600.0)

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
            # Return a FAIL result with error details and all required fields
            # Handle both single and multi-image cases
            if isinstance(image_urls, str):
                image_urls_list = [image_urls]
            else:
                image_urls_list = image_urls
            
            error_result = ImageQualityResult(
                rating=QualityRating.FAIL,
                description=f"Unable to analyze image due to technical error: {str(e)}",
                individual_image_ratings={url: "FAIL" for url in image_urls_list} \
                    if len(image_urls_list) > 1 else None,
                correctness_passed=False,
                consistency_passed=False,
                interpretability_passed=False,
                label_placement_passed=False,
                centroid_object_alignment_passed=False,
                object_counts_passed=False,
                color_use_passed=False,
                composition_passed=False,
                no_object_cut_off_passed=False,
                real_world_consistency_passed=False,
                match_question_prompt_passed=False,
                educational_appropriateness_passed=False
            )
            return error_result.model_dump_json(indent=2)

    # Base system prompt shared between single and multiple image evaluation
    BASE_SYSTEM_PROMPT = """You are an expert image quality assessor for educational content.

## Evaluation Criteria

- **Correctness**: Images are correct and free of logical errors.
- **Consistency**: Images included in the question are consistent with associated text.
- **Interpretability**: Images are not ambiguous or confusing. All text is legible.
    - However, if the background color of the image is transparent, assume the background will be
    white when deciding whether text or other elements are legible.
- **Label Placement**: Labels in the image should be consistently placed across all objects in the
image. Labels should be placed logically, for example centered on the object they are labeling or
just outside the object they are labeling (provided all labels are placed in the same way).
- **Centroid Object Alignment**: Centroids of objects in the image should be aligned consistently
across the image. For example, if the expected description indicates a particular grid alignment or
the image is visually laid out in an implied grid, the image should show that alignment precisely
relative to the centroids of objects in the image. However, do not penalize slight alignment
differences that are not large enough to cause confusion.
- **Object Counts**: The number of each kind of object in the image should match the number of
objects in the expected description exactly and clearly. VERIFYING OBJECT COUNTS IS CRITICAL - DO IT
VERY CAREFULLY.
- **Color Use**: Unless intentionally specified in the expected description, the image should not be
black and white. It should use color to help students understand the content and make it more
engaging. Do not penalize an image for using a transparent background. Do not penalize the image for
slight color differences that are not large enough to cause confusion.
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

## Verifying Object Counts

- If the description and/or question prompt indicates a certain number of objects, the image should
show EXACTLY that number of objects.
- Record the expected and observed number of objects in the object_counts field for all objects
which are expected to have a certain count.
- If the expected count and observed count are different, set is_count_mismatch to True.
- If the image is supposed to contain nested objects with certain counts, use the recursive
structure to verify both container and contained object counts.
    - For example, if the image is supposed to contain 4 baskets each containing 6 apples, create
    one ObjectCountCheck for "baskets" with expected_count=4 and observed_count=4, then in its
    contained_objects field, add 4 ObjectCountCheck entries for "basket_1_apples",
    "basket_2_apples", "basket_3_apples", and "basket_4_apples", each with expected_count=6 and
    their respective observed_count values.
- Pay special attention to counting objects that are supposed to have a count of 7 or 8 as they are
often confused with each other. Count CAREFULLY!

IMAGES OFTEN HAVE OBJECT COUNT ERRORs, so check for it carefully!!!

## Guidelines

- **Be Strict**: If the image does not meet any of the Evaluation Criteria, rate it as FAIL.
Students learning the material will be given any image rated a PASS, so it's critical the image
clearly conveys the intended content.
- **Be Objective**: While the expected description tells you what the image should show, you should
be objective and strict in your evaluation. Even if the image reflects the expected description, if
it does not meet the Evaluation Criteria, rate it as FAIL."""

    async def _evaluate_multiple_images(self, image_urls: List[str], expected_description: str,
    educational_context: str, question_prompt: str = None, is_retry: bool = False,
    delete_failed_images: bool = True) -> str:
        """Evaluate multiple images and return the best one or fail if none are good enough."""
        
        logger.info(f"Evaluating {len(image_urls)} images:")
        for i, url in enumerate(image_urls):
            logger.info(f"  Image {i+1}: {url}")
        
        system_prompt = self.BASE_SYSTEM_PROMPT + """

## Task: Select Best Image

Your task is to:
1. Evaluate all provided images against the expected description, educational context, and
evaluation criteria
2. If at least one image passes all criteria and has no object count mismatches, return PASS with
the URL of the BEST image according to all Evaluation Criteria
    - If multiple images meet the Evaluation Criteria, select the one that is the most visually
    appealing and meets all Evaluation Criteria.
    - NEVER select an image that contains object count mismatches (is_count_mismatch is True for any
    object in the object_counts field).
3. If no image passes all criteria, return FAIL with a summary of the main issues across all images

CRITICAL: You MUST select the URL exactly as provided in the list below. Do NOT modify, truncate, or
create new URLs.

For PASS ratings: You MUST provide the exact URL of the best image in the selected_image_url field
AND explain why it was selected. You must also provide individual PASS/FAIL ratings for each image
in the individual_image_ratings field.
For FAIL ratings: Provide a comprehensive summary of the main issues found across all images and
specific instructions on how to create a better image. You must also provide individual PASS/FAIL
ratings for each image in the individual_image_ratings field.
For NO_ACCESS ratings: Provide a brief explanation of why the images are not accessible or cannot be
reviewed."""

        try:
            # Create URL mapping for reference
            url_list = "\n".join([f"Image {i+1}: {url}" for i, url in enumerate(image_urls)])
            
            user_prompt = f"""Please evaluate these {len(image_urls)} images against the expected
description within the specified educational context and question prompt:

Educational Context: {educational_context}

Question Prompt the image will be used in (if any): {question_prompt}

Expected Description: {expected_description}

IMAGE URL MAPPING:
{url_list}

IMPORTANT: You must select the URL exactly as listed above. Do not modify or create new URLs.

Select the best image that meets all criteria, or indicate if none are acceptable."""

            # Prepare image inputs for OpenAI API
            input_content = [{"role": "developer", "content": system_prompt}]
            
            user_content = [{"type": "input_text", "text": user_prompt}]
            
            # Add all images to the user content
            for i, image_url in enumerate(image_urls):
                if is_retry:
                    # Try downloading the image and passing it as bytes
                    try:
                        await asyncio.sleep(1)  # Small delay between requests
                        response = requests.get(image_url, timeout=60)  # Add explicit timeout
                        response.raise_for_status()  # Raise an exception for bad status codes
                        image_bytes = response.content
                        if image_bytes:
                            image_url = f'data:image/png;base64,{base64.b64encode(image_bytes).decode("utf-8")}'  # noqa: E501
                        else:
                            logger.warning(f"Empty response when downloading image {i+1}")
                    except Exception as e:
                        logger.error(f"Error downloading image {i+1}: {e}")
                        # Keep original URL if download fails
                
                user_content.append({"type": "input_image", "image_url": image_url})
            
            input_content.append({"role": "user", "content": user_content})

            logger.info(f"Evaluating {len(image_urls)} images for quality...")
            
            # Use structured outputs with vision capabilities
            try:
                response = await self.client.responses.parse(
                    model="gpt-5",
                    input=input_content,
                    text_format=ImageQualityResult,
                    reasoning={"effort": "medium"}
                )
            except (APITimeoutError, APIConnectionError, BadRequestError) as api_error:
                logger.warning(f"API error during multi-image evaluation: {api_error}")
                # Check if this is a timeout/download error and we haven't already retried
                if not is_retry and ("timeout" in str(api_error).lower() \
                    or "downloading" in str(api_error).lower()):
                    logger.info(
                        "Retrying multi-image evaluation with base64 encoding due to "
                        "download timeout"
                    )
                    return await self._evaluate_multiple_images(image_urls, expected_description,
                        educational_context, question_prompt, True)
                else:
                    # If retry failed or it's a different error, raise the original exception
                    raise api_error
            
            # Extract the structured response
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if (content_item.type == "output_text" and 
                            hasattr(content_item, "parsed") and 
                            content_item.parsed is not None):
                            
                            result = content_item.parsed
                            
                            # Validate and handle the selected URL for PASS ratings
                            if result.rating == QualityRating.PASS:
                                if not result.selected_image_url:
                                    logger.warning(
                                        "Model returned PASS but no selected_image_url. Using "
                                        "first image."
                                    )
                                    result.selected_image_url = image_urls[0]
                                elif result.selected_image_url not in image_urls:
                                    logger.error(
                                        f"Model selected invalid URL: {result.selected_image_url}"
                                    )
                                    logger.error(f"Valid URLs were: {image_urls}")
                                    logger.warning(
                                        "Model hallucinated a URL. Falling back to first image."
                                    )
                                    result.selected_image_url = image_urls[0]
                                
                                logger.info(
                                    "GPT multi-image quality check result: PASS - Selected: "
                                    f"{result.selected_image_url}"
                                )
                                # Multi-image PASS: delete all unselected images
                                if delete_failed_images:
                                    urls_to_delete = [url for url in image_urls \
                                        if url != result.selected_image_url]
                                    delete_files_from_supabase(urls_to_delete, delay_seconds=5.0)
                            else:
                                logger.error(f"GPT multi-image quality check result: {result}")
                                # Multi-image FAIL: delete all images since none were good enough
                                if delete_failed_images:
                                    delete_files_from_supabase(image_urls, delay_seconds=5.0)
                            
                            if result.rating == QualityRating.NO_ACCESS and not is_retry:
                                return await self._evaluate_multiple_images(image_urls,
                                    expected_description, educational_context, question_prompt,
                                    True, delete_failed_images)
                                
                            return result.model_dump_json(indent=2)
                        elif (content_item.type == "output_text" and 
                              hasattr(content_item, "text")):
                            # Fallback to text if parsed object not available
                            if content_item.text.startswith("PASS"):
                                logger.info(
                                    f"GPT multi-image quality check result: {content_item.text}"
                                )
                            else:
                                logger.error(
                                    f"GPT multi-image quality check result: {content_item.text}"
                                )
                                # Multi-image FAIL: delete all images since none were good enough
                                if delete_failed_images:
                                    delete_files_from_supabase(image_urls, delay_seconds=5.0)
                            return content_item.text
            
            raise RuntimeError("No structured response found in API response")
            
        except Exception as e:
            logger.error(f"Error in multi-image evaluation: {e}")
            error_result = ImageQualityResult(
                rating=QualityRating.FAIL,
                description=f"Unable to evaluate images due to technical error: {str(e)}",
                individual_image_ratings={url: "FAIL" for url in image_urls},
                correctness_passed=False,
                consistency_passed=False,
                interpretability_passed=False,
                label_placement_passed=False,
                centroid_object_alignment_passed=False,
                object_counts_passed=False,
                color_use_passed=False,
                composition_passed=False,
                no_object_cut_off_passed=False,
                real_world_consistency_passed=False,
                match_question_prompt_passed=False,
                educational_appropriateness_passed=False
            )
            # Multi-image FAIL: delete all images since none were good enough
            if delete_failed_images:
                delete_files_from_supabase(image_urls, delay_seconds=5.0)
            return error_result.model_dump_json(indent=2)

    async def _evaluate_single_image(self, image_url: str, expected_description: str,
    educational_context: str, question_prompt: str = None, is_retry: bool = False,
    delete_failed_images: bool = True) -> str:
        """Evaluate a single image."""
        
        system_prompt = self.BASE_SYSTEM_PROMPT + """

## Rating the Image

Rate the image as:
- PASS: If the image accurately depicts the expected content, contains NO object count mismatches,
and passes all Evaluation Criteria.
- FAIL: If there are significant issues with any Evaluation Criteria. All Evaluation Criteria must
pass for a PASS rating.
- NO_ACCESS: If the image is not accessible or cannot be reviewed.

For FAIL ratings, provide specific details about ALL Evaluation Criteria issues in ALL relevant
elements within the image. Include specific instructions on how to resolve the issues.
For PASS ratings, briefly confirm what the image shows correctly.
For NO_ACCESS ratings, provide a brief explanation of why the image is not accessible or cannot be
reviewed."""

        user_prompt = f"""Please evaluate this image against the expected description within the
specified educational context:

Educational Context: {educational_context}

Question Prompt the image will be used in (if any): {question_prompt}

Expected Description: {expected_description}

Analyze the image and determine if it accurately depicts what is described and meets all your
criteria."""

        if is_retry:
            # Try downloading the image and passing it as bytes
            try:
                response = requests.get(image_url, timeout=60)  # Add explicit timeout
                response.raise_for_status()  # Raise an exception for bad status codes
                image_bytes = response.content
                if image_bytes:
                    image_url = f'data:image/png;base64,{base64.b64encode(image_bytes).decode("utf-8")}'  # noqa: E501
                else:
                    logger.warning("Empty response when downloading image")
            except Exception as e:
                logger.error(f"Error downloading image: {e}")
                logger.info("Retrying image quality check with URL in 3 seconds...")
                await asyncio.sleep(3)

        # Use structured outputs with vision capabilities
        logger.info(f"Checking image quality for {image_url}")
        try:
            response = await self.client.responses.parse(
                model="gpt-5",
                input=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "input_text", "text": user_prompt},
                        {"type": "input_image", "image_url": image_url}
                    ]}
                ],
                text_format=ImageQualityResult,
                reasoning={"effort": "medium"}
            )
        except (APITimeoutError, APIConnectionError, BadRequestError) as api_error:
            logger.warning(f"API error during single image evaluation: {api_error}")
            # Check if this is a timeout/download error and we haven't already retried
            if not is_retry and ("timeout" in str(api_error).lower() \
                or "downloading" in str(api_error).lower()):
                logger.info(
                    "Retrying single image evaluation with base64 encoding due to download timeout"
                )
                return await self._evaluate_single_image(image_url, expected_description,
                    educational_context, question_prompt, True)
            else:
                # If retry failed or it's a different error, create a proper FAIL result
                error_result = ImageQualityResult(
                    rating=QualityRating.FAIL,
                    description=f"Unable to analyze image due to API error: {str(api_error)}",
                    correctness_passed=False,
                    consistency_passed=False,
                    interpretability_passed=False,
                    label_placement_passed=False,
                    centroid_object_alignment_passed=False,
                    object_counts_passed=False,
                    color_use_passed=False,
                    composition_passed=False,
                    no_object_cut_off_passed=False,
                    real_world_consistency_passed=False,
                    match_question_prompt_passed=False,
                    educational_appropriateness_passed=False
                )
                return error_result.model_dump_json(indent=2)
        
        # Extract the structured response
        for output_item in response.output:
            if output_item.type == "message":
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        
                        # Return the JSON string representation
                        if content_item.parsed.rating == QualityRating.PASS:
                            logger.info(f"Image quality check result: {content_item.parsed}")
                        else:
                            logger.error(f"Image quality check result: {content_item.parsed}")
                            # Single image FAIL: delete the failed image
                            if delete_failed_images:
                                delete_files_from_supabase([image_url], delay_seconds=5.0)
                        if content_item.parsed.rating == QualityRating.NO_ACCESS and not is_retry:
                            return await self._evaluate_single_image(image_url,
                                expected_description, educational_context,
                                question_prompt=question_prompt, is_retry=True,
                                delete_failed_images=delete_failed_images)
                        return content_item.parsed.model_dump_json(indent=2)
                    elif (content_item.type == "output_text" and 
                          hasattr(content_item, "text")):
                        # Fallback to text if parsed object not available
                        if content_item.text.startswith("PASS"):
                            logger.info(f"Image quality check result: {content_item.text}")
                        else:
                            logger.error(f"Image quality check result: {content_item.text}")
                            # Single image FAIL: delete the failed image
                            if delete_failed_images:
                                delete_files_from_supabase([image_url], delay_seconds=5.0)
                        return content_item.text
        
        raise RuntimeError("No structured response found in API response")


def generate_image_quality_checker_gpt_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the image quality checker tool specification and function."""
    
    checker = ImageQualityCheckerGPT()
    
    async def image_quality_check_function(image_urls: Union[str, List[str]], expected_description:
        str, educational_context: str, question_prompt: str = None,
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
                "question_prompt": {
                    "type": "string",
                    "description": "The prompt of the question that the image is associated " + \
                        "with, if any. This will be used to verify the image is appropriate " + \
                        "for the question."
                },
                "educational_context": {
                    "type": "string",
                    "description": "The educational context of the image, such as the grade " + \
                        "level and subject matter. This will be used to verify the image is " + \
                        "appropriate for a typical student in the target grade trying to learn " + \
                        "the material."
                }
            },
            "required": ["image_urls", "expected_description", "question_prompt",
                        "educational_context"]
        }
    }
    
    return spec, image_quality_check_function 