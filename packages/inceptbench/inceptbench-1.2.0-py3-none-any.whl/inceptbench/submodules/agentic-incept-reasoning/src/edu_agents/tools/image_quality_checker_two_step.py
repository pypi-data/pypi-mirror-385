import logging
import time
import asyncio
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from openai import APIConnectionError, APITimeoutError, BadRequestError
from pydantic import BaseModel

from edu_agents.core.api_key_manager import get_async_openai_client
from utils.supabase_utils import delete_files_from_supabase

logger = logging.getLogger(__name__)

class QualityRating(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NO_ACCESS = "NO_ACCESS"

class ObjectProperties(BaseModel):
    """Properties that can be associated with objects."""
    size: Optional[str] = None
    color: Optional[str] = None
    shape: Optional[str] = None
    material: Optional[str] = None
    position: Optional[str] = None
    other_attributes: Optional[str] = None

class ObjectItem(BaseModel):
    """
    Represents a single object in the hierarchical structure.
    Can contain children objects and optional properties.
    """
    type: str
    id: str
    children: Optional[List['ObjectItem']] = None
    # props: Optional[ObjectProperties] = None

# Enable forward references for recursive model
ObjectItem.model_rebuild()

class ObjectTypeCount(BaseModel):
    """Count for a specific object type."""
    object_type: str
    count: int

class ObjectCountData(BaseModel):
    """
    Hierarchical object counting data structure.
    Contains both rollup counts and detailed hierarchical breakdown.
    """
    scene_id: str
    version: int
    rollup_counts: List[ObjectTypeCount]  # List of object type counts
    items: List[ObjectItem]

class ObjectCountResult(BaseModel):
    """Result of the object counting step."""
    success: bool
    count_data: Optional[ObjectCountData] = None
    error_message: Optional[str] = None

class QualityCheckResult(BaseModel):
    """Result of the quality check step (without counting)."""
    rating: QualityRating
    description: str
    selected_image_url: Optional[str] = None  # For multi-image evaluation
    individual_image_ratings: Optional[Dict[str, str]] = None  # For multi-image: URL -> PASS/FAIL
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

class TwoStepQualityResult(BaseModel):
    """Final result combining object counting and quality check."""
    rating: QualityRating
    description: str
    selected_image_url: Optional[str] = None  # For multi-image evaluation
    individual_image_ratings: Optional[Dict[str, str]] = None  # For multi-image: URL -> PASS/FAIL
    object_count_data: Optional[ObjectCountData] = None
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

class ImageQualityCheckerTwoStep:
    """Two-step image quality checker: first count objects, then evaluate quality."""
    
    def __init__(self):
        # Increase timeout to 600 seconds (10 minutes) for image processing
        self.client = get_async_openai_client(timeout=600.0)

    async def check_image_quality(self, image_urls: Union[str, List[str]], expected_description: str,
        educational_context: str, question_prompt: str = None, is_retry: bool = False,
        delete_failed_images: bool = True) -> str:
        """
        Two-step image quality check: count objects first, then evaluate quality.
        
        Parameters
        ----------
        image_urls : Union[str, List[str]]
            Either a single image URL or a list of image URLs to analyze
        expected_description : str
            Description of what the image is supposed to depict
        educational_context : str
            The educational context of the image
        question_prompt : str, optional
            The prompt of the question that the image is associated with
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
                # Single image evaluation
                return await self._evaluate_single_image(image_urls[0], expected_description,
                    educational_context, question_prompt, is_retry, delete_failed_images)
                
        except Exception as e:
            error_message = f"Error checking image quality: {str(e)}"
            logger.error(error_message)
            
            # Handle both single and multi-image cases
            if isinstance(image_urls, str):
                image_urls_list = [image_urls]
            else:
                image_urls_list = image_urls
            
            error_result = TwoStepQualityResult(
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

    async def _count_objects_in_image(self, image_url: str, is_retry: bool = False) -> ObjectCountResult:
        """
        Step 1: Count all objects in the image without knowing expected description.
        
        Returns detailed hierarchical count data.
        """
        
        system_prompt = """You are an expert object counter and analyzer. Your job is to carefully
examine an image and create a detailed hierarchical inventory of ALL objects you can see.

## Instructions

1. **Identify ALL distinct objects** in the image, no matter how small or seemingly insignificant
2. **Create a hierarchical structure** showing which objects contain or are grouped with other
objects
3. **Count precisely** - accuracy is critical
4. **Assign meaningful IDs** to each object for tracking
5. **Include relevant properties** like size, color, or other distinguishing features when they
matter for counting. If different objects have similar properties but are visually distinctive
(e.g., two objects are both shaded, but one is shaded with texture and the other is plainly shaded),
include the properties that make them distinctive.

## Output Format

You must return a structured JSON with:
- **scene_id**: A descriptive ID for the overall scene
- **version**: Always 1
- **rollup_counts**: List of total counts by object type (e.g., [{"object_type": "table",
"count": 3}, {"object_type": "tray", "count": 12}])
- **items**: Hierarchical list of objects with children and properties

## Hierarchical Structure Guidelines

- Use **parent-child relationships** to show containment (e.g., tables contain trays, trays contain
compartments)
- Give each object a **unique ID** that reflects its hierarchy (e.g.,
"table-1-tray-2-compartment-3")
- Be **consistent** in your naming and ID schemes

## Counting Guidelines

- Count **every instance** of each object type
- If objects are partially visible, count them if you can clearly identify what they are
- If objects appear identical, still count them separately with unique IDs
- Pay special attention to objects that might be easy to miscount (like compartments in trays)

## Example Structure
```json
{
  "scene_id": "classroom-desks-001",
  "version": 1,
  "rollup_counts": [
    {"object_type": "desk", "count": 4},
    {"object_type": "drawer", "count": 8},
    {"object_type": "pencil", "count": 12}
  ],
  "items": [
    {
      "type": "desk",
      "id": "desk-1",
      "children": [
        {
          "type": "drawer", 
          "id": "desk-1-drawer-1",
          "children": [
            {"type": "pencil", "id": "d1-dr1-pencil-1"},
            {"type": "pencil", "id": "d1-dr1-pencil-2"}
          ]
        }
      ]
    }
  ]
}
```

Be extremely careful and methodical in your counting. This data will be used for quality
assessment."""

        user_prompt = """Please analyze this image and create a complete hierarchical inventory of
        all objects you can see. Count carefully and systematically, working from larger containers
        to smaller contained objects."""

        # Note: GPT-5 will download the image directly from the URL during processing

        try:
            logger.info(f"Step 1: Counting objects in image {image_url}")
            response = await self.client.responses.parse(
                model="gpt-5",
                input=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "input_text", "text": user_prompt},
                        {"type": "input_image", "image_url": image_url}
                    ]}
                ],
                text_format=ObjectCountData,
                reasoning={"effort": "low"}
            )
            
            # Extract the structured response
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if (content_item.type == "output_text" and 
                            hasattr(content_item, "parsed") and 
                            content_item.parsed is not None):
                            
                            count_data = content_item.parsed
                            logger.info("Object counting successful. Found " +
                                        f"{len(count_data.rollup_counts)} object types")
                            return ObjectCountResult(success=True, count_data=count_data)
            
            raise RuntimeError("No structured response found in counting API response")
            
        except (APITimeoutError, APIConnectionError, BadRequestError) as api_error:
            logger.warning(f"API error during object counting: {api_error}")
            if not is_retry and ("timeout" in str(api_error).lower() or \
                "downloading" in str(api_error).lower()):
                logger.info("Retrying object counting due to API timeout")
                return self._count_objects_in_image(image_url, True)
            else:
                return ObjectCountResult(success=False,
                    error_message=f"API error during counting: {str(api_error)}")
        except Exception as e:
            logger.error(f"Error counting objects: {e}")
            return ObjectCountResult(success=False, error_message="Error counting objects: " +
                f"{str(e)}")

    async def _evaluate_quality_with_counts(self, image_url: str, object_count_data: ObjectCountData,
        expected_description: str, educational_context: str, question_prompt: str = None,
        is_retry: bool = False) -> QualityCheckResult:
        """
        Step 2: Evaluate image quality using the object counts from step 1.
        
        This step does NOT re-count objects but uses the counts as authoritative.
        """
        
        # Convert count data to a readable summary
        rollup_dict = {item.object_type: item.count for item in object_count_data.rollup_counts}
        count_summary = f"""
OBJECT COUNTS (from step 1 analysis):
Rollup totals: {rollup_dict}

Hierarchical breakdown:
"""
        for item in object_count_data.items:
            count_summary += self._format_object_tree(item, 0)

        system_prompt = """You are an expert image quality assessor for educational content. You
are evaluating an image that has already been analyzed for object counts.

## Evaluation Criteria

- **Correctness**: Images are correct and free of logical errors.
- **Consistency**: Images included in the question are consistent with associated text.
- **Interpretability**: Images are not ambiguous or confusing. All text is legible.
    - However, if the background color of the image is transparent, assume the background will be
    white when deciding whether text or other elements are legible.
- **Label Placement**: Labels in the image should be consistently placed across all objects in the
image.
- **Centroid Object Alignment**: Centroids of objects in the image should be aligned consistently
across the image.
- **Object Counts**: Use the PROVIDED OBJECT COUNT DATA above as the authoritative count. DO NOT
re-count objects yourself. Compare the provided counts to the expected description to determine if
object_counts_passed should be True or False.
- **Color Use**: Unless intentionally specified in the expected description, the image should not be
black and white.
- **Composition**: The image is visually full, without excessive whitespace, and properly centered.
- **No Cut-Off Elements**: ALL essential elements have clear separation from the edge of the image.
- **Real-World Consistency**: If depicting real-world objects, they should be reasonably
recognizable. If the objects are intended to contain a certain number of objects, they should be
capable of containing that number of objects. For example, if a muffin tray is supposed to contain
eight muffins, it must have at least eight muffins compartments or receptacles.
- **Educationally Appropriate**: The image should be appropriate for the target grade level.
- **Match Question Prompt**: If a question prompt is provided, the image should accurately reflect
the content.

## CRITICAL: Object Count Evaluation

- Treat the provided count data as authoritative, but sanity check it against the image to make sure
it is correct. If you cannot verify the count data, set object_counts_passed to False and explain
the discrepancies in your description.
- Compare the provided counts (assuming the count data is correct) with what the expected
description and question prompt indicate should be present
- Set object_counts_passed to True ONLY if the provided counts match the expected counts exactly
- If there are mismatches between provided counts and expected counts, set object_counts_passed to
False and explain the discrepancies in your description

## Rating Guidelines

Rate the image as:
- PASS: If the image meets ALL evaluation criteria including having correct object counts
- FAIL: If there are significant issues with any evaluation criteria
- NO_ACCESS: If the image is not accessible or cannot be reviewed

For FAIL ratings, provide specific details about ALL issues found."""

        user_prompt = f"""Please evaluate this image's quality using the provided object count data.

Educational Context: {educational_context}

Question Prompt the image will be used in (if any): {question_prompt}

Expected Description: {expected_description}

Count data:
{count_summary}

Use the provided object count data to verify if the image contains the correct number of objects as
specified in the expected description. Evaluate all other quality criteria as well."""

        # Note: GPT-5 will download the image directly from the URL during processing

        try:
            logger.info("Step 2: Evaluating image quality with provided counts")
            response = await self.client.responses.parse(
                model="gpt-5",
                input=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "input_text", "text": user_prompt},
                        {"type": "input_image", "image_url": image_url}
                    ]}
                ],
                text_format=QualityCheckResult,
                reasoning={"effort": "medium"}
            )
            
            # Extract the structured response
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if (content_item.type == "output_text" and 
                            hasattr(content_item, "parsed") and 
                            content_item.parsed is not None):
                            
                            quality_result = content_item.parsed
                            logger.info(f"Quality evaluation result: {quality_result.rating}")
                            return quality_result
            
            raise RuntimeError("No structured response found in quality check API response")
            
        except (APITimeoutError, APIConnectionError, BadRequestError) as api_error:
            logger.warning(f"API error during quality evaluation: {api_error}")
            if not is_retry and ("timeout" in str(api_error).lower() or \
                "downloading" in str(api_error).lower()):
                logger.info("Retrying quality evaluation due to API timeout")
                return self._evaluate_quality_with_counts(image_url, object_count_data,
                                expected_description, educational_context, question_prompt, True)
            else:
                return QualityCheckResult(
                    rating=QualityRating.FAIL,
                    description="Unable to evaluate image quality due to API error: " +
                        f"{str(api_error)}",
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
        except Exception as e:
            logger.error(f"Error evaluating quality: {e}")
            return QualityCheckResult(
                rating=QualityRating.FAIL,
                description=f"Error evaluating quality: {str(e)}",
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

    def _format_object_tree(self, item: ObjectItem, depth: int) -> str:
        """Helper to format object tree for readable display."""
        indent = "  " * depth
        result = f"{indent}- {item.type} (id: {item.id})"
        # if item.props:
            # result += f" {item.props}"
        result += "\n"
        
        if item.children:
            for child in item.children:
                result += self._format_object_tree(child, depth + 1)
        
        return result

    async def _evaluate_single_image(self, image_url: str, expected_description: str,
    educational_context: str, question_prompt: str = None, is_retry: bool = False,
    delete_failed_images: bool = True) -> str:
        """Evaluate a single image using the two-step process."""
        
        # Step 1: Count objects
        count_result = await self._count_objects_in_image(image_url, is_retry)
        
        if not count_result.success:
            logger.error(f"Step 1 (counting) failed: {count_result.error_message}")
            error_result = TwoStepQualityResult(
                rating=QualityRating.FAIL,
                description=f"Unable to count objects in image: {count_result.error_message}",
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
            if delete_failed_images:
                delete_files_from_supabase([image_url], delay_seconds=5.0)
            return error_result.model_dump_json(indent=2)
        
        # Step 2: Evaluate quality using counts
        quality_result = await self._evaluate_quality_with_counts(
            image_url, count_result.count_data, expected_description, educational_context,
            question_prompt, is_retry
        )
        
        # Combine results
        final_result = TwoStepQualityResult(
            rating=quality_result.rating,
            description=quality_result.description,
            object_count_data=count_result.count_data,
            correctness_passed=quality_result.correctness_passed,
            consistency_passed=quality_result.consistency_passed,
            interpretability_passed=quality_result.interpretability_passed,
            label_placement_passed=quality_result.label_placement_passed,
            centroid_object_alignment_passed=quality_result.centroid_object_alignment_passed,
            object_counts_passed=quality_result.object_counts_passed,
            color_use_passed=quality_result.color_use_passed,
            composition_passed=quality_result.composition_passed,
            no_object_cut_off_passed=quality_result.no_object_cut_off_passed,
            real_world_consistency_passed=quality_result.real_world_consistency_passed,
            educational_appropriateness_passed=quality_result.educational_appropriateness_passed,
            match_question_prompt_passed=quality_result.match_question_prompt_passed
        )
        
        # Handle image deletion
        if final_result.rating == QualityRating.PASS:
            logger.info("Two-step quality check result: PASS")
        else:
            logger.error(f"Two-step quality check result: {final_result.rating}")
            if delete_failed_images and final_result.rating == QualityRating.FAIL:
                delete_files_from_supabase([image_url], delay_seconds=5.0)
        
        # Handle NO_ACCESS retry
        if final_result.rating == QualityRating.NO_ACCESS and not is_retry:
            return await self._evaluate_single_image(image_url, expected_description, educational_context,
                question_prompt, True, delete_failed_images)
        
        return final_result.model_dump_json(indent=2)

    async def _evaluate_multiple_images(self, image_urls: List[str], expected_description: str,
    educational_context: str, question_prompt: str = None, is_retry: bool = False,
    delete_failed_images: bool = True) -> str:
        """Evaluate multiple images using the two-step process and select the best one."""
        
        logger.info(f"Evaluating {len(image_urls)} images using two-step process:")
        for i, url in enumerate(image_urls):
            logger.info(f"  Image {i+1}: {url}")
        
        # Step 1: Count objects in all images (in parallel)
        logger.info("Step 1: Starting parallel object counting for all images")
        all_count_results = []
        failed_images = []
        start_time = time.time()
        
        # Use asyncio.gather for concurrent processing
        count_tasks = [self._count_objects_in_image(url, is_retry) for url in image_urls]
        count_results = await asyncio.gather(*count_tasks, return_exceptions=True)
        
        # Process results
        for image_url, count_result in zip(image_urls, count_results):
            if isinstance(count_result, Exception):
                failed_images.append(image_url)
                logger.error(f"Exception during counting for image {image_url}: {count_result}")
                # Create a failed result
                failed_result = ObjectCountResult(success=False,
                    error_message=f"Exception during counting: {str(count_result)}")
                all_count_results.append((image_url, failed_result))
            else:
                all_count_results.append((image_url, count_result))
                
                if not count_result.success:
                    failed_images.append(image_url)
                    logger.error(f"Counting failed for image {image_url}: " +
                                f"{count_result.error_message}")
                else:
                    logger.info(f"Counting successful for image {image_url}: found " +
                                f"{len(count_result.count_data.rollup_counts)} object types")
        
        end_time = time.time()
        logger.info(f"Time taken to count objects in all images: {end_time - start_time} seconds")

        # If all images failed counting, return failure
        if len(failed_images) == len(image_urls):
            error_result = TwoStepQualityResult(
                rating=QualityRating.FAIL,
                description="Unable to count objects in any of the provided images",
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
            if delete_failed_images:
                delete_files_from_supabase(image_urls, delay_seconds=5.0)
            return error_result.model_dump_json(indent=2)
        
        # Step 2: Evaluate quality for all images in a single call using count data
        logger.info("Step 2: Evaluating quality for all images using count data")
        
        # Separate successful counting results and failed ones
        successful_count_results = [(url, count_result) for url, count_result in all_count_results \
            if count_result.success]
        failed_count_urls = [url for url, count_result in all_count_results \
            if not count_result.success]
        
        if not successful_count_results:
            # No images had successful counting, so we already returned failure above
            pass
        elif len(successful_count_results) == 1:
            # Single successful image, use single image evaluation
            image_url, count_result = successful_count_results[0]
            start_time = time.time()
            quality_result = self._evaluate_quality_with_counts(
                image_url, count_result.count_data, expected_description, educational_context,
                question_prompt, is_retry
            )
            end_time = time.time()
            logger.info(
                f"Time taken to evaluate quality for single image: {end_time - start_time} seconds"
            )

            # Convert single image result to multi-image format
            individual_ratings = {image_url: quality_result.rating.value}
            for failed_url in failed_count_urls:
                individual_ratings[failed_url] = "FAIL"
                
            if quality_result.rating == QualityRating.PASS:
                final_result = TwoStepQualityResult(
                    rating=QualityRating.PASS,
                    description=quality_result.description,
                    selected_image_url=image_url,
                    individual_image_ratings=individual_ratings,
                    object_count_data=count_result.count_data,
                    correctness_passed=quality_result.correctness_passed,
                    consistency_passed=quality_result.consistency_passed,
                    interpretability_passed=quality_result.interpretability_passed,
                    label_placement_passed=quality_result.label_placement_passed,
                    centroid_object_alignment_passed=quality_result.centroid_object_alignment_passed,
                    object_counts_passed=quality_result.object_counts_passed,
                    color_use_passed=quality_result.color_use_passed,
                    composition_passed=quality_result.composition_passed,
                    no_object_cut_off_passed=quality_result.no_object_cut_off_passed,
                    real_world_consistency_passed=quality_result.real_world_consistency_passed,
                    educational_appropriateness_passed=quality_result.educational_appropriateness_passed,
                    match_question_prompt_passed=quality_result.match_question_prompt_passed
                )
                logger.info(
                    f"Two-step multi-image quality check result: PASS - Selected: {image_url}"
                )
                # Delete unselected images
                if delete_failed_images:
                    urls_to_delete = [url for url in image_urls if url != image_url]
                    delete_files_from_supabase(urls_to_delete, delay_seconds=5.0)
            else:
                final_result = TwoStepQualityResult(
                    rating=QualityRating.FAIL,
                    description=quality_result.description,
                    individual_image_ratings=individual_ratings,
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
                logger.error(
                    "Two-step multi-image quality check result: FAIL - Description: " +
                    f"{quality_result.description}"
                )
                # Delete all images since none passed
                if delete_failed_images:
                    delete_files_from_supabase(image_urls, delay_seconds=5.0)
            
            return final_result.model_dump_json(indent=2)
        else:
            # Multiple successful images, evaluate all together in single call
            start_time = time.time()
            return await self._evaluate_multiple_images_with_counts(
                successful_count_results, failed_count_urls, image_urls, expected_description, 
                educational_context, question_prompt, is_retry, delete_failed_images
            )
            end_time = time.time()
            logger.info(
                f"Time taken to evaluate quality for multiple images: {end_time - start_time} " + 
                "seconds"
            )

    async def _evaluate_multiple_images_with_counts(self, successful_count_results: List[tuple],
    failed_count_urls: List[str], all_image_urls: List[str], expected_description: str,
    educational_context: str, question_prompt: str = None, is_retry: bool = False,
    delete_failed_images: bool = True) -> str:
        """Evaluate multiple images with their count data in a single API call."""
        
        # Build count data summary for all successfully counted images
        count_summaries = {}
        image_urls_with_counts = []
        
        for image_url, count_result in successful_count_results:
            rollup_dict = {item.object_type: item.count \
                for item in count_result.count_data.rollup_counts}
            count_summary = f"""
Image {image_url} OBJECT COUNTS:
Rollup totals: {rollup_dict}

Hierarchical breakdown:
"""
            for item in count_result.count_data.items:
                count_summary += self._format_object_tree(item, 0)
                
            count_summaries[image_url] = count_summary
            image_urls_with_counts.append(image_url)
        
        # Build the comprehensive count data section
        all_count_data = "## PROVIDED OBJECT COUNT DATA FOR ALL IMAGES\n"
        for _, summary in count_summaries.items():
            all_count_data += summary + "\n"
        
        if failed_count_urls:
            all_count_data += "\n## IMAGES WITH FAILED OBJECT COUNTING:\n"
            for url in failed_count_urls:
                all_count_data += f"- {url}: Object counting failed\n"

        system_prompt = """You are an expert image quality assessor for educational content. You are
evaluating multiple images that have already been analyzed for object counts.

## Evaluation Criteria

- **Correctness**: Images are correct and free of logical errors.
- **Consistency**: Images included in the question are consistent with associated text.
- **Interpretability**: Images are not ambiguous or confusing. All text is legible.
- **Label Placement**: Labels in the image should be consistently placed across all objects in the
image.
- **Centroid Object Alignment**: Centroids of objects in the image should be aligned consistently
across the image.
- **Object Counts**: Use the PROVIDED OBJECT COUNT DATA above as the authoritative count. DO NOT
re-count objects yourself. Compare the provided counts to the expected description and question
prompt (if any) to determine if object_counts_passed should be True or False.
- **Color Use**: Unless intentionally specified in the expected description, the image should not be
black and white.
- **Composition**: The image is visually full, without excessive whitespace, and properly centered.
- **No Cut-Off Elements**: ALL essential elements have clear separation from the edge of the image.
- **Real-World Consistency**: If depicting real-world objects, they should be reasonably
recognizable.
- **Educationally Appropriate**: The image should be appropriate for the target grade level.
- **Match Question Prompt**: If a question prompt is provided, the image should accurately reflect
the content.
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
        - Do not penalize the image for differences that do not directly contradict the expected
        description or question prompt. It is important that objects are recognizable, in the
        correct number, and not cut off, but not important that there contain zero discrepancies
        from the expected description and question prompt.
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

## CRITICAL: Object Count Evaluation

- Treat the provided count data as authoritative, but sanity check it against the image to make
sure it is correct. If you cannot verify the count data, set object_counts_passed to False and
explain the discrepancies in your description.
- Compare the provided counts (assuming the count data is correct) with what the expected
description and question prompt indicate should be present
- Set object_counts_passed to True ONLY if the provided counts match the expected counts exactly
- If there are mismatches between provided counts and expected counts, set object_counts_passed to
False

## Task: Select Best Image

Your task is to:
1. Evaluate all provided images against the expected description, educational context, and
evaluation criteria
2. If at least one image passes all criteria and has correct object counts, return PASS with the URL
of the BEST image
3. If no image passes all criteria, return FAIL with a summary of the issues in each image, as well
as guidance on how to create a better image.

CRITICAL: You MUST select the URL exactly as provided in the list below. Do NOT modify, truncate, or
create new URLs.

For PASS ratings: You MUST provide the exact URL of the best image in the selected_image_url field
AND explain why it was selected. You must also provide individual PASS/FAIL ratings for each image
in the individual_image_ratings field.
For FAIL ratings: Provide a comprehensive summary of the main issues found in the images, as well as
guidance on how to create a better image. You must also provide individual PASS/FAIL ratings for
each image in the individual_image_ratings field.
For NO_ACCESS ratings: Provide a brief explanation of why the images are not accessible or cannot be
reviewed."""

        try:
            # Create URL mapping for reference
            url_list = "\n".join([f"Image {i+1}: {url}" for i, url in enumerate(all_image_urls)])
            
            user_prompt = f"""Please evaluate these {len(all_image_urls)} images using the provided
object count data.

Educational Context: {educational_context}

Question Prompt the image will be used in (if any): {question_prompt}

Expected Description: {expected_description}

Count data:
{all_count_data}

IMAGE URL MAPPING:
{url_list}

IMPORTANT: You must select the URL exactly as listed above. Do not modify or create new URLs.

Select the best image that meets all criteria using the provided count data, or indicate if none are
acceptable."""

            # Prepare image inputs for OpenAI API
            input_content = [{"role": "developer", "content": system_prompt}]
            
            user_content = [{"type": "input_text", "text": user_prompt}]
            
            # Add all images to the user content (GPT-5 will download them during processing)
            for image_url in all_image_urls:
                user_content.append({"type": "input_image", "image_url": image_url})
            
            input_content.append({"role": "user", "content": user_content})

            logger.info(f"Evaluating {len(all_image_urls)} images for quality using count data...")
            
            # Use structured outputs with vision capabilities
            try:
                response = await self.client.responses.parse(
                    model="gpt-5",
                    input=input_content,
                    text_format=QualityCheckResult,
                    reasoning={"effort": "medium"}
                )
            except (APITimeoutError, APIConnectionError, BadRequestError) as api_error:
                logger.warning(f"API error during multi-image evaluation with counts: {api_error}")
                # Check if this is a timeout/download error and we haven't already retried
                if not is_retry and ("timeout" in str(api_error).lower() or \
                    "downloading" in str(api_error).lower()):
                    logger.info("Retrying multi-image evaluation due to API timeout")
                    return await self._evaluate_multiple_images_with_counts(successful_count_results,
                        failed_count_urls, all_image_urls, expected_description,
                        educational_context, question_prompt, True, delete_failed_images)
                else:
                    # If retry failed or it's a different error, create a proper FAIL result
                    error_result = TwoStepQualityResult(
                        rating=QualityRating.FAIL,
                        description=f"Unable to evaluate images due to API error: {str(api_error)}",
                        individual_image_ratings={url: "FAIL" for url in all_image_urls},
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
                    if delete_failed_images:
                        delete_files_from_supabase(all_image_urls, delay_seconds=5.0)
                    return error_result.model_dump_json(indent=2)
            
            # Extract the structured response
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if (content_item.type == "output_text" and 
                            hasattr(content_item, "parsed") and 
                            content_item.parsed is not None):
                            
                            quality_result = content_item.parsed
                            
                            # Find the count data for the selected image (if PASS)
                            selected_count_data = None
                            if quality_result.rating == QualityRating.PASS \
                                and quality_result.selected_image_url:
                                # Find the count data for the selected image
                                for image_url, count_result in successful_count_results:
                                    if image_url == quality_result.selected_image_url:
                                        selected_count_data = count_result.count_data
                                        break
                                
                                if not selected_count_data:
                                    logger.warning(
                                        "Could not find count data for selected image: " +
                                        f"{quality_result.selected_image_url}"
                                    )
                            
                            # Convert to final result format
                            final_result = TwoStepQualityResult(
                                rating=quality_result.rating,
                                description=quality_result.description,
                                selected_image_url=quality_result.selected_image_url,
                                individual_image_ratings=quality_result.individual_image_ratings,
                                object_count_data=selected_count_data,
                                correctness_passed=quality_result.correctness_passed,
                                consistency_passed=quality_result.consistency_passed,
                                interpretability_passed=quality_result.interpretability_passed,
                                label_placement_passed=quality_result.label_placement_passed,
                                centroid_object_alignment_passed=quality_result.centroid_object_alignment_passed,
                                object_counts_passed=quality_result.object_counts_passed,
                                color_use_passed=quality_result.color_use_passed,
                                composition_passed=quality_result.composition_passed,
                                no_object_cut_off_passed=quality_result.no_object_cut_off_passed,
                                real_world_consistency_passed=quality_result.real_world_consistency_passed,
                                educational_appropriateness_passed=quality_result.educational_appropriateness_passed,
                                match_question_prompt_passed=quality_result.match_question_prompt_passed
                            )
                            
                            # Handle image deletion
                            if final_result.rating == QualityRating.PASS:
                                logger.info(
                                    "Two-step multi-image quality check result: PASS - " +
                                    f"Selected: {final_result.selected_image_url} - " +
                                    f"Description: {final_result.description}"
                                )
                                # Delete unselected images
                                if delete_failed_images:
                                    urls_to_delete = [url for url in all_image_urls \
                                        if url != final_result.selected_image_url]
                                    delete_files_from_supabase(urls_to_delete, delay_seconds=5.0)
                            else:
                                logger.error(
                                    "Two-step multi-image quality check result: " +
                                    f"{final_result.rating} - Description: " +
                                    f"{final_result.description}"
                                )
                                # Delete all images since none passed
                                if delete_failed_images:
                                    delete_files_from_supabase(all_image_urls, delay_seconds=5.0)
                            
                            if final_result.rating == QualityRating.NO_ACCESS and not is_retry:
                                return self._evaluate_multiple_images_with_counts(
                                    successful_count_results, failed_count_urls, all_image_urls,
                                    expected_description, educational_context, question_prompt,
                                    True, delete_failed_images)
                                
                            return final_result.model_dump_json(indent=2)
                        elif (content_item.type == "output_text" and 
                              hasattr(content_item, "text")):
                            # Fallback to text if parsed object not available
                            logger.error(
                                "Multi-image quality check with counts returned unparsed text: " +
                                f"{content_item.text} - Description: {content_item.text}"
                            )
                            # Delete all images since we couldn't parse the result
                            if delete_failed_images:
                                delete_files_from_supabase(all_image_urls, delay_seconds=5.0)
                            return content_item.text
            
            raise RuntimeError("No structured response found in API response")
            
        except Exception as e:
            logger.error(f"Error in multi-image evaluation with counts: {e}")
            error_result = TwoStepQualityResult(
                rating=QualityRating.FAIL,
                description=f"Unable to evaluate images due to technical error: {str(e)}",
                individual_image_ratings={url: "FAIL" for url in all_image_urls},
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
            # Delete all images since evaluation failed
            if delete_failed_images:
                delete_files_from_supabase(all_image_urls, delay_seconds=5.0)
            return error_result.model_dump_json(indent=2)


def generate_image_quality_checker_two_step_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the two-step image quality checker tool specification and function."""
    
    checker = ImageQualityCheckerTwoStep()
    
    async def image_quality_check_two_step_function(image_urls: Union[str, List[str]],
    expected_description: str, educational_context: str, question_prompt: str = None,
    delete_failed_images: bool = True) -> str:
        """Check if image(s) accurately depict the expected content using two-step process: count
        objects first, then evaluate quality."""
        return await checker.check_image_quality(image_urls, expected_description, educational_context,
        question_prompt=question_prompt, delete_failed_images=delete_failed_images)
    
    spec = {
        "type": "function",
        "name": "check_image_quality_two_step",
        "description": (
            "Evaluate whether image(s) accurately depict expected content using a two-step "
            "process: first count all objects without bias, then evaluate quality based on "
            "those counts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "image_urls": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": (
                        "Either a single image URL (string) or a list of image URLs to analyze and "
                        "evaluate for quality and accuracy."
                    )
                },
                "expected_description": {
                    "type": "string", 
                    "description": (
                        "Description of what the image is supposed to depict or show, focused on a "
                        "precise description of all objects in the image that a student may need "
                        "to identify (including counts of these objects). Don't include details "
                        "that are not relevant to what the student is supposed to observe in the "
                        "image."
                    )
                },
                "question_prompt": {
                    "type": "string",
                    "description": (
                        "The prompt of the question that the image is associated with, if any. "
                        "This will be used to verify the image is appropriate for the question."
                    )
                },
                "educational_context": {
                    "type": "string",
                    "description": (
                        "The educational context of the image, such as the grade level and subject "
                        "matter. This will be used to verify the image is appropriate for a "
                        "typical student in the target grade trying to learn the material."
                    )
                }
            },
            "required": ["image_urls", "expected_description", "question_prompt",
                        "educational_context"]
        }
    }
    
    return spec, image_quality_check_two_step_function
