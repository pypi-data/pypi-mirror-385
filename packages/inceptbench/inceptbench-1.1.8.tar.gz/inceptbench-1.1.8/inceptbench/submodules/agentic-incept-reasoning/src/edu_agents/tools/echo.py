from __future__ import annotations
from typing import Tuple, Callable


def echo(content: str) -> str:
    """Simply returns the input content unchanged."""
    return content


def echo_tool() -> Tuple[dict, Callable]:
    """Returns the tool specification and function for the echo tool."""
    spec = {
        "type": "function",
        "name": "echo",
        "description": "Returns the input content unchanged. Useful for outputting intermediate content so that it can be shown to the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The content to echo back."
                }
            },
            "required": ["content"]
        }
    }
    return spec, echo 