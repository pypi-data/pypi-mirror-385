import asyncio
import json
import logging
import random
from collections import Counter
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from edu_agents.tools.image_quality_checker_claude import generate_image_quality_checker_tool_claude
from edu_agents.tools.image_quality_checker_gemini import generate_image_quality_checker_tool_gemini
from edu_agents.tools.image_quality_checker_gpt import generate_image_quality_checker_gpt_tool
from utils.supabase_utils import delete_files_from_supabase

logger = logging.getLogger(__name__)

class EnsembleQualityRating(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NO_ACCESS = "NO_ACCESS"

class EnsembleImageQualityResult(BaseModel):
    rating: EnsembleQualityRating
    description: str
    selected_image_url: Optional[str] = None  # For multi-image evaluation
    gpt_image_qc_result: Dict[str, Any]
    claude_image_qc_result: Dict[str, Any]
    gemini_image_qc_result: Dict[str, Any]

class EnsembleImageQualityChecker:
    """
    Ensemble image quality checker that calls GPT, Claude, and Gemini QC tools in parallel.
    
    For single images: Returns PASS only if all three tools rate it PASS
    For multiple images: Returns PASS if all three tools rate PASS, then selects URL by majority
    choice with sophisticated tie-breaking
    
    Automatically cleans up unused/failed images:
    - Single image FAIL: deletes the failed image after 5 seconds
    - Multi-image PASS: deletes all unselected images after 5 seconds  
    - Multi-image FAIL: deletes all images after 5 seconds
    """
    
    def __init__(self):
        # Get the individual QC tool functions
        _, self.gpt_qc_function = generate_image_quality_checker_gpt_tool()
        _, self.claude_qc_function = generate_image_quality_checker_tool_claude()
        _, self.gemini_qc_function = generate_image_quality_checker_tool_gemini()
    
    async def check_image_quality(self, image_urls: Union[str, List[str]],
    expected_description: str, educational_context: str, question_prompt: str = None) -> str:
        """
        Check if image(s) match expected description and meet quality standards using GPT, Claude,
        and Gemini QC tools.
        
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
        
        Returns
        -------
        str
            JSON string with ensemble rating and individual tool results
        """
        try:
            logger.info(f"Running ensemble image QC on {image_urls}")
            
            # Run all three QC tools in parallel using asyncio.gather
            # Submit all QC tasks with delete_failed_images=False to prevent individual tools from
            # deleting images
            gpt_task = self.gpt_qc_function(image_urls, expected_description, educational_context,
                question_prompt=question_prompt, delete_failed_images=False)
            claude_task = self.claude_qc_function(image_urls, expected_description,
                educational_context, question_prompt=question_prompt, delete_failed_images=False)
            gemini_task = self.gemini_qc_function(image_urls, expected_description,
                educational_context, question_prompt=question_prompt, delete_failed_images=False)
            
            # Gather results with exception handling
            qc_results = await asyncio.gather(gpt_task, claude_task, gemini_task,
                return_exceptions=True)
            
            # Process results
            results = {}
            tool_names = ["gpt", "claude", "gemini"]
            
            for tool_name, qc_result in zip(tool_names, qc_results):
                try:
                    if isinstance(qc_result, Exception):
                        logger.error(f"Error in {tool_name} QC: {qc_result}")
                        # Create a FAIL result for the failed tool
                        results[f"{tool_name}_image_qc_result"] = {
                            "rating": "FAIL",
                            "description": f"Error in {tool_name} QC: {str(qc_result)}"
                        }
                    else:
                        result_dict = json.loads(qc_result)
                        results[f"{tool_name}_image_qc_result"] = result_dict
                        logger.info(
                            f"{tool_name.upper()} QC result: {result_dict['rating']} - "
                            f"{result_dict.get('description', 'No description')}"
                        )
                except json.JSONDecodeError as json_error:
                    logger.error(f"Error parsing JSON from {tool_name} QC: {json_error}")
                    logger.error(
                        f"Raw response from {tool_name}: {qc_result[:200]}..." \
                            if len(str(qc_result)) > 200 \
                                else f"Raw response from {tool_name}: {qc_result}")
                    # Create a FAIL result for the failed tool
                    results[f"{tool_name}_image_qc_result"] = {
                        "rating": "FAIL",
                        "description": f"Error parsing JSON response from {tool_name} QC: "
                                       f"{str(json_error)}"
                    }
            
            # Aggregate results
            return self._aggregate_results(results, image_urls, question_prompt)
            
        except Exception as e:
            error_message = f"Error in ensemble image QC: {str(e)}"
            logger.error(error_message)
            
            # Return a FAIL result with error details
            error_result = EnsembleImageQualityResult(
                rating=EnsembleQualityRating.FAIL,
                description=error_message,
                gpt_image_qc_result={"rating": "FAIL", "description": "Not executed due to error"},
                claude_image_qc_result={
                    "rating": "FAIL", "description": "Not executed due to error"
                },
                gemini_image_qc_result={
                    "rating": "FAIL", "description": "Not executed due to error"
                }
            )
            return error_result.model_dump_json(indent=2)
    
    def _aggregate_results(self, results: Dict[str, Dict[str, Any]],
    image_urls: Union[str, List[str]], question_prompt: str = None) -> str:
        """Aggregate results from all three QC tools (GPT, Claude, and Gemini)."""
        
        gpt_result = results.get("gpt_image_qc_result", {})
        claude_result = results.get("claude_image_qc_result", {})
        gemini_result = results.get("gemini_image_qc_result", {})
        
        # Extract ratings
        gpt_rating = gpt_result.get("rating", "FAIL")
        claude_rating = claude_result.get("rating", "FAIL")
        gemini_rating = gemini_result.get("rating", "FAIL")
        
        # Check for service unavailability errors (503, timeouts, etc.)
        def is_service_unavailable_error(result_dict: Dict[str, Any]) -> bool:
            description = result_dict.get("description", "").lower()
            
            # Check for explicit HTTP status codes indicating temporary unavailability
            unavailable_status_codes = [503, 502, 504, 429, 500, 408]
            unavailable_status_strings = ["503", "502", "504", "429", "500", "408"]
            
            # Check if result contains explicit status code field
            status_code = result_dict.get("status_code") or result_dict.get("code") \
                or result_dict.get("error_code")
            if status_code:
                try:
                    status_int = int(status_code)
                    if status_int in unavailable_status_codes:
                        return True
                except (ValueError, TypeError):
                    pass
            
            # Check if any unavailability status codes are mentioned in description
            status_code_found = any(code in description for code in unavailable_status_strings)
            
            # Check for common error keywords
            keyword_found = any(error_indicator in description for error_indicator in [
                "unavailable", "overloaded", "try again later", 
                "timeout", "service unavailable", "temporarily unavailable",
                "rate limit", "quota exceeded", "bad gateway", "gateway timeout",
                "internal server error", "request timeout", "too many requests",
                "connection error", "network error", "server error"
            ])
            
            # Check for structured error information (e.g., from API responses)
            error_info = result_dict.get("error", {})
            if isinstance(error_info, dict):
                error_code = error_info.get("code") or error_info.get("status")
                if error_code:
                    try:
                        error_int = int(error_code)
                        if error_int in unavailable_status_codes:
                            return True
                    except (ValueError, TypeError):
                        pass
                
                error_status = str(error_info.get("status", "")).lower()
                if any(status in error_status for status in ["unavailable", "overloaded"]):
                    return True
            
            return status_code_found or keyword_found
        
        gpt_unavailable = gpt_rating == "FAIL" and is_service_unavailable_error(gpt_result)
        claude_unavailable = claude_rating == "FAIL" and is_service_unavailable_error(claude_result)
        gemini_unavailable = gemini_rating == "FAIL" and is_service_unavailable_error(gemini_result)
        
        logger.info(
            f"Individual ratings - GPT: {gpt_rating}, Claude: {claude_rating}, "
            f"Gemini: {gemini_rating}"
        )
        if gpt_unavailable:
            logger.warning(
                f"GPT QC service unavailable - ignoring GPT results. Error: "
                f"{gpt_result.get('description', 'Unknown error')[:200]}"
            )
        if claude_unavailable:
            logger.warning(
                f"Claude QC service unavailable - ignoring Claude results. Error: "
                f"{claude_result.get('description', 'Unknown error')[:200]}"
            )
        if gemini_unavailable:
            logger.warning(
                f"Gemini QC service unavailable - ignoring Gemini results. Error: "
                f"{gemini_result.get('description', 'Unknown error')[:200]}"
            )
        
        # Handle service unavailability scenarios
        available_count = sum(1 for unavail in \
            [gpt_unavailable, claude_unavailable, gemini_unavailable] if not unavail)
        
        if available_count == 0:
            logger.error("All QC services unavailable - treating as FAIL")
            gpt_rating = "FAIL"
            claude_rating = "FAIL"
            gemini_rating = "FAIL"
        elif available_count == 1:
            # Only one service available - use its result for all
            if not gpt_unavailable:
                logger.info(
                    "Using only GPT results due to Claude and Gemini service unavailability"
                )
                claude_rating = gpt_rating
                gemini_rating = gpt_rating
            elif not claude_unavailable:
                logger.info(
                    "Using only Claude results due to GPT and Gemini service unavailability"
                )
                gpt_rating = claude_rating
                gemini_rating = claude_rating
            else:  # not gemini_unavailable
                logger.info(
                    "Using only Gemini results due to GPT and Claude service unavailability"
                )
                gpt_rating = gemini_rating
                claude_rating = gemini_rating
        elif available_count == 2:
            # Two services available - treat unavailable one as agreeing with majority
            if gpt_unavailable:
                logger.info("Using Claude and Gemini results due to GPT service unavailability")
                # GPT will agree with whatever the majority of Claude+Gemini is
                if claude_rating == gemini_rating:
                    gpt_rating = claude_rating
                else:
                    # If Claude and Gemini disagree, treat GPT as agreeing with Claude (arbitrary)
                    gpt_rating = claude_rating
            elif claude_unavailable:
                logger.info("Using GPT and Gemini results due to Claude service unavailability")
                if gpt_rating == gemini_rating:
                    claude_rating = gpt_rating
                else:
                    claude_rating = gpt_rating
            else:  # gemini_unavailable
                logger.info("Using GPT and Claude results due to Gemini service unavailability")
                if gpt_rating == claude_rating:
                    gemini_rating = gpt_rating
                else:
                    gemini_rating = gpt_rating
        
        # Handle single vs multi-image cases
        if isinstance(image_urls, str) or len(image_urls) == 1:
            # Single image: PASS only if all three tools rate it PASS
            single_url = image_urls if isinstance(image_urls, str) else image_urls[0]
            
            if gpt_rating == "PASS" and claude_rating == "PASS" and gemini_rating == "PASS":
                ensemble_rating = EnsembleQualityRating.PASS
                
                # Generate description based on service availability
                available_services = []
                if not gpt_unavailable:
                    available_services.append("GPT")
                if not claude_unavailable:
                    available_services.append("Claude")
                if not gemini_unavailable:
                    available_services.append("Gemini")
                
                if len(available_services) == 3:
                    description = "All three QC tools (GPT, Claude, Gemini) rated the image PASS."
                elif len(available_services) == 2:
                    unavailable_services = [svc for svc in ["GPT", "Claude", "Gemini"] \
                        if svc not in available_services]
                    description = f"Both available QC tools ({', '.join(available_services)}) " + \
                        f"rated the image as PASS ({unavailable_services[0]} unavailable)."
                else:  # len(available_services) == 1
                    description = f"The only available QC tool ({available_services[0]}) rated " + \
                        "the image as PASS (others unavailable)."
                
                # Single image PASS: no deletion needed
                urls_to_delete = []
            else:
                ensemble_rating = EnsembleQualityRating.FAIL
                
                # Identify which tools failed (excluding unavailable ones)
                failed_tools = []
                if gpt_rating != "PASS" and not gpt_unavailable:
                    failed_tools.append("GPT")
                if claude_rating != "PASS" and not claude_unavailable:
                    failed_tools.append("Claude")
                if gemini_rating != "PASS" and not gemini_unavailable:
                    failed_tools.append("Gemini")
                
                # Generate description based on availability
                if available_count == 0:
                    description = "Ensemble FAIL: All QC services are unavailable."
                elif len(failed_tools) == 0:
                    # This shouldn't happen but just in case
                    description = "Ensemble FAIL: Unexpected error in rating evaluation."
                else:
                    available_services = []
                    if not gpt_unavailable:
                        available_services.append("GPT")
                    if not claude_unavailable:
                        available_services.append("Claude")
                    if not gemini_unavailable:
                        available_services.append("Gemini")
                    
                    unavailable_services = [svc for svc in ["GPT", "Claude", "Gemini"] \
                        if svc not in available_services]
                    
                    if len(unavailable_services) == 0:
                        description = f"Ensemble FAIL: {', '.join(failed_tools)} did not rate " + \
                            "the image as PASS. All three tools must agree for a PASS rating."
                    else:
                        description = f"Ensemble FAIL: {', '.join(failed_tools)} did not rate " + \
                            f"the image as PASS ({', '.join(unavailable_services)} " + \
                            "unavailable). All available tools must agree for a PASS rating."
                
                # Single image FAIL: delete the failed image
                urls_to_delete = [single_url]
            
            result = EnsembleImageQualityResult(
                rating=ensemble_rating,
                description=description,
                gpt_image_qc_result=gpt_result,
                claude_image_qc_result=claude_result,
                gemini_image_qc_result=gemini_result
            )
            logger.info(
                f"Ensemble QC result: {result.rating.value}, description: {result.description}"
            )
            
            # Schedule cleanup of failed images
            delete_files_from_supabase(urls_to_delete, delay_seconds=5.0)
            
        else:
            # Multi-image: Use majority choice URL with sophisticated tie-breaking
            gpt_selected = gpt_result.get("selected_image_url") \
                if not gpt_unavailable else None
            claude_selected = claude_result.get("selected_image_url") \
                if not claude_unavailable else None
            gemini_selected = gemini_result.get("selected_image_url") \
                if not gemini_unavailable else None
            
            # Check if all available tools passed
            all_passed = gpt_rating == "PASS" and claude_rating == "PASS" \
                and gemini_rating == "PASS"
            
            # Convert to list if needed for deletion logic
            multi_image_urls = image_urls if isinstance(image_urls, list) else [image_urls]
            
            if all_passed:
                # Collect all non-None selected URLs
                selected_urls = [url for url in [gpt_selected, claude_selected, gemini_selected] \
                    if url is not None]
                
                if selected_urls:
                    # Handle cases based on service availability
                    if available_count == 1:
                        # Only one service available
                        if not gpt_unavailable:
                            selected_url = gpt_selected
                            description = "GPT QC tool rated images as PASS and selected: " + \
                                f"{selected_url} (Claude and Gemini unavailable)"
                        elif not claude_unavailable:
                            selected_url = claude_selected
                            description = "Claude QC tool rated images as PASS and selected: " + \
                                f"{selected_url} (GPT and Gemini unavailable)"
                        else:  # not gemini_unavailable
                            selected_url = gemini_selected
                            description = "Gemini QC tool rated images as PASS and selected: " + \
                                f"{selected_url} (GPT and Claude unavailable)"
                        
                        ensemble_rating = EnsembleQualityRating.PASS
                        urls_to_delete = [url for url in multi_image_urls if url != selected_url]
                    
                    elif available_count == 2:
                        # Two services available - use majority choice logic
                        available_selected_urls = [url for url in selected_urls if url is not None]
                        url_counts = Counter(available_selected_urls)
                        max_count = max(url_counts.values()) if url_counts else 0
                        
                        if max_count == 2:
                            # Two tools agree on the same URL
                            selected_url = url_counts.most_common(1)[0][0]
                            available_services = []
                            if not gpt_unavailable:
                                available_services.append("GPT")
                            if not claude_unavailable:
                                available_services.append("Claude")
                            if not gemini_unavailable:
                                available_services.append("Gemini")
                            unavailable_service = [svc for svc in ["GPT", "Claude", "Gemini"] \
                                if svc not in available_services][0]
                            
                            description = "Both available QC tools " + \
                                f"({', '.join(available_services)}) rated images as PASS and " + \
                                f"agreed on: {selected_url} ({unavailable_service} unavailable)"
                            ensemble_rating = EnsembleQualityRating.PASS
                            urls_to_delete = [url for url in multi_image_urls \
                                if url != selected_url]
                        else:
                            # Tools disagree - use sophisticated preference logic with 2 tools
                            # Get individual ratings from available tools
                            individual_ratings = {}
                            tool_selected = {}
                            
                            if not gpt_unavailable:
                                individual_ratings['gpt'] = gpt_result\
                                    .get("individual_image_ratings", {})
                                tool_selected['gpt'] = gpt_selected
                            if not claude_unavailable:
                                individual_ratings['claude'] = claude_result\
                                    .get("individual_image_ratings", {})
                                tool_selected['claude'] = claude_selected
                            if not gemini_unavailable:
                                individual_ratings['gemini'] = gemini_result\
                                    .get("individual_image_ratings", {})
                                tool_selected['gemini'] = gemini_selected
                            
                            # First priority: URLs where one tool picked as best AND 
                            # other tool rated PASS
                            preferred_urls = []
                            _ = list(tool_selected.keys())
                            
                            for tool1, selected1 in tool_selected.items():
                                if selected1:
                                    for tool2, ratings2 in individual_ratings.items():
                                        if tool1 != tool2 and ratings2.get(selected1) == "PASS":
                                            preferred_urls.append(selected1)
                            
                            preferred_urls = list(set(preferred_urls))  # Remove duplicates
                            
                            if preferred_urls:
                                selected_url = random.choice(preferred_urls)
                                tool_selections = [f"{tool.upper()}: {sel}" \
                                    for tool, sel in tool_selected.items() if sel]
                                description = "Both available QC tools rated images as PASS " + \
                                    "but selected different URLs " + \
                                    f"({', '.join(tool_selections)}). Chose {selected_url} as " + \
                                    "it was selected as best by one tool and rated PASS by the " + \
                                    "other tool."
                                ensemble_rating = EnsembleQualityRating.PASS
                                urls_to_delete = [url for url in multi_image_urls \
                                    if url != selected_url]
                            else:
                                # Second priority: other URLs that both tools rated PASS but
                                # neither picked as best
                                mutually_passed_urls = []
                                available_ratings = list(individual_ratings.values())
                                
                                for url in multi_image_urls:
                                    if all(ratings.get(url, "FAIL") == "PASS" \
                                        for ratings in available_ratings):
                                        mutually_passed_urls.append(url)
                                
                                # Remove the tools' selected URLs since they weren't mutually
                                # preferred
                                other_passed_urls = [url for url in mutually_passed_urls \
                                    if url not in tool_selected.values()]
                                
                                if other_passed_urls:
                                    selected_url = random.choice(other_passed_urls)
                                    tool_selections = [f"{tool.upper()}: {sel}" \
                                        for tool, sel in tool_selected.items() if sel]
                                    description = "Both available QC tools rated images as " + \
                                        "PASS but selected different URLs " + \
                                        f"({', '.join(tool_selections)}). Neither tool's " + \
                                        "selection was rated PASS by the other, so chose " + \
                                        f"{selected_url} from other mutually passed images."
                                    ensemble_rating = EnsembleQualityRating.PASS
                                    urls_to_delete = [url for url in multi_image_urls \
                                        if url != selected_url]
                                else:
                                    # No image was rated PASS by both tools - treat as failure
                                    ensemble_rating = EnsembleQualityRating.FAIL
                                    selected_url = None
                                    tool_selections = [f"{tool.upper()}: {sel}" \
                                        for tool, sel in tool_selected.items() if sel]
                                    description = "Both available QC tools rated images as " + \
                                        "PASS but selected different URLs " + \
                                        f"({', '.join(tool_selections)}). However, no image " + \
                                        "was rated PASS by both tools individually, so " + \
                                        "treating as FAIL."
                                    urls_to_delete = multi_image_urls[:]
                    
                    else:  # available_count == 3
                        # All three tools available - use sophisticated 3-way logic
                        url_counts = Counter(selected_urls)
                        max_count = max(url_counts.values())
                        
                        if max_count == 3:
                            # All three tools agree
                            selected_url = url_counts.most_common(1)[0][0]
                            description = "All three QC tools (GPT, Claude, Gemini) rated " + \
                                f"images as PASS and unanimously selected: {selected_url}"
                            ensemble_rating = EnsembleQualityRating.PASS
                            urls_to_delete = [url for url in multi_image_urls \
                                if url != selected_url]
                        elif max_count == 2:
                            # Two tools agree, one disagrees - use majority choice
                            selected_url = url_counts.most_common(1)[0][0]
                            
                            # Find which tools agreed and which disagreed
                            agreeing_tools = []
                            disagreeing_tool = None
                            disagreeing_url = None
                            
                            if gpt_selected == selected_url:
                                agreeing_tools.append("GPT")
                            else:
                                disagreeing_tool = "GPT"
                                disagreeing_url = gpt_selected
                            
                            if claude_selected == selected_url:
                                agreeing_tools.append("Claude")
                            else:
                                disagreeing_tool = "Claude"
                                disagreeing_url = claude_selected
                            
                            if gemini_selected == selected_url:
                                agreeing_tools.append("Gemini")
                            else:
                                disagreeing_tool = "Gemini" 
                                disagreeing_url = gemini_selected
                            
                            description = "All three QC tools rated images as PASS. " + \
                                f"{', '.join(agreeing_tools)} selected {selected_url} while " + \
                                f"{disagreeing_tool} selected {disagreeing_url}. Using " + \
                                f"majority choice: {selected_url}"
                            ensemble_rating = EnsembleQualityRating.PASS
                            urls_to_delete = [url for url in multi_image_urls \
                                if url != selected_url]
                        else:
                            # All three tools disagree - use sophisticated preference logic
                            gpt_individual_ratings = gpt_result.get("individual_image_ratings", {})
                            claude_individual_ratings = claude_result.\
                                get("individual_image_ratings", {})
                            gemini_individual_ratings = gemini_result.\
                                get("individual_image_ratings", {})
                            
                            # First priority: URLs where one tool picked as best AND majority of
                            # other tools rated PASS
                            preferred_urls = []
                            
                            # Check GPT's selection
                            if gpt_selected and sum(1 for ratings in [claude_individual_ratings,
                                gemini_individual_ratings] \
                                if ratings.get(gpt_selected) == "PASS") >= 1:
                                preferred_urls.append(gpt_selected)
                            
                            # Check Claude's selection
                            if claude_selected and sum(1 for ratings in [gpt_individual_ratings,
                                gemini_individual_ratings] \
                                if ratings.get(claude_selected) == "PASS") >= 1:
                                preferred_urls.append(claude_selected)
                            
                            # Check Gemini's selection
                            if gemini_selected and sum(1 for ratings in [gpt_individual_ratings,
                                claude_individual_ratings] \
                                if ratings.get(gemini_selected) == "PASS") >= 1:
                                preferred_urls.append(gemini_selected)
                            
                            preferred_urls = list(set(preferred_urls))  # Remove duplicates
                            
                            if preferred_urls:
                                selected_url = random.choice(preferred_urls)
                                description = "All three QC tools rated images as PASS but " + \
                                    f"selected different URLs (GPT: {gpt_selected}, " + \
                                    f"Claude: {claude_selected}, Gemini: {gemini_selected}). " + \
                                    f"Chose {selected_url} as it was selected as best by one " + \
                                    "tool and rated PASS by at least one other tool."
                                ensemble_rating = EnsembleQualityRating.PASS
                                urls_to_delete = [url for url in multi_image_urls \
                                    if url != selected_url]
                            else:
                                # Second priority: URLs that majority of tools rated PASS (even if
                                # not selected as best)
                                majority_passed_urls = []
                                for url in multi_image_urls:
                                    pass_count = sum(1 for ratings in [gpt_individual_ratings,
                                        claude_individual_ratings, gemini_individual_ratings] \
                                        if ratings.get(url, "FAIL") == "PASS")
                                    if pass_count >= 2:  # Majority
                                        majority_passed_urls.append(url)
                                
                                # Remove the tools' selected URLs since they weren't preferred
                                other_passed_urls = [url for url in majority_passed_urls \
                                    if url not in [gpt_selected, claude_selected, gemini_selected]]
                                
                                if other_passed_urls:
                                    selected_url = random.choice(other_passed_urls)
                                    description = "All three QC tools rated images as PASS but " + \
                                        f"selected different URLs (GPT: {gpt_selected}, " + \
                                        f"Claude: {claude_selected}, " + \
                                        f"Gemini: {gemini_selected}). None of their selections " + \
                                        f"were rated PASS by others, so chose {selected_url} " + \
                                        "from other images rated PASS by majority."
                                    ensemble_rating = EnsembleQualityRating.PASS
                                    urls_to_delete = [url for url in multi_image_urls \
                                        if url != selected_url]
                                else:
                                    # No image was rated PASS by majority - treat as failure
                                    ensemble_rating = EnsembleQualityRating.FAIL
                                    selected_url = None
                                    description = "All three QC tools rated images as PASS but " + \
                                        f"selected different URLs (GPT: {gpt_selected}, " + \
                                        f"Claude: {claude_selected}, " + \
                                        f"Gemini: {gemini_selected}). However, no image was " + \
                                        "rated PASS by majority of tools individually, so " + \
                                        "treating as FAIL."
                                    urls_to_delete = multi_image_urls[:]
                else:
                    # All tools passed but none selected a URL (shouldn't happen in normal
                    # operation)
                    ensemble_rating = EnsembleQualityRating.FAIL
                    selected_url = None
                    description = "Ensemble FAIL: All available tools rated images as PASS but " + \
                        "none selected a URL."
                    # Delete all images since none were good enough
                    urls_to_delete = multi_image_urls[:]
            else:
                # Not all available tools passed
                ensemble_rating = EnsembleQualityRating.FAIL
                selected_url = None
                
                # Generate failure description based on availability
                if available_count == 0:
                    description = "Ensemble FAIL: All QC services are unavailable."
                else:
                    # Identify which tools failed (excluding unavailable ones)
                    failed_tools = []
                    if gpt_rating != "PASS" and not gpt_unavailable:
                        failed_tools.append("GPT")
                    if claude_rating != "PASS" and not claude_unavailable:
                        failed_tools.append("Claude")
                    if gemini_rating != "PASS" and not gemini_unavailable:
                        failed_tools.append("Gemini")
                    
                    # Generate available and unavailable service lists
                    available_services = []
                    if not gpt_unavailable:
                        available_services.append("GPT")
                    if not claude_unavailable:
                        available_services.append("Claude")
                    if not gemini_unavailable:
                        available_services.append("Gemini")
                    
                    unavailable_services = [svc for svc in ["GPT", "Claude", "Gemini"] \
                        if svc not in available_services]
                    
                    if len(unavailable_services) == 0:
                        description = f"Ensemble FAIL: {', '.join(failed_tools)} did not rate " + \
                            "images as PASS. All three tools must agree for a PASS rating."
                    elif len(unavailable_services) == 1:
                        description = f"Ensemble FAIL: {', '.join(failed_tools)} did not rate " + \
                            f"images as PASS ({unavailable_services[0]} unavailable). All " + \
                            "available tools must agree for a PASS rating."
                    elif len(unavailable_services) == 2:
                        description = f"Ensemble FAIL: {', '.join(failed_tools)} did not rate " + \
                            f"images as PASS ({', '.join(unavailable_services)} unavailable). " + \
                            "The only available tool must rate PASS for a PASS rating."
                    
                # Multi-image FAIL: delete all images since none were good enough
                urls_to_delete = multi_image_urls[:]
            
            result = EnsembleImageQualityResult(
                rating=ensemble_rating,
                description=description,
                selected_image_url=selected_url,
                gpt_image_qc_result=gpt_result,
                claude_image_qc_result=claude_result,
                gemini_image_qc_result=gemini_result
            )
            logger.info(
                f"Ensemble QC result: {result.rating.value}, "
                f"selected_image_url: {result.selected_image_url}, "
                f"description: {result.description}"
            )
            
            # Schedule cleanup of unselected/failed images
            delete_files_from_supabase(urls_to_delete, delay_seconds=5.0)
        
        return result.model_dump_json(indent=2)


def generate_image_quality_checker_ensemble_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the ensemble image quality checker tool specification and function."""
    
    checker = EnsembleImageQualityChecker()
    
    async def image_quality_check_function(image_urls: Union[str, List[str]],
    expected_description: str, educational_context: str, question_prompt: str = None) -> str:
        """Check if image(s) accurately depict the expected content and meet quality standards
        using Claude and Gemini in parallel."""
        return await checker.check_image_quality(image_urls, expected_description,
            educational_context, question_prompt=question_prompt)
    
    spec = {
        "type": "function",
        "name": "check_image_quality",
        "description": "Evaluate whether image(s) accurately depict expected content and meet "
        "quality standards using an ensemble of two AI models (Claude and Gemini) for high "
        "reliability. For single images, returns PASS only if both models agree. For multiple "
        "images, returns PASS if both models rate PASS, then selects URL by consensus or random "
        "choice if they disagree.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_urls": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Either a single image URL (string) or a list of image URLs "
                    "to analyze and evaluate for quality and accuracy."
                },
                "expected_description": {
                    "type": "string", 
                    "description": "Description of what the image is supposed to depict or show, "
                    "focused on a precise description of all objects in the image that a student "
                    "may need to identify (including counts of these objects). Don't include "
                    "details that are not relevant to what the student is supposed to observe in "
                    "the image."
                },
                "educational_context": {
                    "type": "string",
                    "description": "The educational context of the image. This will be used to "
                    "verify the image is appropriate for a typical student in the target grade "
                    "trying to learn the material."
                },
                "question_prompt": {
                    "type": "string",
                    "description": "The prompt of the question that the image is associated with, "
                    "if any. This will be used to verify the image is appropriate for the question."
                }
            },
            "required": ["image_urls", "expected_description", "educational_context",
                "question_prompt"]
        }
    }
    
    return spec, image_quality_check_function
