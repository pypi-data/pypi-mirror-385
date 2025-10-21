from __future__ import annotations

import logging
from typing import Any, Callable, Dict

from edu_agents.athena import AMQMultipleChoice, AMQNumerical, CategorizedContent, ContentCategory
from edu_agents.core.api_key_manager import get_async_openai_client

logger = logging.getLogger(__name__)

class AMQConverter:
    """Converts markdown educational content to AMQ JSON format using OpenAI's structured
    outputs."""
    
    def __init__(self):
        self.client = get_async_openai_client(timeout=180.0)
    
    async def _classify_content(self, markdown_content: str) -> str:
        """
        Classify the content as MCQ or numerical answer question.

        Parameters
        ----------
        markdown_content : str
            Markdown formatted educational content

        Returns
        -------
        str
            The category name ("MCQ" or "NUMERICAL")
        """
        system_prompt = """You are an expert educational content classifier. Your task is to
classify the content into a category and return a specified category name.

The supported categories are:
- Multiple Choice Question: "MCQ" - Questions that provide multiple options to choose from
- Numerical Answer Question: "NUMERICAL" - Questions that require a numerical answer (no multiple
choice options)

Look for indicators like:
- MCQ: Has answer choices labeled with letters (A, B, C, D) or numbers, or explicit multiple choice
format
- NUMERICAL: Asks for a specific number, calculation result, or measurement without providing choice
options"""
        user_prompt = f"""Classify this markdown educational content:

{markdown_content}
"""

        response = await self.client.responses.parse(
            model="gpt-4o",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            text_format=CategorizedContent,
        )

        # Extract the parsed category from the response
        for output_item in response.output:
            if output_item.type == "message":
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        
                        # Return the category value from the parsed object
                        # Defensive check: ensure the value is not a coroutine
                        category = content_item.parsed.category.value
                        if hasattr(category, '__await__'):
                            category = await category
                        return category
        
        # Default to MCQ if classification fails
        logger.warning("Failed to classify content, defaulting to MCQ")
        return ContentCategory.MCQ.value
    
    async def convert_to_amq(self, markdown_content: str) -> str:
        """
        Convert markdown educational content to AMQ JSON format.
        
        Parameters
        ----------
        markdown_content : str
            Markdown formatted educational content
            
        Returns
        -------
        str
            JSON string conforming to the AMQ schema
        """
        logger.info("Converting content to AMQ JSON format")
        try:
            # Classify the content
            category = await self._classify_content(markdown_content)
            
            # Choose the appropriate schema
            if category == ContentCategory.MCQ.value:
                schema = AMQMultipleChoice
                system_prompt = """You are an expert educational content formatter. Your task is to
convert markdown-formatted educational content into AMQ (Auto-graded Multiple-choice Question) JSON
format for multiple choice questions.

Key requirements:
1. Parse the markdown content to extract the question (including any images!), answer options,
correct answer, and any other content you need.
2. The question field should contain ONLY the problem statement plus any images, WITHOUT answer
choices - the choices go in the separate "options" field.
3. The answer field should contain the correct answer as a plain text number only (never LaTeX
formatting). If the correct answer option does include LaTeX, convert it to plain text in the most
readable, natural way. Do not include object names (e.g., if the answer is "42 robots", the answer
field should be "42" instead) or units unless specifying the correct unit is critical to the
problem.
4. Rely on content you are creating to create your response as much as possible. Only create new
content if it is absolutely necessary and not already present.
5. Be very careful not to remove or change any critical aspects of the content (numbers, units,
etc.).
6. If the input question includes an image, ensure the image is included in the question field,
including any question text introducing the problem.
7. Ensure all fields are properly filled - no null values allowed.
8. Remove any answer option indicators (e.g., "A.", "(A)", "1:", etc.) from items in the "options"
array.
9. Ensure that the content of any fields named "answer" is IDENTICAL to the corresponding item in
the "options" array. A question validation process will check this later, and the question will be
rejected if this is not the case.
10. **CRITICAL**: Preserve ALL LaTeX formatting (enclosed in $...$ or $$...$$) and code without
modification in ALL fields EXCEPT any fields named "answer" and the items in the "options" array.
    - Note that the response has multiple layers of nested objects, and you should remove LaTeX from
    any fields named "answer" at any level of nesting, as well as the items in the "options" array.
    Do not remove LaTeX from any of the other fields like "question", "explanation", "content",
    "insights", etc.
    - For ONLY "answer" fields and the items in the "options" array, convert all LaTeX to plain text
    in the most common basic-keyboard-compatible format, because the user will be typing their
    answer on a keyboard and we will check what they type against the "answer" field. For example:
        - If an answer is "$frac{1}{2}$" or "½", the "answer" field should be "1/2" instead.
        - If an answer is "$x \leq 3$" or "x ≤ 3", the "answer" field should be "x <= 3" instead.
        - If an answer is "$5 \\times 5 = 25$", "5 × 5 = 25", or "5 * 5 = 25", the "answer" field
        should be "5 x 5 = 25" instead.
        - If an answer is "$5 \\div 5 = 1$" or "5 ÷ 5 = 1", the "answer" field should be "5 / 5 = 1"
        instead.
11. **CRITICAL**: For multiple choice questions, the "question" field contains ONLY the question
scenario and prompt. All answer choices go in the separate "options" array.
12. **VOICEOVER SCRIPTS**: Create audio-friendly scripts for all components in the voiceover_script
section:
    - question_script: Convert the question to natural speech, describing images and converting math
    to spoken form (e.g., "1/2" becomes "one-half", "x²" becomes "x squared", "≤" becomes "less than
    or equal to")
    - answer_choice_scripts: Convert each answer option to natural speech (e.g., "√9" becomes "the
    square root of 9")
    - explanation_step_scripts: Convert each step to natural speech with step numbers and
    mathematical expressions in spoken form
    - DO NOT give away the answer to a question in the question_script."""

            else:  # NUMERICAL
                schema = AMQNumerical
                system_prompt = """You are an expert educational content formatter. Your task is to
convert markdown-formatted educational content into AMQ (Auto-graded Multiple-choice Question) JSON
format for numerical answer questions.

Key requirements:
1. Parse the markdown content to extract the question (including any images!), correct numerical
answer, and any explanations.
2. The question field should contain ONLY the question scenario plus any images.
3. The answer field should contain the numerical answer as plain text (never LaTeX formatting). If
the correct answer option does include LaTeX, convert it to plain text in the most readable, natural
way.
4. Rely on content you are creating to create your response as much as possible. Only create new
content if it is absolutely necessary and not already present.
5. Be very careful not to remove or change any critical aspects of the content (numbers, units,
etc.).
6. If the input question includes an image, ensure the image is included in the question field,
including any question text introducing the problem.
7. Ensure all fields are properly filled - no null values allowed.
8. **CRITICAL**: Preserve ALL LaTeX formatting (enclosed in $...$ or $$...$$) and code without
modification in ALL fields EXCEPT any fields named "answer" and the items in the "options" array.
    - Note that the response has multiple layers of nested objects, and you should remove LaTeX from
    any fields named "answer" at any level of nesting, as well as the items in the "options" array.
    Do not remove LaTeX from any of the other fields like "question", "explanation", "content",
    "insights", etc.
    - For ONLY "answer" fields and the items in the "options" array, convert all LaTeX to plain text
    in the most common basic-keyboard-compatible format, because the user will be typing their
    answer on a keyboard and we will check what they type against the "answer" field. For example:
        - If an answer is "$frac{1}{2}$" or "½", the "answer" field should be "1/2" instead.
        - If an answer is "$x \\leq 3$" or "x ≤ 3", the "answer" field should be "x <= 3" instead.
        - If an answer is "$5 \\times 5 = 25$", "5 × 5 = 25", or "5 * 5 = 25", the "answer" field
        should be "5 x 5 = 25" instead.
        - If an answer is "$5 \\div 5 = 1$" or "5 ÷ 5 = 1", the "answer" field should be "5 / 5 = 1"
        instead.
9. **VOICEOVER SCRIPTS**: Create audio-friendly scripts for all components in the voiceover_script
section:
    - question_script: Convert the question to natural speech, describing images and converting math
    to spoken form (e.g., "1/2" becomes "one-half", "x²" becomes "x squared", "≤" becomes "less than
    or equal to")
    - answer_choice_scripts: Leave as null since this is a numerical question (not multiple choice)
    - explanation_step_scripts: Convert each step to natural speech with step numbers and
    mathematical expressions in spoken form"""
            user_prompt = f"""Convert this markdown educational content to AMQ JSON format:

{markdown_content}
"""

            # Use structured outputs with the appropriate schema
            response = await self.client.responses.parse(
                model="gpt-4o",
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                text_format=schema,
            )
            
            # Extract the structured response
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if (content_item.type == "output_text" and 
                            hasattr(content_item, "parsed") and 
                            content_item.parsed is not None):
                            
                            # Return the JSON string representation
                            return content_item.parsed.model_dump_json(indent=2, exclude_none=True)
                        elif (content_item.type == "output_text" and 
                              hasattr(content_item, "text")):
                            # Fallback to text if parsed object not available
                            # Defensive check: ensure text is not a coroutine
                            text_content = content_item.text
                            if hasattr(text_content, '__await__'):
                                text_content = await text_content
                            return text_content
            
            raise RuntimeError("No structured response found in API response")
            
        except Exception as e:
            error_message = f"Error converting content to AMQ format: {str(e)}"
            logger.error(error_message)
            raise RuntimeError(error_message) from e


def generate_amq_converter_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the AMQ converter tool specification and function."""
    
    converter = AMQConverter()
    
    async def amq_convert_function(content: str) -> str:
        """Convert educational content to AMQ JSON format."""
        return await converter.convert_to_amq(content)
    
    spec = {
        "type": "function",
        "name": "convert_to_amq",
        "description": (
            "Convert educational content to AMQ (Athena Mastery Quest) JSON format using OpenAI's "
            "structured outputs. This tool should be used to reformat the final response when "
            "amq_json_format is requested. The tool automatically detects whether the content is a "
            "multiple choice question or numerical answer question and formats accordingly."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": (
                        "The complete educational content (markdown format) to convert to AMQ "
                        "(Athena Mastery Quest) JSON format. This should include the question, "
                        "answer options (if MCQ), correct answer, and any explanations."
                    )
                }
            },
            "required": ["content"]
        }
    }
    
    return spec, amq_convert_function 