from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

from anthropic import AsyncAnthropic

from edu_agents.core.api_key_manager import get_async_openai_client
from utils.supabase_utils import upload_video_to_supabase

logger = logging.getLogger(__name__)

# Global flag to control which model provider to use for Manim code generation
# Options: "gpt", "claude"
# 
# Usage:
#   - Set MANIM_MODEL_PROVIDER = GPT_MODEL_PROVIDER for GPT-5 (default)
#   - Set MANIM_MODEL_PROVIDER = CLAUDE_MODEL_PROVIDER for Claude Sonnet
#
# Both providers use the same system prompt and validation for consistency
GPT_MODEL_PROVIDER = "gpt"
CLAUDE_MODEL_PROVIDER = "claude"
MANIM_MODEL_PROVIDER = CLAUDE_MODEL_PROVIDER

# Default video settings
DEFAULT_QUALITY = "h"  # Manim quality: 'l'=480p, 'm'=720p, 'h'=1080p, 'p'=1440p, 'k'=2160p
DEFAULT_FRAME_RATE = 30  # FPS for video output

SYSTEM_PROMPT = """Create exceptional educational animations using Manim Community Edition that truly help students learn mathematical concepts.

## 🎯 What Makes an Outstanding Educational Animation

**CLARITY & PROGRESSION**: Students should be able to follow the logical flow from concept introduction through step-by-step development to final understanding. Each element appears purposefully and builds on what came before.

**VISUAL EFFECTIVENESS**: Mathematical relationships are made visible through coordinated motion, color, and positioning. Abstract concepts become concrete through well-designed visual metaphors and representations.

**PEDAGOGICAL SOUNDNESS**: The animation teaches the way students actually learn - starting with familiar ideas, introducing new concepts gradually, and reinforcing understanding through multiple representations of the same idea.

**PROFESSIONAL QUALITY**: Crisp text that's easy to read, smooth animations that guide attention appropriately, and a clean aesthetic that doesn't distract from the mathematical content.

**STUDENT-CENTERED LANGUAGE**: Every piece of text speaks directly to the learner about what they should understand, notice, or do - not about what the animation is displaying.

## 🎨 Technical Excellence Standards

Your animation will be rendered at 1920×1080 resolution. Use Manim's full coordinate system (14.22 units wide × 8 units tall, spanning from -7.11 to +7.11 horizontally and -4 to +4 vertically) to create spacious, uncluttered layouts.

Create your animation as a class called `EducationalAnimation(Scene)` with a `construct()` method. Set `self.camera.background_color = WHITE` for a clean appearance.

## 🚀 Your Creative Freedom

You have complete creative control over structure, timing, visual design, and pedagogical approach. Focus on creating something that would genuinely help a student understand the mathematical concept being taught."""
USER_PROMPT_REQUIREMENTS = """Create a Python class called `EducationalAnimation(Scene)` that demonstrates the mathematical concept clearly and engagingly. Your code will be executed directly by Manim to produce a high-quality educational video."""


async def _generate_manim_code_gpt(prompt: str, previous_attempt_errors_and_warnings: str = None) -> str:
    """
    Generate Manim Python code using GPT-5.
    
    Parameters
    ----------
    prompt : str
        Description of the animation to generate
    previous_attempt_errors_and_warnings : str, optional
        Context from previous failed attempts
        
    Returns
    -------
    str
        The complete Manim Python code
    """
    try:
        # Build user prompt with optional error context
        user_prompt_parts = [
            f"Create a Manim Community Edition animation that demonstrates: {prompt}"
        ]
        
        # Add previous errors/warnings if provided
        if previous_attempt_errors_and_warnings:
            user_prompt_parts.append(
                "\n\n**IMPORTANT: Previous attempts failed with these errors/warnings:**\n"
                f"{previous_attempt_errors_and_warnings}\n\n"
                "Please avoid these specific issues in your solution."
            )
        logger.info(
            "Previous attempts failed with these errors/warnings: "
            f"{previous_attempt_errors_and_warnings}"
        )
        
        # Add requirements
        user_prompt_parts.append(f"\n\n{USER_PROMPT_REQUIREMENTS}")
        
        user_prompt = "".join(user_prompt_parts)
        client = get_async_openai_client(timeout=300.0)
        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "developer", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        if response.choices[0].finish_reason != 'stop':
            raise Exception(f"Failed to generate animation: {response.choices[0].finish_reason}")

        # Defensive check: ensure content is not a coroutine
        response_content = response.choices[0].message.content
        if hasattr(response_content, '__await__'):
            response_content = await response_content
        manim_code = response_content
        
        # Clean the code (remove markdown code blocks if present)
        if "```python" in manim_code:
            manim_code = manim_code.split("```python")[1].split("```")[0]
        elif "```" in manim_code:
            manim_code = manim_code.split("```")[1].split("```")[0]
        
        manim_code = manim_code.strip()
        # Code generation completed successfully
        
        # Basic validation to catch common errors
        _validate_manim_code(manim_code)
        
        logger.info("Successfully generated Manim animation code")
        return manim_code

    except Exception as e:
        logger.error(f"Error generating Manim animation: {e}")
        raise

async def _generate_manim_code_claude(prompt: str,
previous_attempt_errors_and_warnings: str = None) -> str:
    """
    Generate Manim Python code using Claude Sonnet.
    
    Parameters
    ----------
    prompt : str
        Description of the animation to generate
    previous_attempt_errors_and_warnings : str, optional
        Context from previous failed attempts
        
    Returns
    -------
    str
        The complete Manim Python code
    """
    try:
        # Build user prompt with optional error context
        user_prompt_parts = [
            f"Create a Manim Community Edition animation that demonstrates: {prompt}"
        ]
        
        # Add previous errors/warnings if provided
        if previous_attempt_errors_and_warnings:
            user_prompt_parts.append(
                "\n\n**IMPORTANT: Previous attempts failed with these errors/warnings:**\n"
                f"{previous_attempt_errors_and_warnings}\n\n"
                "Please avoid these specific issues in your solution."
            )
        logger.info(
            "Previous attempts failed with these errors/warnings: "
            f"{previous_attempt_errors_and_warnings}"
        )
        
        # Add requirements
        user_prompt_parts.append(f"\n\n{USER_PROMPT_REQUIREMENTS}")
        
        user_prompt = "".join(user_prompt_parts)

        # Initialize Claude client
        client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        response = await client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=16384,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        if not response.content or len(response.content) == 0:
            raise Exception("Failed to generate animation: empty response from Claude")

        # Defensive check: ensure text is not a coroutine
        response_text = response.content[0].text
        if hasattr(response_text, '__await__'):
            response_text = await response_text
        manim_code = response_text
        
        # Clean the code (remove markdown code blocks if present)
        if "```python" in manim_code:
            manim_code = manim_code.split("```python")[1].split("```")[0]
        elif "```" in manim_code:
            manim_code = manim_code.split("```")[1].split("```")[0]
        
        manim_code = manim_code.strip()
        # Code generation completed successfully
        
        # Basic validation to catch common errors
        _validate_manim_code(manim_code)
        
        logger.info("Successfully generated Manim animation code using Claude")
        return manim_code

    except Exception as e:
        logger.error(f"Error generating Manim animation with Claude: {e}")
        raise

async def _generate_manim_code(prompt: str, previous_attempt_errors_and_warnings: str = None) -> str:
    """
    Generate Manim Python code using the configured model provider.
    
    Parameters
    ----------
    prompt : str
        Description of the animation to generate
    previous_attempt_errors_and_warnings : str, optional
        Context from previous failed attempts
        
    Returns
    -------
    str
        The complete Manim Python code
    """
    provider_name = MANIM_MODEL_PROVIDER.upper()
    logger.info(f"Generating Manim code using {provider_name}")
    
    # Route to the appropriate generation method based on global flag
    if MANIM_MODEL_PROVIDER == CLAUDE_MODEL_PROVIDER:
        return await _generate_manim_code_claude(prompt, previous_attempt_errors_and_warnings)
    else:  # Default to GPT
        return await _generate_manim_code_gpt(prompt, previous_attempt_errors_and_warnings)

def _validate_manim_code(manim_code: str) -> None:
    """
    Perform basic validation on generated Manim code to catch common errors.
    
    Parameters
    ----------
    manim_code : str
        The generated Manim code to validate
        
    Raises
    ------
    Exception
        If validation finds potential issues
    """
    # Check for common table data type errors
    if "Table(" in manim_code:
        # Look for patterns that suggest raw integers in table data
        # Find table_data assignments
        table_patterns = re.findall(r'table_data\s*=\s*\[(.*?)\]', manim_code, re.DOTALL)
        for pattern in table_patterns:
            # Check for unquoted integers (negative or positive)
            if re.search(r'[,\[\s]-?\d+[,\]\s]', pattern):
                logger.warning(
                    "Potential table data type error detected: found unquoted integers in "
                    "table_data"
                )
                logger.warning(
                    "This may cause 'TypeError: sequence item 0: expected str instance, int found'"
                )
                # Don't raise exception, just warn - let Manim handle the actual error
                # This way we don't introduce false positives
                break
    
    # Check for required imports
    if "from manim import *" not in manim_code and "import manim" not in manim_code:
        raise Exception("Missing required Manim import: 'from manim import *'")
    
    # Check for required class structure
    if "class EducationalAnimation(Scene):" not in manim_code:
        raise Exception("Missing required class: 'class EducationalAnimation(Scene):'")
    
    # Check for construct method
    if "def construct(self):" not in manim_code:
        raise Exception("Missing required method: 'def construct(self):'")
    
    # Check for white background setting
    if "self.camera.background_color = WHITE" not in manim_code:
        logger.warning(
            "Missing white background setting. Add 'self.camera.background_color = WHITE' for "
            "educational clarity."
        )
    
    # Check for forbidden camera frame manipulation in basic Scene
    camera_patterns = [
        r'self\.camera\.frame\.animate',
        r'self\.camera\.frame\.move_to',
        r'self\.camera\.frame\.scale',
        r'self\.camera\.frame\.shift'
    ]
    
    for pattern in camera_patterns:
        if re.search(pattern, manim_code):
            raise Exception(
                "Invalid camera operation: Camera frame manipulation is not available in basic "
                "Scene class. Design content to fit within the default frame size instead of using "
                "camera controls."
            )
    
    
    # Light validation for any remaining f-string issues (should be rare after auto-fix)
    if re.search(r'f["\'][^"\']*\{[^}]*\*\*[^}]*\}[^"\']*["\']', manim_code):
        logger.warning(
            "Potential f-string format specifier issue detected after auto-fix. Manual review "
            "recommended."
        )
    
    # Simplified post-auto-fix validation (most issues should be resolved by now)
    if re.search(r'f["\'][^"\']*\{[^}]*\*\*[^}]*\}[^"\']*["\'][^,]*,\s*color\s*=', manim_code):
        logger.warning(
            "Potential f-string format issue may remain after auto-fix. Review recommended."
        )
    
    # Check for variable naming that could cause conflicts
    problematic_vars = [
        r'\bb_val\b',  # b_val might conflict with something
        r'\ba_val\b',  # a_val might conflict  
        r'\bc_val\b',  # c_val might conflict
        r'\bb\s*=',    # single letter variables can conflict
        r'\ba\s*=',
        r'\bc\s*='
    ]
    
    for pattern in problematic_vars:
        if re.search(pattern, manim_code):
            logger.warning(
                "Potentially problematic variable name detected. Use descriptive names like "
                "'a_coeff', 'b_coeff', 'c_coeff' to avoid conflicts."
            )
    
    # Check for LaTeX formatting issues in f-strings
    latex_fstring_patterns = [
        r'MathTex\(f"[^"]*\\frac\{[^}]*\{[^}]*\*\*[^}]*\}[^"]*"\)',
        r'MathTex\(f"[^"]*\{[^}]*-[^}]*\}[^"]*"\)',
    ]
    
    for pattern in latex_fstring_patterns:
        if re.search(pattern, manim_code):
            logger.warning(
                "Complex LaTeX with f-string detected. Use raw strings and calculate values "
                "separately to avoid formatting errors."
            )
    
    # Check for improper table configuration 
    if 'Table(' in manim_code:
        if 'line_config' not in manim_code:
            logger.warning(
                "Table missing line_config for visibility. Add line_config={'stroke_width': 2, "
                "'color': BLACK}"
            )
        if 'element_to_mobject_config' not in manim_code:
            logger.warning(
                "Table missing element_to_mobject_config for text visibility. Add "
                "element_to_mobject_config={'color': BLACK, 'font_size': 20}"
            )
        # Check for table font size
        if 'element_to_mobject_config' in manim_code and 'font_size' in manim_code:
            # Check if font size is too small in table config
            table_font_match = re.search(r'element_to_mobject_config.*?font_size.*?(\d+)',
                                         manim_code, re.DOTALL)
        if table_font_match:
            font_size = int(table_font_match.group(1))
            if font_size < 32:
                logger.warning(
                    f"Table font size {font_size} too small. Use font_size=32 or larger for "
                    "readability at 1920×1080 resolution."
                )
        # Check for Transform on entire table for single updates (helpful for animation quality)
        if re.search(r'Transform\(.*table.*,.*table.*\)', manim_code):
            logger.warning(
                "Using Transform() on entire table detected. Consider progressive row addition or "
                "individual cell updates for better animation."
            )
        # Check if table has any positioning (more flexible than requiring specific coordinates)
        if not re.search(r'\.move_to\(', manim_code) and not re.search(r'\.to_edge\(', manim_code) \
            and not re.search(r'\.next_to\(', manim_code):
            logger.warning(
                "Table may need positioning. Consider adding .next_to(axes, DOWN, buff=0.3) to "
                "position table within main animation area."
            )
    
    # Check for potential grid overflow - axes should be properly sized and positioned
    if 'Axes(' in manim_code:
        if not re.search(r'\.move_to\(\[0,\s*0\.?0?,\s*0\]\)', manim_code):
            logger.warning(
                "Axes should be positioned at [0, 0, 0] to center in main animation area (updated "
                "for full canvas usage)."
            )
    
    # Check for poor axes scaling that creates distortion
    axes_match = re.search(
        r'x_range\s*=\s*\[([^,]+),\s*([^\]]+)\].*?y_range\s*=\s*\[([^,]+),\s*([^\]]+)\]',
        manim_code, re.DOTALL
    )
    if axes_match:
        try:
            x_min, x_max, y_min, y_max = [float(val.strip()) for val in axes_match.groups()]
            x_span = x_max - x_min
            y_span = y_max - y_min
            if y_span > x_span * 2:  # y-axis more than 2x compressed
                logger.warning(
                    f"Poor axes scaling detected: x spans {x_span}, y spans {y_span}. Consider "
                    "reducing y_range for better visual balance."
                )
        except (ValueError, AttributeError):
            pass  # Skip if we can't parse the numbers
    
    # Check for content extending beyond main animation area boundaries
    if 'Table(' in manim_code:
        # Check for tall tables positioned below axes (likely to extend beyond bottom)
        table_rows_match = re.search(r'Table\(\[.*?\]\s*(?:\+.*?)?\)', manim_code, re.DOTALL)
        if table_rows_match and re.search(r'\.next_to\(.*axes.*DOWN', manim_code):
            # Count number of rows in table data (rough estimate)
            row_count = manim_code.count('],[') + manim_code.count('[[')
            if row_count > 6:  # Many rows
                logger.warning(
                    "Tall table (>5 rows) positioned below axes may extend beyond main animation "
                    "area. Consider positioning to RIGHT of axes with smaller x_length."
                )
        
        # Check for explicit positioning that might be outside bounds
        right_positioned_matches = re.findall(r'\.move_to\(\[([4-9])', manim_code)
        if right_positioned_matches:
            for x_pos in right_positioned_matches:
                if float(x_pos) > 7:
                    logger.warning(
                        f"Content positioned at x={x_pos} exceeds main animation area boundary "
                        "(x ≤ 7.11). Keep all content within bounds."
                    )
    
    # Check for font sizes that are too small for readability
    small_font_patterns = [
        r'font_size\s*=\s*1[0-9]\b',  # 10-19 are too small
        r'font_size\s*=\s*2[0-3]\b',  # 20-23 are too small
        r'font_size\s*=\s*[1-9]\b'    # Single digits are definitely too small
    ]
    
    for pattern in small_font_patterns:
        if re.search(pattern, manim_code):
            logger.warning(
                "Font size too small for educational content. Use font_size=20 or larger for "
                "better readability."
            )
    
    # Check for f-strings in Text() objects which can cause weird formatting
    if re.search(r'Text\(f["\']', manim_code):
        logger.warning(
            "F-strings in Text() objects can cause math-like formatting. Use direct strings for "
            "regular text."
        )
    
    # Check for Text() usage instead of recommended Tex() for better rendering
    text_usage = re.findall(r'Text\([^)]*\)', manim_code)
    if text_usage:
        logger.warning(
            "Text() objects detected. Consider using Tex(r\"\\text{...}\") instead for better "
            "kerning and consistent appearance."
        )
    
    # Check for missing font specification in any remaining Text() objects
    text_without_font = re.findall(r'Text\([^)]*\)', manim_code)
    for text_obj in text_without_font:
        if 'font=' not in text_obj:
            logger.warning(
                "Text() object without font specification detected. Add font=\"DejaVu Serif\" "
                "for normal, readable text appearance."
            )
            break  # Only warn once to avoid spam
    
    # Check for missing font_size in MathTex objects
    mathtex_without_font_size = re.findall(r'MathTex\([^)]*\)', manim_code)
    for mathtex_obj in mathtex_without_font_size:
        if 'font_size' not in mathtex_obj:
            logger.warning(
                "MathTex() object without font_size detected. Add font_size=30 or larger for "
                "readability."
            )
            break  # Only warn once to avoid spam
    
    # Check for strongly animation-focused language (reduce false positives)
    strong_animation_phrases = ["animate", "emphasize", "fade in", "fade out", "transform"]
    for phrase in strong_animation_phrases:
        if re.search(rf'\b{phrase}\b.*(?:symmetry|vertex|equation|concept|property|feature)',
                     manim_code, re.IGNORECASE):
            logger.warning(
                f"Animation-focused language detected: '{phrase}'. Consider student-focused "
                "alternatives like 'Notice', 'Identify', 'Write'."
            )
            break  # Only warn once
    
    # Check for redundant titles in final summary
    if re.search(r'summary_title.*=.*VGroup', manim_code) or re.search(r'How to.*VGroup',
                manim_code):
        logger.warning(
            "Redundant title detected in final summary. The main title already exists at y=3.5 - "
            "don't add another title."
        )
    
    # Check for poor final summary alignment
    summary_positioning = re.findall(r'step\d+\.move_to\(\[([^,]+),', manim_code)
    if summary_positioning:
        x_positions = []
        for x_pos in summary_positioning:
            try:
                x_val = float(x_pos.strip())
                x_positions.append(x_val)
            except ValueError:
                continue
        
        if x_positions and not all(abs(x) < 0.5 for x in x_positions):
            logger.warning(
                "Final summary steps appear off-center. Use x=0 for center alignment: "
                "step1.move_to([0, 1.5, 0])"
            )
    
    # Check for 2D coordinates that should be 3D (prevents broadcast errors)
    coordinate_patterns = [
        r'Polygon\([^)]*\[.*?[^,0]\]',  # Polygon with potential 2D coordinates
        r'Line\([^)]*\[.*?[^,0]\]',     # Line with potential 2D coordinates  
        r'move_to\(\[[^,]+,\s*[^,]+\]\)',  # move_to with 2D coordinates
        r'vertices\s*=\s*\[.*?\[[^,]+,\s*[^,\]]+\]',  # vertex lists with 2D coordinates
    ]
    
    for pattern in coordinate_patterns:
        matches = re.findall(pattern, manim_code)
        for match in matches:
            # Check if it ends with ", 0]" (3D) or just "]" (likely 2D)
            if not re.search(r',\s*0\s*\]', match) and '[' in match and ']' in match:
                # Extract the coordinate part to validate
                coord_matches = re.findall(r'\[([-.\d\s,]+)\]', match)
                for coord_str in coord_matches:
                    parts = [part.strip() for part in coord_str.split(',')]
                    if len(parts) == 2:  # Exactly 2 coordinates = 2D (error)
                        raise Exception(
                            f"2D coordinates detected: {match}. "
                            "Manim requires 3D coordinates [x, y, z] for all geometry. "
                            "Add z=0 for 2D shapes: [x, y, 0]"
                        )
    
    # Check for mathematical symbols inside \text{...} (prevents LaTeX compilation errors)
    latex_text_math_patterns = [
        r'\\text\{[^}]*\\geq[^}]*\}',     # ≥ symbol in text
        r'\\text\{[^}]*\\leq[^}]*\}',     # ≤ symbol in text
        r'\\text\{[^}]*\\pm[^}]*\}',      # ± symbol in text
        r'\\text\{[^}]*\\times[^}]*\}',   # × symbol in text
        r'\\text\{[^}]*\\div[^}]*\}',     # ÷ symbol in text
        r'\\text\{[^}]*\\neq[^}]*\}',     # ≠ symbol in text
        r'\\text\{[^}]*\\approx[^}]*\}',  # ≈ symbol in text
        r'\\text\{[^}]*\\infty[^}]*\}',   # ∞ symbol in text
    ]
    
    for pattern in latex_text_math_patterns:
        matches = re.findall(pattern, manim_code)
        if matches:
            symbol_map = {
                'geq': '≥ (greater than or equal)',
                'leq': '≤ (less than or equal)', 
                'pm': '± (plus minus)',
                'times': '× (times)',
                'div': '÷ (division)',
                'neq': '≠ (not equal)',
                'approx': '≈ (approximately)',
                'infty': '∞ (infinity)'
            }
            
            detected_symbol = None
            for symbol, description in symbol_map.items():
                if f'\\{symbol}' in matches[0]:
                    detected_symbol = description
                    break
            
            raise Exception(
                f"Mathematical symbol {detected_symbol} inside \\text{{...}} detected: "
                f"{matches[0]}. LaTeX math symbols cannot be used inside \\text{{...}}. "
                "Use word equivalents (e.g., 'at least', 'greater than') or separate text and math "
                "parts."
            )
    
    # Check for math symbols between text blocks in Tex() objects (common LaTeX error pattern)
    mixed_tex_patterns = [
        r'Tex\([^)]*\\text\{[^}]*\}[^}]*\\times[^}]*\\text\{[^}]*\}', # \text{...} \times \text{...}
        r'Tex\([^)]*\\text\{[^}]*\}[^}]*\\div[^}]*\\text\{[^}]*\}',   # \text{...} \div \text{...}
        r'Tex\([^)]*\\text\{[^}]*\}[^}]*\\pm[^}]*\\text\{[^}]*\}',    # \text{...} \pm \text{...}
        r'Tex\([^)]*\\text\{[^}]*\}[^}]*\\geq[^}]*\\text\{[^}]*\}',   # \text{...} \geq \text{...}
        r'Tex\([^)]*\\text\{[^}]*\}[^}]*\\leq[^}]*\\text\{[^}]*\}',   # \text{...} \leq \text{...}
    ]
    
    for pattern in mixed_tex_patterns:
        matches = re.findall(pattern, manim_code)
        if matches:
            # Extract the math symbol from the pattern
            if '\\times' in pattern:
                symbol = 'times (×)'
            elif '\\div' in pattern:
                symbol = 'div (÷)'  
            elif '\\pm' in pattern:
                symbol = 'pm (±)'
            elif '\\geq' in pattern:
                symbol = 'geq (≥)'
            elif '\\leq' in pattern:
                symbol = 'leq (≤)'
            else:
                symbol = 'math symbol'
                
            raise Exception(
                f"Math symbol {symbol} between text blocks detected in Tex(): "
                f"{matches[0][:80]}...\n"
                f"SOLUTIONS:\n"
                f"1) Use words: Tex(r'\\text{{Area = length times width}}')\n"
                f"2) Use MathTex: MathTex(r'\\text{{Area}} = \\text{{length}} \\times "
                f"\\text{{width}}')\n"
                f"3) Use VGroup: VGroup(Tex(r'\\text{{Area = length }}'), MathTex(r'\\times'), "
                f"Tex(r'\\text{{ width}}')).arrange(RIGHT)"
            )
    
    # Simple line-by-line check for the specific problematic pattern
    problematic_lines = []
    lines = manim_code.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip MathTex calls - they're fine
        if 'MathTex(' in line:
            continue
            
        # Look for Tex() calls with \text{...} followed by math without $...$
        if 'Tex(' in line and '\\text{' in line:
            # Check for math expressions after \text{...} but not within $...$
            # Look for patterns like: \text{...} y = x^2 (without $ delimiters)
            if re.search(r'\\text\{[^}]*\}[^$]*[a-zA-Z]\s*[=+\-*/]\s*[a-zA-Z_0-9^{}()]+[^$]*["\)]',
                         line):
                # Verify it's NOT properly enclosed in $...$
                if not re.search(r'\$[^$]*[a-zA-Z]\s*[=+\-*/].*?\$', line):
                    problematic_lines.append((line_num, line.strip()))
    
    if problematic_lines:
        for line_num, line_content in problematic_lines:
            logger.warning(
                f"Line {line_num}: Tex() with bare math after \\text{{...}} (needs $...$): "
                f"{line_content[:80]}..."
            )
    
    # Check for oversized shapes that violate area boundaries
    oversized_shape_patterns = [
        r'Circle\(radius\s*=\s*(1\.[5-9]|[2-9]|[1-9]\d)',  # radius > 1.4
        r'Square\(side_length\s*=\s*(2\.[5-9]|[3-9]|[1-9]\d)',  # side_length > 2.4
        r'Rectangle\([^)]*width\s*=\s*(2\.9|[3-9]|[1-9]\d)',  # width > 2.8
        r'Rectangle\([^)]*height\s*=\s*(2\.9|[3-9]|[1-9]\d)',  # height > 2.8
    ]
    
    for pattern in oversized_shape_patterns:
        matches = re.findall(pattern, manim_code)
        if matches:
            size_value = matches[0] if isinstance(matches[0], str) else str(matches[0])
            if 'Circle' in pattern:
                logger.warning(
                    f"Circle radius={size_value} may be too large for main animation area. "
                    "Recommended max radius is 1.4 to fit within boundaries y∈[-0.5, +2.5]. "
                    "Consider using Circle(radius=1.4) or smaller for better layout."
                )
            elif 'Square' in pattern:
                logger.warning(
                    f"Square side_length={size_value} may be too large for main animation area. "
                    "Recommended max side_length is 2.4 to fit within boundaries y∈[-0.5, +2.5]. "
                    "Consider using Square(side_length=2.2) or smaller for better layout."
                )
            elif 'Rectangle' in pattern:
                logger.warning(
                    f"Rectangle dimension={size_value} may be too large for main animation area. "
                    "Recommended max dimensions: width≤2.8, height≤2.8 to fit within boundaries "
                    "y∈[-0.5, +2.5]. Consider using Rectangle(width=2.8, height=2.0) or smaller "
                    "for better layout."
                )
    
    # Check for hardcoded marker positioning (suggests incorrect relative positioning)
    hardcoded_marker_patterns = [
        r'angle_marker\.move_to\(\[[-\d\s,]+\]\)',  # Direct coordinate positioning
        r'tick_mark\.move_to\(\[[-\d\s,]+\]\)',     # Direct coordinate positioning
        r'marker\.move_to\(\[[-\d\s,]+\]\)',        # Direct coordinate positioning
    ]
    
    for pattern in hardcoded_marker_patterns:
        matches = re.findall(pattern, manim_code)
        if matches:
            logger.warning(
                f"Hardcoded marker positioning detected: {matches[0]}. "
                "Use shape.get_vertices() or shape.get_edge_center() for relative positioning. "
                "Markers positioned with hardcoded coordinates break after shape transformations."
            )
            break  # Only warn once
    
    # Check for missing shape method usage for proper marker positioning
    if any(marker in manim_code for marker in ['angle_marker', 'tick_mark', 'corner_marker',
    'side_marker']):
        if not any(method in manim_code for method in ['get_vertices', 'get_edge_center',
        'get_corner']):
            logger.warning(
                "Shape markers detected but no relative positioning methods used. "
                "Use shape.get_vertices(), shape.get_edge_center() for proper marker placement "
                "relative to transformed shapes."
            )
    
    # Check for content overlap issues - Write() used when ReplacementTransform() would be better
    write_pattern = r'self\.play\(Write\(([^)]+)\)\)'
    replacement_pattern = r'self\.play\(ReplacementTransform\('
    
    write_matches = re.findall(write_pattern, manim_code)
    replacement_count = len(re.findall(replacement_pattern, manim_code))
    
    # If there are many Write() calls but few ReplacementTransform(), warn about potential overlaps
    if len(write_matches) > 3 and replacement_count < 2:
        logger.warning(
            f"Found {len(write_matches)} Write() calls but only {replacement_count} "
            "ReplacementTransform() calls. When replacing text at the same position, use "
            "ReplacementTransform(old_text, new_text) instead of Write(new_text) to avoid "
            "text overlap issues where old text remains visible under new text."
        )
    
    # Check for equation placement that might overlap with tables or axes
    equation_placement_patterns = [
        r'\.move_to\(\[4[,\s]',      # x=4 placement often overlaps with RIGHT-positioned tables
        r'\.move_to\(\[3\.[5-9]',    # x=3.5+ placement might overlap
        r'\.move_to\(\[0[,\s]',      # x=0 placement overlaps y-axis
        r'\.move_to\(\[0\.0[,\s]',   # x=0.0 placement overlaps y-axis
    ]
    table_right_pattern = r'\.next_to\([^,]+,\s*RIGHT'
    
    has_right_table = bool(re.search(table_right_pattern, manim_code))
    
    # Check for y-axis overlap (x=0 placement)
    y_axis_overlap_patterns = [r'\.move_to\(\[0[,\s]', r'\.move_to\(\[0\.0[,\s]']
    for pattern in y_axis_overlap_patterns:
        if re.search(pattern, manim_code):
            logger.warning(
                "Equation placed at x=0 overlaps with y-axis! "
                "Place equations LEFT of y-axis: x≤-2 (e.g., [-2.5, 2.8, 0]) for better visibility"
            )
            break
    
    # Check for table overlap
    for pattern in equation_placement_patterns[:2]:  # Only check x≥3.5 patterns for table overlap
        if has_right_table and re.search(pattern, manim_code):
            logger.warning(
                "Equation placed at x≥3.5 while table is positioned RIGHT of axes - potential "
                "overlap! Place equations in safe zones: left of y-axis (x≤-2), below axes (y=-0.3)"
            )
            break
    
    # Check for y-axis compression (too many units compressed into small space)
    y_range_pattern = r'y_range\s*=\s*\[([^,]+),\s*([^,\]]+)'
    y_length_pattern = r'y_length\s*=\s*(\d+(?:\.\d+)?)'
    
    y_range_match = re.search(y_range_pattern, manim_code)
    y_length_match = re.search(y_length_pattern, manim_code)
    
    if y_range_match and y_length_match:
        try:
            y_min = float(y_range_match.group(1))
            y_max = float(y_range_match.group(2))
            y_length = float(y_length_match.group(1))
            
            y_span = y_max - y_min
            compression_ratio = y_span / y_length
            
            if compression_ratio > 2.5:  # More than 2.5 units per coordinate unit (tightened)
                logger.warning(
                    f"Y-axis may be too compressed: {y_span} units in y_length={y_length} (ratio: "
                    f"{compression_ratio:.1f}:1). For better proportions, consider smaller y_range "
                    "like [-1, {int(y_min + y_length * 2.5)}] or larger y_length for this range."
                )
        except (ValueError, AttributeError):
            pass  # Skip validation if parsing fails
    
    # Check for section spacing issues (titles too close to axes areas)
    title_patterns = [
        r'bonus.*title.*\.move_to\(\[0,\s*2\.[0-2]',     # Bonus titles at y=2.0-2.2 (too close)
        r'title.*\.move_to\(\[0,\s*2\.[0-2]',           # Any title at y=2.0-2.2
        r'\.move_to\(\[0,\s*2\.[0-2],\s*0\]\)[^}]*title', # Pattern matching title positioning
    ]
    
    for pattern in title_patterns:
        if re.search(pattern, manim_code, re.IGNORECASE):
            logger.warning(
                "Section title positioned too close to main animation area (y≤2.2)! "
                "For clear separation, place section titles at y≥3.2 to avoid overlap with axes "
                "content"
            )
            break
    
    # Check for insufficient font sizes in tables
    table_font_patterns = [
        r'element_to_mobject_config.*font_size.*:.*2[0-7]',   # font_size 20-27 (too small)
        r'font_size.*:.*2[0-7].*element_to_mobject_config',   # reversed order
    ]
    
    for pattern in table_font_patterns:
        matches = re.findall(pattern, manim_code)
        if matches:
            logger.warning(
                f"Table font size appears too small: {matches[0][:50]}... "
                "For better readability, use font_size≥28 in table element_to_mobject_config"
            )
    
    # Check for incomplete content tracking (objects created in loops but not tracked for cleanup)
    loop_creation_patterns = [
        r'for\s+\w+\s+in.*?:\s*.*?(Dot\(|MathTex\(|Tex\(|Circle\(|Line\()',
    ]
    
    cleanup_section_pattern = r'main_objects.*?=.*?\[.*?\]'
    
    has_loop_creation = any(re.search(pattern, manim_code, re.DOTALL) \
        for pattern in loop_creation_patterns)
    has_cleanup_section = bool(re.search(cleanup_section_pattern, manim_code))
    
    if has_loop_creation and has_cleanup_section:
        # Check if there are tracking lists for cleanup
        tracking_patterns = [
            r'coord_labels\s*=\s*\[\]',
            r'labels\s*=\s*\[\]',
            r'dots\s*=\s*\[\]',
            r'\.append\(',
        ]
        
        has_tracking = any(re.search(pattern, manim_code) for pattern in tracking_patterns)
        if not has_tracking:
            logger.warning(
                "Objects created in loops detected but no tracking lists found. "
                "Create tracking lists (coord_labels=[], labels=[]) and append objects for proper "
                "cleanup: coord_labels.append(label); main_objects.extend(coord_labels) before "
                "final summary"
            )
    
    # Check for missing content cleanup before final summary
    if any(summary_indicator in manim_code for summary_indicator in ['step1', 'step2', 'step3',
    'step4', 'step5']):
        # Look for proper content cleanup patterns
        cleanup_patterns = [
            r'FadeOut\(.*VGroup.*\*.*objects',  # FadeOut(VGroup(*objects))
            r'FadeOut\(.*axes.*table.*step_text',  # FadeOut explicit objects
            r'self\.remove\(',  # self.remove() calls
        ]
        
        has_cleanup = any(re.search(pattern, manim_code) for pattern in cleanup_patterns)
        if not has_cleanup:
            logger.warning(
                "Final summary detected but no content cleanup found. "
                "MUST remove ALL main animation and explanation objects before summary using "
                "FadeOut(VGroup(*objects)). Failure to clear content causes overlapping text and "
                "confusing animations."
            )
    
    # Check for incorrect Polygon constructor (list instead of unpacked vertices)
    polygon_list_patterns = [
        r'Polygon\(\s*\[\s*\[',  # Polygon([[...]])
        r'Polygon\(\s*\[\s*\[.*?\]\s*,\s*\[.*?\]\s*,\s*\[.*?\]\s*\]',
    ]
    
    for pattern in polygon_list_patterns:
        if re.search(pattern, manim_code):
            raise Exception(
                "Incorrect Polygon constructor: Polygon([list_of_vertices]). "
                "Use Polygon(*vertices) or Polygon(vertex1, vertex2, vertex3, ...). "
                "Passing a list directly causes 'array element with sequence' error."
            )
    
    # Check for incorrect get_edge_center usage with integer indices
    edge_center_int_patterns = [
        r'\.get_edge_center\(\s*\d+\s*\)',  # .get_edge_center(0), .get_edge_center(1), etc.
        r'\.get_edge_center\(\s*[a-zA-Z_]\w*\s*\)(?=.*for.*range)',  # .get_edge_center(j) in a loop
    ]
    
    for pattern in edge_center_int_patterns:
        if re.search(pattern, manim_code):
            raise Exception(
                "Incorrect get_edge_center() usage: get_edge_center(integer). "
                "Use direction vectors like get_edge_center(UP), get_edge_center(DOWN), "
                "or calculate manually: (vertices[i] + vertices[i+1]) / 2. "
                "Using integer indices causes 'int object is not subscriptable' error."
            )
    
    # Check for common LaTeX syntax errors that cause compilation failures
    latex_error_patterns = [
        r'Tex\([^)]*\\text\{[^}]*$',  # Incomplete \text{...} - missing closing brace
        r'Tex\([^)]*\\text\{[^}]*f\(x\)[^}]*$',  # Math expressions inside \text{...}
        r'Tex\([^)]*\\text\{[^}]*\^[^}]*$',  # Exponents inside \text{...}
        r'Tex\([^)]*[^\\]text\{',  # Missing backslash before text
        r'Tex\([^)]*\\text\{[^}]*\\[^}]*$',  # Incomplete LaTeX commands inside \text
    ]
    
    for pattern in latex_error_patterns:
        if re.search(pattern, manim_code):
            raise Exception(
                "Invalid LaTeX syntax detected that will cause 'latex error converting to dvi'. "
                "Common issues: incomplete \\text{...} braces, math expressions inside "
                "\\text{...}, missing backslashes. Use MathTex() for math expressions and ensure "
                "all braces are closed. Example: Tex(r\"\\text{Step 1: Graph from } x = -3 "
                "\\text{ to } x = 3\", color=BLACK)"
            )

def _execute_manim_code(manim_code: str) -> bytes:
    """
    Execute Manim code and return the rendered video as bytes.
    
    Parameters
    ----------
    manim_code : str
        The Manim Python code to execute
        
    Returns
    -------
    bytes
        The rendered video file as bytes
    """
    # Create a temporary directory for our work
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Write the Manim code to a Python file
        manim_file = temp_path / "animation.py"
        with open(manim_file, 'w') as f:
            f.write(manim_code)
        
        # Set up the command to run Manim
        # Using high quality and 30fps for good quality output
        cmd = [
            sys.executable, "-m", "manim", "render",
            str(manim_file),
            "EducationalAnimation",
            "-q", DEFAULT_QUALITY,
            "--fps", str(DEFAULT_FRAME_RATE),
            "--format", "mp4",
            "--output_file", "animation.mp4"
        ]
        
        try:
            # Run Manim to render the animation
            logger.info(f"Running Manim command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Manim execution failed with return code {result.returncode}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                raise Exception(f"Manim rendering failed: {result.stderr}")
            
            # Find the output video file
            # Manim typically creates output in media/videos/animation/[quality]/
            # Quality mapping: 'l'->480p15, 'm'->720p30, 'h'->1080p60, 'p'->1440p60, 'k'->2160p60
            quality_dir_map = {
                'l': '480p15',
                'm': '720p30', 
                'h': '1080p60',
                'p': '1440p60',
                'k': '2160p60'
            }
            
            quality_dir_name = quality_dir_map.get(DEFAULT_QUALITY, '1080p60')
            media_dir = temp_path / "media" / "videos" / "animation" / quality_dir_name
            video_files = list(media_dir.glob("*.mp4"))
            
            if not video_files:
                # Try alternative output locations - check all quality directories
                animation_dir = temp_path / "media" / "videos" / "animation"
                if animation_dir.exists():
                    for quality_dir in animation_dir.iterdir():
                        if quality_dir.is_dir():
                            video_files = list(quality_dir.glob("*.mp4"))
                            if video_files:
                                break
            
            if not video_files:
                raise Exception("No video file found after Manim rendering")
            
            # Read the video file
            video_file = video_files[0]
            logger.info(f"Found rendered video: {video_file}")
            
            with open(video_file, 'rb') as f:
                video_bytes = f.read()
            
            logger.info(f"Successfully rendered video ({len(video_bytes)} bytes)")
            return video_bytes
            
        except subprocess.TimeoutExpired:
            logger.error("Manim execution timed out")
            raise Exception("Animation rendering timed out") from None
        except Exception as e:
            logger.error(f"Error executing Manim: {e}")
            raise

async def generate_manim_animation(prompt: str, max_retries: int = 3,
previous_attempt_errors_and_warnings: str = None) -> str:
    """
    Generate an educational Manim animation and upload it as a video.
    
    Parameters
    ----------
    prompt : str
        Description of the animation to generate
    max_retries : int, default 3
        Maximum number of retry attempts
    previous_attempt_errors_and_warnings : str, optional
        Context from previous failed attempts to help the model avoid repeating errors.
        Should contain validation errors, warnings, or other failure information.
        
    Returns
    -------
    str
        JSON string containing the URL of the generated video
    """
    logger.info(
        f"Generating Manim animation with prompt (attempts remaining: {max_retries}): {prompt}"
    )
    
    try:
        # Generate Manim code
        manim_code = await _generate_manim_code(prompt, previous_attempt_errors_and_warnings)

        logger.info(f"Manim code:\n{manim_code}")
        
        # Execute Manim to render video
        video_bytes = _execute_manim_code(manim_code)
        
        # Upload video to Supabase
        video_url = upload_video_to_supabase(
            video_bytes=video_bytes,
            content_type="video/mp4",
            bucket_name="incept-videos",
            file_extension=".mp4"
        )
        
        result = {
            "animation_url": video_url,
            "status": "success",
            "type": "manim_video"
        }
        
        return json.dumps(result)
        
    except Exception as e:
        if max_retries > 0:
            logger.error(f"Failed to generate Manim animation: {e}")
            # Pass along the current error for the next attempt
            error_context = str(e)
            if previous_attempt_errors_and_warnings:
                # Accumulate previous errors
                error_context = f"{previous_attempt_errors_and_warnings}\n\nAdditional error: " + \
                                f"{error_context}"
            return await generate_manim_animation(prompt, max_retries - 1, error_context)
        else:
            logger.error(f"Failed to generate Manim animation: {e}")
            return json.dumps({
                "animation_url": None,
                "status": "failed",
                "error": str(e),
                "type": "manim_video"
            })

def generate_manim_animation_tool() -> tuple[dict, Callable]:
    """
    Create the Manim animation generation tool specification.
    
    Returns
    -------
    tuple[dict, Callable]
        Tool specification and function
    """
    spec = {
        "type": "function",
        "name": "generate_manim_animation",
        "description": "Generate an educational mathematical animation using Manim Community "
                       "Edition. Creates high-quality videos for mathematical concepts, geometric "
                       "visualizations, function plotting, and educational demonstrations. Returns "
                       "a JSON string containing the URL of the generated video.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Description of the educational animation to generate. Should "
                    "describe the mathematical concept, visualization, or educational "
                    "demonstration desired. For example: 'Show the graphical method for solving a "
                    "system of linear equations' or 'Animate the Pythagorean theorem with a right "
                    "triangle'. Do not specify a duration for the animation - the tool will pick "
                    "an appropriate duration."
                },
                "previous_attempt_errors_and_warnings": {
                    "type": "string",
                    "description": "Optional context from previous failed attempts. Should contain "
                    "validation errors, warnings, or other failure information to help avoid "
                    "repeating the same mistakes. For example: 'Circle radius=2 too large' or "
                    "'Font size too small'."
                }
            },
            "required": ["prompt"]
        }
    }
    return spec, generate_manim_animation
