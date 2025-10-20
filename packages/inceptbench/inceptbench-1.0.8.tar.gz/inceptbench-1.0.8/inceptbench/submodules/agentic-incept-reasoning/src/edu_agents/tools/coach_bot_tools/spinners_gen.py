from __future__ import annotations

import logging
from typing import Callable, List

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.spinners import (  # noqa: E402
    generate_spinner,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.spinner import (  # noqa: E402
    Spinner,
)

logger = logging.getLogger("coach_bot_tools.spinners")


def generate_coach_bot_spinner_image(
    title: str,
    sections: List[str]
) -> str:
    """
    Generate a probability spinner for teaching chance and probability concepts.
    
    Creates a circular spinner divided into equal sections with category labels.
    Automatically colors sections when color names are used as labels. Useful for
    teaching probability, fractions, and data analysis with engaging themes.
    
    Parameters
    ----------
    title : str
        Clear title that relates to the spinner's content or purpose
    sections : List[str]
        List of section labels (4-10 sections). Available colors that will auto-color 
        the spinner: Red, Blue, Green, Yellow, Pink, Purple. For non-color labels,
        use words with 7 letters or fewer for optimal display.
        
    Returns
    -------
    str
        The URL of the generated spinner image
    """
    
    # Use standardized logging
    log_tool_generation("spinner_image", title=title, sections=sections)
    
    # Create and validate the Spinner stimulus using Pydantic
    spinner_stimulus = Spinner(
        title=title,
        sections=sections
    )
    
    # Generate the image using the spinner function
    image_file_path = generate_spinner(spinner_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_spinner_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for spinner generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_spinner_image",
        description=(
            "Generate a probability spinner for teaching chance and probability concepts. "
            "Creates a circular spinner divided into equal sections with category labels. "
            "Automatically colors sections when color names are used. Useful for teaching "
            "probability, fractions, and data analysis."
        ),
        pydantic_model=Spinner,
        custom_descriptions={
            "title": "Clear title that relates to the spinner's content or purpose",
            "sections": (
                "List of section labels (4-10 sections). Available auto-coloring colors: Red, "
                "Blue, Green, Yellow, Pink, Purple. At least one category must appear 2+ times. "
                "Maximum 5 distinct categories. For best display: use colors or words "
                "≤7 letters (allows 10 sections), otherwise max 8 sections."
            )
        }
    )
    return spec, generate_coach_bot_spinner_image
