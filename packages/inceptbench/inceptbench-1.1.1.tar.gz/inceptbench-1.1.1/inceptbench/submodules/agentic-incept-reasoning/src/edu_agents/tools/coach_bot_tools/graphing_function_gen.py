from __future__ import annotations

import logging
from typing import Callable, Optional

from .coach_bot_utils import (
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.graphing_function import (  # noqa: E402, E501
    draw_graphing_function,
    draw_graphing_function_quadrant_one,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.graphing_function_model import (  # noqa: E402, E501
    GraphingFunction,
    GraphingFunctionQuadrantOne,
)

logger = logging.getLogger("coach_bot_tools.graphing_function_gen")


# Linear Function
def generate_coach_bot_linear_function_image(a: float, b: Optional[float] = None) -> str:
    """
    Generate a linear function graph: y = ax + b.
    
    Creates a mathematical graph of a linear function for educational purposes.
    Perfect for teaching slope-intercept form, linear relationships, and 
    coordinate graphing concepts in algebra and pre-calculus.
    
    Parameters
    ----------
    a : float
        Coefficient 'a' (slope) - must be between -19.99 and 19.99
    b : Optional[float]
        Coefficient 'b' (y-intercept) - must be between -19.99 and 19.99
        
    Returns
    -------
    str
        The URL of the generated linear function graph image
    """
    
    log_tool_generation("generate_coach_bot_linear_function_image", a=a, b=b)
    
    # Create GraphingFunction with function_type set to linear
    function_data = GraphingFunction(function_type="linear", a=a, b=b)
    
    # Generate the image using the graphing function
    image_file_path = draw_graphing_function(function_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)

# Quadratic Function  
def generate_coach_bot_quadratic_function_image(a: float, c: float,
b: Optional[float] = None) -> str:
    """
    Generate a quadratic function graph: y = ax² + bx + c.
    
    Creates a mathematical graph of a quadratic function (parabola) for educational 
    purposes. Perfect for teaching vertex form, axis of symmetry, and quadratic 
    relationships in algebra and pre-calculus.
    
    Parameters
    ----------
    a : float
        Coefficient 'a' (determines parabola direction and width) - must be between -19.99 and 19.99
    c : float
        Coefficient 'c' (y-intercept) - must be between -19.99 and 19.99
    b : Optional[float]
        Coefficient 'b' (affects axis of symmetry) - must be between -19.99 and 19.99
        
    Returns
    -------
    str
        The URL of the generated quadratic function graph image
    """
    
    log_tool_generation("generate_coach_bot_quadratic_function_image", a=a, c=c, b=b)
    
    # Create GraphingFunction with function_type set to quadratic
    function_data = GraphingFunction(function_type="quadratic", a=a, c=c, b=b)
    
    # Generate the image using the graphing function
    image_file_path = draw_graphing_function(function_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)

# Exponential Function
def generate_coach_bot_exponential_function_image(a: float, b: Optional[float] = None) -> str:
    """
    Generate an exponential function graph: y = a * e^(bx).
    
    Creates a mathematical graph of an exponential function for educational purposes.
    Perfect for teaching exponential growth and decay, natural logarithms, and
    advanced algebra concepts including population models and compound interest.
    
    Parameters
    ----------
    a : float
        Coefficient 'a' (vertical scaling factor) - must be between -19.99 and 19.99
    b : Optional[float]
        Coefficient 'b' (growth/decay rate) - must be between -19.99 and 19.99
        
    Returns
    -------
    str
        The URL of the generated exponential function graph image
    """
    
    log_tool_generation("generate_coach_bot_exponential_function_image", a=a, b=b)
    
    # Create GraphingFunction with function_type set to exponential
    function_data = GraphingFunction(function_type="exponential", a=a, b=b)
    
    # Generate the image using the graphing function
    image_file_path = draw_graphing_function(function_data)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)

# Cubic Function
def generate_coach_bot_cubic_function_image(a: float, d: float, b: Optional[float] = None,
c: Optional[float] = None) -> str:
    """Generate a cubic function graph: y = ax³ + bx² + cx + d"""
    logger.info("Generating cubic function graph")
    params = {"function_type": "cubic", "a": a, "d": d}
    if b is not None:
        params["b"] = b
    if c is not None:
        params["c"] = c
    function_data = GraphingFunction(**params)
    image_file_path = draw_graphing_function(function_data)
    return upload_coach_bot_image(image_file_path)

# Square Root Function
def generate_coach_bot_square_root_function_image(a: float, b: Optional[float] = None) -> str:
    """Generate a square root function graph: y = a * √(x + b)"""
    logger.info("Generating square root function graph")
    params = {"function_type": "square_root", "a": a}
    if b is not None:
        params["b"] = b
    function_data = GraphingFunction(**params)
    image_file_path = draw_graphing_function(function_data)
    return upload_coach_bot_image(image_file_path)

# Rational Function
def generate_coach_bot_rational_function_image(a: float, b: Optional[float] = None) -> str:
    """Generate a rational function graph: y = a/x + b"""
    logger.info("Generating rational function graph")
    params = {"function_type": "rational", "a": a}
    if b is not None:
        params["b"] = b
    function_data = GraphingFunction(**params)
    image_file_path = draw_graphing_function(function_data)
    return upload_coach_bot_image(image_file_path)

# Circle
def generate_coach_bot_circle_function_image(a: float, radius: float) -> str:
    """Generate a circle graph: (x-a)² + y² = radius²"""
    logger.info("Generating circle graph")
    params = {"function_type": "circle", "a": a, "radius": radius}
    function_data = GraphingFunction(**params)
    image_file_path = draw_graphing_function(function_data)
    return upload_coach_bot_image(image_file_path)

# Sideways Parabola
def generate_coach_bot_sideways_parabola_function_image(a: float, b: Optional[float] = None) -> str:
    """Generate a sideways parabola graph: x = ay² + b"""
    logger.info("Generating sideways parabola graph")
    params = {"function_type": "sideways_parabola", "a": a}
    if b is not None:
        params["b"] = b
    function_data = GraphingFunction(**params)
    image_file_path = draw_graphing_function(function_data)
    return upload_coach_bot_image(image_file_path)

# Hyperbola
def generate_coach_bot_hyperbola_function_image(a: float, x_radius: float, y_radius: float) -> str:
    """Generate a hyperbola graph"""
    logger.info("Generating hyperbola graph")
    params = {"function_type": "hyperbola", "a": a, "x_radius": x_radius, "y_radius": y_radius}
    function_data = GraphingFunction(**params)
    image_file_path = draw_graphing_function(function_data)
    return upload_coach_bot_image(image_file_path)

# Ellipse
def generate_coach_bot_ellipse_function_image(a: float, x_radius: float, y_radius: float) -> str:
    """Generate an ellipse graph"""
    logger.info("Generating ellipse graph")
    params = {"function_type": "ellipse", "a": a, "x_radius": x_radius, "y_radius": y_radius}
    function_data = GraphingFunction(**params)
    image_file_path = draw_graphing_function(function_data)
    return upload_coach_bot_image(image_file_path)


# Quadrant I Functions - Restricted to positive x and y values

def generate_coach_bot_linear_function_quadrant_one_image(a: float,
b: Optional[float] = None) -> str:
    """Generate a linear function graph in quadrant I: y = ax + b"""
    logger.info("Generating linear function graph (quadrant I)")
    params = {"function_type": "linear", "a": a}
    if b is not None:
        params["b"] = b
    function_data = GraphingFunctionQuadrantOne(**params)
    image_file_path = draw_graphing_function_quadrant_one(function_data)
    return upload_coach_bot_image(image_file_path)

def generate_coach_bot_quadratic_function_quadrant_one_image(a: float, c: float,
b: Optional[float] = None) -> str:
    """Generate a quadratic function graph in quadrant I: y = ax² + bx + c"""
    logger.info("Generating quadratic function graph (quadrant I)")
    params = {"function_type": "quadratic", "a": a, "c": c}
    if b is not None:
        params["b"] = b
    function_data = GraphingFunctionQuadrantOne(**params)
    image_file_path = draw_graphing_function_quadrant_one(function_data)
    return upload_coach_bot_image(image_file_path)

def generate_coach_bot_exponential_function_quadrant_one_image(a: float,
b: Optional[float] = None) -> str:
    """Generate an exponential function graph in quadrant I: y = a * e^(bx)"""
    logger.info("Generating exponential function graph (quadrant I)")
    params = {"function_type": "exponential", "a": a}
    if b is not None:
        params["b"] = b
    function_data = GraphingFunctionQuadrantOne(**params)
    image_file_path = draw_graphing_function_quadrant_one(function_data)
    return upload_coach_bot_image(image_file_path)

def generate_coach_bot_cubic_function_quadrant_one_image(a: float, d: float,
b: Optional[float] = None, c: Optional[float] = None) -> str:
    """Generate a cubic function graph in quadrant I: y = ax³ + bx² + cx + d"""
    logger.info("Generating cubic function graph (quadrant I)")
    params = {"function_type": "cubic", "a": a, "d": d}
    if b is not None:
        params["b"] = b
    if c is not None:
        params["c"] = c
    function_data = GraphingFunctionQuadrantOne(**params)
    image_file_path = draw_graphing_function_quadrant_one(function_data)
    return upload_coach_bot_image(image_file_path)

def generate_coach_bot_square_root_function_quadrant_one_image(a: float,
b: Optional[float] = None) -> str:
    """Generate a square root function graph in quadrant I: y = a * √(x + b)"""
    logger.info("Generating square root function graph (quadrant I)")
    params = {"function_type": "square_root", "a": a}
    if b is not None:
        params["b"] = b
    function_data = GraphingFunctionQuadrantOne(**params)
    image_file_path = draw_graphing_function_quadrant_one(function_data)
    return upload_coach_bot_image(image_file_path)

def generate_coach_bot_rational_function_quadrant_one_image(a: float,
b: Optional[float] = None) -> str:
    """Generate a rational function graph in quadrant I: y = a/x + b"""
    logger.info("Generating rational function graph (quadrant I)")
    params = {"function_type": "rational", "a": a}
    if b is not None:
        params["b"] = b
    function_data = GraphingFunctionQuadrantOne(**params)
    image_file_path = draw_graphing_function_quadrant_one(function_data)
    return upload_coach_bot_image(image_file_path)


# Tool specifications for individual function types

# Linear function tools
def generate_coach_bot_linear_function_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for linear function generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_linear_function_image",
        "description": (
            "Generate a linear function graph: y = ax + b. Creates mathematical "
            "graphs for teaching slope-intercept form, linear relationships, and "
            "coordinate graphing concepts in algebra and pre-calculus education."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number", 
                    "description": (
                        "Coefficient 'a' representing the slope of the line. Determines how "
                        "steep the line is and its direction (positive slopes rise, negative "
                        "slopes fall). Must be between -19.99 and 19.99 for optimal visualization."
                    ), 
                    "minimum": -19.99, 
                    "maximum": 19.99
                },
                "b": {
                    "type": "number", 
                    "description": (
                        "Coefficient 'b' representing the y-intercept of the line. This is where "
                        "the line crosses the y-axis. Optional parameter that defaults to 0. "
                        "Must be between -19.99 and 19.99 for optimal visualization."
                    ), 
                    "minimum": -19.99, 
                    "maximum": 19.99
                }
            },
            "required": ["a"]
        }
    }
    return spec, generate_coach_bot_linear_function_image

def generate_coach_bot_quadratic_function_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_quadratic_function_image",
        "description": "Generate a quadratic function graph: y = ax² + bx + c",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (parabola shape)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "c": {
                    "type": "number",
                    "description": "Coefficient 'c' (y-intercept)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (linear term)",
                    "minimum": -19.99,
                    "maximum": 19.99
                }
            },
            "required": ["a", "c"]
        }
    }
    return spec, generate_coach_bot_quadratic_function_image

def generate_coach_bot_exponential_function_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_exponential_function_image",
        "description": "Generate an exponential function graph: y = a * e^(bx)",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (amplitude)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (growth rate)",
                    "minimum": -19.99,
                    "maximum": 19.99
                }
            },
            "required": ["a"]
        }
    }
    return spec, generate_coach_bot_exponential_function_image

def generate_coach_bot_cubic_function_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_cubic_function_image",
        "description": "Generate a cubic function graph: y = ax³ + bx² + cx + d",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (cubic term)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "d": {
                    "type": "number",
                    "description": "Coefficient 'd' (y-intercept)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (quadratic term)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "c": {
                    "type": "number",
                    "description": "Coefficient 'c' (linear term)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
            },
            "required": ["a", "d"]
        }
    }
    return spec, generate_coach_bot_cubic_function_image

def generate_coach_bot_square_root_function_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_square_root_function_image",
        "description": "Generate a square root function graph: y = a * √(x + b)",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (amplitude)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (horizontal shift)",
                    "minimum": -19.99,
                    "maximum": 19.99
                }
            },
            "required": ["a"]
        }
    }
    return spec, generate_coach_bot_square_root_function_image

def generate_coach_bot_rational_function_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_rational_function_image",
        "description": "Generate a rational function graph: y = a/x + b",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (numerator)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (vertical shift)",
                    "minimum": -19.99,
                    "maximum": 19.99
                }
            },
            "required": ["a"]
        }
    }
    return spec, generate_coach_bot_rational_function_image

def generate_coach_bot_circle_function_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_circle_function_image",
        "description": "Generate a circle graph: (x-a)² + y² = radius²",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Horizontal center position",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "radius": {
                    "type": "number",
                    "description": "Circle radius",
                    "minimum": 0.1,
                    "maximum": 14.99
                }
            },
            "required": ["a", "radius"]
        }
    }
    return spec, generate_coach_bot_circle_function_image

def generate_coach_bot_sideways_parabola_function_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_sideways_parabola_function_image",
        "description": "Generate a sideways parabola graph: x = ay² + b",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (parabola shape)",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (horizontal shift)",
                    "minimum": -19.99,
                    "maximum": 19.99
                }
            },
            "required": ["a"]
        }
    }
    return spec, generate_coach_bot_sideways_parabola_function_image

def generate_coach_bot_hyperbola_function_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_hyperbola_function_image",
        "description": "Generate a hyperbola graph",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a'",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "x_radius": {
                    "type": "number",
                    "description": "Horizontal radius",
                    "minimum": 0.1,
                    "maximum": 14.99
                },
                "y_radius": {
                    "type": "number",
                    "description": "Vertical radius",
                    "minimum": 0.1,
                    "maximum": 14.99
                }
            },
            "required": ["a", "x_radius", "y_radius"]
        }
    }
    return spec, generate_coach_bot_hyperbola_function_image

def generate_coach_bot_ellipse_function_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_ellipse_function_image",
        "description": "Generate an ellipse graph",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a'",
                    "minimum": -19.99,
                    "maximum": 19.99
                },
                "x_radius": {
                    "type": "number",
                    "description": "Horizontal radius",
                    "minimum": 0.1,
                    "maximum": 14.99
                },
                "y_radius": {
                    "type": "number",
                    "description": "Vertical radius",
                    "minimum": 0.1,
                    "maximum": 14.99
                }
            },
            "required": ["a", "x_radius", "y_radius"]
        }
    }
    return spec, generate_coach_bot_ellipse_function_image

# Quadrant I function tools
def generate_coach_bot_linear_function_quadrant_one_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_linear_function_quadrant_one_image",
        "description": "Generate a linear function graph in quadrant I: y = ax + b",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (slope)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (y-intercept)",
                    "minimum": -14.99,
                    "maximum": 14.99
                }
            },
            "required": ["a"]
        }
    }
    return spec, generate_coach_bot_linear_function_quadrant_one_image

def generate_coach_bot_quadratic_function_quadrant_one_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_quadratic_function_quadrant_one_image",
        "description": "Generate a quadratic function graph in quadrant I: y = ax² + bx + c",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (parabola shape)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
                "c": {
                    "type": "number",
                    "description": "Coefficient 'c' (y-intercept)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (linear term)",
                    "minimum": -14.99,
                    "maximum": 14.99
                }
            },
            "required": ["a", "c"]
        }
    }
    return spec, generate_coach_bot_quadratic_function_quadrant_one_image

def generate_coach_bot_exponential_function_quadrant_one_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_exponential_function_quadrant_one_image",
        "description": "Generate an exponential function graph in quadrant I: y = a * e^(bx)",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (amplitude)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (growth rate)",
                    "minimum": -14.99,
                    "maximum": 14.99
                }
            },
            "required": ["a"]
        }
    }
    return spec, generate_coach_bot_exponential_function_quadrant_one_image

def generate_coach_bot_cubic_function_quadrant_one_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_cubic_function_quadrant_one_image",
        "description": "Generate a cubic function graph in quadrant I: y = ax³ + bx² + cx + d",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (cubic term)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
                "d": {
                    "type": "number",
                    "description": "Coefficient 'd' (y-intercept)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (quadratic term)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
                "c": {
                    "type": "number",
                    "description": "Coefficient 'c' (linear term)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
            },
            "required": ["a", "d"]
        }
    }
    return spec, generate_coach_bot_cubic_function_quadrant_one_image

def generate_coach_bot_square_root_function_quadrant_one_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_square_root_function_quadrant_one_image",
        "description": "Generate a square root function graph in quadrant I: y = a * √(x + b)",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (amplitude)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (horizontal shift)",
                    "minimum": -14.99,
                    "maximum": 14.99
                }
            },
            "required": ["a"]
        }
    }
    return spec, generate_coach_bot_square_root_function_quadrant_one_image

def generate_coach_bot_rational_function_quadrant_one_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_coach_bot_rational_function_quadrant_one_image",
        "description": "Generate a rational function graph in quadrant I: y = a/x + b",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coefficient 'a' (numerator)",
                    "minimum": -14.99,
                    "maximum": 14.99
                },
                "b": {
                    "type": "number",
                    "description": "Coefficient 'b' (vertical shift)",
                    "minimum": -14.99,
                    "maximum": 14.99
                }
            },
            "required": ["a"]
        }
    }
    return spec, generate_coach_bot_rational_function_quadrant_one_image
