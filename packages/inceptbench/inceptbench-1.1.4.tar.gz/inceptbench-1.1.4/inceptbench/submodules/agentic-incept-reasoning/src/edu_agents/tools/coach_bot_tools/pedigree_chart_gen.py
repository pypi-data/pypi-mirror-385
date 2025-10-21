from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.pedigree_chart import (  # noqa: E402
    draw_pedigree_chart,
)

logger = logging.getLogger("coach_bot_tools.pedigree_chart")


# Pydantic models for validation
class PedigreeRelationship(BaseModel):
    """Individual relationship record in a pedigree chart."""
    Person_1: str = Field(..., min_length=1, 
                         description="ID of the first person in the relationship")
    Person_2: Optional[str] = Field(None, min_length=1, 
                                   description="ID of the second person (required for Child and "
                                               "Spouse relations)")
    Relation: str = Field(..., description="Type of relationship between the people")
    Gender: str = Field(..., 
                       description="Gender of Person_1 (M for male, F for female)") 
    affected: bool = Field(..., 
                          description="Whether Person_1 has the trait or condition being tracked")
    
    @model_validator(mode='after')
    def validate_relationship(self):
        # Validate gender
        if self.Gender not in ["M", "F"]:
            raise ValueError(f"Gender must be 'M' or 'F', got '{self.Gender}'")
        
        # Validate relation type
        valid_relations = ["Earliest Ancestor", "Child", "Spouse"]
        if self.Relation not in valid_relations:
            raise ValueError(f"Relation must be one of {valid_relations}, got '{self.Relation}'")
        
        # Person_2 is required for Child and Spouse relations
        if self.Relation in ["Child", "Spouse"]:
            if not self.Person_2:
                raise ValueError(f"Person_2 is required for {self.Relation} relations")
        
        return self


class PedigreeChart(BaseModel):
    """Complete pedigree chart with family relationships and optional caption."""
    ancestry: List[PedigreeRelationship] = Field(..., min_length=1, 
                                                 description="List of family relationships")
    caption: Optional[str] = Field(None, 
                                  description="Optional caption text to display below the chart")
    
    @model_validator(mode='after')
    def validate_chart_consistency(self):
        # Check that we have exactly one earliest ancestor
        earliest_ancestors = [rel for rel in self.ancestry if rel.Relation == "Earliest Ancestor"]
        if len(earliest_ancestors) != 1:
            raise ValueError("Ancestry data must include exactly one 'Earliest Ancestor' relation")
        
        # Verify that all Person_2 references exist as Person_1 somewhere
        all_person_1s = {rel.Person_1 for rel in self.ancestry}
        for relation in self.ancestry:
            if (relation.Relation in ["Child", "Spouse"] and 
                    relation.Person_2 and relation.Person_2 not in all_person_1s):
                raise ValueError(
                    f"Person_2 '{relation.Person_2}' in {relation.Relation} relation "
                    f"must exist as Person_1 in another record"
                )
        
        return self


def generate_coach_bot_pedigree_chart_image(
    ancestry: List[Dict[str, Any]],
    caption: Optional[str] = None
) -> str:
    """
    Generate a family pedigree chart showing hereditary relationships.
    
    Creates a visual family tree diagram showing relationships between family members
    and tracking inherited traits or conditions. Useful for teaching genetics concepts,
    inheritance patterns, and family relationship analysis.
    
    Note: GraphViz warnings about "Illegal value filled for STYLE" in the legend are
    expected and do not affect chart generation - they come from the legend formatting
    in the underlying drawing function.
    
    Parameters
    ----------
    ancestry : List[Dict[str, Any]]
        List of relationship records, each containing:
        - Person_1: ID of the first person  
        - Person_2: ID of the second person (required for Child and Spouse relations)
        - Relation: Type of relationship ('Earliest Ancestor', 'Child', 'Spouse')
        - Gender: Gender of Person_1 ('M' for male, 'F' for female)
        - affected: Boolean indicating if Person_1 has the trait/condition being tracked
    caption : Optional[str]
        Optional caption text to display below the chart
        
    Returns
    -------
    str
        The URL of the generated pedigree chart image
    """
    
    # Use standardized logging
    log_tool_generation("pedigree_chart_image", relationship_count=len(ancestry), 
                       has_caption=caption is not None)
    
    # Create and validate the PedigreeChart using Pydantic
    # This handles all validation: required fields, data types, enums, 
    # one earliest ancestor, Person_2 requirements, logical consistency
    pedigree_chart = PedigreeChart(ancestry=ancestry, caption=caption)
    
    # Prepare the data structure expected by the drawing function
    chart_data = {
        "ancestry": [rel.model_dump() for rel in pedigree_chart.ancestry]
    }
    
    if pedigree_chart.caption:
        chart_data["caption"] = pedigree_chart.caption
    
    # Generate the image using the pedigree chart function
    # Note: GraphViz warnings about "STYLE" attributes in legend are expected
    # and come from the underlying drawing function's HTML table formatting
    image_file_path = draw_pedigree_chart(chart_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_pedigree_chart_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for pedigree chart generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_pedigree_chart_image",
        description=(
            "Generate family pedigree charts for genetics and heredity education. Creates visual "
            "family tree diagrams showing inheritance patterns, genetic relationships, and trait "
            "transmission across generations. Perfect for teaching genetics concepts, hereditary "
            "diseases, Mendelian inheritance, pedigree analysis, and family relationship studies. "
            "Each family member is represented with their gender (squares for males, circles for "
            "females) and trait status (filled shapes for affected individuals, empty for "
            "unaffected). Supports complex family structures with multiple generations, marriages, "
            "and offspring. Ideal for biology lessons, genetics problems, inheritance exercises, "
            "and scientific literacy activities. Note: GraphViz warnings about STYLE attributes "
            "are expected and do not affect chart generation."
        ),
        pydantic_model=PedigreeChart,
        custom_descriptions={
            "ancestry": (
                "List of family relationship records defining the pedigree structure. Each record "
                "represents one person and their relationship to others in the family tree. Must "
                "include exactly one 'Earliest Ancestor' (the starting point of the family tree). "
                "For 'Child' and 'Spouse' relationships, Person_2 must reference an existing "
                "Person_1 to establish the family connection. Educational example: "
                "[{'Person_1': 'A', 'Relation': 'Earliest Ancestor', 'Gender': 'M', "
                "'affected': False}, {'Person_1': 'B', 'Person_2': 'A', 'Relation': 'Spouse', "
                "'Gender': 'F', 'affected': True}, {'Person_1': 'C', 'Person_2': 'A', "
                "'Relation': 'Child', 'Gender': 'M', 'affected': False}]. Perfect for genetics "
                "education."
            ),
            "caption": (
                "Optional educational caption to display below the pedigree chart. Use for "
                "providing context, explaining the genetic trait being tracked, describing "
                "inheritance patterns, or adding instructional guidance for students. "
                "Examples: 'Inheritance of Huntington's Disease', 'Three-Generation Family "
                "Pedigree Showing Autosomal Dominant Trait', 'Pedigree Analysis Exercise'."
            )
        }
    )
    return spec, generate_coach_bot_pedigree_chart_image
