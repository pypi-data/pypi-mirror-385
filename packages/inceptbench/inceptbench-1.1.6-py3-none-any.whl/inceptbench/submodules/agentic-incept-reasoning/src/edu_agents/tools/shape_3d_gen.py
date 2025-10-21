from __future__ import annotations

import io
import logging
from typing import Callable, List, Dict, Any, Tuple, NamedTuple
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont


from utils.supabase_utils import upload_image_to_supabase

logger = logging.getLogger(__name__)

def calculate_viewing_direction_from_angle(angle_degrees: float, tilt_degrees: float = 0) -> np.ndarray:
    """
    Calculate the viewing direction vector based on the isometric projection angle and optional Y tilt.
    
    The projection equations are:
        proj_x = x - z * cos(angle)
        proj_y = (y + z * sin(angle)) * cos(tilt)  (with Y tilt applied)
    
    This defines the viewing direction for depth sorting.
    
    Parameters
    ----------
    angle_degrees : float
        Isometric projection angle in degrees
    tilt_degrees : float
        Additional Y viewing angle tilt in degrees (flattens the view)
        
    Returns
    -------
    np.ndarray
        Normalized viewing direction vector
    """
    # Convert to radians
    angle_rad = np.radians(angle_degrees)
    tilt_rad = np.radians(tilt_degrees)
    
    # Start with base viewing direction for isometric projection
    # This gives us [-cos(angle), sin(angle), -1]
    viewing_dir = np.array([-np.cos(angle_rad), np.sin(angle_rad), -1])
    
    # Apply Y tilt by rotating the viewing direction in the Y-Z plane
    # This simulates looking from a flatter (more top-down) angle
    if tilt_degrees != 0:
        # Rotation matrix around X-axis (rotates in Y-Z plane)
        cos_tilt = np.cos(tilt_rad)
        sin_tilt = np.sin(tilt_rad)
        rotation_x = np.array([
            [1, 0,        0       ],
            [0, cos_tilt, -sin_tilt],
            [0, sin_tilt,  cos_tilt]
        ])
        viewing_dir = rotation_x @ viewing_dir
    
    # Normalize the viewing direction
    return viewing_dir / np.linalg.norm(viewing_dir)

def calculate_viewing_direction_without_tilt(angle_degrees: float) -> np.ndarray:
    """
    Calculate the viewing direction vector based on the isometric projection angle without tilt.
    
    Parameters
    ----------
    angle_degrees : float
        Isometric projection angle in degrees
        
    Returns
    -------
    np.ndarray
        Normalized viewing direction vector
    """
    # Convert to radians
    angle_rad = np.radians(angle_degrees)
    
    # Base viewing direction for isometric projection
    viewing_dir = np.array([-np.cos(angle_rad), np.sin(angle_rad), -1])
    
    # Normalize the viewing direction
    return viewing_dir / np.linalg.norm(viewing_dir)

# Constants
class RenderingConstants:
    """Constants for 3D shape rendering (excluding projection angle which is global)."""
    # Image settings
    IMAGE_WIDTH = 1200
    IMAGE_HEIGHT = 1200
    BACKGROUND_COLOR = (255, 255, 255, 255)
    
    # Depth values for z-ordering
    FACE_DEPTH_FACTOR = 0.8
    EDGE_LABEL_DEPTH = -2000
    RIGHT_ANGLE_DEPTH = -2500
    POINT_LABEL_DEPTH = -3000
    
    # Visual settings
    FACE_OPACITY = 0.7
    EDGE_WIDTH = 8
    POINT_RADIUS = 4
    RIGHT_ANGLE_SIZE = 50
    RIGHT_ANGLE_WIDTH = 4
    
    # Font settings
    EDGE_LABEL_FONT_SIZE = 48
    POINT_LABEL_FONT_SIZE = 48
    EDGE_LABEL_BG_PADDING = 8
    EDGE_LABEL_BG_ALPHA = 204  # 80% opacity
    
    # Layout settings
    IMAGE_SCALE_FACTOR = 0.9
    PADDING_FACTOR = 0.1
    POINT_LABEL_OFFSET = 0.8
    
    # Algorithm settings
    RIGHT_ANGLE_THRESHOLD = 0.1  # Dot product threshold for right angle detection



class DrawableElement(NamedTuple):
    """Represents an element that can be drawn with its depth and data."""
    depth: float
    element_type: str
    element_data: Dict[str, Any]
    projected_points: Dict[str, Tuple[float, float]]
    point_lookup: Dict[str, Tuple[float, float, float]]
    faces: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

def isometric_projection(x: float, y: float, z: float, angle_degrees: float, tilt_degrees: float = 0) -> tuple[float, float]:
    """
    Apply isometric projection to convert 3D coordinates to 2D.
    
    Parameters
    ----------
    x, y, z : float
        3D coordinates (where positive Y is "up" in Cartesian space)
    angle_degrees : float
        Isometric projection angle in degrees
    tilt_degrees : float
        Additional Y viewing angle tilt in degrees (flattens the view)
        
    Returns
    -------
    tuple[float, float]
        2D coordinates after projection
    """
    # Scale z-coordinate to reduce apparent depth
    z = z * 0.7
    
    # Apply isometric projection
    angle = np.radians(angle_degrees)
    
    proj_x = x - z * np.cos(angle)  # Use angle for x projection (depth goes left)
    proj_y = y + z * np.sin(angle)  # Use angle for y projection (positive Y is up)
    
    # Apply Y viewing angle tilt to flatten the perspective
    if tilt_degrees != 0:
        tilt_rad = np.radians(tilt_degrees)
        # Compress Y dimension to simulate viewing from a flatter angle
        proj_y = proj_y * np.cos(tilt_rad)
    
    return proj_x, proj_y

def calculate_viewing_depth(point_3d: np.ndarray, viewing_direction: np.ndarray) -> float:
    """
    Calculate the depth of a 3D point in the viewing direction.
    
    Parameters
    ----------
    point_3d : np.ndarray
        3D coordinates
    viewing_direction : np.ndarray
        Viewing direction vector
        
    Returns
    -------
    float
        Depth in viewing direction (higher values are further away)
    """
    return np.dot(point_3d, viewing_direction)

def calculate_face_depth(face_points: List[tuple[float, float, float]], viewing_direction: np.ndarray) -> float:
    """
    Calculate the depth of a face in the viewing direction for proper z-ordering.
    
    Parameters
    ----------
    face_points : List[tuple[float, float, float]]
        List of 3D coordinates of the face vertices
    viewing_direction : np.ndarray
        Viewing direction vector
        
    Returns
    -------
    float
        Depth in viewing direction (higher values are further away)
    """
    centroid = np.mean(face_points, axis=0)
    return calculate_viewing_depth(centroid, viewing_direction)

def calculate_edge_depth(start_point: tuple[float, float, float], 
                        end_point: tuple[float, float, float], viewing_direction: np.ndarray) -> float:
    """
    Calculate the depth of an edge in the viewing direction for proper z-ordering.
    
    Parameters
    ----------
    start_point, end_point : tuple[float, float, float]
        3D coordinates of the edge endpoints
    viewing_direction : np.ndarray
        Viewing direction vector
        
    Returns
    -------
    float
        Depth in viewing direction (higher values are further away)
    """
    midpoint = np.array([(start_point[0] + end_point[0]) / 2,
                        (start_point[1] + end_point[1]) / 2,
                        (start_point[2] + end_point[2]) / 2])
    return calculate_viewing_depth(midpoint, viewing_direction)

# Removed complex hidden line detection functions - now using z-order rendering with transparency

def find_right_angles(points: Dict[str, tuple[float, float, float]], 
                     edges: List[Dict[str, Any]], 
                     faces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Find right angles on the highest-z face based on connected edges.
    
    Parameters
    ----------
    points : Dict[str, tuple[float, float, float]]
        Dictionary mapping point names to 3D coordinates
    edges : List[Dict[str, Any]]
        List of edges in the shape
    faces : List[Dict[str, Any]]
        List of faces in the shape
        
    Returns
    -------
    List[Dict[str, Any]]
        List of right angles with vertex point and two edge vectors
    """
    # Find the face with the highest average z-coordinate
    highest_z_face = None
    highest_z_avg = float('-inf')
    
    for face in faces:
        face_points = [points[name] for name in face['points']]
        face_z_avg = np.mean([p[2] for p in face_points])
        if face_z_avg > highest_z_avg:
            highest_z_avg = face_z_avg
            highest_z_face = face
    
    if highest_z_face is None:
        return []
    
    # Get points on the highest-z face
    highest_z_points = set(highest_z_face['points'])
    
    right_angles = []
    
    # Group edges by their endpoints
    point_edges = {}
    for edge in edges:
        start = edge['start_point']
        end = edge['end_point']
        
        if start not in point_edges:
            point_edges[start] = []
        if end not in point_edges:
            point_edges[end] = []
            
        point_edges[start].append((end, edge))
        point_edges[end].append((start, edge))
    
    # Check each point that is on the highest-z face
    for point_name, connected_edges in point_edges.items():
        if point_name not in highest_z_points or len(connected_edges) < 2:
            continue
            
        point_coord = points[point_name]
        
        # Check all pairs of edges at this point
        for i in range(len(connected_edges)):
            for j in range(i + 1, len(connected_edges)):
                other_point1, edge1 = connected_edges[i]
                other_point2, edge2 = connected_edges[j]
                
                # Only consider right angles where BOTH other endpoints are also on the highest-z face
                if other_point1 not in highest_z_points or other_point2 not in highest_z_points:
                    continue
                
                # Calculate vectors from the point to the other endpoints
                coord1 = points[other_point1]
                coord2 = points[other_point2]
                
                vec1 = np.array([coord1[0] - point_coord[0], 
                               coord1[1] - point_coord[1], 
                               coord1[2] - point_coord[2]])
                vec2 = np.array([coord2[0] - point_coord[0], 
                               coord2[1] - point_coord[1], 
                               coord2[2] - point_coord[2]])
                
                # Normalize vectors
                vec1 = vec1 / np.linalg.norm(vec1)
                vec2 = vec2 / np.linalg.norm(vec2)
                
                # Check if angle is close to 90 degrees (dot product close to 0)
                dot_product = np.dot(vec1, vec2)
                if abs(dot_product) < RenderingConstants.RIGHT_ANGLE_THRESHOLD:  # Close to perpendicular
                    right_angles.append({
                        'vertex': point_name,
                        'vector1': vec1,
                        'vector2': vec2,
                        'coord': point_coord
                    })
    
    return right_angles

def get_shape_bounds(projected_points: Dict[str, tuple[float, float]]) -> tuple[float, float, float, float]:
    """
    Get the bounding box of all projected points.
    
    Parameters
    ----------
    projected_points : Dict[str, tuple[float, float]]
        Dictionary mapping point names to 2D projected coordinates
        
    Returns
    -------
    tuple[float, float, float, float]
        (min_x, max_x, min_y, max_y) bounds
    """
    if not projected_points:
        return 0, 0, 0, 0
        
    x_coords = [p[0] for p in projected_points.values()]
    y_coords = [p[1] for p in projected_points.values()]
    
    return min(x_coords), max(x_coords), min(y_coords), max(y_coords)

def get_smart_label_position(point_name: str, point_2d: tuple[float, float], 
                           bounds: tuple[float, float, float, float], 
                           offset: float = 0.3,
                           faces: List[Dict[str, Any]] = None,
                           projected_points: Dict[str, tuple[float, float]] = None,
                           point_lookup: Dict[str, tuple[float, float, float]] = None,
                           edges: List[Dict[str, Any]] = None) -> tuple[float, float, str, str]:
    """
    Calculate smart label position to avoid overlapping with the shape.
    Uses edge-vector-based positioning when edge information is available.
    
    Parameters
    ----------
    point_name : str
        Name of the point
    point_2d : tuple[float, float]
        2D coordinates of the point
    bounds : tuple[float, float, float, float]
        Bounding box of the shape (min_x, max_x, min_y, max_y)
    offset : float
        Distance to offset the label from the point
    faces : List[Dict[str, Any]], optional
        List of faces (unused in current implementation)
    projected_points : Dict[str, tuple[float, float]], optional
        Dictionary of projected points for vector calculation
    point_lookup : Dict[str, tuple[float, float, float]], optional
        Dictionary of 3D points (unused in current implementation)
    edges : List[Dict[str, Any]], optional
        List of edges to determine connected points
        
    Returns
    -------
    tuple[float, float, str, str]
        (label_x, label_y, horizontal_alignment, vertical_alignment)
    """
    x, y = point_2d
    
    # If edge information is available, use edge-vector-based positioning
    if edges is not None and projected_points is not None:
        # Find all edges that connect to this point
        connected_points = []
        for edge in edges:
            if edge['start_point'] == point_name:
                connected_points.append(edge['end_point'])
            elif edge['end_point'] == point_name:
                connected_points.append(edge['start_point'])
        
        if connected_points:
            # Calculate normalized edge vectors from connected points to this point
            normalized_edge_vectors = []
            for other_point in connected_points:
                other_x, other_y = projected_points[other_point]
                # Vector from other point to this point (continuing past the point)
                vec_x = x - other_x
                vec_y = y - other_y
                
                # Normalize each edge vector so length doesn't affect the average direction
                length = np.sqrt(vec_x*vec_x + vec_y*vec_y)
                if length > 0:  # Avoid zero vectors
                    normalized_edge_vectors.append((vec_x / length, vec_y / length))
            
            if normalized_edge_vectors:
                # Average all normalized edge vectors to get the resultant direction
                avg_x = np.mean([v[0] for v in normalized_edge_vectors])
                avg_y = np.mean([v[1] for v in normalized_edge_vectors])
                
                # Normalize the averaged vector (in case it's not unit length due to cancellation)
                length = np.sqrt(avg_x*avg_x + avg_y*avg_y)
                if length > 0:
                    dx_norm = avg_x / length
                    dy_norm = avg_y / length
                    
                    # Position label along the averaged direction vector
                    label_x = x + dx_norm * offset
                    label_y = y + dy_norm * offset
                    
                    # Determine alignment based on direction vector
                    ha = 'left' if dx_norm > 0 else 'right'
                    va = 'bottom' if dy_norm > 0 else 'top'
                    
                    return label_x, label_y, ha, va
    
    # Fallback to shape-center-based positioning if face info not available
    min_x, max_x, min_y, max_y = bounds
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    
    # Calculate direction vector from shape center to point
    dx = x - center_x
    dy = y - center_y
    
    # Normalize the direction vector
    length = np.sqrt(dx*dx + dy*dy)
    if length > 0:
        dx_norm = dx / length
        dy_norm = dy / length
    else:
        # If point is at center, default to right
        dx_norm = 1
        dy_norm = 0
    
    # Position label along the direction vector
    label_x = x + dx_norm * offset
    label_y = y + dy_norm * offset
    
    # Determine alignment based on direction vector
    ha = 'left' if dx_norm > 0 else 'right'
    va = 'bottom' if dy_norm > 0 else 'top'
    
    return label_x, label_y, ha, va

def detect_ambiguous_edge_labels(edges: List[Dict[str, Any]], 
                                projected_points: Dict[str, tuple[float, float]]) -> Dict[str, tuple[float, float]]:
    """
    Detect potentially ambiguous edge label placements and suggest better positions.
    
    Parameters
    ----------
    edges : List[Dict[str, Any]]
        List of edges in the shape
    projected_points : Dict[str, tuple[float, float]]
        Dictionary mapping point names to 2D projected coordinates
        
    Returns
    -------
    Dict[str, tuple[float, float]]
        Dictionary mapping edge labels to adjusted positions
    """
    edge_label_positions = {}
    
    for edge in edges:
        edge_label = edge.get('label', None)
        if not edge_label:
            continue
            
        start_name = edge['start_point']
        end_name = edge['end_point']
        start_2d = projected_points[start_name]
        end_2d = projected_points[end_name]
        
        # Calculate default midpoint
        mid_x = (start_2d[0] + end_2d[0]) / 2
        mid_y = (start_2d[1] + end_2d[1]) / 2
        
        # Calculate edge direction vector
        edge_vec = (end_2d[0] - start_2d[0], end_2d[1] - start_2d[1])
        edge_length = np.sqrt(edge_vec[0]**2 + edge_vec[1]**2)
        
        if edge_length > 0:
            # Normalize edge vector
            edge_vec_norm = (edge_vec[0] / edge_length, edge_vec[1] / edge_length)
            
            # Calculate perpendicular vector
            perp_vec = (-edge_vec_norm[1], edge_vec_norm[0])
            
            # Check if there are other edges near this midpoint
            offset_distance = 0.5
            has_nearby_edges = False
            
            for other_edge in edges:
                if other_edge == edge:
                    continue
                    
                other_start = projected_points[other_edge['start_point']]
                other_end = projected_points[other_edge['end_point']]
                other_mid_x = (other_start[0] + other_end[0]) / 2
                other_mid_y = (other_start[1] + other_end[1]) / 2
                
                # Check if the other edge's midpoint is close to this edge's midpoint
                distance = np.sqrt((other_mid_x - mid_x)**2 + (other_mid_y - mid_y)**2)
                if distance < 1.0:  # Close proximity threshold
                    has_nearby_edges = True
                    break
            
            # If there are nearby edges, offset the label
            if has_nearby_edges:
                adjusted_x = mid_x + perp_vec[0] * offset_distance
                adjusted_y = mid_y + perp_vec[1] * offset_distance
                edge_label_positions[edge_label] = (adjusted_x, adjusted_y)
            else:
                edge_label_positions[edge_label] = (mid_x, mid_y)
    
    return edge_label_positions

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def parse_color(color_value: Any, default_color: str = 'black') -> tuple[int, int, int]:
    """
    Parse color value into RGB tuple.
    
    Parameters
    ----------
    color_value : Any
        Color as string (hex or named) or RGB tuple
    default_color : str
        Default color name if parsing fails
        
    Returns
    -------
    tuple[int, int, int]
        RGB color tuple
    """
    if isinstance(color_value, str):
        if color_value.startswith('#'):
            return hex_to_rgb(color_value)
        else:
            # Common color map
            color_map = {
                'black': (0, 0, 0),
                'white': (255, 255, 255),
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
                'yellow': (255, 255, 0),
                'cyan': (0, 255, 255),
                'magenta': (255, 0, 255),
                'purple': (128, 0, 128),
                'orange': (255, 165, 0),
                'brown': (165, 42, 42),
                'pink': (255, 192, 203),
                'lime': (0, 255, 0),
                'teal': (0, 128, 128),
                'indigo': (75, 0, 130),
                'gray': (128, 128, 128),
                'lightgray': (211, 211, 211),
                'lightblue': (173, 216, 230),
                'lightgreen': (144, 238, 144),
                'lightcoral': (240, 128, 128),
                'lightyellow': (255, 255, 224),
                'lightcyan': (224, 255, 255),
                'lightmagenta': (255, 181, 197),
                'lightpurple': (216, 191, 216),
                'lightorange': (255, 215, 0),
                'lightbrown': (139, 69, 19),
                'lightpink': (255, 182, 193),
                'lightlime': (204, 255, 204),
                'lightteal': (173, 216, 230),
                'lightindigo': (138, 43, 226),
            }
            # Strip all whitespace, including internal whitespace, and convert to lowercase
            color_value = color_value.strip().lower().replace(' ', '')
            return color_map.get(color_value, (0, 0, 0))
    elif isinstance(color_value, (tuple, list)) and len(color_value) >= 3:
        return tuple(color_value[:3])
    else:
        # Fallback to default
        return parse_color(default_color)

def load_font(size: int) -> ImageFont.ImageFont:
    """
    Load a font with the specified size, trying multiple fallbacks.
    Includes extensive fallbacks for Linux/Amazon Linux systems.
    
    Parameters
    ----------
    size : int
        Font size in points
        
    Returns
    -------
    ImageFont.ImageFont
        Loaded font object
    """
    # List of font paths to try, in order of preference
    font_paths = [
        # macOS fonts
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        
        # Windows fonts
        "arial.ttf",
        "Arial.ttf",
        
        # Common Linux font locations - Liberation fonts (common on RHEL/CentOS/Amazon Linux)
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/LiberationSans-Regular.ttf",
        
        # DejaVu fonts (very common on Linux)
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        
        # GNU FreeFont (common fallback)
        "/usr/share/fonts/gnu-free/FreeSans.ttf",
        "/usr/share/fonts/truetype/gnu-free/FreeSans.ttf",
        
        # Red Hat fonts (Amazon Linux 2023+)
        "/usr/share/fonts/redhat/RedHatDisplay-Regular.ttf",
        "/usr/share/fonts/truetype/redhat/RedHatDisplay-Regular.ttf",
        
        # Ubuntu/Debian fonts
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        
        # Generic Linux paths
        "/usr/share/fonts/TTF/arial.ttf",
        "/usr/share/fonts/truetype/arial.ttf",
        "/usr/share/fonts/opentype/arial.ttf",
        
        # System fallbacks via alternatives (RHEL/CentOS style)
        "/etc/alternatives/default-font",
        "/usr/share/fonts/default.ttf",
    ]
    
    # Try each font path
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue
    
    # If all else fails, use the default font
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        # Older PIL versions don't support size parameter
        return ImageFont.load_default()



def calculate_text_position(center_x: int, center_y: int, text: str, 
                          font: ImageFont.ImageFont, draw: ImageDraw.ImageDraw,
                          alignment: tuple[str, str] = ('center', 'center')) -> tuple[int, int]:
    """
    Calculate text position based on alignment.
    
    Parameters
    ----------
    center_x, center_y : int
        Center position for the text
    text : str
        Text to position
    font : ImageFont.ImageFont
        Font object
    draw : ImageDraw.ImageDraw
        Draw object for text measurement
    alignment : tuple[str, str]
        (horizontal, vertical) alignment: 'left'/'center'/'right', 'top'/'center'/'bottom'
        
    Returns
    -------
    tuple[int, int]
        (x, y) position for text drawing
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    ha, va = alignment
    
    if ha == 'right':
        final_x = center_x - text_width
    elif ha == 'center':
        final_x = center_x - text_width // 2
    else:  # 'left'
        final_x = center_x
        
    if va == 'top':
        final_y = center_y - text_height
    elif va == 'center':
        final_y = center_y - text_height // 2
    else:  # 'bottom'
        final_y = center_y
    
    return final_x, final_y

def process_shape_points(points: List[Dict[str, Any]], angle_degrees: float, tilt_degrees: float = 0) -> tuple[Dict[str, Tuple[float, float, float]], Dict[str, Tuple[float, float]]]:
    """
    Process shape points: create lookup dictionaries and project to 2D.
    
    Parameters
    ----------
    points : List[Dict[str, Any]]
        List of point definitions
    angle_degrees : float
        Isometric projection angle in degrees
    tilt_degrees : float
        Additional tilt rotation around Z-axis in degrees
        
    Returns
    -------
    tuple[Dict[str, Tuple[float, float, float]], Dict[str, Tuple[float, float]]]
        (point_lookup, projected_points) dictionaries
    """
    point_lookup = {}
    projected_points = {}
    
    for point in points:
        name = point['name']
        x, y, z = point['x'], point['y'], point['z']
        point_lookup[name] = (x, y, z)
        
        # Project to 2D
        proj_x, proj_y = isometric_projection(x, y, z, angle_degrees, tilt_degrees)
        projected_points[name] = (proj_x, proj_y)
    
    return point_lookup, projected_points

def create_drawable_elements(shape: Dict[str, Any], point_lookup: Dict[str, Tuple[float, float, float]], 
                           projected_points: Dict[str, Tuple[float, float]], viewing_direction: np.ndarray) -> List[DrawableElement]:
    """
    Create drawable elements for a single shape.
    
    Parameters
    ----------
    shape : Dict[str, Any]
        Shape definition
    point_lookup : Dict[str, Tuple[float, float, float]]
        3D point coordinates lookup
    projected_points : Dict[str, Tuple[float, float]]
        2D projected coordinates lookup
    viewing_direction : np.ndarray
        Viewing direction vector for depth calculations
        
    Returns
    -------
    List[DrawableElement]
        List of drawable elements with depth ordering
    """
    points = shape.get('points', [])
    edges = shape.get('edges', [])
    faces = shape.get('faces', [])
    
    elements = []
    
    # Add faces
    for face in faces:
        face_point_names = face['points']
        face_3d_points = [point_lookup[name] for name in face_point_names]
        depth = calculate_face_depth(face_3d_points, viewing_direction) * RenderingConstants.FACE_DEPTH_FACTOR
        elements.append(DrawableElement(depth, 'face', face, projected_points, point_lookup, faces, edges))
    
    # Add edges
    for edge in edges:
        start_3d = point_lookup[edge['start_point']]
        end_3d = point_lookup[edge['end_point']]
        depth = calculate_edge_depth(start_3d, end_3d, viewing_direction)
        elements.append(DrawableElement(depth, 'edge', edge, projected_points, point_lookup, faces, edges))
    
    # Add edge labels
    for edge in edges:
        if edge.get('label'):
            elements.append(DrawableElement(RenderingConstants.EDGE_LABEL_DEPTH, 'edge_label', edge, 
                                          projected_points, point_lookup, faces, edges))
    
    # Add point dots
    for point in points:
        actual_depth = calculate_viewing_depth(np.array(point_lookup[point['name']]), viewing_direction)
        elements.append(DrawableElement(actual_depth, 'point', point, projected_points, point_lookup, faces, edges))
    
    # Add point labels
    for point in points:
        if point.get('label'):
            elements.append(DrawableElement(RenderingConstants.POINT_LABEL_DEPTH, 'point_label', point, 
                                          projected_points, point_lookup, faces, edges))
    
    # Add right angles
    right_angles = find_right_angles(point_lookup, edges, faces)
    for right_angle in right_angles:
        elements.append(DrawableElement(RenderingConstants.RIGHT_ANGLE_DEPTH, 'right_angle', right_angle, 
                                      projected_points, point_lookup, faces, edges))
    
    return elements

def create_coordinate_transform(all_projected_points: List[Tuple[float, float]]) -> Callable[[float, float], Tuple[int, int]]:
    """
    Create a coordinate transformation function from projected 2D points to image coordinates.
    
    Parameters
    ----------
    all_projected_points : List[Tuple[float, float]]
        All projected 2D points to determine bounds
        
    Returns
    -------
    Callable[[float, float], Tuple[int, int]]
        Function that converts projected coordinates to image coordinates
    """
    if all_projected_points:
        x_coords = [p[0] for p in all_projected_points]
        y_coords = [p[1] for p in all_projected_points]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # Add padding
        x_range = x_max - x_min
        y_range = y_max - y_min
        padding = max(x_range, y_range) * RenderingConstants.PADDING_FACTOR
        
        proj_x_min, proj_x_max = x_min - padding, x_max + padding
        proj_y_min, proj_y_max = y_min - padding, y_max + padding
        
        # Calculate scale to fit in image
        scale_x = RenderingConstants.IMAGE_WIDTH / (proj_x_max - proj_x_min)
        scale_y = RenderingConstants.IMAGE_HEIGHT / (proj_y_max - proj_y_min)
        scale = min(scale_x, scale_y) * RenderingConstants.IMAGE_SCALE_FACTOR
        
        # Center the image
        center_x = RenderingConstants.IMAGE_WIDTH / 2
        center_y = RenderingConstants.IMAGE_HEIGHT / 2
        proj_center_x = (proj_x_min + proj_x_max) / 2
        proj_center_y = (proj_y_min + proj_y_max) / 2
    else:
        scale = 50
        center_x = RenderingConstants.IMAGE_WIDTH / 2
        center_y = RenderingConstants.IMAGE_HEIGHT / 2
        proj_center_x = 0
        proj_center_y = 0
    
    def project_to_image_coords(x: float, y: float) -> Tuple[int, int]:
        """Convert projected coordinates to image coordinates."""
        img_x = center_x + (x - proj_center_x) * scale
        img_y = center_y - (y - proj_center_y) * scale  # Flip Y axis
        return int(img_x), int(img_y)
    
    return project_to_image_coords

def render_face(draw: ImageDraw.ImageDraw, element: DrawableElement, project_to_image_coords: Callable):
    """Render a face element."""
    face_color = element.element_data.get('color', '#lightgray')
    rgb = parse_color(face_color, 'lightgray')
    
    # Get face vertices in image coordinates
    face_points = []
    for point_name in element.element_data['points']:
        proj_x, proj_y = element.projected_points[point_name]
        img_x, img_y = project_to_image_coords(proj_x, proj_y)
        face_points.append((img_x, img_y))
    
    if len(face_points) >= 3:
        # If this is a white backing face, use full opacity
        if face_color == 'white' and element.element_data.get('is_backing_face', False):
            face_color_with_alpha = (*rgb, 255)  # Full opacity for backing faces
        else:
            # Use semi-transparency for colored faces
            face_color_with_alpha = (*rgb, int(255 * RenderingConstants.FACE_OPACITY))
        draw.polygon(face_points, fill=face_color_with_alpha)

def render_edge(draw: ImageDraw.ImageDraw, element: DrawableElement, project_to_image_coords: Callable):
    """Render an edge element."""
    edge_color = element.element_data.get('color', 'black')
    
    # Handle both tuple colors with alpha and string colors
    if isinstance(edge_color, tuple):
        edge_color_with_alpha = edge_color  # Use the color tuple as is, preserving alpha
    else:
        edge_rgb = parse_color(edge_color)
        edge_color_with_alpha = (*edge_rgb, 255)  # Default to full alpha for string colors
    
    start_proj = element.projected_points[element.element_data['start_point']]
    end_proj = element.projected_points[element.element_data['end_point']]
    
    start_img = project_to_image_coords(*start_proj)
    end_img = project_to_image_coords(*end_proj)
    
    # Handle dashed lines
    if element.element_data.get('dashed', False):
        # Calculate the total line length
        dx = end_img[0] - start_img[0]
        dy = end_img[1] - start_img[1]
        length = (dx * dx + dy * dy) ** 0.5
        
        # Create dash pattern - each dash and gap is 10 pixels
        dash_length = 10
        num_segments = int(length / dash_length)
        
        # Draw individual dash segments
        for i in range(0, num_segments, 2):
            t1 = i / num_segments
            t2 = min((i + 1) / num_segments, 1.0)
            
            x1 = start_img[0] + dx * t1
            y1 = start_img[1] + dy * t1
            x2 = start_img[0] + dx * t2
            y2 = start_img[1] + dy * t2
            
            draw.line([(x1, y1), (x2, y2)], fill=edge_color_with_alpha, width=RenderingConstants.EDGE_WIDTH)
    else:
        draw.line([start_img, end_img], fill=edge_color_with_alpha, width=RenderingConstants.EDGE_WIDTH)

def render_edge_label(draw: ImageDraw.ImageDraw, element: DrawableElement, project_to_image_coords: Callable):
    """Render an edge label element."""
    edge_label = element.element_data.get('label')
    if not edge_label:
        return
    
    edge_rgb = parse_color(element.element_data.get('color', 'black'))
    
    start_proj = element.projected_points[element.element_data['start_point']]
    end_proj = element.projected_points[element.element_data['end_point']]
    
    start_img = project_to_image_coords(*start_proj)
    end_img = project_to_image_coords(*end_proj)
    
    # Calculate label position
    label_x = (start_img[0] + end_img[0]) // 2
    label_y = (start_img[1] + end_img[1]) // 2
    
    font = load_font(RenderingConstants.EDGE_LABEL_FONT_SIZE)
    
    # Get text size for proper centering
    bbox = draw.textbbox((0, 0), edge_label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Draw label background
    bg_left = label_x - text_width // 2 - RenderingConstants.EDGE_LABEL_BG_PADDING
    bg_top = label_y - text_height // 2 - RenderingConstants.EDGE_LABEL_BG_PADDING
    bg_right = label_x + text_width // 2 + RenderingConstants.EDGE_LABEL_BG_PADDING
    bg_bottom = label_y + text_height // 2 + RenderingConstants.EDGE_LABEL_BG_PADDING
    
    draw.rectangle([bg_left, bg_top, bg_right, bg_bottom], 
                 fill=(255, 255, 255, RenderingConstants.EDGE_LABEL_BG_ALPHA), outline=None)
    
    # Draw text with baseline adjustment
    text_x = label_x - text_width // 2
    text_y = label_y - text_height // 2 - bbox[1]
    draw.text((text_x, text_y), edge_label, fill=(*edge_rgb, 255), font=font)

def render_point(draw: ImageDraw.ImageDraw, element: DrawableElement, project_to_image_coords: Callable):
    """Render a point element."""
    # Skip rendering if hide_point flag is set
    if element.element_data.get('hide_point', False):
        return
        
    point_rgb = parse_color(element.element_data.get('color', 'black'))
    
    proj_x, proj_y = element.projected_points[element.element_data['name']]
    img_x, img_y = project_to_image_coords(proj_x, proj_y)
    
    draw.ellipse([img_x - RenderingConstants.POINT_RADIUS, img_y - RenderingConstants.POINT_RADIUS, 
                 img_x + RenderingConstants.POINT_RADIUS, img_y + RenderingConstants.POINT_RADIUS], 
                fill=(*point_rgb, 255))

def render_point_label(draw: ImageDraw.ImageDraw, element: DrawableElement, project_to_image_coords: Callable):
    """Render a point label element."""
    point_label = element.element_data.get('label')
    if not point_label:
        return
    
    point_rgb = parse_color(element.element_data.get('color', 'black'))
    point_name = element.element_data['name']
    
    proj_x, proj_y = element.projected_points[point_name]
    
    font = load_font(RenderingConstants.POINT_LABEL_FONT_SIZE)
    
    # Smart positioning
    shape_bounds = get_shape_bounds(element.projected_points)
    label_x, label_y, ha, va = get_smart_label_position(
        point_name, (proj_x, proj_y), shape_bounds, 
        offset=RenderingConstants.POINT_LABEL_OFFSET, 
        faces=element.faces, projected_points=element.projected_points, 
        point_lookup=element.point_lookup, edges=element.edges)
    
    label_img_x, label_img_y = project_to_image_coords(label_x, label_y)
    
    # Calculate final text position
    final_x, final_y = calculate_text_position(label_img_x, label_img_y, point_label, font, draw, (ha, va))
    draw.text((final_x, final_y), point_label, fill=(*point_rgb, 255), font=font)

def render_right_angle(draw: ImageDraw.ImageDraw, element: DrawableElement, project_to_image_coords: Callable, angle_degrees: float, tilt_degrees: float = 0):
    """Render a right angle indicator element."""
    vertex_name = element.element_data['vertex']
    vertex_2d = element.projected_points[vertex_name]
    vec1_3d = element.element_data['vector1']
    vec2_3d = element.element_data['vector2']
    
    # Project the vectors to 2D
    vertex_coord = element.element_data['coord']
    point1_3d = (vertex_coord[0] + vec1_3d[0] * 0.5, 
                vertex_coord[1] + vec1_3d[1] * 0.5, 
                vertex_coord[2] + vec1_3d[2] * 0.5)
    point2_3d = (vertex_coord[0] + vec2_3d[0] * 0.5, 
                vertex_coord[1] + vec2_3d[1] * 0.5, 
                vertex_coord[2] + vec2_3d[2] * 0.5)
    
    point1_2d = isometric_projection(*point1_3d, angle_degrees, tilt_degrees)
    point2_2d = isometric_projection(*point2_3d, angle_degrees, tilt_degrees)
    
    # Calculate 2D vectors
    vec1_2d = (point1_2d[0] - vertex_2d[0], point1_2d[1] - vertex_2d[1])
    vec2_2d = (point2_2d[0] - vertex_2d[0], point2_2d[1] - vertex_2d[1])
    
    # Normalize 2D vectors
    vec1_2d_norm = np.linalg.norm(vec1_2d)
    vec2_2d_norm = np.linalg.norm(vec2_2d)
    
    if vec1_2d_norm > 0 and vec2_2d_norm > 0:
        vec1_2d = (vec1_2d[0] / vec1_2d_norm, vec1_2d[1] / vec1_2d_norm)
        vec2_2d = (vec2_2d[0] / vec2_2d_norm, vec2_2d[1] / vec2_2d_norm)
        
        vertex_img = project_to_image_coords(*vertex_2d)
        
        # Calculate the four corners of the square
        corner1_img = (vertex_img[0] + vec1_2d[0] * RenderingConstants.RIGHT_ANGLE_SIZE, 
                      vertex_img[1] - vec1_2d[1] * RenderingConstants.RIGHT_ANGLE_SIZE)
        corner2_img = (vertex_img[0] + vec1_2d[0] * RenderingConstants.RIGHT_ANGLE_SIZE + vec2_2d[0] * RenderingConstants.RIGHT_ANGLE_SIZE, 
                      vertex_img[1] - vec1_2d[1] * RenderingConstants.RIGHT_ANGLE_SIZE - vec2_2d[1] * RenderingConstants.RIGHT_ANGLE_SIZE)
        corner3_img = (vertex_img[0] + vec2_2d[0] * RenderingConstants.RIGHT_ANGLE_SIZE, 
                      vertex_img[1] - vec2_2d[1] * RenderingConstants.RIGHT_ANGLE_SIZE)
        
        # Draw the square
        square_points = [vertex_img, corner1_img, corner2_img, corner3_img]
        draw.polygon(square_points, outline=(0, 0, 0, 180), width=RenderingConstants.RIGHT_ANGLE_WIDTH)

def render_all_elements(img: Image.Image, all_drawable_elements: List[DrawableElement], 
                       project_to_image_coords: Callable, angle_degrees: float, tilt_degrees: float = 0) -> str:
    """
    Render all drawable elements and return the final image URL.
    
    Parameters
    ----------
    img : Image.Image
        Base image to render onto
    all_drawable_elements : List[DrawableElement]
        All elements to render
    project_to_image_coords : Callable
        Coordinate transformation function
    angle_degrees : float
        Isometric projection angle in degrees
    tilt_degrees : float
        Additional tilt rotation around Z-axis in degrees
        
    Returns
    -------
    str
        URL of the generated image
    """
    # Sort elements by depth (back to front)
    all_drawable_elements.sort(key=lambda x: x.depth, reverse=True)
    
    # Rendering function lookup
    renderers = {
        'face': render_face,
        'edge': render_edge,
        'edge_label': render_edge_label,
        'point': render_point,
        'point_label': render_point_label,
    }
    
    # Draw all elements in z-order
    for element in all_drawable_elements:
        # Create a new layer for this element
        layer = Image.new('RGBA', (RenderingConstants.IMAGE_WIDTH, RenderingConstants.IMAGE_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        
        # Render element using appropriate renderer
        if element.element_type in renderers:
            renderers[element.element_type](draw, element, project_to_image_coords)
        elif element.element_type == 'right_angle':
            render_right_angle(draw, element, project_to_image_coords, angle_degrees, tilt_degrees)
        
        # Composite this layer onto the main image
        img = Image.alpha_composite(img, layer)
    
    # Save and upload
    buf = io.BytesIO()
    # Save with transparency enabled - no need to convert to RGB
    img.save(buf, format='PNG', dpi=(100, 100))
    buf.seek(0)
    
    image_bytes = buf.getvalue()
    public_url = upload_image_to_supabase(
        image_bytes=image_bytes,
        content_type="image/png",
        bucket_name="incept-images"
    )
    
    return public_url

def generate_cone_points_and_faces(center_x: float, center_y: float, center_z: float,
                                 radius: float, apex_x: float, apex_y: float, apex_z: float,
                                 num_segments: int = 64, base_label: str = None, apex_label: str = None,
                                 radius_label: str = None, height_label: str = None,
                                 curved_face_color: str = 'lightcoral') -> Dict[str, Any]:
    """
    Generate points and faces for a cone.
    
    Parameters
    ----------
    center_x, center_y, center_z : float
        Center point of the circular base
    radius : float
        Radius of the circular base
    apex_x, apex_y, apex_z : float
        Apex point of the cone
    num_segments : int
        Number of segments to approximate the circular base
    curved_face_color : str
        Color to use for the curved faces of the cone
        
    Returns
    -------
    Dict[str, Any]
        Dictionary with 'points', 'edges', 'faces' for the cone
    """
    points = []
    edges = []
    faces = []
    
    # Add center point of base
    base_point = {"name": "base_center", "x": center_x, "y": center_y, "z": center_z}
    if base_label:
        base_point["label"] = base_label
    points.append(base_point)
    
    # Add apex point
    apex_point = {"name": "apex", "x": apex_x, "y": apex_y, "z": apex_z}
    if apex_label:
        apex_point["label"] = apex_label
    points.append(apex_point)
    
    # Generate points around the circular base
    for i in range(num_segments):
        angle = 2 * math.pi * i / num_segments
        point_x = center_x + radius * math.cos(angle)
        point_z = center_z + radius * math.sin(angle)
        points.append({
            "name": f"base_{i}",
            "x": point_x,
            "y": center_y,
            "z": point_z,
            "hide_point": True
        })
    
    # Create edges around the base (full circle)
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        edges.append({"start_point": f"base_{i}", "end_point": f"base_{next_i}"})
    
    # Add radius edge (from center to first base point)
    right_point_idx = 0
    radius_black_color = (0, 0, 0, 180)
    radius_edge = {"start_point": "base_center", "end_point": f"base_{right_point_idx}", "color": radius_black_color}
    if radius_label:
        radius_edge["label"] = radius_label
    edges.append(radius_edge)
    
    # Add height edge (from base center to apex)
    height_black_color = (0, 0, 0, 128)
    height_edge = {"start_point": "base_center", "end_point": "apex", "color": height_black_color}
    if height_label:
        height_edge["label"] = height_label
    edges.append(height_edge)
    
    # Create triangular faces from apex to base edges
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        faces.append({
            "points": ["apex", f"base_{i}", f"base_{next_i}"],
            "color": curved_face_color
        })
    
    # Create the base face
    base_points = [f"base_{i}" for i in range(num_segments)]
    faces.append({
        "points": base_points,
        "color": curved_face_color
    })
    
    return {
        "points": points,
        "edges": edges,
        "faces": faces,
        "shape_name": "Cone"
    }

def generate_sphere_points_and_faces(center_x: float, center_y: float, center_z: float,
                                   radius: float, num_latitude: int = 64, num_longitude: int = 64,
                                   center_label: str = None, radius_label: str = None,
                                   curved_face_color: str = 'lightcoral',
                                   hemisphere_axis_angle: float | None = None) -> Dict[str, Any]:
    """
    Generate points and faces for a sphere or hemisphere.
    
    Parameters
    ----------
    center_x, center_y, center_z : float
        Center point of the sphere
    radius : float
        Radius of the sphere
    num_latitude : int
        Number of latitude divisions
    num_longitude : int
        Number of longitude divisions
    curved_face_color : str
        Color to use for the curved faces of the sphere
    hemisphere_axis_angle : float | None
        If not None, creates a hemisphere with the flat side oriented at this angle in the xy-plane
        (in degrees, 0 = flat side on bottom showing top half, 90 = flat side on left showing right half)
        
    Returns
    -------
    Dict[str, Any]
        Dictionary with 'points', 'edges', 'faces' for the sphere/hemisphere
    """
    points = []
    edges = []
    faces = []
    
    # Add center point
    center_point = {"name": "center", "x": center_x, "y": center_y, "z": center_z}
    if center_label:
        center_point["label"] = center_label
    points.append(center_point)
    
    # For hemispheres, calculate the normal vector of the cut plane
    if hemisphere_axis_angle is not None:
        angle_rad = math.radians(hemisphere_axis_angle)
        cut_normal = np.array([math.sin(angle_rad), math.cos(angle_rad), 0])
    
    # Keep track of which points exist for edge generation
    existing_points = {"center"}
    
    # Generate points using spherical coordinates
    for lat in range(num_latitude + 1):
        theta = math.pi * lat / num_latitude  # 0 to pi
        for lon in range(num_longitude):
            phi = 2 * math.pi * lon / num_longitude  # 0 to 2pi
            
            # Calculate point position
            point_x = center_x + radius * math.sin(theta) * math.cos(phi)
            point_y = center_y + radius * math.cos(theta)
            point_z = center_z + radius * math.sin(theta) * math.sin(phi)
            
            point_name = f"sphere_{lat}_{lon}"
            
            # For hemispheres, check if point is on the correct side of the cut plane
            if hemisphere_axis_angle is not None:
                point_vec = np.array([point_x - center_x, point_y - center_y, point_z - center_z])
                if np.dot(point_vec, cut_normal) < 0:
                    continue
            
            # Set hide_point flag for all sphere points
            points.append({
                "name": point_name,
                "x": point_x,
                "y": point_y,
                "z": point_z,
                "hide_point": True
            })
            existing_points.add(point_name)
    
    # Add radius edge (from center to equator point)
    if radius_label:
        equator_point = f"sphere_{num_latitude//2}_0"
        if equator_point in existing_points:
            radius_edge = {"start_point": "center", "end_point": equator_point, "label": radius_label}
            edges.append(radius_edge)
    
    # Add equatorial circle edges
    equator_lat = num_latitude // 2  # Middle latitude is the equator
    for lon in range(num_longitude):
        next_lon = (lon + 1) % num_longitude
        start_point = f"sphere_{equator_lat}_{lon}"
        end_point = f"sphere_{equator_lat}_{next_lon}"
        
        # Only add edge if both points exist
        if start_point in existing_points and end_point in existing_points:
            edges.append({
                "start_point": start_point,
                "end_point": end_point
            })
    
    # Create faces between adjacent points
    for lat in range(num_latitude):
        for lon in range(num_longitude):
            next_lon = (lon + 1) % num_longitude
            
            # Current row points
            p1 = f"sphere_{lat}_{lon}"
            p2 = f"sphere_{lat}_{next_lon}"
            # Next row points
            p3 = f"sphere_{lat + 1}_{lon}"
            p4 = f"sphere_{lat + 1}_{next_lon}"
            
            # Skip faces that involve missing points
            if not all(p in existing_points for p in [p1, p2, p3, p4]):
                continue
            
            # Create two triangles for each quad
            faces.append({
                "points": [p1, p2, p4],
                "color": curved_face_color
            })
            faces.append({
                "points": [p1, p4, p3],
                "color": curved_face_color
            })
    
    # For hemispheres, add the flat face at the cut plane
    if hemisphere_axis_angle is not None:
        # Find all points that lie on the cut plane (within a small epsilon)
        cut_points = []
        for point in points:
            if point["name"] == "center":
                continue
            point_vec = np.array([point["x"] - center_x, point["y"] - center_y, point["z"] - center_z])
            if abs(np.dot(point_vec, cut_normal)) < 1e-10:
                cut_points.append(point["name"])
        
        # Sort the cut points to form a circle
        if cut_points:
            # Calculate angles of points in the cut plane
            cut_point_angles = []
            for point_name in cut_points:
                point = next(p for p in points if p["name"] == point_name)
                point_vec = np.array([point["x"] - center_x, point["y"] - center_y, point["z"] - center_z])
                # Project point onto plane perpendicular to cut_normal
                perp1 = np.array([-cut_normal[1], cut_normal[0], 0])  # Perpendicular in xy-plane
                perp2 = np.cross(cut_normal, perp1)  # Second perpendicular vector
                angle = math.atan2(np.dot(point_vec, perp2), np.dot(point_vec, perp1))
                cut_point_angles.append((angle, point_name))
            
            # Sort by angle
            cut_points = [p[1] for p in sorted(cut_point_angles)]
            
            # Add the flat face
            faces.append({
                "points": cut_points,
                "color": curved_face_color
            })
            
            # Add edges along the cut plane for better visualization
            for i in range(len(cut_points)):
                next_i = (i + 1) % len(cut_points)
                edges.append({
                    "start_point": cut_points[i],
                    "end_point": cut_points[next_i]
                })
    
    return {
        "points": points,
        "edges": edges,
        "faces": faces,
        "shape_name": "Hemisphere" if hemisphere_axis_angle is not None else "Sphere"
    }

def generate_cylinder_points_and_faces(base1_x: float, base1_y: float, base1_z: float,
                                     base2_x: float, base2_y: float, base2_z: float,
                                     radius: float, num_segments: int = 64,
                                     base1_label: str = None, base2_label: str = None,
                                     radius_label: str = None, height_label: str = None,
                                     curved_face_color: str = 'lightcoral') -> Dict[str, Any]:
    """
    Generate points and faces for a cylinder.
    
    Parameters
    ----------
    base1_x, base1_y, base1_z : float
        Center point of the first circular base
    base2_x, base2_y, base2_z : float
        Center point of the second circular base
    radius : float
        Radius of the circular bases
    num_segments : int
        Number of segments to approximate the circular bases
    curved_face_color : str
        Color to use for the curved faces of the cylinder
        
    Returns
    -------
    Dict[str, Any]
        Dictionary with 'points', 'edges', 'faces' for the cylinder
    """
    points = []
    edges = []
    faces = []
    
    # Add center points
    base1_point = {"name": "base1_center", "x": base1_x, "y": base1_y, "z": base1_z}
    if base1_label:
        base1_point["label"] = base1_label
    points.append(base1_point)
    
    base2_point = {"name": "base2_center", "x": base2_x, "y": base2_y, "z": base2_z}
    if base2_label:
        base2_point["label"] = base2_label
    points.append(base2_point)
    
    # Calculate the axis vector and perpendicular vectors
    axis = np.array([base2_x - base1_x, base2_y - base1_y, base2_z - base1_z])
    axis = axis / np.linalg.norm(axis)
    
    # Find two perpendicular vectors to the axis
    if abs(axis[0]) < 0.9:
        perp1 = np.cross(axis, [1, 0, 0])
    else:
        perp1 = np.cross(axis, [0, 1, 0])
    perp1 = perp1 / np.linalg.norm(perp1)
    perp2 = np.cross(axis, perp1)
    perp2 = perp2 / np.linalg.norm(perp2)
    
    # Generate points around both circular bases
    for i in range(num_segments):
        angle = 2 * math.pi * i / num_segments
        offset = radius * (math.cos(angle) * perp1 + math.sin(angle) * perp2)
        
        # Base 1 point
        point1_x = base1_x + offset[0]
        point1_y = base1_y + offset[1]
        point1_z = base1_z + offset[2]
        points.append({
            "name": f"base1_{i}",
            "x": point1_x,
            "y": point1_y,
            "z": point1_z,
            "hide_point": True
        })
        
        # Base 2 point
        point2_x = base2_x + offset[0]
        point2_y = base2_y + offset[1]
        point2_z = base2_z + offset[2]
        points.append({
            "name": f"base2_{i}",
            "x": point2_x,
            "y": point2_y,
            "z": point2_z,
            "hide_point": True
        })
    
    # Create edges around both bases (full circles)
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        edges.append({"start_point": f"base1_{i}", "end_point": f"base1_{next_i}"})
        edges.append({"start_point": f"base2_{i}", "end_point": f"base2_{next_i}"})
    
    # Create only silhouette edges between bases (not all connecting lines)
    # Add edges at key points: front-left, front-right, back-left, back-right for 3D appearance
    quarter_seg = num_segments // 4
    silhouette_points = [
        quarter_seg,
        3 * quarter_seg
    ]
    
    for point_idx in silhouette_points:
        edges.append({"start_point": f"base1_{point_idx}", "end_point": f"base2_{point_idx}"})
    
    # Add radius edge (from center to right side point for clear visibility)
    right_point_idx = 3 * quarter_seg
    radius_edge = {"start_point": "base1_center", "end_point": f"base1_{right_point_idx}"}
    if radius_label:
        radius_edge["label"] = radius_label
    edges.append(radius_edge)
    
    # Add height edge (between base centers)
    height_edge = {"start_point": "base1_center", "end_point": "base2_center"}
    if height_label:
        height_edge["label"] = height_label
    edges.append(height_edge)
    
    # Create side faces (rectangles)
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        faces.append({
            "points": [f"base1_{i}", f"base1_{next_i}", f"base2_{next_i}", f"base2_{i}"],
            "color": curved_face_color
        })
    
    # Create the base faces
    base1_points = [f"base1_{i}" for i in range(num_segments)]
    base2_points = [f"base2_{i}" for i in range(num_segments)]
    faces.append({
        "points": base1_points,
        "color": curved_face_color
    })
    faces.append({
        "points": base2_points,
        "color": curved_face_color
    })
    
    return {
        "points": points,
        "edges": edges,
        "faces": faces,
        "shape_name": "Cylinder"
    }

def generate_3d_shape_image(shapes: List[Dict[str, Any]], background_color: str = 'transparent') -> str:
    """
    Generate an image of one or more 3D shapes using isometric projection with proper z-order compositing.
    
    Uses standard Cartesian coordinates where positive Y is "up".
    
    Parameters
    ----------
    shapes : List[Dict[str, Any]]
        List of shapes to render. Each shape should have:
        - points: List of dicts with 'name', 'x', 'y', 'z', 'color' (optional), 'label' (optional)
          where positive Y corresponds to higher vertical placement
        - edges: List of dicts with 'start_point', 'end_point', 'color' (optional), 'label' (optional)
        - faces: List of dicts with 'points' (list of point names), 'color' (optional), 'label' (optional)
        - shape_name: Optional name for the shape
    background_color : str, default 'transparent'
        The background color behind the shapes. Use 'transparent' for transparent background,
        or any valid color name or hex code.
        
    Returns
    -------
    str
        The URL of the generated 3D shape image
    """
    logger.info(f"Generating 3D shape image with {len(shapes)} shapes using PIL")
    
    # Check if any shapes are curved (cone, cylinder, sphere) to determine projection angle
    has_curved_shapes = any(shape.get('shape_type') in ['cone', 'cylinder', 'sphere', 'hemisphere'] for shape in shapes)
    
    # Determine projection angle and tilt based on shape types
    if has_curved_shapes:
        angle_degrees = -90
        tilt_degrees = 33
        logger.info(f"Curved shapes detected, using {angle_degrees}° projection angle with {tilt_degrees}° tilt")
    else:
        angle_degrees = -25
        tilt_degrees = 0
        logger.info(f"Polyhedron shapes detected, using {angle_degrees}° projection angle with {tilt_degrees}° tilt")
    
    # Create base image with specified background
    if background_color == 'transparent':
        img = Image.new('RGBA', 
                       (RenderingConstants.IMAGE_WIDTH, RenderingConstants.IMAGE_HEIGHT), 
                       (0, 0, 0, 0))  # Fully transparent
    else:
        bg_color = parse_color(background_color)
        img = Image.new('RGBA', 
                       (RenderingConstants.IMAGE_WIDTH, RenderingConstants.IMAGE_HEIGHT), 
                       (*bg_color, 255))  # Solid background
    
    # Track all projected points and drawable elements
    all_projected_points = []
    all_drawable_elements = []
    all_white_faces = []
    
    # First pass: Process shapes and collect white backing faces
    processed_shapes = []
    for shape in shapes:
        shape_type = shape.get('shape_type', 'polyhedron')
        
        if shape_type == 'cone':
            cone_data = generate_cone_points_and_faces(
                center_x=shape['base_center']['x'],
                center_y=shape['base_center']['y'],
                center_z=shape['base_center']['z'],
                radius=shape['radius'],
                apex_x=shape['apex']['x'],
                apex_y=shape['apex']['y'],
                apex_z=shape['apex']['z'],
                base_label=shape.get('base_center', {}).get('label'),
                apex_label=shape.get('apex', {}).get('label'),
                radius_label=shape.get('radius_label'),
                height_label=shape.get('height_label'),
                curved_face_color=shape.get('curved_face_color', 'lightcoral')
            )
            processed_shapes.append(cone_data)
        elif shape_type == 'sphere':
            sphere_data = generate_sphere_points_and_faces(
                center_x=shape['center']['x'],
                center_y=shape['center']['y'],
                center_z=shape['center']['z'],
                radius=shape['radius'],
                center_label=shape.get('center', {}).get('label'),
                radius_label=shape.get('radius_label'),
                curved_face_color=shape.get('curved_face_color', 'lightcoral'),
                hemisphere_axis_angle=shape.get('hemisphere_axis_angle')
            )
            processed_shapes.append(sphere_data)
        elif shape_type == 'cylinder':
            cylinder_data = generate_cylinder_points_and_faces(
                base1_x=shape['base1_center']['x'],
                base1_y=shape['base1_center']['y'],
                base1_z=shape['base1_center']['z'],
                base2_x=shape['base2_center']['x'],
                base2_y=shape['base2_center']['y'],
                base2_z=shape['base2_center']['z'],
                radius=shape['radius'],
                base1_label=shape.get('base1_center', {}).get('label'),
                base2_label=shape.get('base2_center', {}).get('label'),
                radius_label=shape.get('radius_label'),
                height_label=shape.get('height_label'),
                curved_face_color=shape.get('curved_face_color', 'lightcoral')
            )
            processed_shapes.append(cylinder_data)
        else:
            processed_shapes.append(shape)
    
    # Process all shapes and create white backing faces
    for shape in processed_shapes:
        point_lookup, projected_points = process_shape_points(shape.get('points', []), angle_degrees, tilt_degrees)
        all_projected_points.extend(projected_points.values())
        
        # Create white backing faces
        white_faces = []
        for face in shape.get('faces', []):
            white_face = face.copy()
            white_face['color'] = 'white'  # Set color to white
            white_face['is_backing_face'] = True  # Mark as backing face
            white_faces.append(white_face)
        
        if white_faces:
            white_points = []
            for point in shape.get('points', []):
                white_point = point.copy()
                white_point['label'] = None
                white_points.append(white_point)
            white_shape = {
                'points': white_points,
                'edges': [],  # No edges needed for backing faces
                'faces': white_faces
            }
            all_white_faces.append((white_shape, point_lookup, projected_points))
    
    # Second pass: Add all white backing faces first, then process regular shapes
    viewing_direction_no_tilt = calculate_viewing_direction_without_tilt(angle_degrees)
    
    # Add all white backing faces with maximum depth to ensure they're rendered first
    max_depth = float('inf')
    for white_shape, point_lookup, projected_points in all_white_faces:
        white_elements = create_drawable_elements(white_shape, point_lookup, projected_points, viewing_direction_no_tilt)
        # Set all white face elements to maximum depth
        white_elements = [element._replace(depth=max_depth) if element.element_type == 'face' else element 
                        for element in white_elements]
        all_drawable_elements.extend(white_elements)
    
    # Now add all regular shapes
    for shape in processed_shapes:
        point_lookup, projected_points = process_shape_points(shape.get('points', []), angle_degrees, tilt_degrees)
        shape_elements = create_drawable_elements(shape, point_lookup, projected_points, viewing_direction_no_tilt)
        all_drawable_elements.extend(shape_elements)
    
    # Calculate coordinate transformation and create projection function
    project_to_image_coords = create_coordinate_transform(all_projected_points)
    
    # Render all elements and return final image
    return render_all_elements(img, all_drawable_elements, project_to_image_coords, angle_degrees, tilt_degrees)

def generate_3d_shape_image_tool() -> tuple[dict, Callable]:
    spec = {
        "type": "function",
        "name": "generate_3d_shape_image",
                        "description": "Generate an image of one or more 3D geometric shapes using isometric projection. Uses standard Cartesian coordinates where positive Y is 'up'. Supports both polyhedra (defined by points/edges/faces) and curved shapes (cones, spheres, cylinders) with smooth circular components.\n\nIMPORTANT USAGE RULES:\n1. Point coordinates MUST be objects with x, y, z properties: {\"x\": 1.0, \"y\": 2.0, \"z\": 3.0}\n2. Point names in edges and faces MUST exactly match point names defined in the points array\n3. Colors must be either valid color names ('red', 'blue', 'lightgray') or valid hex codes ('#FF0000')\n4. All point names used in edges and faces must be defined in the points array first\n5. For polyhedra: points, edges, and faces arrays are all required\n6. For curved shapes: use the specific parameters (base_center, apex, radius, etc.)\n\nEXAMPLE CUBE:\n{\n  \"shapes\": [{\n    \"shape_type\": \"polyhedron\",\n    \"points\": [\n      {\"name\": \"A\", \"x\": 0, \"y\": 0, \"z\": 0, \"label\": \"A\"},\n      {\"name\": \"B\", \"x\": 1, \"y\": 0, \"z\": 0, \"label\": \"B\"},\n      {\"name\": \"C\", \"x\": 1, \"y\": 1, \"z\": 0, \"label\": \"C\"},\n      {\"name\": \"D\", \"x\": 0, \"y\": 1, \"z\": 0, \"label\": \"D\"}\n    ],\n    \"edges\": [\n      {\"start_point\": \"A\", \"end_point\": \"B\"},\n      {\"start_point\": \"B\", \"end_point\": \"C\"},\n      {\"start_point\": \"C\", \"end_point\": \"D\"},\n      {\"start_point\": \"D\", \"end_point\": \"A\"}\n    ],\n    \"faces\": [\n      {\"points\": [\"A\", \"B\", \"C\", \"D\"], \"color\": \"lightblue\"}\n    ]\n  }]\n}",
        "parameters": {
            "type": "object",
            "properties": {
                "shapes": {
                    "type": "array",
                    "description": "List of 3D shapes to render in the image",
                    "items": {
                        "type": "object",
                        "properties": {
                            "shape_type": {
                                "type": "string",
                                "enum": ["polyhedron", "cone", "sphere", "cylinder"],
                                "description": "Type of shape: 'polyhedron' for shapes defined by points/edges/faces, 'cone' for cones, 'sphere' for spheres, 'cylinder' for cylinders"
                            },
                            "points": {
                                "type": "array",
                                "description": "List of 3D points (vertices) that define the shape (for polyhedron type only)",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "Unique name for this point (used to reference in edges and faces). Use simple alphanumeric names like 'A', 'B1', 'vertex_top', etc. Avoid special characters."
                                        },
                                        "x": {
                                            "type": "number",
                                            "description": "X coordinate of the point (must be a number, not a string or other type)"
                                        },
                                        "y": {
                                            "type": "number", 
                                            "description": "Y coordinate of the point (positive Y is up, must be a number)"
                                        },
                                        "z": {
                                            "type": "number",
                                            "description": "Z coordinate of the point (must be a number, not a string or other type)"
                                        },
                                        "color": {
                                            "type": "string",
                                            "description": "Color of the point (optional, defaults to black). Must be a valid color name like 'red', 'blue', 'lightgray' or a hex code like '#FF0000'. Do NOT use invalid color names."
                                        },
                                        "label": {
                                            "type": ["string", "null"],
                                            "description": "Text label for the point (optional, null for no label)"
                                        }
                                    },
                                    "required": ["name", "x", "y", "z"]
                                }
                            },
                            "edges": {
                                "type": "array",
                                "description": "List of edges (lines) connecting points (for polyhedron type only)",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "start_point": {
                                            "type": "string",
                                            "description": "Name of the starting point (MUST exactly match a point name from the points array)"
                                        },
                                        "end_point": {
                                            "type": "string",
                                            "description": "Name of the ending point (MUST exactly match a point name from the points array)"
                                        },
                                        "color": {
                                            "type": "string",
                                            "description": "Color of the edge (optional, defaults to black). Must be a valid color name like 'red', 'blue', 'lightgray' or a hex code like '#FF0000'."
                                        },
                                        "dashed": {
                                            "type": "boolean",
                                            "description": "Whether to render the edge as a dashed line (optional, defaults to false)"
                                        },
                                        "label": {
                                            "type": ["string", "null"],
                                            "description": "Text label for the edge (optional, null for no label)."
                                        }
                                    },
                                    "required": ["start_point", "end_point"]
                                }
                            },
                            "faces": {
                                "type": "array",
                                "description": "List of faces (polygons) defined by connecting points (for polyhedron type only)",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "points": {
                                            "type": "array",
                                            "description": "List of point names that define the face (in order). Each name MUST exactly match a point name from the points array.",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "color": {
                                            "type": "string",
                                            "description": "Color of the face (optional, defaults to lightgray). Must be a valid color name like 'red', 'blue', 'lightgray' or a hex code like '#FF0000'."
                                        },
                                        "label": {
                                            "type": ["string", "null"],
                                            "description": "Text label for the face (optional, null for no label)"
                                        }
                                    },
                                    "required": ["points"]
                                }
                            },
                            "base_center": {
                                "type": "object",
                                "description": "Center point of the cone's circular base (for cone type only). Must be an object with x, y, z number properties.",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "z": {"type": "number"},
                                    "label": {"type": "string", "description": "Optional label for the base center"}
                                },
                                "required": ["x", "y", "z"]
                            },
                            "apex": {
                                "type": "object",
                                "description": "Apex point of the cone (for cone type only). Must be an object with x, y, z number properties.",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "z": {"type": "number"},
                                    "label": {"type": "string", "description": "Optional label for the apex"}
                                },
                                "required": ["x", "y", "z"]
                            },
                            "center": {
                                "type": "object",
                                "description": "Center point of the sphere (for sphere type only). Must be an object with x, y, z number properties.",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "z": {"type": "number"},
                                    "label": {"type": "string", "description": "Optional label for the center"}
                                },
                                "required": ["x", "y", "z"]
                            },
                            "base1_center": {
                                "type": "object",
                                "description": "Center point of the first circular base (for cylinder type only). Must be an object with x, y, z number properties.",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "z": {"type": "number"},
                                    "label": {"type": "string", "description": "Optional label for the first base"}
                                },
                                "required": ["x", "y", "z"]
                            },
                            "base2_center": {
                                "type": "object",
                                "description": "Center point of the second circular base (for cylinder type only). Must be an object with x, y, z number properties.",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "z": {"type": "number"},
                                    "label": {"type": "string", "description": "Optional label for the second base"}
                                },
                                "required": ["x", "y", "z"]
                            },
                            "radius": {
                                "type": "number",
                                "description": "Radius of the circular base (for cone/cylinder) or sphere (for sphere type only)",
                                "minimum": 0
                            },
                            "radius_label": {
                                "type": "string",
                                "description": "Optional label for the radius measurement (displayed on radius edge)"
                            },
                            "height_label": {
                                "type": "string",
                                "description": "Optional label for the height measurement (displayed on height edge, for cone/cylinder only)"
                            },
                            "curved_face_color": {
                                "type": "string",
                                "description": "Color of the curved faces of the cone/cylinder/sphere (optional, defaults to lightcoral). Must be a valid color name or hex code."
                            },
                            "hemisphere_axis_angle": {
                                "type": "number",
                                "description": "For hemispheres only: if provided, creates a hemisphere with the flat side oriented at this angle in the xy-plane (in degrees, 0 = parallel to y-axis, 90 = parallel to x-axis). MUST be specified to create a hemisphere. Set to None to create a full sphere. Ensure calculations for the center of the hemisphere are correct given the half of a full sphere that won't be included. For example, if placing a hemisphere on top of a cylinder, the center of the hemisphere should be the same as the center of the top of the cylinder, not the center of the top of the cylinder plus the radius of the hemisphere."
                            },
                            "num_latitude": {
                                "type": "integer",
                                "description": "Number of latitude divisions for sphere (optional, defaults to 16)",
                                "minimum": 3,
                                "maximum": 32
                            },
                            "num_longitude": {
                                "type": "integer",
                                "description": "Number of longitude divisions for sphere (optional, defaults to 32)",
                                "minimum": 3,
                                "maximum": 64
                            },
                            "shape_name": {
                                "type": "string",
                                "description": "Optional name for the shape"
                            }
                        },
                        "required": ["shape_type"],
                        "if": {
                            "properties": {
                                "shape_type": {"const": "polyhedron"}
                            }
                        },
                        "then": {
                            "required": ["points", "edges", "faces"]
                        },
                        "else": {
                            "if": {
                                "properties": {
                                    "shape_type": {"const": "cone"}
                                }
                            },
                            "then": {
                                "required": ["base_center", "apex", "radius"]
                            },
                            "else": {
                                "if": {
                                    "properties": {
                                        "shape_type": {"const": "sphere"}
                                    }
                                },
                                "then": {
                                    "required": ["center", "radius"]
                                },
                                "else": {
                                    "if": {
                                        "properties": {
                                            "shape_type": {"const": "cylinder"}
                                        }
                                    },
                                    "then": {
                                        "required": ["base1_center", "base2_center", "radius"]
                                    }
                                }
                            }
                        }
                    }
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the shapes. Use 'transparent' for transparent background, or any valid color name ('white', 'red', 'blue', 'lightgray', etc.) or hex code ('#FF0000'). Defaults to 'transparent'. Valid color names include: black, white, red, green, blue, yellow, cyan, magenta, purple, orange, brown, pink, lime, teal, indigo, gray, lightgray, lightblue, lightgreen, lightcoral, lightyellow, lightcyan, lightmagenta, lightpurple, lightorange, lightbrown, lightpink, lightlime, lightteal, lightindigo."
                }
            },
            "required": ["shapes"]
        }
    }
    return spec, generate_3d_shape_image

