from __future__ import annotations

import logging
from typing import Any, Callable, Dict

from edu_agents.core.api_key_manager import get_async_openai_client

logger = logging.getLogger(__name__)

class LatexDelimiterFixer:
    """Fixes incorrectly delimited LaTeX in content (markdown, JSON, structured data) 
    using OpenAI's GPT-5.
    """
    
    def __init__(self):
        self.client = get_async_openai_client(timeout=180.0)
    
    async def fix_latex_delimiters(self, markdown_content: str) -> str:
        """
        Fix incorrectly delimited LaTeX in content using GPT-5.
        
        This method scans content (markdown, JSON, structured data) for LaTeX that uses 
        incorrect delimiters (like parentheses or brackets) and corrects them to use 
        proper markdown LaTeX delimiters ($...$ for inline, $$...$$ for display).
        
        Parameters
        ----------
        markdown_content : str
            Content that may contain incorrectly delimited LaTeX (markdown, JSON, etc.)
            
        Returns
        -------
        str
            Corrected content with proper LaTeX delimiters
        """
        system_prompt = """You are a LaTeX delimiter correction specialist. Your ONLY job is to
scan content and fix incorrectly delimited LaTeX expressions.

CRITICAL REQUIREMENTS:
1. Make NO OTHER MODIFICATIONS to the content whatsoever - do not change wording, structure,
formatting, or anything else
2. ONLY fix LaTeX delimiter issues - nothing else
3. Convert incorrectly delimited LaTeX to use proper markdown LaTeX delimiters:
   - Use $...$ for inline LaTeX expressions
   - Use $$...$$ for display/block LaTeX expressions
4. Be careful not to mistake parentheses or brackets WITHIN a LaTeX expression for incorrect
delimiters
5. Return the COMPLETE corrected content exactly as provided, with ONLY LaTeX delimiters fixed. If
no LaTeX errors are found, return the content exactly as provided.
6. **IMPORTANT**: Look for LaTeX delimiters within JSON strings, structured content, and any other
context where LaTeX might be embedded. Even if content appears within JSON or other structured
formats, still fix the LaTeX delimiters.

Common LaTeX delimiter problems to fix:
- \\\\(...\\\\) → $...$
- \\\\[...\\\\] → $$...$$
- \\(...\\) → $...$
- \\[...\\] → $$...$$
- \(...\) → $...$
- \[...\] → $$...$$
- (...) → $...$
- [...] → $$...$$

- Any strings that appear to contain LaTeX operators with matching incorrect delimiters: "Calculate
(5 \\times 5 = 25)." → "Calculate $5 \\times 5 = 25$."
- Any other non-dollar-sign LaTeX delimiters → proper $ or $$ delimiters

Examples:
- "The equation \\(x + 2 = 5\\) shows..." → "The equation $x + 2 = 5$ shows..."
- "\\[\\frac{a}{b} = c\\]" → "$$\\frac{a}{b} = c$$"
- "We have \\\\(\\sqrt{16}\\\\) equals 4" → "We have $\\sqrt{16}$ equals 4"
- "The equation (2 \\times (3 + 4))" → "The equation $2 \\times (3 + 4)$"
- "Look at the equation \\[2 \\times (3 + 4)\\]" → "Look at the equation $$2 \\times (3 + 4)$$"

JSON/Structured Content Examples:
- "content": "A formula is \\(a + b = c\\) here." → "content": "A formula is $a + b = c$ here."
- "text": "\\[\\frac{x}{y} = z\\]" → "text": "$$\\frac{x}{y} = z$$"
- {"title": "Math", "content": "\\(\\text{number} \\times \\text{value}\\)"} → 
  {"title": "Math", "content": "$\\text{number} \\times \\text{value}$"}

**CRITICAL**: Pay special attention to LaTeX content that includes \\text{} commands, mathematical
operators like \\times, \\div, \\frac{}{}, etc., as these are strong indicators of LaTeX that
needs proper delimiters regardless of the surrounding context.

IMPORTANT: Leave already correctly delimited LaTeX (using $ or $$) COMPLETELY unchanged."""

        user_prompt = f"""{markdown_content}"""

        try:
            logger.info("Calling OpenAI to fix LaTeX delimiters in content")
            response = await self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            
            # Defensive check: ensure content is not a coroutine
            response_content = response.choices[0].message.content
            if hasattr(response_content, '__await__'):
                response_content = await response_content
            corrected_content = response_content.strip()
            
            # Log if any changes were made
            if corrected_content != markdown_content:
                logger.info("LaTeX delimiter corrections applied to content")
                # Log a brief sample of what changed for debugging
                if len(markdown_content) < 500:
                    logger.debug(f"Original: {markdown_content}")
                    logger.debug(f"Corrected: {corrected_content}")
            else:
                logger.debug("No LaTeX delimiter corrections needed")
            
            return corrected_content
            
        except Exception as e:
            logger.error(f"Error fixing LaTeX delimiters: {str(e)}")
            # Return original content if correction fails
            return markdown_content


def generate_latex_delimiter_fix_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the LaTeX delimiter fix tool specification and function."""
    
    fixer = LatexDelimiterFixer()
    
    async def latex_delimiter_fix_function(content: str) -> str:
        """Fix LaTeX delimiters in content (markdown, JSON, structured data)."""
        return await fixer.fix_latex_delimiters(content)
    
    spec = {
        "type": "function",
        "name": "fix_latex_delimiters",
        "description": (
            "Fix incorrectly delimited LaTeX expressions in content (markdown, JSON, "
            "structured data) by converting them to use proper $ and $$ delimiters. "
            "This tool only modifies LaTeX delimiters and makes no other changes to the content."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": (
                        "The content (markdown, JSON, structured data) that may contain "
                        "incorrectly delimited LaTeX expressions to be fixed."
                    )
                }
            },
            "required": ["content"]
        }
    }
    
    return spec, latex_delimiter_fix_function 