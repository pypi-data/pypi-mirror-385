from __future__ import annotations

import logging
from typing import Callable, Dict, Optional, Union

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.equation_tape_diagram import (  # noqa: E402, E501
    draw_equation_tape_diagram,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.equation_tape_diagram import (  # noqa: E402, E501
    AdditionDiagram,
    ComparisonDiagram,
    DivisionDiagram,
    EqualGroupsDiagram,
    EquationTapeDiagramWrapper,
    MultiplicationDiagram,
    SubtractionDiagram,
)

logger = logging.getLogger("coach_bot_tools.equation_tape_diagram")


def generate_coach_bot_equation_tape_diagram_image(
    diagram_type: str,
    diagram_config: Dict[str, Union[str, int, float, Optional[Union[str, int, float]]]]
) -> str:
    """
    Generate an equation tape diagram for visual math problem solving.
    
    Creates tape diagrams (also known as bar models or strip diagrams) to represent
    mathematical relationships visually. Supports addition, subtraction, multiplication,
    division, equal groups, and comparison formats.
    
    Parameters
    ----------
    diagram_type : str
        Type of diagram to create: "addition", "subtraction", "equal_groups", 
        "division", "multiplication", or "comparison"
    diagram_config : Dict[str, Union[str, int, float, Optional[Union[str, int, float]]]]
        Configuration for the specific diagram type. Structure varies by type:
        
        For addition:
        - unknown: "part1", "part2", or "total"
        - part1: Value or None if unknown
        - part2: Value or None if unknown  
        - total: Value or None if unknown
        - variable_symbol: Symbol for unknown (e.g., "x", "?")
        
        For subtraction:
        - unknown: "start", "change", or "result"
        - start: Starting value or None if unknown
        - change: Change value or None if unknown
        - result: Result value or None if unknown
        - variable_symbol: Symbol for unknown
        
        For equal_groups:
        - unknown: "groups", "group_size", or "total"
        - groups: Number of groups or None if unknown
        - group_size: Size of each group or None if unknown
        - total: Total amount or None if unknown
        - variable_symbol: Symbol for unknown
        
        For division:
        - unknown: "dividend", "divisor", or "quotient"
        - dividend: Dividend value or None if unknown
        - divisor: Divisor value or None if unknown
        - quotient: Quotient value or None if unknown
        - variable_symbol: Symbol for unknown
        
        For multiplication:
        - unknown: "factor", "factor2", or "product"
        - factor: First factor or None if unknown
        - factor2: Second factor or None if unknown
        - product: Product value or None if unknown
        - variable_symbol: Symbol for unknown
        
        For comparison:
        - diagram_type: Type of diagrams to compare
        - correct_diagram: Configuration for correct diagram
        - distractor_diagram: Configuration for distractor diagram
        
    Returns
    -------
    str
        The URL of the generated equation tape diagram image
    """
    
    log_tool_generation(
        "generate_coach_bot_equation_tape_diagram_image",
        diagram_type=diagram_type,
        diagram_config=diagram_config
    )
    
    # Create the appropriate diagram object based on type
    if diagram_type == "addition":
        diagram = AdditionDiagram(
            type="addition",
            unknown=diagram_config["unknown"],
            part1=diagram_config.get("part1"),
            part2=diagram_config.get("part2"),
            total=diagram_config.get("total"),
            variable_symbol=diagram_config.get("variable_symbol")
        )
    elif diagram_type == "subtraction":
        diagram = SubtractionDiagram(
            type="subtraction",
            unknown=diagram_config["unknown"],
            start=diagram_config.get("start"),
            change=diagram_config.get("change"),
            result=diagram_config.get("result"),
            variable_symbol=diagram_config.get("variable_symbol")
        )
    elif diagram_type == "equal_groups":
        diagram = EqualGroupsDiagram(
            type="equal_groups",
            unknown=diagram_config["unknown"],
            groups=diagram_config.get("groups"),
            group_size=diagram_config.get("group_size"),
            total=diagram_config.get("total"),
            variable_symbol=diagram_config.get("variable_symbol")
        )
    elif diagram_type == "division":
        diagram = DivisionDiagram(
            type="division",
            unknown=diagram_config["unknown"],
            dividend=diagram_config.get("dividend"),
            divisor=diagram_config.get("divisor"),
            quotient=diagram_config.get("quotient"),
            variable_symbol=diagram_config.get("variable_symbol")
        )
    elif diagram_type == "multiplication":
        diagram = MultiplicationDiagram(
            type="multiplication",
            unknown=diagram_config["unknown"],
            factor=diagram_config.get("factor"),
            factor2=diagram_config.get("factor2"),
            product=diagram_config.get("product"),
            variable_symbol=diagram_config.get("variable_symbol")
        )
    elif diagram_type == "comparison":
        # Handle nested diagram creation for comparison
        correct_config = diagram_config["correct_diagram"]
        distractor_config = diagram_config["distractor_diagram"]
        inner_type = diagram_config["diagram_type"]
        
        # Create nested diagrams based on the inner type
        if inner_type == "addition":
            correct_diagram = AdditionDiagram(type="addition", **correct_config)
            distractor_diagram = AdditionDiagram(type="addition", **distractor_config)
        elif inner_type == "subtraction":
            correct_diagram = SubtractionDiagram(type="subtraction", **correct_config)
            distractor_diagram = SubtractionDiagram(type="subtraction", **distractor_config)
        elif inner_type == "equal_groups":
            correct_diagram = EqualGroupsDiagram(type="equal_groups", **correct_config)
            distractor_diagram = EqualGroupsDiagram(type="equal_groups", **distractor_config)
        elif inner_type == "division":
            correct_diagram = DivisionDiagram(type="division", **correct_config)
            distractor_diagram = DivisionDiagram(type="division", **distractor_config)
        elif inner_type == "multiplication":
            correct_diagram = MultiplicationDiagram(type="multiplication", **correct_config)
            distractor_diagram = MultiplicationDiagram(type="multiplication", **distractor_config)
        else:
            raise ValueError(f"Unsupported inner diagram type for comparison: {inner_type}")
        
        diagram = ComparisonDiagram(
            type="comparison",
            diagram_type=inner_type,
            correct_diagram=correct_diagram,
            distractor_diagram=distractor_diagram
        )
    else:
        raise ValueError(f"Unsupported diagram type: {diagram_type}")
    
    # Wrap the diagram in the required wrapper
    diagram_wrapper = EquationTapeDiagramWrapper(root=diagram)
    
    # Generate the image using the equation tape diagram function
    image_file_path = draw_equation_tape_diagram(diagram_wrapper)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_equation_tape_diagram_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for equation tape diagram generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_equation_tape_diagram_image",
        "description": (
            "Generate equation tape diagrams for visual mathematics problem solving and algebraic "
            "thinking instruction. Creates tape diagrams (also known as bar models, strip "
            "diagrams, or length models) to represent mathematical relationships and unknown "
            "quantities visually. Supports 6 diagram types: addition, subtraction, multiplication, "
            "division, equal groups, and side-by-side comparison exercises. COMPARISON diagrams "
            "show two similar diagrams side-by-side for evaluation, critical thinking, and 'which "
            "is correct?' exercises. Perfect for elementary and middle school mathematics "
            "education, pre-algebra instruction, word problem visualization, assessment creation, "
            "and developing algebraic reasoning skills. Each diagram type requires specifying "
            "which value is unknown (with variable symbol) and validates mathematical constraints."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "diagram_type": {
                    "type": "string",
                    "enum": ["addition", "subtraction", "equal_groups", "division",
                            "multiplication", "comparison"],
                    "description": (
                        "Type of equation tape diagram to create: 'addition' for part-part-whole "
                        "relationships, 'subtraction' for take-away or difference problems, "
                        "'equal_groups' for repeated addition/multiplication grouping, 'division' "
                        "for sharing or partitioning, 'multiplication' for factor-product "
                        "relationships, 'comparison' for side-by-side evaluation exercises showing "
                        "correct vs incorrect diagrams for critical thinking and assessment."
                    )
                },
                "diagram_config": {
                    "type": "object",
                    "description": (
                        "Configuration dictionary for the specific diagram type. CRITICAL: All "
                        "diagram types (addition, subtraction, multiplication, division, "
                        "equal_groups) MUST include 'unknown' field specifying which value is "
                        "missing and 'variable_symbol' for the unknown. Exactly one mathematical "
                        "value should be null to represent the unknown quantity. For comparison "
                        "diagrams, provide 'diagram_type' plus nested 'correct_diagram' and "
                        "'distractor_diagram' configurations (each following the same structure as "
                        "single diagrams)."
                    ),
                    "oneOf": [
                        {
                            "title": "Addition Diagram Configuration",
                            "description": "Part-part-whole addition tape diagram showing two "
                                           "addends combining to form a total",
                            "properties": {
                                "unknown": {
                                    "type": "string",
                                    "enum": ["part1", "part2", "total"],
                                    "description": (
                                        "Which value is unknown in addition. CRITICAL VALIDATION "
                                        "RULES: If unknown='part1' then part1=null AND part2+total "
                                        "must be provided (? + 5 = 12). If unknown='part2' then "
                                        "part2=null AND part1+total must be provided (7 + ? = 15). "
                                        "If unknown='total' then total=null AND part1+part2 must "
                                        "be provided (8 + 6 = ?). Exactly one field should be "
                                        "null, the other two must have numeric values."
                                    )
                                },
                                "part1": {
                                    "type": ["number", "null"],
                                    "description": "First addend value (set to null if this is the "
                                                   "unknown quantity)"
                                },
                                "part2": {
                                    "type": ["number", "null"],
                                    "description": "Second addend value (set to null if this is "
                                                   "the unknown quantity)"
                                },
                                "total": {
                                    "type": ["number", "null"],
                                    "description": "Sum/total value (set to null if this is the "
                                                   "unknown quantity)"
                                },
                                "variable_symbol": {
                                    "type": "string",
                                    "description": "Symbol to represent the unknown value (e.g., "
                                                   "'x', '?', 'n', 'y')"
                                }
                            },
                            "required": ["unknown", "variable_symbol"],
                            "additionalProperties": False
                        },
                        {
                            "title": "Subtraction Diagram Configuration",
                            "description": "Start-change-result subtraction tape diagram showing "
                                           "take-away or difference relationships",
                            "properties": {
                                "unknown": {
                                    "type": "string",
                                    "enum": ["start", "change", "result"],
                                    "description": (
                                        "Which value is unknown in subtraction. CRITICAL "
                                        "VALIDATION RULES: If unknown='start' then start=null AND "
                                        "change+result must be provided (? - 8 = 7). If "
                                        "unknown='change' then change=null AND start+result must "
                                        "be provided (15 - ? = 9). If unknown='result' then "
                                        "result=null AND start+change must be provided "
                                        "(20 - 6 = ?). Exactly one field should be null, the other "
                                        "two must have numeric values."
                                    )
                                },
                                "start": {
                                    "type": ["number", "null"],
                                    "description": "Starting/initial value (set to null if this is "
                                                   "the unknown quantity)"
                                },
                                "change": {
                                    "type": ["number", "null"],
                                    "description": "Amount being subtracted/taken away (set to "
                                                   "null if this is the unknown quantity)"
                                },
                                "result": {
                                    "type": ["number", "null"],
                                    "description": "Final result/difference (set to null if this "
                                                   "is the unknown quantity)"
                                },
                                "variable_symbol": {
                                    "type": "string",
                                    "description": "Symbol to represent the unknown value (e.g., "
                                                   "'x', '?', 'n', 'y')"
                                }
                            },
                            "required": ["unknown", "variable_symbol"],
                            "additionalProperties": False
                        },
                        {
                            "title": "Equal Groups Diagram Configuration",
                            "description": "Equal groups tape diagram for repeated addition and "
                                           "early multiplication concepts",
                            "properties": {
                                "unknown": {
                                    "type": "string",
                                    "enum": ["groups", "group_size", "total"],
                                    "description": (
                                        "Which value is unknown in equal groups. CRITICAL "
                                        "VALIDATION RULES: If unknown='groups' then groups=null "
                                        "AND group_size+total must be provided (? groups of 4 = "
                                        "20). If unknown='group_size' then group_size=null AND "
                                        "groups+total must be provided (5 groups of ? = 30). "
                                        "If unknown='total' then total=null AND groups+group_size "
                                        "must be provided (3 groups of 8 = ?). Exactly one field "
                                        "should be null, the other two must have numeric values."
                                    )
                                },
                                "groups": {
                                    "type": ["number", "null"],
                                    "description": "Number of equal groups (set to null if this is "
                                                   "the unknown quantity)"
                                },
                                "group_size": {
                                    "type": ["number", "null"],
                                    "description": "Number of items in each group (set to null if "
                                                   "this is the unknown quantity)"
                                },
                                "total": {
                                    "type": ["number", "null"],
                                    "description": "Total number of items across all groups (set "
                                                   "to null if this is the unknown quantity)"
                                },
                                "variable_symbol": {
                                    "type": "string",
                                    "description": "Symbol to represent the unknown value (e.g., "
                                                   "'x', '?', 'n', 'y')"
                                }
                            },
                            "required": ["unknown", "variable_symbol"],
                            "additionalProperties": False
                        },
                        {
                            "title": "Division Diagram Configuration",
                            "description": "Division tape diagram showing partitioning or sharing "
                                           "relationships",
                            "properties": {
                                "unknown": {
                                    "type": "string",
                                    "enum": ["dividend", "divisor", "quotient"],
                                    "description": (
                                        "Which value is unknown in division. CRITICAL VALIDATION"
                                        "RULES: If unknown='dividend' then dividend=null AND "
                                        "divisor+quotient must be provided (? ÷ 6 = 8). If "
                                        "unknown='divisor' then divisor=null AND dividend+quotient "
                                        "must be provided (48 ÷ ? = 6). If unknown='quotient' then "
                                        "quotient=null AND dividend+divisor must be provided (36 ÷ "
                                        "4 = ?). Exactly one field should be null, the other two "
                                        "must have numeric values."
                                    )
                                },
                                "dividend": {
                                    "type": ["number", "null"],
                                    "description": "Total amount being divided (set to null if "
                                                   "this is the unknown quantity)"
                                },
                                "divisor": {
                                    "type": ["number", "null"],
                                    "description": "Number of groups or group size (set to null if "
                                                   "this is the unknown quantity)"
                                },
                                "quotient": {
                                    "type": ["number", "null"],
                                    "description": "Result per group or number of groups (set to "
                                                   "null if this is the unknown quantity)"
                                },
                                "variable_symbol": {
                                    "type": "string",
                                    "description": "Symbol to represent the unknown value (e.g., "
                                                   "'x', '?', 'n', 'y')"
                                }
                            },
                            "required": ["unknown", "variable_symbol"],
                            "additionalProperties": False
                        },
                        {
                            "title": "Multiplication Diagram Configuration",
                            "description": "Multiplication tape diagram showing factor-product "
                                           "relationships and scaling",
                            "properties": {
                                "unknown": {
                                    "type": "string",
                                    "enum": ["factor", "product"],
                                    "description": (
                                        "Which value is unknown in multiplication. CRITICAL "
                                        "VALIDATION RULES: If unknown='factor' then factor2=null "
                                        "AND factor+product must be provided (6 × ? = 42). If "
                                        "unknown='product' then product=null AND factor+factor2 "
                                        "must be provided (9 × 6 = ?). NOTE: The drawing function "
                                        "only supports unknown='factor' (meaning factor2 missing) "
                                        "and unknown='product'. It does not support "
                                        "unknown='factor2' (factor missing)."
                                    )
                                },
                                "factor": {
                                    "type": ["number", "null"],
                                    "description": "First factor/multiplier (set to null if this "
                                                   "is the unknown quantity)"
                                },
                                "factor2": {
                                    "type": ["number", "null"],
                                    "description": "Second factor/multiplicand (set to null if "
                                                   "this is the unknown quantity)"
                                },
                                "product": {
                                    "type": ["number", "null"],
                                    "description": "Product/result of multiplication (set to null "
                                                   "if this is the unknown quantity)"
                                },
                                "variable_symbol": {
                                    "type": "string",
                                    "description": "Symbol to represent the unknown value (e.g., "
                                                   "'x', '?', 'n', 'y')"
                                }
                            },
                            "required": ["unknown", "variable_symbol"],
                            "additionalProperties": False
                        },
                        {
                            "title": "Comparison Diagram Configuration",
                            "description": "Side-by-side comparison of two tape diagrams for "
                                           "evaluation and critical thinking exercises. Creates "
                                           "'Diagram A' vs 'Diagram B' for 'which is correct?' "
                                           "type questions. Perfect for assessment, error "
                                           "analysis, and teaching students to identify correct vs "
                                           "incorrect mathematical representations.",
                            "properties": {
                                "diagram_type": {
                                    "type": "string",
                                    "enum": ["addition", "subtraction", "equal_groups", "division",
                                            "multiplication"],
                                    "description": (
                                        "Type of mathematical operation for both diagrams being "
                                        "compared. Both diagrams must be of the same type (e.g., "
                                        "both addition, both multiplication) to enable meaningful "
                                        "comparison and evaluation exercises. NOTE: For "
                                        "multiplication comparisons, only unknown='factor' and "
                                        "unknown='product' are supported."
                                    )
                                },
                                "correct_diagram": {
                                    "type": "object",
                                    "description": (
                                        "Configuration for the mathematically correct diagram "
                                        "(labeled as 'Diagram A'). MUST include 'unknown' field "
                                        "and 'variable_symbol' plus the mathematical values for "
                                        "the specified diagram_type. Example for addition: "
                                        "{\"unknown\": \"part1\", \"variable_symbol\": \"x\", "
                                        "\"part1\": null, \"part2\": 5, \"total\": 12}. "
                                        "This represents the correct mathematical relationship."
                                    )
                                },
                                "distractor_diagram": {
                                    "type": "object",
                                    "description": (
                                        "Configuration for the incorrect/distractor diagram "
                                        "(labeled as 'Diagram B'). MUST include 'unknown' field "
                                        "and 'variable_symbol' plus mathematical values for the "
                                        "specified diagram_type, but with incorrect relationships. "
                                        "Example: {\"unknown\": \"part1\", \"variable_symbol\": "
                                        "\"x\", \"part1\": null, \"part2\": 5, \"total\": 13}. "
                                        "Used to test student critical evaluation skills."
                                    )
                                }
                            },
                            "required": ["diagram_type", "correct_diagram", "distractor_diagram"],
                            "additionalProperties": False
                        }
                    ]
                }
            },
            "required": ["diagram_type", "diagram_config"]
        }
    }
    return spec, generate_coach_bot_equation_tape_diagram_image
