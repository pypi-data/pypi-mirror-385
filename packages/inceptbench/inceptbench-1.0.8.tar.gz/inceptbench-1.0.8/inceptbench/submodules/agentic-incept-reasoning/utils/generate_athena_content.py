#!/usr/bin/env python3
"""
Athena Content Generation Pipeline

This script generates educational content using the production API, evaluates it for quality,
converts to structured Athena format, and uploads to the database.

Usage:
    python generate_athena_content.py <curriculum_tsv_path> <num_content> [--verbose] [--content-type question|teach]
"""

import argparse
import csv
import json
import logging
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
from athena_uploader import AthenaUploader

TEACH_CONTENT = "teach"
QUESTION_CONTENT = "question"
CONTENT_TYPES = {
    TEACH_CONTENT: "cbf38842-1d4a-11f0-85fd-0eb28d3c3f3f",
    QUESTION_CONTENT: "c5e41b97-1ba4-11f0-85fd-0eb28d3c3f3f"
}

EASY_DIFFICULTY = "easy"
MEDIUM_DIFFICULTY = "medium"
HARD_DIFFICULTY = "hard"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Suppress httpx HTTP request logs to reduce clutter
logging.getLogger("httpx").setLevel(logging.WARNING)

API_BASE_URL = "https://inceptapi.rp.devfactory.com/api"
# API_BASE_URL = "http://localhost:8000"

@dataclass
class CurriculumRow:
    """Represents a row from the curriculum TSV."""
    grade: str
    subject: str
    unit: str
    cluster: str
    standard: str
    standard_description: str
    standard_extended_id: str  # Informational only
    content_generator_config_id: str  # Set based on content type, used for Athena uploader
    standard_id: str  # Used for Athena uploader

@dataclass
class GenerationTask:
    """Represents a single content generation task."""
    curriculum: CurriculumRow
    content_num: int
    difficulty: Optional[str] = None  # For questions: "easy", "medium", "hard"

@dataclass
class StandardTask:
    """Represents all content generation tasks for a single standard."""
    curriculum: CurriculumRow
    num_content: int
    content_type: str

@dataclass
class TaskResult:
    """Represents the result of a generation task."""
    task: GenerationTask
    success: bool
    error_message: Optional[str] = None
    attempts: int = 0
    markdown_content: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None
    athena_content: Optional[Dict[str, Any]] = None
    conversation_context: Optional[List[str]] = None  # Track previous content for variety

@dataclass
class StandardResult:
    """Represents the results of all content generation for a single standard."""
    standard_task: StandardTask
    task_results: List[TaskResult]
    success: bool
    error_message: Optional[str] = None

def get_grade_name_from_number(grade_number: str) -> str:
    """Get the grade name from the grade number."""
    grade_number = grade_number.strip()
    if grade_number == "K" or grade_number == "0":
        return "Kindergarten"
    elif grade_number == "1":
        return "1st Grade"
    elif grade_number == "2":
        return "2nd Grade"
    elif grade_number == "3":
        return "3rd Grade"
    elif grade_number == "4":
        return "4th Grade"
    elif grade_number == "5":
        return "5th Grade"
    elif grade_number == "6":
        return "6th Grade"
    elif grade_number == "7":
        return "7th Grade"
    elif grade_number == "8":
        return "8th Grade"
    elif grade_number == "9":
        return "9th Grade"
    elif grade_number == "10":
        return "10th Grade"
    elif grade_number == "11":
        return "11th Grade"
    elif grade_number == "12":
        return "12th Grade"
    else:
        return grade_number

def get_content_generator_config_id(content_type: str) -> str:
    """Get the content generator config ID based on content type."""
    if content_type in CONTENT_TYPES:
        return CONTENT_TYPES[content_type]
    else:
        raise ValueError(f"Invalid content type: {content_type}")

def distribute_difficulties(total_count: int) -> List[str]:
    """
    Distribute difficulties across the requested number of questions.
    
    Logic: n/3 each of easy, medium, hard, with remainder going to medium.
    
    Examples:
    - 10 questions: 3 easy, 4 medium, 3 hard  
    - 11 questions: 3 easy, 5 medium, 3 hard
    - 12 questions: 4 easy, 4 medium, 4 hard
    
    Parameters
    ----------
    total_count : int
        Total number of questions to generate
        
    Returns
    -------
    List[str]
        List of difficulty levels in order
    """
    base_count = total_count // 3
    remainder = total_count % 3
    
    easy_count = base_count
    medium_count = base_count + remainder  # Remainder goes to medium
    hard_count = base_count
    
    difficulties = []
    difficulties.extend([EASY_DIFFICULTY] * easy_count)
    difficulties.extend([MEDIUM_DIFFICULTY] * medium_count)
    difficulties.extend([HARD_DIFFICULTY] * hard_count)
    
    return difficulties

class ContentGenerator:
    """Handles the content generation pipeline."""
    
    def __init__(self, max_retries: int = 3, max_workers: int = 10, verbose: bool = False):
        self.max_retries = max_retries
        self.max_workers = max_workers
        self.verbose = verbose
        self.uploader = AthenaUploader()
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def _make_api_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, 
                         timeout: int = 600) -> requests.Response:
        """Make a request to the production API with retry logic."""
        url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                if self.verbose:
                    logger.debug(f"API {method} to {endpoint} (attempt {attempt + 1}/{self.max_retries})")
                
                if method.upper() == "POST":
                    response = requests.post(url, json=data, timeout=timeout)
                else:
                    response = requests.get(url, params=data, timeout=timeout)
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    backoff_time = min(2 ** attempt, 10)
                    logger.warning(f"API request failed (attempt {attempt + 1}), retrying in {backoff_time}s: {str(e)}")
                    time.sleep(backoff_time)
                else:
                    logger.error(f"API request failed after {self.max_retries} attempts: {str(e)}")
                    raise
    
    def _generate_prompt(self, curriculum: CurriculumRow, content_type: str, 
                        difficulty: Optional[str] = None, conversation_context: List[str] = None) -> str:
        """Generate a prompt that includes conversation context for variety."""
        grade_name = get_grade_name_from_number(curriculum.grade)
        # Build the list of curriculum elements, excluding empty standard
        curriculum_elements = [curriculum.unit, curriculum.cluster]
        
        # Only include standard if it's not empty
        if curriculum.standard and curriculum.standard.strip():
            curriculum_elements.append(curriculum.standard)
        
        curriculum_elements.append(curriculum.standard_description)
        
        # Join elements with commas
        curriculum_text = ", ".join(curriculum_elements)

        # Build context string if we have previous content
        context_prefix = ""
        if conversation_context and len(conversation_context) > 0:
            context_prefix = f"You will be creating a new question or teaching explanation for this concept in {grade_name} {curriculum.subject}: {curriculum_text}. "
            context_prefix += "The content you create should be different from all the previous ones you have made in how it tests mastery of the concept, the scenario it describes, and numerical and other details, yet it should still follow all guidelines. "
            context_prefix += "\n\n" + "="*50 + "\n\n"
            context_prefix += "Previously generated content for this concept:\n"
            for i, prev_content in enumerate(conversation_context, 1):
                # Truncate at the answer information separator to keep only the question part
                separator = "**Answer Information**"
                truncate_index = prev_content.find(separator)
                if truncate_index != -1:
                    # Found the separator, truncate just before it
                    truncated_content = prev_content[:truncate_index].strip()
                else:
                    # Fallback to full content if separator not found
                    truncated_content = prev_content
                context_prefix += f"\n--- Previous Content {i} ---\n{truncated_content}\n"
            context_prefix += "\n" + "="*50 + "\n\n"

        # For questions, include difficulty specification
        if content_type == QUESTION_CONTENT:
            difficulty_text = f"{difficulty} difficulty " if difficulty else ""
            if conversation_context:
                # Follow-up prompt for maintaining variety
                main_prompt = f"Give me another {difficulty_text}multiple-choice question with an image stimulus for the same concept. It should be different from all the previous ones you have made in how it tests mastery of the concept, the scenario it describes, and numerical and other details, yet it should still follow all guidelines. As a reminder, the concept is {grade_name} {curriculum.subject}: {curriculum_text}"
            else:
                # Initial prompt
                main_prompt = f"Give me a {difficulty_text}multiple-choice question with an image stimulus for {grade_name} {curriculum.subject}: {curriculum_text}"

        elif content_type == TEACH_CONTENT:
            if conversation_context:
                # Follow-up prompt for teaching content
                main_prompt = f"Give me another teaching explanation of the same concept that's different from all the previous ones you have made. As a reminder, the concept is {grade_name} {curriculum.subject}: {curriculum_text}"
            else:
                # Initial prompt
                main_prompt = f"Teach me about the following concept in {grade_name} {curriculum.subject}: {curriculum_text}"
        else:
            raise ValueError(f"Invalid content type: {content_type}")
        
        # Combine context and main prompt
        full_prompt = context_prefix + main_prompt
        
        return full_prompt
    
    def _generate_content(self, prompt: str) -> str:
        """Generate content using the existing API format.
        
        Returns:
            str: The generated content
        """
        data = {
            "prompt": prompt,
            "model": "incept"
        }
        
        # Make streaming request
        url = f"{API_BASE_URL}/respond"
        final_content = ""
        
        for attempt in range(self.max_retries):
            try:
                if self.verbose:
                    logger.debug(f"API POST to /respond (attempt {attempt + 1}/{self.max_retries})")
                    logger.debug(f"Prompt length: {len(prompt)} characters")
                
                response = requests.post(url, json=data, timeout=600, stream=True)
                response.raise_for_status()
                
                # Process the SSE stream line by line
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        # Handle both SSE format ("data: {...}") and direct JSON format ("{...}")
                        json_data = None
                        if line.startswith('data: '):
                            # SSE format
                            json_data = line[6:]  # Remove 'data: ' prefix
                        elif line.strip().startswith('{') and line.strip().endswith('}'):
                            # Direct JSON format
                            json_data = line.strip()
                        
                        if json_data:
                            try:
                                event_data = json.loads(json_data)
                                if self.verbose:
                                    # Filter out verbose events to reduce log noise
                                    event_type = event_data.get('type', '')
                                    if event_type not in ('text_delta', 'reasoning_delta', 'response_delta'):
                                        logger.debug(f"Received event: {event_data}")
                                
                                event_type = event_data.get('type')
                                if event_type == 'response_final':
                                    event_payload = event_data.get('data', {})
                                    final_content = event_payload.get('text', '')
                                    break
                                elif event_type == 'error':
                                    error_payload = event_data.get('data', {})
                                    error_msg = error_payload.get('text', 'Unknown error')
                                    error_type = error_payload.get('error_type', 'Unknown error type')
                                    raise ValueError(f"API error ({error_type}): {error_msg}")
                            except json.JSONDecodeError:
                                # Skip malformed lines
                                if self.verbose:
                                    logger.debug(f"Skipping malformed JSON line: {line}")
                                continue
                
                if final_content:
                    break
                elif attempt < self.max_retries - 1:
                    backoff_time = min(2 ** attempt, 10)
                    logger.warning(f"No final content found (attempt {attempt + 1}), retrying in {backoff_time}s")
                    time.sleep(backoff_time)
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    backoff_time = min(2 ** attempt, 10)
                    logger.warning(f"API request failed (attempt {attempt + 1}), retrying in {backoff_time}s: {str(e)}")
                    time.sleep(backoff_time)
                else:
                    logger.error(f"API request failed after {self.max_retries} attempts: {str(e)}")
                    raise
        
        if not final_content:
            raise ValueError("No final content found in API response after all retries")
        
        return final_content
    
    def _evaluate_content(self, content: str) -> Dict[str, Any]:
        """Evaluate content using the production API."""
        data = {"content": content}
        response = self._make_api_request("POST", "/evaluate", data)
        return response.json()["evaluation"]
    
    def _is_evaluation_acceptable(self, evaluation: Dict[str, Any], retry_count: int, task: GenerationTask, content_type: str) -> bool:
        """Check if evaluation meets quality standards."""
        try:
            # Parse evaluation if it's a string
            if isinstance(evaluation, str):
                evaluation = json.loads(evaluation)
            
            # Check overall rating
            overall_rating = evaluation.get("overall", {}).get("result", "")
            overall_acceptability = ["SUPERIOR", "ACCEPTABLE"] if retry_count < 2 and content_type == QUESTION_CONTENT else ["SUPERIOR", "ACCEPTABLE"]
            if overall_rating not in overall_acceptability:
                return False
            
            if overall_rating == "ACCEPTABLE":
                logger.warning(f"Allowing ACCEPTABLE content for {task.curriculum.standard} "
                           f"content {task.content_num} on retry {retry_count}")
            
            if content_type == TEACH_CONTENT:
                # allow SUPERIOR teach content always, or ACCEPTABLE teach content on retry 2+
                if overall_rating == "SUPERIOR":
                    cyan_start = "\033[96m"
                    color_end = "\033[0m"
                    logger.info(f"{cyan_start}SUPERIOR{color_end} teaching content for {task.curriculum.standard} "
                                f"content {task.content_num} on retry {retry_count}")
                return overall_rating in overall_acceptability and \
                    evaluation.get("accuracy_and_rigor", {}).get("result", "FAIL") == "PASS"

            # Check all criteria for FAIL
            criteria_fields = [
                "curriculum_alignment", "cognitive_demand", "accuracy_and_rigor",
                "variety", "image_quality", "reveals_misconceptions",
                "question_type_appropriateness", "engagement_and_relevance",
                "instructional_support", "clarity_and_accessibility"
            ]
            
            for field in criteria_fields:
                if field in evaluation:
                    result = evaluation[field].get("result", "FAIL")
                    if result == "FAIL":
                        return False
            if overall_rating == "SUPERIOR":
                cyan_start = "\033[96m"
                color_end = "\033[0m"
                logger.info(f"{cyan_start}SUPERIOR{color_end} question content for {task.curriculum.standard} "
                            f"content {task.content_num} on retry {retry_count}")
            return True
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.error(f"Error parsing evaluation: {str(e)}")
            return False
    
    def _convert_to_athena(self, content: str) -> Dict[str, Any]:
        """Convert content to Athena format using the production API."""
        data = {"content": content}
        response = self._make_api_request("POST", "/convert-to-athena", data)
        return response.json()["structured_content"]
    
    def _upload_to_athena(self, athena_content: Dict[str, Any], curriculum: CurriculumRow, 
                         difficulty: Optional[str] = None) -> bool:
        """Upload content to Athena database."""
        return self.uploader.upload_content(athena_content, curriculum, difficulty)
    
    def _process_single_task(self, task: GenerationTask, content_type: str, 
                           conversation_context: List[str] = None) -> TaskResult:
        """Process a single content generation task."""
        result = TaskResult(task=task, success=False)
        
        difficulty_text = f" ({task.difficulty} difficulty)" if task.difficulty else ""
        logger.info(f"Processing {get_grade_name_from_number(task.curriculum.grade)} {task.curriculum.subject} "
                   f"content {task.content_num}{difficulty_text}: {task.curriculum.standard}")
        
        for attempt in range(self.max_retries):
            result.attempts = attempt + 1
            
            try:
                # Step 1: Generate prompt with conversation context
                full_prompt = self._generate_prompt(task.curriculum, content_type, task.difficulty, conversation_context)
                
                if self.verbose:
                    logger.debug(f"Generated prompt length: {len(full_prompt)} characters")
                    if conversation_context:
                        logger.debug(f"Previous context includes {len(conversation_context)} content pieces")
                
                # Step 2: Generate content using prompt-based approach
                context_length = len(conversation_context) if conversation_context else 0
                logger.info(f"Content {task.content_num} attempt {attempt + 1}: generating with context from {context_length} previous pieces")
                    
                markdown_content = self._generate_content(full_prompt)
                result.markdown_content = markdown_content
                
                # Log snippet of content to check for variety
                content_snippet = markdown_content[:200].replace('\n', ' ')
                logger.info(f"Content {task.content_num} snippet: {content_snippet}...")
                
                if self.verbose:
                    logger.debug(f"Generated content: {markdown_content[:100]}...")
                
                # Step 3: Evaluate content
                if self.verbose:
                    logger.debug(f"Evaluating content (attempt {attempt + 1})")
                    
                evaluation = self._evaluate_content(markdown_content)
                result.evaluation = evaluation
                
                # Step 4: Check if evaluation is acceptable
                if not self._is_evaluation_acceptable(evaluation, attempt, task, content_type):
                    logger.warning(f"Content {task.content_num} attempt {attempt + 1}: evaluation failed")
                    if attempt < self.max_retries - 1:
                        backoff_time = min(2 ** attempt, 10)
                        logger.warning(f"Content quality insufficient for {task.curriculum.standard} content {task.content_num} (attempt {attempt + 1}), "
                                     f"retrying in {backoff_time}s")
                        if self.verbose:
                            logger.warning(f"Evaluation: {evaluation}")
                        time.sleep(backoff_time)
                        continue
                    else:
                        result.error_message = "Content quality insufficient after max retries"
                        logger.error(f"Failed {task.curriculum.standard} content {task.content_num}: "
                                   f"{result.error_message}")
                        if self.verbose:
                            logger.error(f"Final Evaluation: {evaluation}")
                        return result
                
                logger.info(f"Content quality check passed for {task.curriculum.standard} "
                           f"content {task.content_num}")
                
                # Step 5 & 6: Convert to Athena format and upload (with retries)
                upload_success = False
                for upload_attempt in range(self.max_retries):
                    try:
                        if self.verbose:
                            logger.debug(f"Converting to Athena format (upload attempt {upload_attempt + 1})")

                        athena_content = self._convert_to_athena(markdown_content)
                        result.athena_content = athena_content

                        if self.verbose:
                            logger.debug(f"Uploading to Athena database (upload attempt {upload_attempt + 1})")

                        upload_success = self._upload_to_athena(athena_content, task.curriculum, task.difficulty)

                        if upload_success:
                            difficulty_text = f" ({task.difficulty} difficulty)" if task.difficulty else ""
                            logger.info(f"Successfully completed {task.curriculum.standard} "
                                       f"content {task.content_num}{difficulty_text}")
                            result.success = True
                            
                            # Only add content to conversation context after successful completion
                            if conversation_context:
                                updated_context = conversation_context.copy()
                            else:
                                updated_context = []
                            updated_context.append(markdown_content)
                            result.conversation_context = updated_context
                            
                            return result
                        elif upload_attempt < self.max_retries - 1:
                            backoff_time = min(2 ** upload_attempt, 10)
                            logger.warning(f"Upload failed for {task.curriculum.standard} content {task.content_num} "
                                         f"(upload attempt {upload_attempt + 1}), retrying in {backoff_time}s")
                            time.sleep(backoff_time)
                        else:
                            result.error_message = "Failed to upload to Athena database after max retries"
                            logger.error(f"Upload failed for {task.curriculum.standard} "
                                       f"content {task.content_num} after {self.max_retries} attempts")
                            return result

                    except Exception as e:
                        if upload_attempt < self.max_retries - 1:
                            backoff_time = min(2 ** upload_attempt, 10)
                            logger.warning(f"Error during Athena conversion/upload for {task.curriculum.standard} "
                                         f"content {task.content_num} (upload attempt {upload_attempt + 1}): {str(e)}, "
                                         f"retrying in {backoff_time}s")
                            time.sleep(backoff_time)
                        else:
                            result.error_message = f"Error during Athena conversion/upload: {str(e)}"
                            logger.error(f"Athena conversion/upload failed for {task.curriculum.standard} "
                                       f"content {task.content_num} after {self.max_retries} attempts: {str(e)}")
                            return result
                
            except Exception as e:
                error_msg = f"Error in attempt {attempt + 1}: {str(e)}"
                
                if attempt < self.max_retries - 1:
                    backoff_time = min(2 ** attempt, 10)
                    logger.warning(f"{error_msg}, retrying in {backoff_time}s")
                    time.sleep(backoff_time)
                else:
                    result.error_message = error_msg
                    logger.error(f"Failed {task.curriculum.standard} content {task.content_num}: "
                               f"{error_msg}")
        
        return result
    
    def _process_standard_task(self, standard_task: StandardTask) -> StandardResult:
        """Process all content generation for a single standard serially to maintain conversation context."""
        task_results = []
        conversation_context = None  # Start with no conversation context
        success_count = 0
        
        logger.info(f"Processing standard: {get_grade_name_from_number(standard_task.curriculum.grade)} {standard_task.curriculum.subject} - "
                   f"{standard_task.curriculum.standard} ({standard_task.num_content} content pieces)")
        
        # Distribute difficulties for questions
        difficulties = []
        if standard_task.content_type == QUESTION_CONTENT:
            difficulties = distribute_difficulties(standard_task.num_content)
            logger.info(f"Difficulty distribution for {standard_task.curriculum.standard}: {difficulties}")
        
        for content_num in range(1, standard_task.num_content + 1):
            # Assign difficulty for questions
            difficulty = difficulties[content_num - 1] if difficulties else None
            
            # Create individual task for this content piece
            task = GenerationTask(
                curriculum=standard_task.curriculum, 
                content_num=content_num,
                difficulty=difficulty
            )
            
            # Log conversation context before processing
            context_length = len(conversation_context) if conversation_context else 0
            logger.info(f"Processing content {content_num} with conversation context: {context_length} previous content pieces")
            
            # Process the task, passing the conversation context for variety
            result = self._process_single_task(task, standard_task.content_type, conversation_context)
            task_results.append(result)
            
            if result.success:
                success_count += 1
                # Update conversation context for the next content generation in this standard
                if hasattr(result, 'conversation_context') and result.conversation_context:
                    logger.info(f"Content {content_num} succeeded - updating conversation context")
                    logger.info(f"  Previous context: {len(conversation_context) if conversation_context else 0} pieces")
                    logger.info(f"  New context: {len(result.conversation_context)} pieces")
                    conversation_context = result.conversation_context
                else:
                    logger.error(f"CRITICAL: Content {content_num} succeeded but no conversation context returned!")
            else:
                logger.warning(f"Content {content_num} failed - conversation context preserved")
                logger.warning(f"  Keeping context: {len(conversation_context) if conversation_context else 0} pieces")
        
        # Determine overall success
        overall_success = success_count > 0  # At least one piece of content succeeded
        error_message = None
        if success_count == 0:
            error_message = "Failed to generate any content for this standard"
        elif success_count < standard_task.num_content:
            error_message = f"Generated {success_count}/{standard_task.num_content} content pieces"
        
        logger.info(f"Completed standard {standard_task.curriculum.standard}: "
                   f"{success_count}/{standard_task.num_content} content pieces successful")
        
        return StandardResult(
            standard_task=standard_task,
            task_results=task_results,
            success=overall_success,
            error_message=error_message
        )
    
    def load_curriculum(self, csv_path: str, content_type: str) -> List[CurriculumRow]:
        """Load curriculum data from TSV file."""
        curriculum_rows = []
        
        # Get the appropriate content generator config ID for this content type
        config_id = get_content_generator_config_id(content_type)
        
        with open(csv_path, 'r', newline='', encoding='utf-8') as tsvfile:
            # Use tab delimiter for TSV files
            reader = csv.DictReader(tsvfile, delimiter='\t')
            
            for row in reader:
                # Clean up quoted values if present (remove surrounding quotes)
                cleaned_row = {}
                for key, value in row.items():
                    # Remove surrounding quotes if present
                    clean_key = key.strip().strip('"')
                    clean_value = value.strip().strip('"') if value else ''
                    cleaned_row[clean_key] = clean_value
                
                curriculum_row = CurriculumRow(
                    grade=cleaned_row['GRADE'],
                    subject=cleaned_row['SUBJECT'],
                    unit=cleaned_row['UNIT'],
                    cluster=cleaned_row['CLUSTER'],
                    standard=cleaned_row['STANDARD'],
                    standard_description=cleaned_row['STANDARD_DESCRIPTION'],
                    standard_extended_id=cleaned_row['STANDARD_EXTENDED_ID'],
                    content_generator_config_id=config_id,  # Set based on content type
                    standard_id=cleaned_row['STANDARD_ID']
                )
                curriculum_rows.append(curriculum_row)
        
        logger.info(f"Loaded {len(curriculum_rows)} curriculum standards from {csv_path}")
        logger.info(f"Using content_generator_config_id: {config_id} for content type: {content_type}")
        return curriculum_rows
    
    def generate_content(self, curriculum_rows: List[CurriculumRow], 
                        num_content: int, content_type: str) -> List[TaskResult]:
        """Generate content for all curriculum rows with specified number of content.
        
        Content for each standard is generated serially to maintain conversation context,
        while different standards are processed in parallel.
        """
        
        # Create standard tasks (one per curriculum row)
        standard_tasks = []
        for curriculum in curriculum_rows:
            standard_task = StandardTask(
                curriculum=curriculum,
                num_content=num_content,
                content_type=content_type
            )
            standard_tasks.append(standard_task)
        
        total_standards = len(standard_tasks)
        total_content = total_standards * num_content
        logger.info(f"Starting generation of {total_content} contents across {total_standards} standards "
                   f"using {self.max_workers} workers")
        logger.info(f"Content within each standard will be generated serially for variety, "
                   f"standards will be processed in parallel")
        
        all_task_results = []
        completed_standards = 0
        
        # Process standards in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all standard tasks
            future_to_standard = {
                executor.submit(self._process_standard_task, standard_task): standard_task 
                for standard_task in standard_tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_standard):
                standard_result = future.result()
                completed_standards += 1
                
                # Add all individual task results to the main results list
                all_task_results.extend(standard_result.task_results)
                
                # Log standard completion (with cyan color for visibility)
                successful_content = len([r for r in standard_result.task_results if r.success])
                status = "SUCCESS" if successful_content == num_content else "FAILED"
                marker = "✓" if successful_content == num_content else "✗"
                # Use ANSI bright cyan color for SUCCESS completion messages
                cyan_start = "\033[96m"
                # Use ANSI bright red color for FAILED completion messages
                red_start = "\033[91m"
                # Reset color
                color_start = cyan_start if successful_content == num_content else red_start
                color_end = "\033[0m"
                logger.info(f"{color_start}{marker} Completed {completed_standards}/{total_standards} standards - "
                           f"Result: {status} for {standard_result.standard_task.curriculum.standard_id}; {standard_result.standard_task.curriculum.standard_extended_id}; {standard_result.standard_task.curriculum.standard}; {standard_result.standard_task.curriculum.standard_description}; "
                           f"({successful_content}/{num_content} content pieces successful){color_end}")
        
        return all_task_results
    
    def print_summary(self, results: List[TaskResult]):
        """Print a summary of generation results."""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print(f"\n{'='*60}")
        print(f"GENERATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total tasks: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        print(f"Success rate: {len(successful)/len(results)*100:.1f}%")
        
        # Show difficulty breakdown for questions
        question_results = [r for r in results if r.task.difficulty is not None]
        if question_results:
            print(f"\nDIFFICULTY BREAKDOWN (Questions):")
            print(f"{'-'*60}")
            for difficulty in [EASY_DIFFICULTY, MEDIUM_DIFFICULTY, HARD_DIFFICULTY]:
                difficulty_results = [r for r in question_results if r.task.difficulty == difficulty]
                if difficulty_results:
                    difficulty_successful = [r for r in difficulty_results if r.success]
                    success_rate = len(difficulty_successful) / len(difficulty_results) * 100
                    print(f"{difficulty.capitalize()}: {len(difficulty_successful)}/{len(difficulty_results)} "
                          f"({success_rate:.1f}% success rate)")
        
        if failed:
            print(f"\nFAILED TASKS:")
            print(f"{'-'*60}")
            for result in failed:
                difficulty_text = f" ({result.task.difficulty})" if result.task.difficulty else ""
                print(f"• {get_grade_name_from_number(result.task.curriculum.grade)} {result.task.curriculum.subject} "
                      f"C{result.task.content_num}{difficulty_text}: {result.task.curriculum.standard_id} {result.task.curriculum.standard_extended_id} {result.task.curriculum.standard_description}")
                print(f"  Error: {result.error_message}")
                print(f"  Attempts: {result.attempts}")
                print()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Athena educational content")
    parser.add_argument("curriculum_tsv", help="Path to curriculum TSV file")
    parser.add_argument("num_content", type=int, help="Number of content to generate per curriculum row")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--max-threads", "-t", type=int, default=10, help="Maximum number of worker threads")
    parser.add_argument("--max-retries", "-r", type=int, default=3, help="Maximum number of retries per task")
    parser.add_argument("--content-type", "-c", type=str, default=QUESTION_CONTENT, choices=[QUESTION_CONTENT, TEACH_CONTENT], help=f"Content type to generate ({QUESTION_CONTENT} or {TEACH_CONTENT})")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.curriculum_tsv).exists():
        logger.error(f"Curriculum TSV file not found: {args.curriculum_tsv}")
        return 1
    
    if args.num_content <= 0:
        logger.error("Number of content types must be greater than 0")
        return 1
    
    # Initialize generator
    generator = ContentGenerator(
        max_retries=args.max_retries,
        max_workers=args.max_threads,
        verbose=args.verbose
    )
    
    try:
        # Load curriculum
        curriculum_rows = generator.load_curriculum(args.curriculum_tsv, args.content_type)
        
        if not curriculum_rows:
            logger.error("No curriculum data found in TSV file")
            return 1
        
        # Generate content
        start_time = time.time()
        results = generator.generate_content(curriculum_rows, args.num_content, args.content_type)
        end_time = time.time()
        
        # Print summary
        generator.print_summary(results)
        
        print(f"\nTotal execution time: {end_time - start_time:.1f} seconds")
        
        # Return non-zero exit code if there were failures
        failed_count = len([r for r in results if not r.success])
        return 1 if failed_count > 0 else 0
        
    except KeyboardInterrupt:
        logger.info("Generation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 