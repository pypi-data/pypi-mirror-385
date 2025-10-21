import json
import logging
import markdown
import os
import textwrap
from typing import Dict, Any, Callable, List
from pydantic import BaseModel
from edu_agents.core.api_key_manager import get_async_openai_client
from enum import Enum
from edu_agents.athena import MultipleChoiceQuestion, TextEntryQuestion

logger = logging.getLogger(__name__)

class UnknownContentTypeError(Exception):
    """Raised when the content type is unknown."""
    pass

class UnsupportedContentTypeError(Exception):
    """Raised when the content type is unsupported."""
    pass

class ContentCategory(Enum):
    MCQ = "MCQ"
    TEXT_ENTRY = "Text Entry"
    TEACHING_EXPLANATION = "Teaching Explanation"

class CategorizedContent(BaseModel):
    category: ContentCategory

class AthenaFormatter:
    """Converts markdown educational content to structured JSON format using OpenAI's structured outputs."""
    
    def __init__(self):
        self.client = get_async_openai_client(timeout=180.0)
    
    async def _classify_content(self, markdown_content: str) -> str:
        """
        Classify the content into a category.

        Parameters
        ----------
        markdown_content : str
            Markdown formatted educational content

        Returns
        -------
        str
            The category name
        """
        system_prompt = """You are an expert educational content classifier. Your task is to classify the content into a category
and return a specified category name.

The supported categories are:
- Multiple Choice Question: "MCQ"
- Text Entry Question: "Text Entry"
- Teaching Explanation: "Teaching Explanation"
        """
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
        
        raise UnknownContentTypeError("No parsed category found in API response")
    
    def _get_schema(self, category: str) -> BaseModel:
        """
        Get the schema for the content category.

        Parameters
        ----------
        category : str
            The content category

        Returns
        -------
        BaseModel
            The schema for the content
        """
        if category == ContentCategory.MCQ.value:
            schema = MultipleChoiceQuestion
        elif category == ContentCategory.TEXT_ENTRY.value:
            schema = TextEntryQuestion
        else:
            raise UnsupportedContentTypeError(f"Unsupported category: {category}")
        
        if schema is None:
            raise UnsupportedContentTypeError(f"No schema found for category {category}")
        
        return schema

    async def _process_answers_with_llm(self, markdown_content: str) -> str:
        """
        Use LLM to process the entire content and wrap answers in details tags.
        
        Parameters
        ----------
        markdown_content : str
            Original markdown content
            
        Returns
        -------
        str
            Modified markdown content with answers wrapped in details tags
        """
        system_prompt = """You are an expert at identifying and formatting answer content in educational materials.

Your task is to take the entire markdown content and return it with all answer content wrapped in HTML details tags.

For any content that appears to be an "answer" that should be hidden behind a collapsible section:
- Wrap it in: `<details><summary><strong>Click to see answer</strong></summary>[answer content]</details>`
- For numbered answers (like "X. Answer text"), replace the entire line with this instead: `**X.**<details><summary><strong>Click to see answer</strong></summary>` (where X is the number of the answer within the numbered list). Do not add a newline after the number.
- Do not introduce new lines (`\\n`), breaks (`<br>`), paragraphs (`<p>`), or any other HTML tags between the `<details>` and `</details>` tags.
- You may expand, clarify, or lightly reword answer content so it makes sense as a section that would explain how to arrive at the answer to a student.
- Each answer section should explain how to arrive at the correct answer to a student, drawing on the selected solution strategy if appropriate. Rewording the answer content to make it more student-friendly is always allowed (though you must double check all rewordings to ensure they are accurate and correct).

This includes:
- Answers in answer key sections (numbered lists like "1. Answer text")
- Solutions to problems or exercises  
- Explanations to independent practice problems that explicitly reveal the answer to a question
- Any content that provides the solution/response to a question or problem

This does not include:
- Answers to Worked Examples or Scaffolded Practice Problems
- Explanations that are part of a Worked Example or Scaffolded Practice Problem

Rules:
- Return the COMPLETE markdown content with modifications
- Only wrap content that is clearly an answer to something
- Place answer details sections after the question and space for students to write their answer (if present in the original content). Be careful NOT to insert the answer details section within a markdown block in the original content, and NOT to change the original question numbering (questions within each section should be numbered sequentially). When you do this, if you placed all answers in an answer key section after their corresponding questions, also delete the corresponding answer key section, including its section header.
- Preserve (or even add) explanations for how to arrive at the answer within the answer details section
- Preserve all other content exactly as-is (headers, questions, explanations, etc.)
- Do NOT wrap question text itself
- Do NOT wrap general instructional content
- Do NOT wrap section headers
- Do NOT introduce new lines (`\\n`), breaks (`<br>`), paragraphs (`<p>`), or any other HTML tags between the `<details>` and `</details>` tags.
- Be conservative - only wrap obvious answer content
- Do NOT use code fences (```) or wrap your response in any code blocks
- Return the raw markdown content directly without any formatting wrappers"""
        
        user_prompt = f"""Process this educational content and wrap all answer content in details tags:

{markdown_content}"""
        
        # Use regular chat completion instead of structured output
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1  # Low temperature for consistency
        )
        
        # Extract the text response directly
        if response.choices and response.choices[0].message.content:
            modified_content = response.choices[0].message.content.strip()
            
            # Clean up any code fences that the LLM might have added
            # Remove markdown code fences (```markdown, ```, etc.)
            if modified_content.startswith('```'):
                lines = modified_content.split('\n')
                # Remove first line if it's a code fence
                if lines[0].startswith('```'):
                    lines = lines[1:]
                # Remove last line if it's a closing code fence
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                modified_content = '\n'.join(lines)
            
            # Remove any leading/trailing whitespace again after cleaning
            modified_content = modified_content.strip()
            
            return modified_content
        
        # Fallback to original content if processing fails
        return markdown_content

    async def format_content(self, markdown_content: str) -> str:
        """
        Convert markdown educational content to structured JSON format.
        
        Parameters
        ----------
        markdown_content : str
            Markdown formatted educational content
            
        Returns
        -------
        str
            JSON string conforming to the JSON schema or dict with html_content for teaching explanations
        """
        try:
            # First classify the content
            category = await self._classify_content(markdown_content)
            tag_questions = True
            
            # Handle teaching explanation content differently
            if category == ContentCategory.TEACHING_EXPLANATION.value:
                # Clean up literal \n strings and convert them to actual newlines
                cleaned_content = markdown_content.replace('\\n', '\n')
                
                if tag_questions:
                    # Detect answer content using LLM
                    cleaned_content = await self._process_answers_with_llm(cleaned_content)
                
                # Convert markdown to HTML with extensions for better rendering
                html_content = markdown.markdown(
                    cleaned_content,
                    extensions=[
                        'tables',           # Enable table support
                        'fenced_code',      # Better code block support
                        'codehilite',       # Syntax highlighting
                        'attr_list',        # Allow adding attributes to elements
                        'def_list',         # Definition lists
                        'footnotes',        # Footnote support
                        'toc'               # Table of contents
                    ],
                    extension_configs={
                        'codehilite': {
                            'css_class': 'highlight',
                            'use_pygments': False  # Use CSS classes instead of inline styles
                        }
                    }
                )

                # Add basic modern styling
                # First create the template with dedented structure
                html_template = textwrap.dedent("""
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; line-height: 1.6; color: #333; max-width: 100%;">
                    <style>
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                            margin: 1rem 0;
                            background-color: white;
                            border-radius: 8px;
                            overflow: hidden;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                            border: 2px solid #dee2e6;
                        }}
                        th, td {{
                            padding: 12px 16px;
                            text-align: left;
                            border: 1px solid #dee2e6;
                        }}
                        th {{
                            background-color: #f8f9fa;
                            font-weight: 600;
                            color: #495057;
                            border-bottom: 2px solid #dee2e6;
                        }}
                        tr:hover {{
                            background-color: #f8f9fa;
                        }}
                        h1, h2, h3, h4, h5, h6 {{
                            color: #2c3e50;
                            margin: 1.5rem 0 0.5rem 0;
                            font-weight: 600;
                        }}
                        h1 {{ font-size: 2rem; }}
                        h2 {{ font-size: 1.5rem; }}
                        h3 {{ font-size: 1.25rem; }}
                        p {{ margin: 0.75rem 0; }}
                        ul, ol {{ margin: 0.75rem 0; padding-left: 1.5rem; }}
                        li {{ margin: 0.35rem 0; }}
                        code {{
                            background-color: #f1f3f4;
                            padding: 2px 6px;
                            border-radius: 4px;
                            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                            font-size: 0.9em;
                        }}
                        pre {{
                            background-color: #f8f9fa;
                            padding: 1rem;
                            border-radius: 6px;
                            overflow-x: auto;
                            border-left: 4px solid #007bff;
                        }}
                        blockquote {{
                            border-left: 4px solid #007bff;
                            margin: 1rem 0;
                            padding-left: 1rem;
                            color: #6c757d;
                            font-style: italic;
                        }}
                        hr {{
                            border: none;
                            height: 2px;
                            background: linear-gradient(to right, #007bff, transparent);
                            margin: 2rem 0;
                        }}
                        img {{
                            max-width: 400px;
                            height: auto;
                            margin: 1rem 0;
                            border-radius: 4px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        }}
                    </style>
                    {content}
                </div>
                """).strip()
                
                # Then substitute the html_content without affecting its whitespace
                styled_html = html_template.format(content=html_content)

                # Return as JSON string with htmlContent key
                result = {"htmlContent": styled_html}
                return json.dumps(result, indent=2)
            
            # For other content types, use the existing OpenAI API approach
            system_prompt = """You are an expert educational content formatter. Your task is to convert markdown-formatted educational content into a structured JSON format.

Key requirements:
1. Parse the markdown content to extract the question, answer options, and any additional information.
2. Map as much of the markdown content to the JSON schema as makes sense.
3. Be very careful not to remove or change any critical aspects of the content (e.g., numbers, units, etc. in questions or answers)
4. If necessary, lightly reword the content so it refers to actions the user of a software UI would take instead of actions a student might take on paper. For example, "select" instead of "circle" the correct answer.
5. If necessary, you may remove requests for the user to do something that is not possible to represent in the JSON schema. For example, if the question asks the user to explain their reasoning but the JSON schema does not have a field for that, you may remove the request for the user to explain their reasoning.
6. When possible, infer the content of all JSON fields from the markdown content. For example, infer an explanation for why certain answers are correct or incorrect from related information in the markdown content.
7. The explanation you include for the correct answer MUST be a step-by-step explanation of how to arrive at the correct answer starting from the question and first principles, without relying on the student already having mastery of the material. For example, if the student is learning how to use division to divide objects into equal groups, the explanation should walk through the steps of recognizing division as the appropriate operation to use and then applying it to create a solution, NOT merely telling them to use division as a single step.
8. Use the difficulty level as a light guide to adjust the focus and level of detail in explanations, while keeping all explanations accessible to students at any mastery level (since students of varying abilities may encounter questions of any difficulty):
    - Easy: Emphasize foundational concepts and step-by-step breakdowns of basic operations.
    - Medium: Focus on connecting basic concepts to solve multi-step problems and strategic thinking.
    - Hard: Emphasize advanced problem-solving techniques and sophisticated reasoning while still explaining key steps.
9. You may use the same information to infer the content of multiple JSON fields. For example, you might infer both explanations for answers and learning content from the same information.
10. If you are creating a worked example and there is a question stimulus, include that stimulus in the first step of the worked example steps, but include no stimulus in any other step.
11. For content that is a question, replace references to the location of the image with "the image". For example, use "the image" instead of "the image above" or "the image below".
12. Do not treat any text in the markdown content as a text stimulus unless it is explicitly labeled as such in the markdown content. For example, "Look at the image below" is not a text stimulus. It's part of the question prompt.
13. No fields may be null. To leave a field blank, use an empty string.
14. Ensure the JSON is complete and valid.

The output must conform exactly to the JSON schema."""

            user_prompt = f"""Convert this markdown educational content to structured JSON format:

{markdown_content}
"""

            schema = self._get_schema(category)

            # Use structured outputs with the appropriate schema
            response = await self.client.responses.parse(
                model="o3",
                input=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                text_format=schema,
                reasoning={"effort": "medium"}
            )
            
            # Extract the structured response
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if (content_item.type == "output_text" and 
                            hasattr(content_item, "parsed") and 
                            content_item.parsed is not None):
                            
                            # Return the JSON string representation, excluding null values
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
            
        except UnknownContentTypeError:
            # Let content type errors bubble up to be handled by the API
            raise
        except UnsupportedContentTypeError:
            # Let content type errors bubble up to be handled by the API
            raise
        except Exception as e:
            error_message = f"Error formatting content with Athena: {str(e)}"
            logger.error(error_message)
            raise RuntimeError(error_message)


def generate_athena_formatter_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the Athena formatter tool specification and function."""
    
    formatter = AthenaFormatter()
    
    async def athena_format_function(markdown_content: str) -> str:
        """Convert markdown educational content to structured MCQ format."""
        return await formatter.format_content(markdown_content)
    
    spec = {
        "type": "function",
        "name": "format_with_athena",
        "description": "Convert markdown educational content to structured multiple choice question format using OpenAI's structured outputs. Creates a JSON response conforming to the MultipleChoiceQuestion schema with proper question structure, answer options, stimulus content, and worked examples.",
        "parameters": {
            "type": "object",
            "properties": {
                "markdown_content": {
                    "type": "string",
                    "description": "Markdown formatted educational content containing questions, answers, explanations, and any supporting materials. Can include text, images, and instructional content."
                }
            },
            "required": ["markdown_content"]
        }
    }
    
    return spec, athena_format_function 