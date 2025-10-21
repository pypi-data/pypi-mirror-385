from __future__ import annotations

import logging
from typing import Callable, Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)

def generate_svg_shape(
    shape_type: str,
    x: float,
    y: float,
    size: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    radius: Optional[float] = None,
    color: str = "black",
    fill: str = "none",
    stroke_width: float = 2,
    rotation: float = 0,
    points: Optional[List[Tuple[float, float]]] = None,
    opacity: float = 1.0,
    template: bool = False,
    **kwargs
) -> str:
    """
    Generate SVG code for a shape based on high-level parameters.
    
    Parameters
    ----------
    shape_type : str
        Type of shape ('circle', 'rect', 'square', 'line', 'polygon', 'path', etc.)
    x : float
        X-coordinate for the shape's position
    y : float
        Y-coordinate for the shape's position
    size : Optional[float], default None
        Size parameter for shapes like squares
    width : Optional[float], default None
        Width for shapes like rectangles
    height : Optional[float], default None
        Height for shapes like rectangles
    radius : Optional[float], default None
        Radius for circles and rounded corners
    color : str, default "black"
        Stroke color for the shape
    fill : str, default "none"
        Fill color for the shape. Use "none" for transparent.
    stroke_width : float, default 2
        Width of the shape's outline
    rotation : float, default 0
        Rotation angle in degrees
    points : Optional[List[Tuple[float, float]]], default None
        List of (x,y) points for polygon or polyline
    opacity : float, default 1.0
        Opacity of the shape (0.0 to 1.0)
    template : bool, default False
        If True, returns a template with placeholder attributes that can be replaced
    **kwargs
        Additional shape-specific parameters
        
    Returns
    -------
    str
        SVG code snippet for the requested shape
    """
    logger.info(f"Generating SVG code for shape: {shape_type}")
    
    # Common attributes for all shapes
    if template:
        common_attrs = 'stroke="{color}" stroke-width="{stroke_width}" fill="{fill}" opacity="{opacity}"'
        transform = ' transform="rotate({rotation} {x} {y})"' if rotation != 0 else ''
    else:
        common_attrs = f'stroke="{color}" stroke-width="{stroke_width}" fill="{fill}" opacity="{opacity}"'
        transform = f' transform="rotate({rotation} {x} {y})"' if rotation != 0 else ''
    
    # Generate shape-specific SVG code
    if shape_type.lower() == 'circle':
        if radius is None:
            if size is not None:
                radius = size / 2
            else:
                radius = 10  # Default radius
                
        if template:
            return f'<circle cx="{{x}}" cy="{{y}}" r="{radius}" {common_attrs}{transform} />'
        else:
            return f'<circle cx="{x}" cy="{y}" r="{radius}" {common_attrs}{transform} />'
    
    elif shape_type.lower() == 'rect' or shape_type.lower() == 'rectangle':
        w = width if width is not None else (size if size is not None else 20)
        h = height if height is not None else (size if size is not None else 20)
        rx = kwargs.get('rx', 0)  # Rounded corner x-radius
        ry = kwargs.get('ry', 0)  # Rounded corner y-radius
        
        if template:
            return f'<rect x="{{x}}" y="{{y}}" width="{w}" height="{h}" rx="{rx}" ry="{ry}" {common_attrs}{transform} />'
        else:
            return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{ry}" {common_attrs}{transform} />'
    
    elif shape_type.lower() == 'square':
        s = size if size is not None else 20
        
        if template:
            return f'<rect x="{{x}}" y="{{y}}" width="{s}" height="{s}" {common_attrs}{transform} />'
        else:
            return f'<rect x="{x}" y="{y}" width="{s}" height="{s}" {common_attrs}{transform} />'
    
    elif shape_type.lower() == 'line':
        if template:
            x2 = kwargs.get('x2', "{{x2}}")
            y2 = kwargs.get('y2', "{{y2}}")
            return f'<line x1="{{x}}" y1="{{y}}" x2="{x2}" y2="{y2}" {common_attrs}{transform} />'
        else:
            x2 = kwargs.get('x2', x + (width if width is not None else 50))
            y2 = kwargs.get('y2', y + (height if height is not None else 0))
            return f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" {common_attrs}{transform} />'
    
    elif shape_type.lower() == 'polygon' or shape_type.lower() == 'polyline':
        if points is None or len(points) < 2:
            if template:
                points_str = "{{points}}"
            else:
                raise ValueError("Points list is required for polygon/polyline and must contain at least 2 points")
        else:
            points_str = ' '.join([f"{px},{py}" for px, py in points])
        
        return f'<{shape_type.lower()} points="{points_str}" {common_attrs}{transform} />'
    
    elif shape_type.lower() == 'ellipse':
        rx = width / 2 if width is not None else (size / 2 if size is not None else 15)
        ry = height / 2 if height is not None else (size / 2 if size is not None else 10)
        
        if template:
            return f'<ellipse cx="{{x}}" cy="{{y}}" rx="{rx}" ry="{ry}" {common_attrs}{transform} />'
        else:
            return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" {common_attrs}{transform} />'
    
    elif shape_type.lower() == 'path':
        if template:
            path_data = kwargs.get('d', "{{d}}")
        else:
            path_data = kwargs.get('d', '')
            if not path_data:
                raise ValueError("Path data ('d' parameter) is required for path shapes")
                
        return f'<path d="{path_data}" {common_attrs}{transform} />'
    
    elif shape_type.lower() == 'text':
        text_content = kwargs.get('text', "{{text}}" if template else '')
        font_size = kwargs.get('font_size', 12)
        font_family = kwargs.get('font_family', 'Arial')
        text_anchor = kwargs.get('text_anchor', 'start')  # start, middle, end
        
        # For text, fill is usually the text color and stroke might be none
        text_attrs = f'font-family="{font_family}" font-size="{font_size}" text-anchor="{text_anchor}"'
        
        if template:
            return f'<text x="{{x}}" y="{{y}}" {text_attrs} fill="{{color}}" stroke="{{fill}}" stroke-width="{{stroke_width}}" opacity="{{opacity}}"{transform}>{{text_content}}</text>'
        else:
            return f'<text x="{x}" y="{y}" {text_attrs} fill="{color}" stroke="{fill}" stroke-width="{stroke_width}" opacity="{opacity}"{transform}>{text_content}</text>'
    
    elif shape_type.lower() == 'triangle':
        # Equilateral triangle by default
        s = size if size is not None else 20
        h = s * 0.866  # Height of an equilateral triangle (√3/2 * side)
        
        if template:
            center_x = "{{x}}"
            center_y = "{{y}}"
            points = [
                (f"{{{center_x}}}", f"{{{center_y}}} - {h/2}"),
                (f"{{{center_x}}} - {s/2}", f"{{{center_y}}} + {h/2}"),
                (f"{{{center_x}}} + {s/2}", f"{{{center_y}}} + {h/2}")
            ]
            points_str = ' '.join([f"{px},{py}" for px, py in points])
        else:
            points = [
                (x, y - h/2),           # Top
                (x - s/2, y + h/2),     # Bottom left
                (x + s/2, y + h/2)      # Bottom right
            ]
            points_str = ' '.join([f"{px},{py}" for px, py in points])
            
        return f'<polygon points="{points_str}" {common_attrs}{transform} />'
    
    else:
        raise ValueError(f"Unsupported shape type: {shape_type}")


def apply_template_values(template: str, **kwargs) -> str:
    """
    Replace placeholders in a template with actual values.
    
    Parameters
    ----------
    template : str
        SVG template with placeholders in curly braces
    **kwargs : dict
        Key-value pairs for replacing placeholders
        
    Returns
    -------
    str
        The template with placeholders replaced by values
    """
    result = template
    for key, value in kwargs.items():
        placeholder = "{" + key + "}"
        result = result.replace(placeholder, str(value))
    return result


def batch_generate_shapes(
    shape_template: str,
    positions: List[Tuple[float, float]],
    attributes: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate multiple instances of a shape template with different positions and attributes.
    
    Parameters
    ----------
    shape_template : str
        SVG template for the shape with placeholders in curly braces
    positions : List[Tuple[float, float]]
        List of (x, y) positions for each instance
    attributes : Optional[List[Dict[str, Any]]], default None
        List of attribute dictionaries for each shape instance
        
    Returns
    -------
    str
        Concatenated SVG code for all shape instances
    """
    logger.info(f"Batch generating shapes with template: {shape_template}")
    if attributes is None:
        attributes = [{} for _ in positions]
    
    if len(attributes) != len(positions):
        raise ValueError("The number of attribute dictionaries must match the number of positions")
    
    result = []
    for (x, y), attrs in zip(positions, attributes):
        shape_attrs = {"x": x, "y": y, **attrs}
        result.append(apply_template_values(shape_template, **shape_attrs))
    
    return "\n".join(result)


def generate_svg_shape_tool() -> Tuple[Dict[str, Any], Callable]:
    """
    Creates a tool specification and implementation for generating SVG shape code.
    
    Returns
    -------
    Tuple[Dict[str, Any], Callable]
        A tuple containing the tool specification and the implementation function
    """
    spec = {
        "type": "function",
        "name": "generate_svg_shape",
        "description": "Generate SVG code for a specific shape that can be included in a larger SVG image.",
        "parameters": {
            "type": "object",
            "properties": {
                "shape_type": {
                    "type": "string",
                    "description": "Type of shape: 'circle', 'rect', 'square', 'line', 'polygon', 'ellipse', 'path', 'text', 'triangle', etc."
                },
                "x": {
                    "type": "number",
                    "description": "X-coordinate for the shape's position"
                },
                "y": {
                    "type": "number",
                    "description": "Y-coordinate for the shape's position"
                },
                "size": {
                    "type": "number",
                    "description": "Size parameter for shapes like squares and triangles"
                },
                "width": {
                    "type": "number",
                    "description": "Width for shapes like rectangles"
                },
                "height": {
                    "type": "number",
                    "description": "Height for shapes like rectangles"
                },
                "radius": {
                    "type": "number",
                    "description": "Radius for circles"
                },
                "color": {
                    "type": "string",
                    "description": "Stroke color for the shape (CSS color name or hex code)"
                },
                "fill": {
                    "type": "string",
                    "description": "Fill color for the shape. Use 'none' for transparent."
                },
                "stroke_width": {
                    "type": "number",
                    "description": "Width of the shape's outline"
                },
                "rotation": {
                    "type": "number",
                    "description": "Rotation angle in degrees"
                },
                "points": {
                    "type": "array",
                    "description": "List of [x,y] points for polygon or polyline",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"}
                    }
                },
                "opacity": {
                    "type": "number",
                    "description": "Opacity of the shape (0.0 to 1.0)"
                },
                "template": {
                    "type": "boolean",
                    "description": "If true, returns a template with placeholders that can be reused with different position/color values"
                }
            },
            "required": ["shape_type", "x", "y"]
        }
    }
    
    return spec, generate_svg_shape


def generate_svg_shape_batch_tool() -> Tuple[Dict[str, Any], Callable]:
    """
    Creates a tool specification and implementation for batch generation of 
    multiple instances of the same shape with different positions and attributes.
    
    Returns
    -------
    Tuple[Dict[str, Any], Callable]
        A tuple containing the tool specification and the implementation function
    """
    spec = {
        "type": "function",
        "name": "batch_generate_shapes",
        "description": "Generate multiple instances of a shape template with different positions and attributes.",
        "parameters": {
            "type": "object",
            "properties": {
                "shape_template": {
                    "type": "string",
                    "description": "SVG template for the shape with placeholders in curly braces, generated using generate_svg_shape with template=true"
                },
                "positions": {
                    "type": "array",
                    "description": "List of [x,y] positions for each shape instance",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"}
                    }
                },
                "attributes": {
                    "type": "array",
                    "description": "List of attribute dictionaries for each shape instance (e.g., [{\"fill\": \"blue\"}, {\"fill\": \"red\"}])",
                    "items": {
                        "type": "object"
                    }
                }
            },
            "required": ["shape_template", "positions"]
        }
    }
    
    return spec, batch_generate_shapes 