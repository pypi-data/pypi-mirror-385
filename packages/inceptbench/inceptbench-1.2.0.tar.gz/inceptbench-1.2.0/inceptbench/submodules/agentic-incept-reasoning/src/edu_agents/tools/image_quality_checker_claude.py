import asyncio
import base64
import logging
import os
from enum import Enum
from time import time
from typing import Any, Callable, Dict, List, Optional, Union

import requests
from anthropic import AsyncAnthropic
from pydantic import BaseModel

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

class ImageQualityChecker:
    """Checks image quality and accuracy against expected descriptions using Claude Sonnet 4's
    vision capabilities."""
    
    SYSTEM_PROMPT = """You are an expert image quality assessor for educational content.
{task_description}

IMPORTANT: You must complete ALL evaluation steps systematically BEFORE making any rating
determination.
Do NOT decide whether content passes or fails until you have completed your full analysis.

## Evaluation Criteria

- **Correctness**: Images are correct and free of logical errors.
- **Consistency**: Images included in the question are consistent with associated text.
- **Interpretability**: Images are not ambiguous or confusing. All text is legible.
- **Visual Clarity and Pedagogical Appropriateness**: 
    - CRITICAL: The image must have a single, cohesive visual narrative appropriate for 
      student learning
    - NO floating, disconnected, or unnatural visual elements (e.g., objects suspended in air 
      with no support that wouldn't naturally be suspended)
    - NO redundant visual representations that create confusion (e.g., showing the same conceptual
    objects both floating above AND inside containers)
    - Objects must be positioned in natural, logical ways that make pedagogical sense
    - The image should help student understanding, not create visual confusion or distraction
    - Ask: "Would a grade-level student looking at this image be confused by any visual elements?"
    If yes, FAIL
    - Images must be visually coherent, not weird amalgamations of disconnected elements
    - **SYSTEMATIC EVALUATION REQUIRED**: Examine every visual element for natural positioning, 
      logical relationships, and pedagogical clarity before making any rating determination
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
objects in the expected description exactly and clearly. VERIFYING OBJECT COUNTS IS CRITICAL - DO
IT VERY CAREFULLY!
  **SYSTEMATIC ENUMERATION REQUIRED**: For each type of object that should have a specific count:
  * ENUMERATE each individual object (e.g., "Basket 1: apple 1, apple 2, apple 3...")  
  * LIST the location/position of each object as you count it
  * PROVIDE the total count only after individual enumeration
  * If objects are grouped (e.g., items in containers), enumerate within each group separately
  Count multiple times to ensure accuracy. Count objects VERY CAREFULLY - verify each count multiple
  times. Do not accept "approximately" when exact counts are specified - if text says "8 apples 
  each" then there must be exactly 8, not 6 or 7.
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
should be reasonably recognizable as that object. Objects with specific relationships to each other,
such as "inside," "below," or "on top of" should be accurately depicted. Pay attention because
sometimes these relationships are implied; for example, if the context specifies "3 circles filled
with 4 stars", the stars should be completely contained within the circles.
- **Educationally Appropriate**: The image should be appropriate for a typical student in the target
grade trying to learn the material. However, as long as objects would be recognizable to a
grade-level student, do not penalize the image for not matching a certain version of a similar
object.
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
        - In another example, if the expected image is supposed to contain 6 empty baskets, and the
        image contains 6 identifiable baskets, but the baskets are closed so you cannot tell if
        they are truly empty or not, allow it. Inability to be certain the baskets are empty is
        not a blocking issue. However, note that the image would NOT be acceptable if it contained
        6 baskets that were visibly NOT empty.
        - Do not penalize the image for differences that do not directly contradict the expected
        description or question prompt. It is important that objects are recognizable, in the
        correct number, and not cut off, but not important that there contain zero discrepancies
        from the expected description and question prompt.
        - However, note that on objects like bookshelves, the top of the bookshelf is not
        considered a shelf, so it does not count as a shelf for the purpose of counting shelves.
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
    - As long as they are not confusing, disruptive, or distracting, do not penalize the image for
    using decorative elements.
    - If several objects are described as "identical", they do not need to be literally identical,
    as long as they are easily identifiable as the same type of object. For example, gift bags that
    are supposed to be identical, but are different colors and otherwise identical, are acceptable.
- **Express Your Preferences through Selected URL, not Failing Other Good Images**: If you prefer a
particular image for some reason, indicate that by choosing it in the selected_image_url field,
rather than by rating other images that otherwise meet the Evaluation Criteria as a FAIL.

{rating_guidelines}

You must use the {tool_name} tool to provide your structured evaluation."""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    async def _count_objects_without_bias(self, image_urls: Union[str, List[str]],
    is_retry: bool = False) -> Dict[str, Any]:
        """
        Count objects in image(s) without any bias from expected descriptions or context.
        
        Returns dictionary with object counts for each image or single image.
        """
        if isinstance(image_urls, str):
            image_urls = [image_urls]
        
        system_prompt = """You are an expert at precise object counting in images. You will use a
systematic, adaptive approach that works for any counting scenario.

CRITICAL: You will receive NO information about expected counts. Count only what you observe.

## Universal Counting Strategy

**STEP 1 - SCENE ANALYSIS:**
- Analyze the image to understand the counting challenge
- Classify the scenario:
  * SCATTERED: Individual objects distributed across the image
  * GROUPED: Objects organized in containers/groups (plates, bowls, etc.)
  * CLUSTERED: Objects touching/overlapping but not in containers
  * MIXED: Multiple object types or complex arrangements
- Identify all distinct object types present

**STEP 2 - ADAPTIVE COUNTING APPROACH:**

For SCATTERED objects:
- Use systematic grid scanning (divide image into regions)
- Count each object type separately
- Mark objects mentally as you count to avoid double-counting

For GROUPED objects:
- Count containers first, then contents of each container
- Record per-group counts for verification
- Check if groups are consistent (same count per group)

For CLUSTERED objects:
- Use edge detection and separation techniques mentally
- Count visible objects only (>80% visible)
- Be extra careful with touching/overlapping objects

For MIXED scenarios:
- Count each object type independently
- Use color, shape, size differences to distinguish types
- Double-check boundaries between different object types

**STEP 3 - MULTI-METHOD VERIFICATION:**
- **Method 1 - Systematic Scan**: Divide image into regions, count methodically
- **Method 2 - Type-Based Count**: Count each object type separately
- **Method 3 - Alternative Pattern**: Use the most appropriate alternative based on scenario
- **Cross-verify**: All methods should agree within 1-2 objects

## Critical Counting Rules

- **VISIBILITY RULE**: Only count objects >80% visible
- **EDGE POLICY**: Objects cut off by image boundaries don't count
- **OCCLUSION HANDLING**: If objects are heavily overlapped/ambiguous → REJECT image
- **EDUCATIONAL SUITABILITY**: If a student couldn't clearly count these objects → REJECT
- **PRECISION REQUIREMENT**: Be exact, not approximate
- **CONTEXT CLUES**: Use visual cues (stems, handles, outlines) to distinguish objects

## Quality Control Checks

1. **Sanity Check**: Does the total make sense given the image size and object density?
2. **Method Agreement**: Do all counting methods agree within acceptable range?
3. **Confidence Assessment**: How clear and unambiguous are the objects?
4. **Student Suitability**: Could a grade-level student count these objects clearly?

## Output Requirements

For each object type found:
1. **Scenario Classification**: What type of counting challenge is this?
2. **Counting Strategy Used**: Which approach was most appropriate?
3. **Method Results**: Results from each verification method
4. **Final Count**: Verified count after cross-checking
5. **Confidence Level**: Based on object clarity and method agreement
6. **Quality Assessment**: Whether image is suitable for educational counting

## Confidence Assessment

Rate your confidence for each object type based on:
- **HIGH**: Objects are clearly distinct, well-lit, unobscured, easy to count
- **MEDIUM**: Some objects partially overlapped or in shadows, but still countable
- **LOW**: Objects difficult to distinguish, heavily overlapping, or ambiguous lighting

## Output Requirements

For each object type, you must provide:
1. **Method 1 count** (grid scanning) with quadrant breakdown
2. **Method 2 count** (enumeration) with object positions
3. **Method 3 count** (verification recount) 
4. **Final verified count** (resolved if methods differed)
5. **Confidence level** (high/medium/low)
6. **Detailed enumeration** of each object's location and identifying features

You must be absolutely certain of your final counts. When in doubt, examine more carefully and be
conservative."""

        try:
            # Prepare message content
            if len(image_urls) == 1:
                message_text = """Please carefully count all distinct objects in this image using
the universal counting strategy. Be systematic and thorough.

IMPORTANT STEPS:
1. ANALYZE the image first - what type of counting scenario is this? (scattered, grouped, clustered,
mixed)
2. CHOOSE the most appropriate counting approach for this specific scenario
3. COUNT using your chosen method, being precise and systematic
4. VERIFY using alternative methods appropriate to the scenario
5. CROSS-CHECK that all methods agree within acceptable range

REJECT if objects are overlapping, ambiguous, or impossible for students to count clearly."""
            else:
                message_text = f"""Please carefully count all distinct objects in each of these
{len(image_urls)} images using the universal counting strategy. Provide separate counts for each
image.

IMPORTANT STEPS FOR EACH IMAGE:
1. ANALYZE the image first - what type of counting scenario is this? (scattered, grouped,
clustered, mixed)
2. CHOOSE the most appropriate counting approach for this specific scenario
3. COUNT using your chosen method, being precise and systematic
4. VERIFY using alternative methods appropriate to the scenario
5. CROSS-CHECK that all methods agree within acceptable range

REJECT if objects are overlapping, ambiguous, or impossible for students to count clearly."""
            
            message_content = [{"type": "text", "text": message_text}]
            
            # Add images to message
            for i, image_url in enumerate(image_urls):
                if len(image_urls) > 1:
                    message_content.append({
                        "type": "text", 
                        "text": f"=== IMAGE {i+1} (URL: {image_url}) ==="
                    })
                
                if is_retry:
                    try:
                        await asyncio.sleep(1)
                        image_response = requests.get(image_url)
                        image_response.raise_for_status()
                        image_bytes = image_response.content
                        if image_bytes:
                            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                            content_type = image_response.headers.get('content-type', 'image/png')
                            media_type = "image/jpeg" if 'jpeg' in content_type \
                                or 'jpg' in content_type else "image/png"
                            
                            message_content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64
                                }
                            })
                    except Exception as e:
                        logger.error(f"Error downloading image {i+1}: {e}")
                        message_content.append({
                            "type": "image",
                            "source": {"type": "url", "url": image_url}
                        })
                else:
                    message_content.append({
                        "type": "image",
                        "source": {"type": "url", "url": image_url}
                    })

            # Define structured output tool for object counting
            tools = [{
                "name": "object_count_report",
                "description": "Report detailed object counts for each image",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_counts": {
                            "type": "array",
                            "description": "Object counts for each image",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "image_url": {
                                        "type": "string",
                                        "description": "URL of the image being analyzed"
                                    },
                                    "image_index": {
                                        "type": "integer", 
                                        "description": "Index of image (1-based) in the provided "
                                                       "sequence"
                                    },
                                    "overall_confidence": {
                                        "type": "string",
                                        "enum": ["high", "medium", "low"],
                                        "description": "Overall confidence level for this image's "
                                                       "counts"
                                    },
                                    "image_rejected": {
                                        "type": "boolean",
                                        "description": "True if image should be rejected due to "
                                                       "obscured/ambiguous objects"
                                    },
                                    "rejection_reason": {
                                        "type": "string",
                                        "description": "Reason for rejection if image_rejected is "
                                                       "true"
                                    },
                                    "counting_process_summary": {
                                        "type": "string",
                                        "description": "Summary of the multi-method counting "
                                                       "process used"
                                    },
                                    "object_types": {
                                        "type": "array",
                                        "description": "List of different object types found with "
                                                       "counts",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "object_name": {
                                                    "type": "string",
                                                    "description": "Name/type of object (e.g., "
                                                                   "'baskets', 'apples')"
                                                },
                                                "method_a_count": {
                                                    "type": "integer",
                                                    "description": "Count from container-by-"
                                                                   "container method"
                                                },
                                                "method_a_details": {
                                                    "type": "string",
                                                    "description": "Details from container-by-"
                                                                   "container counting"
                                                },
                                                "method_b_count": {
                                                    "type": "integer",
                                                    "description": "Count from systematic grid "
                                                                   "scan method"
                                                },
                                                "method_b_details": {
                                                    "type": "string",
                                                    "description": "Details from grid scanning "
                                                                   "method"
                                                },
                                                "method_c_count": {
                                                    "type": "integer",
                                                    "description": "Count from type-based counting "
                                                                   "method"
                                                },
                                                "method_c_details": {
                                                    "type": "string",
                                                    "description": "Details from type-based "
                                                                   "counting"
                                                },
                                                "scenario_classification": {
                                                    "type": "string",
                                                    "enum": ["scattered", "grouped", "clustered",
                                                            "mixed"],
                                                    "description": "Type of counting scenario "
                                                                   "identified"
                                                },
                                                "counting_strategy_used": {
                                                    "type": "string", 
                                                    "description": "Which counting approach was "
                                                                   "most appropriate for this "
                                                                   "scenario"
                                                },
                                                "method_agreement": {
                                                    "type": "string",
                                                    "description": "Analysis of agreement between "
                                                                   "different counting methods"
                                                },
                                                "sanity_check": {
                                                    "type": "string",
                                                    "description": "Assessment of whether the "
                                                                   "count makes sense given image "
                                                                   "characteristics"
                                                },
                                                "quality_assessment": {
                                                    "type": "string",
                                                    "description": "Whether image is suitable for "
                                                                   "educational counting"
                                                },
                                                "confidence_level": {
                                                    "type": "string",
                                                    "enum": ["high", "medium", "low"],
                                                    "description": "Confidence level for this "
                                                                   "object type count"
                                                },
                                                "final_verified_count": {
                                                    "type": "integer",
                                                    "description": "Final verified count after "
                                                                   "resolving any discrepancies"
                                                },
                                                "count_discrepancies": {
                                                    "type": "string",
                                                    "description": "Any discrepancies between "
                                                                   "methods and how they were "
                                                                   "resolved"
                                                },
                                                "container_relationship": {
                                                    "type": "string",
                                                    "description": "If objects are inside "
                                                                   "containers, describe the "
                                                                   "relationship (e.g., "
                                                                   "'apples inside baskets')"
                                                }
                                            },
                                            "required": ["object_name", "scenario_classification",
                                                        "counting_strategy_used", "method_1_count",
                                                        "method_2_count", "method_3_count", 
                                                        "final_verified_count", "confidence_level"]
                                        }
                                    }
                                },
                                "required": ["image_url", "image_index", "overall_confidence",
                                            "counting_process_summary", "object_types"]
                            }
                        }
                    },
                    "required": ["image_counts"]
                }
            }]

            logger.info(f"Counting objects in {len(image_urls)} image(s) without bias...")
            
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=16384,
                system=system_prompt,
                tools=tools,
                tool_choice={"type": "tool", "name": "object_count_report"},
                messages=[{"role": "user", "content": message_content}]
            )
            
            # Extract counting results
            for content in response.content:
                if content.type == "tool_use" and content.name == "object_count_report":
                    return content.input
            
            # Fallback
            return {"image_counts": []}
            
        except Exception as e:
            logger.error(f"Error in unbiased object counting: {e}")
            return {"error": str(e), "image_counts": []}
    
    async def _evaluate_quality_with_counts(self, image_urls: Union[str, List[str]],
    expected_description: str, educational_context: str, question_prompt: str,
    count_results: Dict[str, Any], is_retry: bool = False) -> Dict[str, Any]:
        """
        Evaluate image quality using unbiased object count results and expected context.
        
        This is the second step that combines the unbiased counts with the expected description
        to determine if images pass quality standards.
        """
        if isinstance(image_urls, str):
            image_urls = [image_urls]
            
        # For single image vs multi-image evaluation
        if len(image_urls) == 1:
            return await self._evaluate_single_with_counts(image_urls[0], expected_description, 
                                                   educational_context, question_prompt, 
                                                   count_results, is_retry)
        else:
            return await self._evaluate_multiple_with_counts(image_urls, expected_description,
                                                     educational_context, question_prompt,
                                                     count_results, is_retry)
    
    async def _evaluate_single_with_counts(self, image_url: str, expected_description: str,
    educational_context: str, question_prompt: str, count_results: Dict[str, Any],
    is_retry: bool = False) -> Dict[str, Any]:
        """Evaluate single image quality using count results and context."""
        
        system_prompt = self.SYSTEM_PROMPT.format(
            task_description="You are evaluating an image's quality using UNBIASED object count "
                             "data that was collected separately to avoid counting bias. Use this"
                             "count data along with the expected description to determine if the "
                             "image meets standards.",
            rating_guidelines="""## Rating Using Count Data and Context

You will receive:
1. UNBIASED OBJECT COUNTS: Detailed counts of all objects found in the image, collected without
   knowledge of what should be present, verified through multiple counting methods.
2. EXPECTED DESCRIPTION: What the image is supposed to show
3. EDUCATIONAL CONTEXT: The learning context for the image
4. QUESTION PROMPT: The question context (if any)

## Evaluation Process

1. COMPARE COUNTS: Compare the unbiased FINAL VERIFIED COUNTS (ignore preliminary method counts)
against what's expected in the description. Create ObjectCountCheck entries for each object type
that has specific count requirements. Use only the final_verified_count from the count data - this
has been cross-verified through multiple methods.

2. EVALUATE OTHER CRITERIA: Assess all other Evaluation Criteria:
   - Visual Clarity and Pedagogical Appropriateness
   - Correctness and Consistency
   - Interpretability
   - Label Placement, Composition, etc.

3. MAKE DETERMINATION:
   - PASS: If object counts match expectations AND all other criteria are met
   - FAIL: If object counts don't match OR any other criteria fail
   - NO_ACCESS: If image cannot be accessed

CRITICAL: The object counts provided are unbiased observations verified through multiple counting
methods (grid scanning, enumeration, cross-verification). Trust these FINAL VERIFIED counts and
compare them directly to the expected counts. Do not re-count objects in the image.

ADDITIONAL OBSCURED OBJECTS CHECK: Even if counting was successful, you must also evaluate whether
the image contains obscured, overlapping, or ambiguously positioned objects that would make it
unsuitable for educational use. If students cannot clearly and unambiguously count objects in the
image, rate as FAIL regardless of count accuracy.

For FAIL ratings: Explain which criteria failed and provide specific improvement instructions.
For PASS ratings: Confirm what the image shows correctly.""",
            tool_name="image_quality_assessment_with_counts"
        )

        # Find count data for this image
        image_count_data = None
        if "image_counts" in count_results:
            for img_data in count_results["image_counts"]:
                if img_data["image_url"] == image_url:
                    image_count_data = img_data
                    break
        
        if not image_count_data:
            return {
                "rating": "FAIL",
                "description": "No count data available for image evaluation",
                "object_counts": []
            }
        
        # Prepare message with count data
        count_summary = self._format_count_data_for_evaluation(image_count_data)
        
        message_content = [
            {"type": "text", "text": f"""Please evaluate this image's quality using the unbiased
object count data:

UNBIASED OBJECT COUNT DATA (collected without knowledge of expectations):
{count_summary}

Educational Context: {educational_context}

Question Prompt the image will be used in (if any): {question_prompt}

Expected Description: {expected_description}

Compare the unbiased counts to the expected description and evaluate against all criteria."""}
        ]
        
        # Add the actual image for visual assessment of non-counting criteria
        if is_retry:
            try:
                await asyncio.sleep(1)
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                image_bytes = image_response.content
                if image_bytes:
                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    content_type = image_response.headers.get('content-type', 'image/png')
                    media_type = "image/jpeg" if 'jpeg' in content_type \
                        or 'jpg' in content_type else "image/png"
                    message_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64
                        }
                    })
            except Exception as e:
                logger.error(f"Error downloading image: {e}")
                message_content.append({
                    "type": "image",
                    "source": {"type": "url", "url": image_url}
                })
        else:
            message_content.append({
                "type": "image",
                "source": {"type": "url", "url": image_url}
            })

        # Define structured output tool
        tools = [{
            "name": "image_quality_assessment_with_counts",
            "description": "Evaluate image quality using unbiased count data and expected context",
            "input_schema": {
                "type": "object",
                "properties": {
                    "count_comparison": {
                        "type": "string",
                        "description": "Detailed comparison of unbiased counts vs expected counts"
                    },
                    "other_criteria_evaluation": {
                        "type": "string", 
                        "description": "Assessment of visual clarity, pedagogical appropriateness, "
                                       "and other criteria"
                    },
                    "rating": {
                        "type": "string",
                        "enum": ["PASS", "FAIL", "NO_ACCESS"],
                        "description": "Overall quality rating"
                    },
                    "description": {
                        "type": "string",
                        "description": "Summary of assessment decision"
                    },
                    "object_counts": {
                        "type": "array",
                        "description": "Object count verification using unbiased count data",
                        "items": {
                            "type": "object",
                            "properties": {
                                "object_name": {"type": "string"},
                                "expected_count": {"type": "integer"},
                                "observed_count": {"type": "integer"},
                                "is_count_mismatch": {"type": "boolean"},
                                "contained_objects": {
                                    "type": "array",
                                    "items": {"$ref": "#"}
                                }
                            },
                            "required": ["object_name", "expected_count", "observed_count",
                                        "is_count_mismatch"]
                        }
                    }
                },
                "required": ["count_comparison", "other_criteria_evaluation", "rating",
                            "description", "object_counts"]
            }
        }]

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=16384,
                system=system_prompt,
                tools=tools,
                tool_choice={"type": "tool", "name": "image_quality_assessment_with_counts"},
                messages=[{"role": "user", "content": message_content}]
            )
            
            for content in response.content:
                if content.type == "tool_use" \
                    and content.name == "image_quality_assessment_with_counts":
                    return content.input
            
            return {
                "rating": "FAIL", 
                "description": "Unexpected response format",
                "object_counts": []
            }
            
        except Exception as e:
            logger.error(f"Error in quality evaluation with counts: {e}")
            return {
                "rating": "FAIL",
                "description": f"Error evaluating image: {str(e)}",
                "object_counts": []
            }
    
    async def _evaluate_multiple_with_counts(self, image_urls: List[str], expected_description: str,
    educational_context: str, question_prompt: str, count_results: Dict[str, Any],
    is_retry: bool = False) -> Dict[str, Any]:
        """Evaluate multiple images using count results to select the best one."""
        
        system_prompt = self.SYSTEM_PROMPT.format(
            task_description="You are evaluating multiple images using UNBIASED object count data "
                           "to select the best image that meets quality standards.",
            rating_guidelines="""## Multi-Image Selection Using Count Data and Confidence

You will receive:
1. UNBIASED OBJECT COUNTS: For each image, detailed counts collected without knowledge of
expectations, including confidence levels
2. EXPECTED DESCRIPTION: What images should show
3. EDUCATIONAL CONTEXT & QUESTION PROMPT: Learning context

## Evaluation Process

1. For each image, compare its unbiased FINAL VERIFIED COUNTS (ignore preliminary method counts) to
expected description requirements
2. Evaluate other criteria (visual clarity, pedagogical appropriateness, etc.)  
3. Select the BEST image using this priority order:
   
   **PRIORITY 1 - Correctness**: Images with correct object counts vs expected
   **PRIORITY 2 - Confidence Level**: Among correct images, prefer higher confidence
   **PRIORITY 3 - Aesthetics**: Among equal confidence, prefer most visually appealing
   **PRIORITY 4 - Random**: Among aesthetically equal, select any

CRITICAL: Use the provided unbiased FINAL VERIFIED COUNT data - do not re-count objects. 
These are factual observations collected without bias, verified through multiple methods.

ADDITIONAL OBSCURED OBJECTS CHECK: Even if counting was successful, you must also evaluate whether
any images contain obscured, overlapping, or ambiguously positioned objects that would make them
unsuitable for educational use. Images with such issues should be rated as FAIL regardless of count
accuracy.

CONFIDENCE HIERARCHY: high > medium > low
- If Image A has correct counts with HIGH confidence and Image B has correct counts with MEDIUM
confidence, choose Image A
- Only consider aesthetics if confidence levels are equal

Return PASS with selected_image_url if at least one image meets standards.
Return FAIL if no images meet standards.""",
            tool_name="multi_image_quality_assessment_with_counts"
        )

        # Format all count data for comparison
        all_count_summaries = []
        for img_data in count_results.get("image_counts", []):
            count_summary = self._format_count_data_for_evaluation(img_data)
            all_count_summaries.append(
                f"IMAGE {img_data['image_index']} ({img_data['image_url']}):\n{count_summary}"
            )
        
        url_list = "\n".join([f"Image {i+1}: {url}" for i, url in enumerate(image_urls)])
        count_data_text = "\n\n".join(all_count_summaries)
        
        message_content = [{
            "type": "text", 
            "text": f"""Please evaluate these {len(image_urls)} images using the unbiased object
count data:

UNBIASED OBJECT COUNT DATA (collected without knowledge of expectations):
{count_data_text}

Educational Context: {educational_context}
Question Prompt: {question_prompt}
Expected Description: {expected_description}

IMAGE URL MAPPING:
{url_list}

Select the best image that meets all criteria using the unbiased count data."""
        }]
        
        # Add all images for visual assessment
        for i, image_url in enumerate(image_urls):
            message_content.append({
                "type": "text", 
                "text": f"=== IMAGE {i+1} (URL: {image_url}) ==="
            })
            
            if is_retry:
                try:
                    await asyncio.sleep(1)
                    image_response = requests.get(image_url)
                    image_response.raise_for_status()
                    image_bytes = image_response.content
                    if image_bytes:
                        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                        content_type = image_response.headers.get('content-type', 'image/png')
                        media_type = "image/jpeg" if 'jpeg' in content_type \
                            or 'jpg' in content_type else "image/png"
                        message_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        })
                except Exception as e:
                    logger.error(f"Error downloading image {i+1}: {e}")
                    message_content.append({
                        "type": "image",
                        "source": {"type": "url", "url": image_url}
                    })
            else:
                message_content.append({
                    "type": "image",
                    "source": {"type": "url", "url": image_url}
                })

        # Define structured output tool for multi-image evaluation
        tools = [{
            "name": "multi_image_quality_assessment_with_counts",
            "description": "Evaluate multiple images using count data and select the best one",
            "input_schema": {
                "type": "object",
                "properties": {
                    "individual_evaluations": {
                        "type": "string",
                        "description": "Detailed evaluation of each image comparing counts to "
                                       "expectations"
                    },
                    "selection_rationale": {
                        "type": "string",
                        "description": "Explanation of which image was selected and why, or why "
                                       "all failed"
                    },
                    "rating": {
                        "type": "string",
                        "enum": ["PASS", "FAIL", "NO_ACCESS"],
                        "description": "Overall rating - PASS if at least one image meets criteria"
                    },
                    "description": {
                        "type": "string",
                        "description": "Summary of final decision"
                    },
                    "selected_image_url": {
                        "type": "string",
                        "description": "URL of best image (required for PASS ratings)"
                    },
                    "individual_image_ratings": {
                        "type": "object",
                        "description": "Individual PASS/FAIL rating for each image URL",
                        "additionalProperties": {"type": "string", "enum": ["PASS", "FAIL"]}
                    },
                    "object_counts": {
                        "type": "array", 
                        "description": "Count verification for selected image",
                        "items": {
                            "type": "object",
                            "properties": {
                                "object_name": {"type": "string"},
                                "expected_count": {"type": "integer"},
                                "observed_count": {"type": "integer"}, 
                                "is_count_mismatch": {"type": "boolean"},
                                "contained_objects": {"type": "array", "items": {"$ref": "#"}}
                            },
                            "required": ["object_name", "expected_count", "observed_count",
                                        "is_count_mismatch"]
                        }
                    }
                },
                "required": ["individual_evaluations", "selection_rationale", "rating",
                            "description", "individual_image_ratings", "object_counts"]
            }
        }]

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=16384,
                system=system_prompt,
                tools=tools,
                tool_choice={"type": "tool", "name": "multi_image_quality_assessment_with_counts"},
                messages=[{"role": "user", "content": message_content}]
            )
            
            for content in response.content:
                if content.type == "tool_use" \
                    and content.name == "multi_image_quality_assessment_with_counts":
                    return content.input
            
            return {
                "rating": "FAIL",
                "description": "Unexpected response format",
                "individual_image_ratings": {url: "FAIL" for url in image_urls},
                "object_counts": []
            }
            
        except Exception as e:
            logger.error(f"Error in multi-image evaluation with counts: {e}")
            return {
                "rating": "FAIL", 
                "description": f"Error evaluating images: {str(e)}",
                "individual_image_ratings": {url: "FAIL" for url in image_urls},
                "object_counts": []
            }
    
    def _format_count_data_for_evaluation(self, image_count_data: Dict[str, Any]) -> str:
        """Format count data into readable text for evaluation."""
        
        # Check if image was rejected during counting
        if image_count_data.get("image_rejected", False):
            rejection_reason = image_count_data.get("rejection_reason", "Obscured objects detected")
            return f"IMAGE REJECTED during counting step: {rejection_reason}"
        
        output = [
            "Multi-Method Counting Process: "
            f"{image_count_data.get('counting_process_summary', 'N/A')}"
        ]
        output.append(f"Overall Confidence: {image_count_data.get('overall_confidence', 'N/A')}")
        output.append("\nFinal Verified Object Counts:")
        
        for obj_type in image_count_data.get('object_types', []):
            name = obj_type['object_name']
            final_count = obj_type['final_verified_count']
            confidence = obj_type['confidence_level']
            scenario = obj_type.get('scenario_classification', 'N/A')
            strategy = obj_type.get('counting_strategy_used', '')
            method_agreement = obj_type.get('method_agreement', '')
            sanity_check = obj_type.get('sanity_check', '')
            quality_assessment = obj_type.get('quality_assessment', '')
            container_rel = obj_type.get('container_relationship', '')
            discrepancies = obj_type.get('count_discrepancies', '')
            
            output.append(f"  {name}: {final_count} (confidence: {confidence})")
            output.append(f"    Scenario: {scenario}")
            if strategy:
                output.append(f"    Strategy used: {strategy}")
            if method_agreement:
                output.append(f"    Method agreement: {method_agreement}")
            if sanity_check:
                output.append(f"    Sanity check: {sanity_check}")
            if quality_assessment:
                output.append(f"    Quality assessment: {quality_assessment}")
            if container_rel:
                output.append(f"    Relationship: {container_rel}")
            if discrepancies:
                output.append(f"    Method discrepancies: {discrepancies}")
                
            # Show method breakdown for transparency
            method_1 = obj_type.get('method_1_count', 'N/A')
            method_2 = obj_type.get('method_2_count', 'N/A')
            method_3 = obj_type.get('method_3_count', 'N/A')
            output.append(
                f"    Method counts: Systematic={method_1}, Type-Based={method_2}, "
                f"Alternative={method_3}"
            )
        
        return "\n".join(output)
    
    async def check_image_quality(self, image_urls: Union[str, List[str]],
    expected_description: str, educational_context: str, question_prompt: str = None,
    is_retry: bool = False, delete_failed_images: bool = True) -> str:
        """
        Check if image(s) match expected description and meet quality standards using two-step
        process.
        
        This method implements a two-step evaluation process to avoid bias in object counting:
        1. First step: Count objects in images without any context about what should be present
        2. Second step: Use the unbiased counts plus expected context to evaluate quality
        
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
            
            logger.info(f"Starting two-step quality evaluation for {len(image_urls)} image(s)")
            start_time = time()
            
            # STEP 1: Count objects without bias (no knowledge of expected content)
            logger.info("Step 1: Counting objects without context bias...")
            count_results = await self._count_objects_without_bias(image_urls, is_retry)
            
            if "error" in count_results:
                logger.error(f"Error in object counting step: {count_results['error']}")
                error_result = ImageQualityResult(
                    rating=QualityRating.FAIL,
                    description=f"Unable to count objects: {count_results['error']}",
                    object_counts=None
                )
                if delete_failed_images:
                    delete_files_from_supabase(image_urls, delay_seconds=5.0)
                return error_result.model_dump_json(indent=2)
            
            # Check if any images were rejected during counting due to obscured objects
            rejected_images = []
            valid_images = []
            
            for img_data in count_results.get("image_counts", []):
                if img_data.get("image_rejected", False):
                    rejected_images.append({
                        "url": img_data["image_url"],
                        "reason": img_data.get("rejection_reason", "Obscured objects detected")
                    })
                else:
                    valid_images.append(img_data["image_url"])
            
            # Log rejected images but don't fail unless ALL images are rejected
            if rejected_images:
                rejection_reasons = [f"{img['url']}: {img['reason']}" for img in rejected_images]
                logger.info(
                    f"Images rejected during counting step: {len(rejected_images)} out of "
                    f"{len(image_urls)}"
                )
                logger.info(f"Rejected: {'; '.join(rejection_reasons)}")
                
                # Only fail if ALL images were rejected
                if not valid_images:
                    logger.error("All images rejected during counting step")
                    error_result = ImageQualityResult(
                        rating=QualityRating.FAIL,
                        description="All images rejected due to obscured/ambiguous objects: " + \
                                    f"{'; '.join(rejection_reasons)}",
                        object_counts=None
                    )
                    if delete_failed_images:
                        delete_files_from_supabase(image_urls, delay_seconds=5.0)
                    return error_result.model_dump_json(indent=2)
                
                # Delete only the rejected images
                if delete_failed_images:
                    rejected_urls = [img['url'] for img in rejected_images]
                    delete_files_from_supabase(rejected_urls, delay_seconds=5.0)
                
                # Update image_urls to only include valid images for Step 2
                image_urls = valid_images
                logger.info(f"Proceeding to Step 2 with {len(valid_images)} valid images")
            
            # STEP 2: Evaluate quality using unbiased counts and expected context
            logger.info("Step 2: Evaluating quality using count results and context...")
            quality_results = await self._evaluate_quality_with_counts(
                image_urls, expected_description, educational_context, 
                question_prompt, count_results, is_retry
            )

            end_time = time()
            logger.info(f"Time taken to evaluate quality: {end_time - start_time} seconds")
            
            # Convert results to ImageQualityResult format
            rating = QualityRating(quality_results["rating"])
            
            # Parse object counts from quality results
            def parse_object_counts(counts_data):
                if not counts_data:
                    return None
                object_counts = []
                for count_data in counts_data:
                    contained = None
                    if count_data.get("contained_objects"):
                        contained = parse_object_counts(count_data["contained_objects"])
                    obj_check = ObjectCountCheck(
                        object_name=count_data["object_name"],
                        expected_count=count_data["expected_count"],
                        observed_count=count_data["observed_count"],
                        is_count_mismatch=count_data["is_count_mismatch"],
                        contained_objects=contained
                    )
                    object_counts.append(obj_check)
                return object_counts

            object_counts = parse_object_counts(quality_results.get("object_counts"))
            
            # Handle different result formats (single vs multi-image)
            selected_url = quality_results.get("selected_image_url")
            individual_ratings = quality_results.get("individual_image_ratings")
            
            # For multi-image results, validate and fix selected URL
            if len(image_urls) > 1 and rating == QualityRating.PASS:
                if not selected_url or selected_url not in image_urls:
                    logger.warning(
                        "Invalid selected URL in multi-image result, attempting to fix..."
                    )
                    if individual_ratings:
                        passing_urls = [url for url in image_urls \
                            if individual_ratings.get(url) == "PASS"]
                        if passing_urls:
                            selected_url = passing_urls[0]
                        else:
                            logger.warning("No passing images found, using first image")
                            selected_url = image_urls[0]
                    else:
                        selected_url = image_urls[0]
            
            result = ImageQualityResult(
                rating=rating,
                description=quality_results["description"],
                selected_image_url=selected_url,
                individual_image_ratings=individual_ratings,
                object_counts=object_counts
            )
            
            # Handle image deletion based on results
            if result.rating == QualityRating.PASS:
                if len(image_urls) > 1:
                    # Multi-image PASS: delete unselected images
                    logger.info("Two-step quality check result: PASS - Selected: " + \
                                f"{result.selected_image_url}")
                    if delete_failed_images:
                        urls_to_delete = [url for url in image_urls \
                            if url != result.selected_image_url]
                        if urls_to_delete:
                            delete_files_from_supabase(urls_to_delete, delay_seconds=5.0)
                else:
                    # Single image PASS
                    logger.info(f"Two-step quality check result: PASS - Image: {image_urls[0]}")
            else:
                # FAIL: delete all images
                logger.error(f"Two-step quality check result: FAIL - {result.description}")
                if delete_failed_images:
                    delete_files_from_supabase(image_urls, delay_seconds=5.0)
            
            return result.model_dump_json(indent=2)
                
        except Exception as e:
            error_message = f"Error in two-step image quality check: {str(e)}"
            logger.error(error_message)
            # Return a FAIL result with error details
            error_result = ImageQualityResult(
                rating=QualityRating.FAIL,
                description=f"Unable to analyze image due to technical error: {str(e)}",
                object_counts=None
            )
            if delete_failed_images:
                delete_files_from_supabase(image_urls if isinstance(image_urls, list) \
                    else [image_urls], delay_seconds=5.0)
            return error_result.model_dump_json(indent=2)

    async def _evaluate_multiple_images(self, image_urls: List[str], expected_description: str,
    educational_context: str, question_prompt: str = None, is_retry: bool = False,
    delete_failed_images: bool = True) -> str:
        """Evaluate multiple images and return the best one or fail if none are good enough."""
        
        logger.info(f"Evaluating {len(image_urls)} images:")
        for i, url in enumerate(image_urls):
            logger.info(f"  Image {i+1}: {url}")
        
        system_prompt = self.SYSTEM_PROMPT.format(
            task_description="You are evaluating multiple images to select the best one that "
            "accurately depicts the expected content and meets quality standards.",
            rating_guidelines="""## Task: Select Best Image

Your task is to:
1. Evaluate all provided images against the expected description, educational context, question
prompt, and evaluation criteria
2. Use the object_counts data structure to carefully record all object counts in the image. Count
objects CAREFULLY! Pay particular attention to objects which are hidden or cut off -- objects
must be at least 80% visible to be considered "visible" for counting purposes. Any image that
does not have the correct counts for all specified objects should be rated as FAIL.
3. CRITICAL: Check for visual clarity and pedagogical appropriateness:
   - Are there floating, disconnected, or unnatural visual elements?
   - Are there redundant or confusing visual representations?
   - Would grade-level students be confused by any visual elements?
   Any such issues are grounds for FAIL.
4. If at least one image meets all criteria, return a PASS rating with the URL of the BEST image
according to all Evaluation Criteria as the selected_image_url.
   - If multiple images meet the Evaluation Criteria, select the one that is the most visually
   appealing, accurate, aesthetic, and meets all Evaluation Criteria.
   - If multiple images are equally appealing in all respects and meet all Evaluation Criteria,
   select one at random.
5. If no image meets the criteria, return FAIL with a summary of the main issues across all images

CRITICAL: You MUST select the URL exactly as provided in the list below. Do NOT modify, truncate, or
create new URLs.

For PASS ratings: You MUST provide the exact URL of the best image in the selected_image_url field
AND explain why it was selected. You must also provide individual PASS/FAIL ratings for each image
in the individual_image_ratings field.
For FAIL ratings: Provide a comprehensive summary of the main issues found across all images and
specific instructions on how to create a better image. You must also provide individual PASS/FAIL
ratings for each image in the individual_image_ratings field.

CRITICAL: Complete your full systematic evaluation of ALL images against ALL criteria FIRST.
Document your complete analysis including:
- Object count verification for each image
- Visual clarity and pedagogical appropriateness assessment 
- Evaluation against all criteria listed above

Only AFTER completing this comprehensive analysis should you determine ratings and select URLs.
This systematic approach ensures accurate assessment and prevents premature conclusions.""",
            tool_name="multi_image_quality_assessment"
        )

        try:
            # Create URL mapping for reference
            url_list = "\n".join([f"Image {i+1}: {url}" for i, url in enumerate(image_urls)])
            
            # Prepare image content for all images
            message_content = [
                {"type": "text", "text": f"""Please evaluate these {len(image_urls)} images against
the expected description within the specified educational context:

Educational Context: {educational_context}

Question Prompt the image will be used in (if any): {question_prompt}

Expected Description: {expected_description}

IMAGE URL MAPPING:
{url_list}

IMPORTANT: You must select the URL exactly as listed above. Do not modify or create new URLs.

Select the best image that meets all criteria, or indicate if none are acceptable."""}
            ]
            
            # Add all images to the message
            for i, image_url in enumerate(image_urls):
                # Add a text label before each image
                message_content.append({
                    "type": "text", 
                    "text": f"=== IMAGE {i+1} (URL: {image_url}) ==="
                })
                
                if is_retry:
                    # Try downloading the image and passing it as bytes
                    try:
                        await asyncio.sleep(1)  # Small delay between requests
                        image_response = requests.get(image_url)
                        image_response.raise_for_status()
                        image_bytes = image_response.content
                        if image_bytes:
                            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                            content_type = image_response.headers.get('content-type', 'image/png')
                            if 'jpeg' in content_type or 'jpg' in content_type:
                                media_type = "image/jpeg"
                            else:
                                media_type = "image/png"
                            
                            message_content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64
                                }
                            })
                    except Exception as e:
                        logger.error(f"Error downloading image {i+1}: {e}")
                        # Fallback to URL
                        message_content.append({
                            "type": "image",
                            "source": {
                                "type": "url",
                                "url": image_url
                            }
                        })
                else:
                    message_content.append({
                        "type": "image",
                        "source": {
                            "type": "url",
                            "url": image_url
                        }
                    })

            # Define the structured output tool for multiple images
            tools = [
                {
                    "name": "multi_image_quality_assessment",
                    "description": "Provide a structured assessment of multiple images and select "
                                   "the best one.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "analysis": {
                                "type": "string",
                                "description": "Complete systematic evaluation performed before "
                                               "making final determination. Include object count "
                                               "verification, visual clarity assessment, and "
                                               "evaluation against all criteria for each image."
                            },
                            "rating": {
                                "type": "string",
                                "enum": ["PASS", "FAIL", "NO_ACCESS"],
                                "description": "Overall quality rating - PASS if at least one "
                                               "image meets criteria, FAIL if none do. Set this "
                                               "field AFTER completing analysis."
                            },
                            "description": {
                                "type": "string",
                                "description": "Concise summary of the final assessment decision "
                                               "based on the completed analysis."
                            },
                            "selected_image_url": {
                                "type": "string",
                                "description": "URL of the best image - must be exactly one of the "
                                               "provided URLs. REQUIRED when rating is PASS, omit "
                                               "when rating is FAIL or NO_ACCESS."
                            },
                            "individual_image_ratings": {
                                "type": "object",
                                "description": "Dictionary mapping each image URL to its "
                                               "individual PASS/FAIL rating. REQUIRED for all "
                                               "multi-image evaluations.",
                                "additionalProperties": {
                                    "type": "string",
                                    "enum": ["PASS", "FAIL"]
                                }
                            },
                            "object_counts": {
                                "type": "array",
                                "description": "Detailed object count verification for the "
                                               "selected image",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "object_name": {
                                            "type": "string",
                                            "description": "Name/type of the object being counted"
                                        },
                                        "expected_count": {
                                            "type": "integer",
                                            "description": "Number of objects expected from "
                                                           "description"
                                        },
                                        "observed_count": {
                                            "type": "integer", 
                                            "description": "Number of objects actually counted in "
                                                           "image"
                                        },
                                        "is_count_mismatch": {
                                            "type": "boolean",
                                            "description": "Whether expected and observed counts "
                                                           "differ"
                                        },
                                        "contained_objects": {
                                            "type": "array",
                                            "description": "For nested counting (e.g., items "
                                                           "within containers)",
                                            "items": {"$ref": "#"}
                                        }
                                    },
                                    "required": ["object_name", "expected_count", "observed_count",
                                                "is_count_mismatch"]
                                }
                            }
                        },
                        "required": ["analysis", "rating", "description",
                                    "individual_image_ratings", "object_counts"],
                        "additionalProperties": False
                    }
                }
            ]

            logger.info(f"Evaluating {len(image_urls)} images for quality...")
            
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=16384,
                system=system_prompt,
                tools=tools,
                tool_choice={"type": "tool", "name": "multi_image_quality_assessment"},
                messages=[
                    {"role": "user", "content": message_content}
                ]
            )
            
            # Extract the structured response from tool use
            for content in response.content:
                if content.type == "tool_use" and content.name == "multi_image_quality_assessment":
                    tool_input = content.input
                    
                    # Create the result object
                    # Need to use a bit of extra logic to look at individual ratings because
                    # sometimes Claude gives an overall FAIL but changes its mind and gives a PASS
                    # for one or more of the individual images.
                    rating = tool_input["rating"]
                    individual_ratings = tool_input.get("individual_image_ratings", {})
                    all_ratings = [rating] + list(individual_ratings.values())
                    overall_rating = QualityRating.PASS if "PASS" in all_ratings \
                        else QualityRating.FAIL
                    selected_url = None
                    
                    if overall_rating == QualityRating.PASS:
                        selected_url = tool_input.get("selected_image_url")
                        
                        # Handle case where model returns PASS but no URL
                        if not selected_url:
                            logger.warning(
                                "Model returned PASS but no selected_image_url. Using first "
                                "passing image."
                            )
                            passing_urls = [url for url in image_urls \
                                if individual_ratings[url] == "PASS"]
                            if passing_urls:
                                selected_url = passing_urls[0]
                            else:
                                logger.warning(
                                    "No passing images found despite overall PASS. Using first "
                                    "image."
                                )
                                selected_url = image_urls[0]
                        # Validate that the selected URL is from the provided list
                        elif selected_url not in image_urls:
                            logger.error(f"Model selected invalid URL: {selected_url}")
                            logger.error(f"Valid URLs were: {image_urls}")
                            logger.warning(
                                "Selected URL not found in provided list. Falling back to first "
                                "passing image."
                            )
                            passing_urls = [url for url in image_urls \
                                if individual_ratings[url] == "PASS"]
                            if passing_urls:
                                selected_url = passing_urls[0]
                            else:
                                logger.warning(
                                    "No passing images found. Falling back to first image."
                                )
                                selected_url = image_urls[0]
                     
                    # Parse object counts (reuse the same function)
                    def parse_object_counts(counts_data):
                        if not counts_data:
                            return None
                        object_counts = []
                        for count_data in counts_data:
                            contained = None
                            if count_data.get("contained_objects"):
                                contained = parse_object_counts(count_data["contained_objects"])
                            obj_check = ObjectCountCheck(
                                object_name=count_data["object_name"],
                                expected_count=count_data["expected_count"],
                                observed_count=count_data["observed_count"],
                                is_count_mismatch=count_data["is_count_mismatch"],
                                contained_objects=contained
                            )
                            object_counts.append(obj_check)
                        return object_counts

                    object_counts = parse_object_counts(tool_input.get("object_counts"))
                    
                    result = ImageQualityResult(
                        rating=overall_rating,
                        description=tool_input["description"],
                        selected_image_url=selected_url,
                        individual_image_ratings=individual_ratings,
                        object_counts=object_counts
                    )
                    
                    if result.rating == QualityRating.PASS:
                        logger.info(f"Claude multi-image quality check result: PASS - Selected: "
                                    f"{result.selected_image_url}")
                        # Multi-image PASS: delete all unselected images
                        if delete_failed_images:
                            urls_to_delete = [url for url in image_urls \
                                                if url != result.selected_image_url]
                            delete_files_from_supabase(urls_to_delete, delay_seconds=5.0)
                    else:
                        logger.error(f"Claude multi-image quality check result: {result}")
                        # Multi-image FAIL: delete all images since none were good enough  
                        if delete_failed_images:
                            delete_files_from_supabase(image_urls, delay_seconds=5.0)
                        
                    if result.rating == QualityRating.NO_ACCESS and not is_retry:
                        return await self._evaluate_multiple_images(image_urls,
                            expected_description, educational_context, question_prompt, True,
                            delete_failed_images)
                        
                    return result.model_dump_json(indent=2)
            
            # Fallback if no tool use found
            result = ImageQualityResult(
                rating=QualityRating.FAIL,
                description="Unexpected response format from image evaluation",
                individual_image_ratings={url: "FAIL" for url in image_urls},
                object_counts=None
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
                individual_image_ratings={url: "FAIL" for url in image_urls},
                object_counts=None
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
            task_description="Your task is to evaluate whether an image accurately depicts what "
            "it's supposed to show and meets quality standards for educational use.",
            rating_guidelines="""## Rating the Image

Use the object_counts data structure to carefully record all object counts in the image. Count
objects CAREFULLY! Pay particular attention to objects which are hidden or cut off -- objects
must be at least 80% visible to be considered "visible" for counting purposes. Any image that
does not have the correct counts for all specified objects should be rated as FAIL.

Rate the image as:
- PASS: If the image accurately depicts the expected content and meets ALL Evaluation Criteria.
- FAIL: If there are ANY significant issues with Evaluation Criteria. Particular attention to:
  * Incorrect object counts (must be exactly as specified, not approximate)
  * Floating, disconnected, or unnatural visual elements  
  * Redundant or confusing visual representations
  * Any elements that would confuse grade-level students
  ALL Evaluation Criteria must be met for a PASS rating.
- NO_ACCESS: If the image is not accessible or cannot be reviewed.

For FAIL ratings, provide specific details about ALL Evaluation Criteria issues in ALL relevant
elements within the image. Include specific instructions on how to resolve the issues.
For PASS ratings, briefly confirm what the image shows correctly.
For NO_ACCESS ratings, provide a brief explanation of why the image is not accessible or cannot be
reviewed.

CRITICAL: Complete your full systematic evaluation against ALL criteria FIRST.
Document your complete analysis including:
- Detailed object count verification
- Visual clarity and pedagogical appropriateness assessment
- Evaluation against all criteria listed above

Only AFTER completing this comprehensive analysis should you assign a rating.
This systematic approach ensures accurate assessment and prevents premature conclusions.""",
            tool_name="image_quality_assessment"
        )

        user_prompt = f"""Please evaluate this image against the expected description within the
specified educational context:

Educational Context: {educational_context}

Question Prompt the image will be used in (if any): {question_prompt}

Expected Description: {expected_description}

Analyze the image and determine if it accurately depicts what is described and meets all your
criteria."""

        if is_retry:
            # Try downloading the image and passing it as bytes
            logger.info("Retrying image quality check with URL in 3 seconds...")
            await asyncio.sleep(3)
            try:
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                image_bytes = image_response.content
                if image_bytes:
                    # Convert to base64 for Anthropic API
                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    
                    # Determine media type from response headers or URL
                    content_type = image_response.headers.get('content-type', 'image/png')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        media_type = "image/jpeg"
                    else:
                        media_type = "image/png"
                        
                    image_content = {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64
                        }
                    }
            except Exception as e:
                logger.error(f"Error downloading image: {e}")
                logger.info("Retrying image quality check with URL in 3 seconds...")
                await asyncio.sleep(3)
                # Fallback to image URL
                image_content = {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": image_url
                    }
                }
        else:
            logger.info(f"Checking image quality for {image_url}")
            # Use image URL directly
            image_content = {
                "type": "image", 
                "source": {
                    "type": "url",
                    "url": image_url
                }
            }

        # Define the structured output tool
        tools = [
            {
                "name": "image_quality_assessment",
                "description": "Provide a structured assessment of image quality for educational "
                               "content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "analysis": {
                            "type": "string",
                            "description": "Complete systematic evaluation performed before "
                                           "making final determination. Include object count "
                                           "verification, visual clarity assessment, and "
                                           "evaluation against all criteria."
                        },
                        "rating": {
                            "type": "string",
                            "enum": ["PASS", "FAIL", "NO_ACCESS"],
                            "description": "Overall quality rating for the image (determined AFTER "
                                           "completing analysis)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Concise summary of the final assessment decision "
                                           "based on the completed analysis"
                        },
                        "object_counts": {
                            "type": "array",
                            "description": "Detailed object count verification for all objects "
                                           "expected to have specific counts",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "object_name": {
                                        "type": "string",
                                        "description": "Name/type of the object being counted"
                                    },
                                    "expected_count": {
                                        "type": "integer",
                                        "description": "Number of objects expected from description"
                                    },
                                    "observed_count": {
                                        "type": "integer", 
                                        "description": "Number of objects actually counted in image"
                                    },
                                    "is_count_mismatch": {
                                        "type": "boolean",
                                        "description": "Whether expected and observed counts differ"
                                    },
                                    "contained_objects": {
                                        "type": "array",
                                        "description": "For nested counting (e.g., items within "
                                                       "containers)",
                                        "items": {"$ref": "#"}
                                    }
                                },
                                "required": ["object_name", "expected_count", "observed_count",
                                            "is_count_mismatch"]
                            }
                        }
                    },
                    "required": ["analysis", "rating", "description", "object_counts"]
                }
            }
        ]

        # Use Claude Sonnet 4 with vision capabilities and structured output
        logger.info(f"Checking image quality for image at {image_url}...")
        
        message_content = [
            {"type": "text", "text": user_prompt},
            image_content
        ]
        
        response = await self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=16384,
            system=system_prompt,
            tools=tools,
            tool_choice={"type": "tool", "name": "image_quality_assessment"},
            messages=[
                {"role": "user", "content": message_content}
            ]
        )
        
        # Extract the structured response from tool use
        for content in response.content:
            if content.type == "tool_use" and content.name == "image_quality_assessment":
                tool_input = content.input
                
                # Create the result object
                rating = QualityRating(tool_input["rating"])
                
                # Parse object counts
                def parse_object_counts(counts_data):
                    if not counts_data:
                        return None
                    object_counts = []
                    for count_data in counts_data:
                        contained = None
                        if count_data.get("contained_objects"):
                            contained = parse_object_counts(count_data["contained_objects"])
                        obj_check = ObjectCountCheck(
                            object_name=count_data["object_name"],
                            expected_count=count_data["expected_count"],
                            observed_count=count_data["observed_count"],
                            is_count_mismatch=count_data["is_count_mismatch"],
                            contained_objects=contained
                        )
                        object_counts.append(obj_check)
                    return object_counts

                object_counts = parse_object_counts(tool_input.get("object_counts"))
                
                result = ImageQualityResult(
                    rating=rating,
                    description=tool_input["description"],
                    object_counts=object_counts
                )
                
                if result.rating == QualityRating.PASS:
                    logger.info(f"Image quality check result: {result}")
                else:
                    logger.error(f"Image quality check result: {result}")
                    # Single image FAIL: delete the failed image
                    if delete_failed_images:
                        delete_files_from_supabase([image_url], delay_seconds=5.0)
                    
                if result.rating == QualityRating.NO_ACCESS and not is_retry:
                    return await self._evaluate_single_image(image_url, expected_description,
                        educational_context, question_prompt, True, delete_failed_images)
                    
                return result.model_dump_json(indent=2)
        
        # Fallback if no tool use found (shouldn't happen with tool_choice)
        response_text = response.content[0].text if response.content else "No response content"
        result = ImageQualityResult(
            rating=QualityRating.FAIL,
            description=f"Unexpected response format: {response_text}",
            object_counts=None
        )
        # Single image FAIL: delete the failed image
        if delete_failed_images:
            delete_files_from_supabase([image_url], delay_seconds=5.0)
        return result.model_dump_json(indent=2)


def generate_image_quality_checker_tool_claude() -> tuple[Dict[str, Any], Callable]:
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
        "description": "Evaluate whether image(s) accurately depict expected content and meet "
                       "quality standards for educational use. Can evaluate a single image or "
                       "multiple images. For multiple images, returns the best one that meets "
                       "standards or fails if none are acceptable.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_urls": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Either a single image URL (string) or a list of image URLs to "
                                   "analyze and evaluate for quality and accuracy."
                },
                "expected_description": {
                    "type": "string", 
                    "description": "Description of what the image is supposed to depict or show, "
                                   "focused on a precise description of all objects in the image "
                                   "that a student may need to identify (including counts of these "
                                   "objects). Don't include details that are not relevant to what "
                                   "the student is supposed to observe in the image."
                },
                "educational_context": {
                    "type": "string",
                    "description": "The educational context of the image. This will be used to "
                                   "verify the image is appropriate for a typical student in the "
                                   "target grade trying to learn the material."
                },
                "question_prompt": {
                    "type": "string",
                    "description": "The prompt of the question that the image is associated with, "
                                   "if any. This will be used to verify the image is appropriate "
                                   "for the question."
                }
            },
            "required": ["image_urls", "expected_description", "educational_context",
                        "question_prompt"]
        }
    }
    
    return spec, image_quality_check_function 