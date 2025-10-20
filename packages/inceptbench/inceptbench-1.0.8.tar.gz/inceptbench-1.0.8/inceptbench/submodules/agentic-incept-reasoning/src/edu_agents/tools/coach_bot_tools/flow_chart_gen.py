from __future__ import annotations

import logging
from typing import Callable, Dict, List

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.flow_chart import (  # noqa: E402
    create_flowchart,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.flowchart import (  # noqa: E402
    Flowchart,
    FlowchartData,
    FlowchartEdge,
    FlowchartNode,
    ShapeEnum,
)

logger = logging.getLogger("coach_bot_tools.flow_chart")


def generate_coach_bot_flowchart_image(
    nodes: List[Dict],
    edges: List[Dict],
    orientation: str = "horizontal"
) -> str:
    """
    Generate a flowchart diagram with nodes and edges.
    
    Args:
        nodes: List of node dictionaries with 'id', 'label', and 'shape' keys
        edges: List of edge dictionaries with 'from_', 'to', and optional 'label' keys  
        orientation: Flow direction - 'horizontal' (left to right) or 'vertical' (top to bottom)
        
    Returns:
        str: URL to the uploaded flowchart image
    """
    # Use standardized logging
    log_tool_generation("flowchart_image", node_count=len(nodes), edge_count=len(edges),
                        orientation=orientation)
    
    # Convert and validate input dictionaries to Pydantic models
    flowchart_nodes = []
    for node in nodes:
        flowchart_node = FlowchartNode(
            id=node["id"],
            label=node.get("label"),
            shape=ShapeEnum(node["shape"])
        )
        flowchart_nodes.append(flowchart_node)
    
    flowchart_edges = []
    for edge in edges:
        flowchart_edge = FlowchartEdge(
            from_=edge["from_"],
            to=edge["to"],
            label=edge.get("label")
        )
        flowchart_edges.append(flowchart_edge)
    
    # Create flowchart data structure
    flowchart_data = FlowchartData(
        nodes=flowchart_nodes,
        edges=flowchart_edges,
        orientation=orientation
    )
    
    # Create and validate the complete flowchart using Pydantic
    # This validates node/edge relationships and orientation constraints
    flowchart = Flowchart(flowchart=flowchart_data)
    image_file_path = create_flowchart(flowchart)
    
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_flowchart_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for flowchart generation."""
    # Note: This uses an enhanced static spec because the wrapper interface is flattened
    # (takes List[Dict] for nodes/edges) while the Pydantic models use nested objects
    spec = {
        "type": "function",
        "name": "generate_coach_bot_flowchart_image",
        "description": (
            "Generate a flowchart diagram with connected nodes and edges for process "
            "visualization, decision trees, and workflow documentation. Supports different node "
            "shapes for different purposes: rectangles for processes, diamonds for decisions, "
            "ellipses for start/end, and plaintext for annotations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "nodes": {
                    "type": "array",
                    "description": (
                        "List of flowchart nodes defining the process steps, decisions, or "
                        "endpoints. Each node must have a unique ID that other nodes can reference "
                        "in edges."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": (
                                    "Unique identifier for the node (e.g., 'start', 'process1', "
                                    "'decision1', 'end'). Must be referenced in edges to create "
                                    "connections."
                                )
                            },
                            "label": {
                                "type": "string", 
                                "description": (
                                    "Text label displayed inside the node (maximum 50 characters). "
                                    "Should be concise and describe the step or decision. Optional "
                                    "for plaintext nodes."
                                ),
                                "maxLength": 50
                            },
                            "shape": {
                                "type": "string",
                                "enum": ["rectangle", "ellipse", "diamond", "plaintext"],
                                "description": (
                                    "Shape of the node indicating its purpose: "
                                    "'rectangle' for processes/actions, 'ellipse' for start/end "
                                    "points, 'diamond' for decision points, 'plaintext' for "
                                    "labels/annotations."
                                )
                            }
                        },
                        "required": ["id", "shape"]
                    },
                    "minItems": 1,
                    "maxItems": 10
                },
                "edges": {
                    "type": "array",
                    "description": (
                        "List of directed edges connecting the nodes to show process flow. "
                        "Each edge connects two nodes using their IDs and can optionally include "
                        "a label (e.g., 'Yes', 'No', 'Next')."
                    ),
                    "items": {
                        "type": "object", 
                        "properties": {
                            "from_": {
                                "type": "string",
                                "description": (
                                    "ID of the starting node for this edge. Must match an existing "
                                    "node ID."
                                )
                            },
                            "to": {
                                "type": "string",
                                "description": (
                                    "ID of the ending node for this edge. Must match an existing "
                                    "node ID."
                                )
                            },
                            "label": {
                                "type": "string",
                                "description": (
                                    "Optional label for the edge (maximum 40 characters). "
                                    "Useful for decision outcomes like 'Yes', 'No', or process "
                                    "flow indicators."
                                ),
                                "maxLength": 40
                            }
                        },
                        "required": ["from_", "to"]
                    },
                    "minItems": 1,
                    "maxItems": 12
                },
                "orientation": {
                    "type": "string",
                    "enum": ["horizontal", "vertical"],
                    "description": (
                        "Flow direction of the flowchart: 'horizontal' flows left-to-right, "
                        "'vertical' flows top-to-bottom. Default is horizontal."
                    ),
                    "default": "horizontal"
                }
            },
            "required": ["nodes", "edges"]
        }
    }
    return spec, generate_coach_bot_flowchart_image
