from __future__ import annotations

import io
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

import matplotlib
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Ellipse, Polygon, Rectangle

from utils.supabase_utils import upload_image_to_supabase

# Set matplotlib to use a non-interactive backend
matplotlib.use('Agg')

# Configure matplotlib to prevent memory leaks and limit figure accumulation
matplotlib.rcParams['figure.max_open_warning'] = 5  # Warn much earlier
matplotlib.rcParams['figure.raise_window'] = False   # Don't raise GUI windows

logger = logging.getLogger(__name__)

def calculate_shape_bounds(points: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    """
    Calculate the bounding box of a set of 2D points.
    
    Parameters
    ----------
    points : List[Tuple[float, float]]
        List of (x, y) coordinates
        
    Returns
    -------
    Tuple[float, float, float, float]
        (min_x, max_x, min_y, max_y) bounds
    """
    if not points:
        return 0, 0, 0, 0
        
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    return min(x_coords), max(x_coords), min(y_coords), max(y_coords)

def calculate_angle_marker_size(bounds: Tuple[float, float, float, float]) -> float:
    """
    Calculate appropriate angle marker size based on shape bounds.
    
    Parameters
    ----------
    bounds : Tuple[float, float, float, float]
        (min_x, max_x, min_y, max_y) bounds
        
    Returns
    -------
    float
        Radius for angle markers
    """
    x_range = bounds[1] - bounds[0]
    y_range = bounds[3] - bounds[2]
    shape_size = max(x_range, y_range)
    return shape_size * 0.1  # Angle marker is 10% of shape size

def calculate_centroid(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate the centroid of a set of points.
    
    Parameters
    ----------
    points : List[Tuple[float, float]]
        List of (x, y) coordinates
        
    Returns
    -------
    Tuple[float, float]
        (x, y) coordinates of centroid
    """
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    return np.mean(x_coords), np.mean(y_coords)

def draw_angle_marker(ax: plt.Axes, 
                     vertex: Tuple[float, float],
                     point1: Tuple[float, float],
                     point2: Tuple[float, float],
                     radius: float,
                     color: str = 'black',
                     label: Optional[str] = None) -> None:
    """
    Draw an angle marker and optional label between two edges meeting at a vertex.
    Uses vector cross products to determine the correct angle direction, ensuring
    interior angles are drawn correctly. For right angles (90°), draws a square
    indicator instead of an arc, showing only the two interior edges that meet at
    the corner point.
    
    Parameters
    ----------
    ax : plt.Axes
        Matplotlib axes to draw on
    vertex : Tuple[float, float]
        (x, y) coordinates of angle vertex
    point1, point2 : Tuple[float, float]
        (x, y) coordinates of points forming the angle
    radius : float
        Radius of the angle marker arc or size of right angle square
    color : str
        Color for the angle marker and label
    label : Optional[str]
        Label to draw near the angle marker
    """
    # Calculate vectors from vertex to points
    vec1 = np.array([point1[0] - vertex[0], point1[1] - vertex[1]])
    vec2 = np.array([point2[0] - vertex[0], point2[1] - vertex[1]])
    
    # Normalize vectors
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
    
    # Calculate dot product to check for right angle
    dot_product = np.clip(np.dot(vec1_norm, vec2_norm), -1.0, 1.0)
    angle = np.arccos(dot_product)
    is_right_angle = abs(angle - np.pi/2) < 0.01  # Allow small deviation from 90°
    
    if is_right_angle:
        # For right angles, draw a square indicator (only interior edges)
        # Calculate the two points that form the right angle square with the vertex
        p1_dist = radius * vec1_norm * 0.7
        p2_dist = radius * vec2_norm * 0.7
        
        # Calculate the corner point of the square
        corner_point = np.array([vertex[0], vertex[1]]) + p1_dist + p2_dist
        
        # Draw the two edges that meet at the corner point
        ax.plot([vertex[0] + p1_dist[0], corner_point[0]],
                [vertex[1] + p1_dist[1], corner_point[1]],
                color=color, linewidth=3, zorder=6)
        ax.plot([vertex[0] + p2_dist[0], corner_point[0]],
                [vertex[1] + p2_dist[1], corner_point[1]],
                color=color, linewidth=3, zorder=6)
        
        # Position label near the corner point but slightly inside
        if label is not None:
            # Move label position slightly towards vertex to avoid overlap
            label_x = corner_point[0] + radius * 0.3 * (vec1_norm[0] + vec2_norm[0])
            label_y = corner_point[1] + radius * 0.3 * (vec1_norm[1] + vec2_norm[1])
            
            text = ax.text(label_x, label_y, label,
                          color=color, ha='center', va='center',
                          fontsize=22, weight='bold', zorder=7)
            text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    else:
        # Calculate angles in the range [-π, π)
        start_angle = np.arctan2(vec1[1], vec1[0])
        end_angle = np.arctan2(vec2[1], vec2[0])
        
        # Calculate cross product to determine correct direction
        cross_z = vec1[0] * vec2[1] - vec1[1] * vec2[0]
        
        # If cross product is negative, we need to draw the larger angle
        if cross_z < 0:
            # Adjust end_angle to get the larger angle
            if end_angle > start_angle:
                end_angle -= 2 * np.pi
            elif end_angle < start_angle:
                end_angle += 2 * np.pi
                
            # Swap angles to maintain counterclockwise drawing
            start_angle, end_angle = end_angle, start_angle
        else:
            # Ensure we draw counterclockwise for positive cross product
            if end_angle < start_angle:
                end_angle += 2 * np.pi
        
        # Convert to degrees for matplotlib
        theta1 = np.degrees(start_angle)
        theta2 = np.degrees(end_angle)
        
        # Draw arc
        arc = Arc((vertex[0], vertex[1]), 2 * radius, 2 * radius,
                 theta1=theta1, theta2=theta2, color=color, linewidth=3, zorder=6)
        ax.add_patch(arc)
        
        # Add label if specified
        if label is not None:
            # Calculate the actual angle being drawn
            angle_diff = theta2 - theta1
            if angle_diff < 0:
                angle_diff += 360
            
            # Calculate the bisector angle
            # For angles > 180°, we want to bisect the smaller angle (360° - angle_diff)
            if angle_diff > 180:
                mid_angle = theta1 + (360 - angle_diff) / 2 + 180
            else:
                mid_angle = theta1 + angle_diff / 2
                
            # Convert back to radians for positioning
            mid_angle_rad = np.radians(mid_angle)
            label_x = vertex[0] + radius * 1.5 * np.cos(mid_angle_rad)
            label_y = vertex[1] + radius * 1.5 * np.sin(mid_angle_rad)
            
            text = ax.text(label_x, label_y, label,
                          color=color, ha='center', va='center',
                          fontsize=22, weight='bold', zorder=7)
            text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])

def draw_axis_marker(ax: plt.Axes,
                    center: Tuple[float, float],
                    length: float,
                    angle: float,
                    color: str = 'black',
                    label: Optional[str] = None) -> None:
    """
    Draw an axis marker through the center of an ellipse.
    
    Parameters
    ----------
    ax : plt.Axes
        Matplotlib axes to draw on
    center : Tuple[float, float]
        (x, y) coordinates of ellipse center
    length : float
        Length of the axis (full diameter)
    angle : float
        Angle of the axis in radians
    color : str
        Color for the axis line and label
    label : Optional[str]
        Label to draw near the axis
    """
    # Calculate endpoint coordinates
    dx = length/2 * np.cos(angle)
    dy = length/2 * np.sin(angle)
    
    # Draw line through center
    ax.plot([center[0] - dx, center[0] + dx],
            [center[1] - dy, center[1] + dy],
            color=color, linewidth=3, zorder=1)
    
    # Add label if specified
    if label is not None:
        label_x = center[0] + (dx * 0.5)
        label_y = center[1] + (dy * 0.5)
        
        text = ax.text(label_x, label_y, label,
                      color=color, ha='center', va='center',
                      fontsize=22, weight='bold', zorder=2,
                      bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))
        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])

def check_for_common_vertex_errors(vertices: List[Dict[str, Any]],
fill_color: Optional[str]) -> Optional[str]:
    """
    Check for common vertex ordering errors when using fill_color.
    Returns warning message if potential issue detected, None otherwise.
    """
    if not fill_color or fill_color == 'transparent' or len(vertices) <= 4:
        return None
    
    # Check for the common error pattern: rectangular shape with interior division points
    if len(vertices) == 6:
        coords = [(v['x'], v['y']) for v in vertices]
        y_values = [p[1] for p in coords]
        
        # If we have exactly 2 unique Y values and 3 points at each Y level,
        # this suggests a rectangle with interior division points included
        unique_y = list(set(y_values))
        if len(unique_y) == 2:
            bottom_y, top_y = min(unique_y), max(unique_y)
            bottom_points = [p for p in coords if p[1] == bottom_y]
            top_points = [p for p in coords if p[1] == top_y]
            
            if len(bottom_points) == 3 and len(top_points) == 3:
                vertex_names = [v['name'] for v in vertices]
                return (
                    f"Warning: Vertex list appears to include interior division points "
                    f"({', '.join(vertex_names)}), which may create white gaps in filled polygons. "
                    f"Consider using only corner vertices or separate polygons."
                )
    
    return None

def process_polygon(ax: plt.Axes,
                   vertices: List[Dict[str, Any]],
                   edges: List[Dict[str, Any]],
                   angles: List[Dict[str, Any]],
                   fill_color: Optional[str] = None,
                   label: Optional[str] = None) -> Tuple[float, float, float, float]:
    """
    Process and draw a polygon with its vertices, edges, angles, and labels.
    
    Parameters
    ----------
    ax : plt.Axes
        Matplotlib axes to draw on
    vertices : List[Dict[str, Any]]
        List of vertex definitions
    edges : List[Dict[str, Any]]
        List of edge definitions
    angles : List[Dict[str, Any]]
        List of angle definitions
    fill_color : Optional[str]
        Color to fill the polygon with. Use 'transparent' for no fill.
    label : Optional[str]
        Label for the entire polygon
        
    Returns
    -------
    Tuple[float, float, float, float]
        (min_x, max_x, min_y, max_y) bounds of the polygon
    """
    # Check for common vertex ordering errors and log warning if found
    vertex_warning = check_for_common_vertex_errors(vertices, fill_color)
    if vertex_warning:
        logger.warning(vertex_warning)
    
    # Create vertex lookup
    vertex_lookup = {v['name']: (v['x'], v['y']) for v in vertices}
    
    # Get all points for bounds calculation
    points = list(vertex_lookup.values())
    bounds = calculate_shape_bounds(points)
    
    # Draw filled polygon if fill color specified and not transparent
    if fill_color and fill_color != 'transparent':
        polygon = Polygon(points, facecolor=fill_color, alpha=1.0, zorder=1)
        ax.add_patch(polygon)
    
    # Auto-generate edges if none provided (connect vertices in order to form closed polygon)
    if len(edges) == 0:
        vertex_names = [v['name'] for v in vertices]
        auto_edges = []
        for i in range(len(vertex_names)):
            start_point = vertex_names[i]
            end_point = vertex_names[(i + 1) % len(vertex_names)]
            auto_edges.append({
                'start_point': start_point,
                'end_point': end_point
            })
        edges = auto_edges
    
    # Draw edges
    for edge in edges:
        start = vertex_lookup[edge['start_point']]
        end = vertex_lookup[edge['end_point']]
        color = edge.get('color', 'black')
        # Handle empty string colors and transparent
        if not color or color.strip() == '' or color.strip().lower() == 'transparent':
            color = 'black'
        style = '--' if edge.get('style', 'solid') == 'dashed' else '-'
        
        ax.plot([start[0], end[0]], [start[1], end[1]],
                color=color, linestyle=style, linewidth=3, zorder=5)
        
        # Add edge label if specified
        if 'label' in edge:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            
            text = ax.text(mid_x, mid_y, edge['label'],
                         color=color, ha='center', va='center',
                         fontsize=22, weight='bold', zorder=7,
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))
            text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    
    # Create a mapping of vertex to its connected points from edges
    vertex_connections = {}
    for edge in edges:
        start = edge['start_point']
        end = edge['end_point']
        if start not in vertex_connections:
            vertex_connections[start] = []
        if end not in vertex_connections:
            vertex_connections[end] = []
        vertex_connections[start].append(end)
        vertex_connections[end].append(start)
    
    # Create a mapping of vertex to its angles
    vertex_angles = {}
    
    # First add angles from explicit angle definitions
    for angle in angles:
        vertex = angle['vertex']
        if vertex not in vertex_angles:
            vertex_angles[vertex] = []
        # Calculate vectors for this angle
        v_point = vertex_lookup[vertex]
        p1 = vertex_lookup[angle['point1']]
        p2 = vertex_lookup[angle['point2']]
        vec1 = np.array([p1[0] - v_point[0], p1[1] - v_point[1]])
        vec2 = np.array([p2[0] - v_point[0], p2[1] - v_point[1]])
        # Calculate angle in radians
        angle1 = np.arctan2(vec1[1], vec1[0])
        angle2 = np.arctan2(vec2[1], vec2[0])
        vertex_angles[vertex].append((angle1, angle2))
    
    # Then calculate angles from edges for vertices without explicit angles
    for vertex_name, connected_points in vertex_connections.items():
        if vertex_name not in vertex_angles and len(connected_points) >= 2:
            vertex_angles[vertex_name] = []
            v_point = vertex_lookup[vertex_name]
            # Calculate angles between each pair of connected points
            for i in range(len(connected_points)):
                for j in range(i + 1, len(connected_points)):
                    p1 = vertex_lookup[connected_points[i]]
                    p2 = vertex_lookup[connected_points[j]]
                    vec1 = np.array([p1[0] - v_point[0], p1[1] - v_point[1]])
                    vec2 = np.array([p2[0] - v_point[0], p2[1] - v_point[1]])
                    angle1 = np.arctan2(vec1[1], vec1[0])
                    angle2 = np.arctan2(vec2[1], vec2[0])
                    vertex_angles[vertex_name].append((angle1, angle2))
    
    # Draw vertices and their labels
    for vertex in vertices:
        x, y = vertex['x'], vertex['y']
        marker_size = 6 if vertex.get('show_vertex_point_marker', False) else 1
        color = vertex.get('color', 'black')
        # Handle empty string colors and transparent
        if not color or color.strip() == '' or color.strip().lower() == 'transparent':
            color = 'black'
        name = vertex['name']
        
        ax.plot(x, y, 'o', color=color, markersize=marker_size, zorder=10)
        
        if 'label' in vertex:
            # Calculate label position based on angles
            if name in vertex_angles:
                # Get all angles for this vertex
                angles_at_vertex = vertex_angles[name]
                # Convert all angles to be in [0, 2π)
                normalized_angles = []
                for a1, a2 in angles_at_vertex:
                    if a1 < 0:
                        a1 += 2 * np.pi
                    if a2 < 0:
                        a2 += 2 * np.pi
                    normalized_angles.extend([a1, a2])
                # Sort angles
                normalized_angles.sort()
                # Find largest gap between angles
                n = len(normalized_angles)
                max_gap = 0
                gap_mid_angle = 0
                for i in range(n):
                    next_i = (i + 1) % n
                    gap = normalized_angles[next_i] - normalized_angles[i]
                    if gap < 0:
                        gap += 2 * np.pi
                    if gap > max_gap:
                        max_gap = gap
                        gap_mid_angle = normalized_angles[i] + gap / 2
                        if gap_mid_angle >= 2 * np.pi:
                            gap_mid_angle -= 2 * np.pi
                
                # Position label in direction of gap bisector
                label_distance = np.sqrt(
                    (bounds[1] - bounds[0])**2 + (bounds[3] - bounds[2])**2) * 0.05
                label_x = x + label_distance * np.cos(gap_mid_angle)
                label_y = y + label_distance * np.sin(gap_mid_angle)
            else:
                # If no angles defined, use a default offset
                label_x = x + (bounds[1] - bounds[0]) * 0.05
                label_y = y + (bounds[3] - bounds[2]) * 0.05
            
            text = ax.text(label_x, label_y, vertex['label'],
                         color=color, ha='center', va='center',
                         fontsize=22, weight='bold', zorder=11)
            text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    
    # Draw angles
    angle_marker_size = calculate_angle_marker_size(bounds)
    for angle in angles:
        p1 = vertex_lookup[angle['point1']]
        vertex = vertex_lookup[angle['vertex']]
        p2 = vertex_lookup[angle['point2']]
        color = angle.get('color', 'black')
        # Handle empty string colors and transparent
        if not color or color.strip() == '' or color.strip().lower() == 'transparent':
            color = 'black'
        
        draw_angle_marker(ax, vertex, p1, p2, angle_marker_size, color, angle.get('label'))
    
    # Add shape label if specified
    if label:
        centroid = calculate_centroid(points)
        text = ax.text(centroid[0], centroid[1], label,
                      ha='center', va='center',
                      fontsize=22, weight='bold', zorder=11)
        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    
    return bounds

def process_ellipse(ax: plt.Axes,
                   center: Dict[str, Any],
                   x_axis: Optional[Dict[str, Any]] = None,
                   y_axis: Optional[Dict[str, Any]] = None,
                   radius: Optional[Dict[str, Any]] = None,
                   diameter: Optional[Dict[str, Any]] = None,
                   ellipse_edge_color: str = 'black',
                   fill_color: Optional[str] = None,
                   label: Optional[str] = None) -> Tuple[float, float, float, float]:
    """
    Process and draw an ellipse with its center, axes, and labels.
    
    Parameters
    ----------
    ax : plt.Axes
        Matplotlib axes to draw on
    center : Dict[str, Any]
        Center point definition
    x_axis : Optional[Dict[str, Any]]
        X-axis definition (horizontal axis)
    y_axis : Optional[Dict[str, Any]]
        Y-axis definition (vertical axis)
    radius : Optional[Dict[str, Any]]
        Radius definition (for circles)
    diameter : Optional[Dict[str, Any]]
        Diameter definition (for circles, alternative to radius)
    ellipse_edge_color : str
        Color for the ellipse edge
    fill_color : Optional[str]
        Color to fill the ellipse with. Use 'transparent' for no fill.
    label : Optional[str]
        Label for the entire ellipse
        
    Returns
    -------
    Tuple[float, float, float, float]
        (min_x, max_x, min_y, max_y) bounds of the ellipse
    """
    # Get center coordinates
    center_x, center_y = center['x'], center['y']
    
    # Determine if this is a circle or ellipse
    if radius is not None:
        width = height = 2 * radius['magnitude']
        is_circle = True
        circle_size = radius['magnitude']
        measurement = radius
        is_diameter = False
    elif diameter is not None:
        width = height = diameter['magnitude']
        is_circle = True
        circle_size = diameter['magnitude'] / 2
        measurement = diameter
        is_diameter = True
    elif x_axis is not None and y_axis is not None:
        width = 2 * x_axis['magnitude']  # Width determined by x-axis
        height = 2 * y_axis['magnitude']  # Height determined by y-axis
        is_circle = abs(width - height) < 1e-10
        measurement = None  # For ellipses, we don't have a single measurement
        is_diameter = False
        if is_circle:
            circle_size = width / 2  # For circles created via x/y axes
        else:
            circle_size = None  # Not applicable for true ellipses
    else:
        # Fallback for improperly specified ellipses - create a default unit circle
        logger.warning(
            "Ellipse specified without radius, diameter, or x/y axes. Creating unit circle."
        )
        width = height = 2.0  # Default diameter of 2 units
        is_circle = True
        circle_size = 1.0
        measurement = None
        is_diameter = False
    
    # Create and add the ellipse patches
    if fill_color and fill_color != 'transparent':
        # Draw filled ellipse with full opacity
        fill_ellipse = Ellipse((center_x, center_y), width, height,
                           facecolor=fill_color, edgecolor='none',
                           alpha=1.0, zorder=4)
        ax.add_patch(fill_ellipse)
    
    # Draw edge ellipse (always solid)
    edge_ellipse = Ellipse((center_x, center_y), width, height,
                       facecolor='none', edgecolor=ellipse_edge_color,
                       alpha=1.0, linewidth=3, zorder=5)
    ax.add_patch(edge_ellipse)
    
    # Draw axis markers
    if is_circle:
        if measurement and ('label' in measurement or 'color' in measurement):
            color = measurement.get('color', 'black')
            # Handle empty string colors and transparent
            if not color or color.strip() == '' or color.strip().lower() == 'transparent':
                color = 'black'
            if is_diameter:
                # Draw diameter line through center
                dx = circle_size  # This is already radius length since we divided by 2 earlier
                ax.plot([center_x - dx, center_x + dx],
                       [center_y, center_y],
                       color=color, linewidth=3, zorder=6)
                
                # Add diameter label above the line
                if 'label' in measurement:
                    # Position label above the line
                    label_y_offset = circle_size * 0.07  # Offset by 7% of radius
                    text = ax.text(center_x, center_y - label_y_offset, measurement['label'],
                                 color=color, ha='center', va='top',
                                 fontsize=22, weight='bold', zorder=7,
                                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))
                    text.set_path_effects([path_effects.withStroke(linewidth=3,
                                            foreground='white')])
            else:
                # Draw radius line from center to right
                radius_end_x = center_x + circle_size
                ax.plot([center_x, radius_end_x],
                       [center_y, center_y],
                       color=color, linewidth=3, zorder=3)
                
                # Add radius label at midpoint
                if 'label' in measurement:
                    mid_x = (center_x + radius_end_x) / 2
                    text = ax.text(mid_x, center_y, measurement['label'],
                                 color=color, ha='center', va='center',
                                 fontsize=22, weight='bold', zorder=7,
                                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))
                    text.set_path_effects(
                        [path_effects.withStroke(linewidth=3, foreground='white')])
    else:
        # Draw both axes
        if x_axis:
            x_color = x_axis.get('color', 'black')
            if not x_color or x_color.strip() == '' or x_color.strip().lower() == 'transparent':
                x_color = 'black'
            draw_axis_marker(ax, (center_x, center_y), width,
                           0, x_color, x_axis.get('label'))
        if y_axis:
            y_color = y_axis.get('color', 'black')
            if not y_color or y_color.strip() == '' or y_color.strip().lower() == 'transparent':
                y_color = 'black'
            draw_axis_marker(ax, (center_x, center_y), height,
                           np.pi/2, y_color, y_axis.get('label'))
    
    # Check if center point should be shown (default False)
    show_center_point = center.get('show_center_point', False)
    
    # Get center color for both point and label
    center_color = center.get('color', 'black')
    # Handle empty string colors and transparent
    if not center_color or center_color.strip() == '' \
        or center_color.strip().lower() == 'transparent':
        center_color = 'black'
    
    # Draw center point if requested
    if show_center_point:
        # Calculate marker size dynamically based on circle size
        if is_circle and circle_size is not None:
            # Scale marker size with radius, constrained between 2 and 8
            markersize = min(max(circle_size * 0.4, 2), 8)
        else:
            # For ellipses, use average of width and height
            avg_size = (width + height) / 4.0  # Divide by 4 to get average radius
            markersize = min(max(avg_size * 0.4, 2), 8)
        
        ax.plot(center_x, center_y, 'o', color=center_color, markersize=markersize, zorder=10)
    
    # Handle labels
    if label and 'label' not in center:
        # Place the shape label at the center point
        text = ax.text(center_x, center_y, label,
                      ha='center', va='center',
                      fontsize=22, weight='bold', zorder=11)
        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    elif 'label' in center:
        # Add center label with offset
        if is_circle and circle_size is not None:
            x_offset = 0
            y_offset = circle_size * 0.05
        else:
            # Use x_axis and y_axis for offset calculations
            if x_axis and y_axis:
                x_offset = (x_axis["magnitude"] + y_axis["magnitude"]) / 2.0 * 0.1
                y_offset = x_offset / 2.0
            else:
                # Fallback offset for degenerate cases
                x_offset = width * 0.05
                y_offset = height * 0.05
        text = ax.text(center_x + x_offset, center_y + y_offset, center['label'],
                  color=center_color, ha='center', va='bottom',
                  fontsize=22, weight='bold', zorder=11)
        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    elif label:
        # Show shape label at center when no center label exists
        text = ax.text(center_x, center_y, label,
                      ha='center', va='center',
                      fontsize=22, weight='bold', zorder=11)
        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    
    # Calculate bounds
    bounds = (center_x - width/2, center_x + width/2,
              center_y - height/2, center_y + height/2)
    
    # Debug logging for degenerate cases
    if width <= 0 or height <= 0:
        logger.warning(
            f"Ellipse has zero or negative dimensions: width={width}, height={height},",
            f"radius={radius}, diameter={diameter}"
        )
    
    return bounds

def process_groups(ax: plt.Axes, shapes: List[Dict[str, Any]]) -> None:
    """
    Process shape groups and draw outline rectangles around groups with multiple shapes.
    
    Parameters
    ----------
    ax : plt.Axes
        Matplotlib axes to draw on
    shapes : List[Dict[str, Any]]
        List of shapes that may contain group_id properties
    """
    # Group shapes by group_id
    groups = {}
    for i, shape in enumerate(shapes):
        group_id = shape.get('group_id')
        if group_id:
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append((i, shape))
    
    # Draw rectangles for groups with multiple shapes
    group_padding = 0.25  # Fixed padding in coordinate units
    
    for _group_id, group_shapes in groups.items():
        if len(group_shapes) <= 1:
            continue  # Skip groups with only one shape
        
        # Calculate bounds for all shapes in the group
        all_group_bounds = []
        for _shape_index, shape in group_shapes:
            if shape['shape_type'] == 'polygon':
                # Calculate polygon bounds from vertices
                vertices = shape['vertices']
                points = [(v['x'], v['y']) for v in vertices]
                bounds = calculate_shape_bounds(points)
            else:  # ellipse
                center = shape['center']
                center_x, center_y = center['x'], center['y']
                
                # Determine ellipse size
                if 'radius' in shape:
                    width = height = 2 * shape['radius']['magnitude']
                elif 'diameter' in shape:
                    width = height = shape['diameter']['magnitude']
                elif 'x_axis' in shape and 'y_axis' in shape:
                    width = 2 * shape['x_axis']['magnitude']
                    height = 2 * shape['y_axis']['magnitude']
                else:
                    # Fallback
                    width = height = 2.0
                
                bounds = (center_x - width/2, center_x + width/2,
                         center_y - height/2, center_y + height/2)
            
            all_group_bounds.append(bounds)
        
        # Calculate overall group bounds
        if all_group_bounds:
            min_x = min(b[0] for b in all_group_bounds)
            max_x = max(b[1] for b in all_group_bounds)
            min_y = min(b[2] for b in all_group_bounds)
            max_y = max(b[3] for b in all_group_bounds)
            
            # Add padding
            min_x -= group_padding
            max_x += group_padding
            min_y -= group_padding
            max_y += group_padding
            
            # Draw dashed black rectangle
            width = max_x - min_x
            height = max_y - min_y
            rect = Rectangle((min_x, min_y), width, height,
                           linewidth=2, edgecolor='black', facecolor='none',
                           linestyle='--', zorder=0)
            ax.add_patch(rect)

def generate_2d_shape_image(shapes: List[Dict[str, Any]],
background_color: str = 'transparent') -> str:
    """
    Generate an image of 2D shapes including polygons and ellipses.
    
    Parameters
    ----------
    shapes : List[Dict[str, Any]]
        List of shapes to render. Each shape should have:
        - shape_type: 'polygon' or 'ellipse'
        For polygons:
        - vertices: List of dicts with 'name', 'x', 'y', 'color' (optional), 'label' (optional)
        - edges: List of dicts with 'start_point', 'end_point', 'color' (optional),
                'label' (optional), 'style' (optional, 'solid' or 'dashed')
        - angles: List of dicts with 'point1', 'vertex', 'point2', 'color' (optional),
                 'label' (optional)
        For ellipses:
        - center: Dict with 'x', 'y', 'color' (optional), 'label' (optional), 'show_center_point'
        (optional, defaults to True)
        - x_axis: Dict with 'magnitude', 'label' (optional), 'color' (optional)
        - y_axis: Dict with 'magnitude', 'label' (optional), 'color' (optional)
        For circles (use ONE of these options):
        - radius: Dict with 'magnitude', 'label' (optional), 'color' (optional)
        - diameter: Dict with 'magnitude', 'label' (optional), 'color' (optional)
        Common options:
        - fill_color: Color to fill the shape with (optional)
        - label: Label for the entire shape (optional)
        - ellipse_edge_color: Color for ellipse edge (optional, ellipses only)
    background_color : str, default 'white'
        The background color behind the shapes. Use 'transparent' for transparent background,
        or any valid matplotlib color name or hex code.
        
    Returns
    -------
    str
        URL of the generated image
    """
    logger.info(
        f"Generating 2D shape image with {len(shapes)} shapes and background: {background_color}"
    )
    
    # Create figure and axes
    fig = plt.figure(figsize=(10, 10), dpi=100)
    
    # Set figure and axes background
    if background_color == 'transparent':
        fig.patch.set_alpha(0)
    else:
        fig.patch.set_facecolor(background_color)
    
    ax = fig.add_subplot(111)
    
    # Set axes background to match figure
    if background_color == 'transparent':
        ax.patch.set_alpha(0)
    else:
        ax.patch.set_facecolor(background_color)
    
    # Process groups first to draw group outlines behind shapes
    process_groups(ax, shapes)
    
    # Process each shape and track bounds
    all_bounds = []
    for shape in shapes:
        if shape['shape_type'] == 'polygon':
            bounds = process_polygon(
                ax,
                shape['vertices'],
                shape.get('edges', []),
                shape.get('angles', []),
                shape.get('fill_color') if shape.get('fill_color') \
                    and shape.get('fill_color').strip() != '' else None,
                shape.get('label')
            )
        else:  # ellipse
            bounds = process_ellipse(
                ax,
                shape['center'],
                shape.get('x_axis'),
                shape.get('y_axis'),
                shape.get('radius'),
                shape.get('diameter'), # Added diameter
                shape.get('ellipse_edge_color', 'black') \
                    if shape.get('ellipse_edge_color', 'black') \
                        and shape.get('ellipse_edge_color', 'black').strip() != '' \
                            and shape.get('ellipse_edge_color', 'black').strip().lower() \
                                != 'transparent' else 'black',
                shape.get('fill_color') if shape.get('fill_color') \
                    and shape.get('fill_color').strip() != '' else None,
                shape.get('label')
            )
        all_bounds.append(bounds)
    
    # Calculate overall bounds
    if all_bounds:
        min_x = min(b[0] for b in all_bounds)
        max_x = max(b[1] for b in all_bounds)
        min_y = min(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)
        
        # Calculate padding with minimum value to avoid degenerate cases
        x_range = max_x - min_x
        y_range = max_y - min_y
        max_range = max(x_range, y_range)
        
        # Use a minimum padding of 1.0 if the shape has no extent (degenerate case)
        padding = max(max_range * 0.1, 1.0)
        
        ax.set_xlim(min_x - padding, max_x + padding)
        ax.set_ylim(min_y - padding, max_y + padding)
    
    # Set equal aspect ratio and remove axes
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Save to bytes buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1,
                transparent=(background_color == 'transparent'))
    buf.seek(0)
    plt.close(fig)
    
    # Upload to Supabase
    image_bytes = buf.getvalue()
    public_url = upload_image_to_supabase(
        image_bytes=image_bytes,
        content_type="image/png",
        bucket_name="incept-images"
    )
    
    return public_url

def generate_2d_shape_image_tool() -> tuple[dict, Callable]:
    """Create the tool specification and return it with the function."""
    spec = {
        "type": "function",
        "name": "generate_2d_shape_image",
        "description": (
            "Generate an image of one or more 2D shapes including polygons and ellipses with "
            "vertices, edges, angles, and labels. It is YOUR RESPONSIBILITY to label edges "
            "sufficiently for students to understand the shape(s) and answer questions about them. "
            "ALWAYS rely on the tool to place labels appropriately when you specify a label. NEVER "
            "create shapes just because you want to be sure to place certain labels.\n\nCRITICAL "
            "COLOR REQUIREMENTS - READ THIS CAREFULLY:\n- **EACH SHAPE MUST HAVE ITS OWN COLOR "
            "SPECIFIED** - colors are NOT shared or inferred across shapes\n- If you want 10 green "
            "circles, you MUST create 10 separate shape objects, each with \"fill_color\": "
            "\"green\"\n- Colors will NOT be applied automatically to similar shapes\n- ALL color "
            "properties are OPTIONAL - omit them entirely if you don't want to specify a color\n"
            "- NEVER use empty strings ('') for colors - this will cause errors\n- Valid colors: "
            "'red', 'blue', 'green', 'black', 'gray', 'orange', 'purple', 'brown', 'pink', "
            "'yellow', 'cyan', 'magenta', 'lightblue', 'lightgreen', or hex codes like '#FF0000'\n"
            "- If unsure about a color, simply omit the color property and the default will be "
            "used\n\nCRITICAL POLYGON REQUIREMENTS:\n- For polygon shapes, you MUST always specify "
            "edges explicitly to control which vertices are connected\n- When a question involves "
            "finding perimeter or area of a polygon, you MUST label at least one edge in each "
            "independent direction (e.g., one horizontal and one vertical edge for rectangles), "
            "unless the missing dimension is explicitly given in text and not needed from the "
            "picture. Pay VERY CLOSE ATTENTION to which edges you are labeling so the labels are "
            "placed on the intended edges given how this tool draws figures, and so that no edges "
            "contradict each other. \n- If edges are not provided, the tool will automatically "
            "connect vertices in order to form a closed polygon as a fallback\n- For best results "
            "and control, always define edges explicitly\n\nCRITICAL POLYGON VERTEX ORDERING:\n- "
            "When using fill_color, vertices define the boundary of the filled area and MUST trace "
            "a simple, non-self-intersecting outline\n- NEVER list vertices that cause the polygon "
            "path to \"double back\" on itself, as this creates unfilled triangular gaps\n- NEVER "
            "include interior division points in the vertex list of a filled polygon - this is the "
            "most common cause of white triangular gaps\n- For shapes with interior divisions "
            "(e.g., a rectangle split by a line), use one of these approaches:\n  1. Create "
            "separate filled polygons for each section\n  2. Create one outer polygon without "
            "fill_color and add interior edges separately\n  3. List vertices in proper outline "
            "order (e.g., for a divided rectangle: A-B-C-F-D instead of A-B-C-D-E-F)\n\nCRITICAL "
            "ELLIPSE REQUIREMENTS:\n- For ellipse shapes, you MUST specify size using ONE of these "
            "options:\n  1. \"radius\": {\"magnitude\": number} for circles\n  2. \"diameter\": "
            "{\"magnitude\": number} for circles\n  3. \"x_axis\" AND \"y_axis\" both with "
            "magnitudes for ellipses\n- Never create an ellipse with only a center point - it must "
            "have size information\n\nEXAMPLE - Multiple green circles (note each has its own "
            "fill_color):\n[{\n  \"shape_type\": \"ellipse\",\n  \"center\": {\"x\": 0, \"y\": 0},"
            "\n  \"radius\": {\"magnitude\": 1},\n  \"fill_color\": \"green\"\n}, {\n  "
            "\"shape_type\": \"ellipse\",\n  \"center\": {\"x\": 3, \"y\": 0},\n  \"radius\": "
            "{\"magnitude\": 1},\n  \"fill_color\": \"green\"\n}]\n\nEXAMPLE - Polygon with "
            "explicit edges:\n{\n  \"shape_type\": \"polygon\",\n  \"vertices\": [{\"name\": "
            "\"A\", \"x\": 0, \"y\": 0}, {\"name\": \"B\", \"x\": 2, \"y\": 0}, {\"name\": \"C\", "
            "\"x\": 1, \"y\": 2}],\n  \"edges\": [{\"start_point\": \"A\", \"end_point\": \"B\"}, "
            "{\"start_point\": \"B\", \"end_point\": \"C\"}, {\"start_point\": \"C\", "
            "\"end_point\": \"A\"}],\n  \"fill_color\": \"lightblue\"\n}\n\nEXAMPLE - INCORRECT "
            "(will cause errors):\n{\n  \"vertices\": [{\"name\": \"A\", \"x\": 0, \"y\": 0, "
            "\"color\": \"\"}], // Empty string!\n  \"fill_color\": \"\" // Empty string!\n}"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "shapes": {
                    "type": "array",
                    "description": (
                        "List of shapes to render. It is your responsibility to align the shapes "
                        "in a clean, aesthetically pleasing layout, bearing in mind that polygons "
                        "are specified by their vertices and ellipses are specified by their "
                        "center point and x/y axes."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "shape_type": {
                                "type": "string",
                                "enum": ["polygon", "ellipse"],
                                "description": "Type of shape to render"
                            },
                            "vertices": {
                                "type": "array",
                                "description": "List of vertices for polygon shapes",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "x": {"type": "number"},
                                        "y": {"type": "number"},
                                        "color": {
                                            "type": "string",
                                            "description": (
                                                "OPTIONAL color for the vertex. Valid values: "
                                                "'red', 'blue', 'green', 'black', 'gray', "
                                                "'orange', 'purple', 'brown', 'pink', 'yellow', "
                                                "'cyan', 'magenta', or hex codes like '#FF0000'. "
                                                "NEVER use empty string. Omit this property to use "
                                                "default black."
                                            )
                                        },
                                        "label": {
                                            "type": "string",
                                            "description": (
                                                "OPTIONAL text label for the vertex. Omit this "
                                                "property to use no label. If you label a vertex, "
                                                "ensure the label matches the correct value of the "
                                                "vertex as used elsewhere in the content. NOTE: "
                                                "when you use the same vertex in multiple shapes, "
                                                "you should only label it once. The code that "
                                                "draws the shapes will decide how to label the "
                                                "vertex optimally."
                                            )
                                            },
                                        "show_vertex_point_marker": {
                                            "type": "boolean",
                                            "default": False
                                        }
                                    },
                                    "required": ["name", "x", "y"]
                                }
                            },
                            "edges": {
                                "type": "array",
                                "description": (
                                    "List of edges for polygon shapes. RECOMMENDED: Always specify "
                                    "edges explicitly to control which vertices are connected and "
                                    "ensure the desired polygon shape. As a fallback, if not "
                                    "provided, edges will be auto-generated by connecting vertices "
                                    "in order to form a closed polygon."
                                ),
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "start_point": {"type": "string"},
                                        "end_point": {"type": "string"},
                                        "color": {
                                            "type": "string",
                                            "description": (
                                                "OPTIONAL color for the edge. Valid values: 'red', "
                                                "'blue', 'green', 'black', 'gray', 'orange', "
                                                "'purple', 'brown', 'pink', 'yellow', 'cyan', "
                                                "'magenta', or hex codes like '#FF0000'. NEVER use "
                                                "empty string. Omit this property to use default "
                                                "black."
                                            )
                                        },
                                        "label": {
                                            "type": "string",
                                            "description": (
                                                "OPTIONAL text label for the edge. Omit this "
                                                "property to use no label. If you label an edge, "
                                                "ensure the label matches the correct value of the "
                                                "edge as used elsewhere in the content, and "
                                                "ESPECIALLY ensure the label matches any labels "
                                                "used on other edges elsewhere in the content. "
                                                "Double check that enough edges are labeled to "
                                                "allow a student to understand the shape(s) and "
                                                "answer questions about them. Also double check "
                                                "that no labels contradict each other, for example "
                                                "ensure edges of equal length do not have "
                                                "contradictory labels. If the generated content "
                                                "will ask students to find area or perimeter, at "
                                                "least one edge parallel to every unique axis must "
                                                "carry a label. When a composite polygon is used "
                                                "(e.g., an L-shape split into rectangles), also "
                                                "label any interior edge whose length is required "
                                                "for calculations."
                                            )
                                        },
                                        "style": {
                                            "type": "string",
                                            "enum": ["solid", "dashed"]
                                        }
                                    },
                                    "required": ["start_point", "end_point"]
                                }
                            },
                            "angles": {
                                "type": "array",
                                "description": "List of angles to mark in polygon shapes",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "point1": {"type": "string"},
                                        "vertex": {"type": "string"},
                                        "point2": {"type": "string"},
                                        "color": {
                                            "type": "string",
                                            "description": (
                                                "OPTIONAL color for the angle marker. Valid "
                                                "values: 'red', 'blue', 'green', 'black', 'gray', "
                                                "'orange', 'purple', 'brown', 'pink', 'yellow', "
                                                "'cyan', 'magenta', or hex codes like '#FF0000'. "
                                                "NEVER use empty string. Omit this property to use "
                                                "default black."
                                            )
                                        },
                                        "label": {
                                            "type": "string",
                                            "description": (
                                                "OPTIONAL text label for the angle. Omit this "
                                                "property to use no label. If you label an angle, "
                                                "ensure the label matches the correct value of the "
                                                "angle as used elsewhere in the content, and "
                                                "ESPECIALLY ensure the label matches any labels "
                                                "used on other angles elsewhere in the content. "
                                                "Double check that enough angles are labeled to "
                                                "allow a student to understand the shape(s) and "
                                                "answer questions about them. Also double check "
                                                "that no labels contradict each other, for example "
                                                "ensure angles of equal size do not have "
                                                "contradictory labels."
                                            )
                                        }
                                    },
                                    "required": ["point1", "vertex", "point2"]
                                }
                            },
                            "center": {
                                "type": "object",
                                "description": (
                                    "Center point for ellipse shapes. REQUIRED for all ellipse "
                                    "shapes. Label the center point ONLY if you don't want to "
                                    "label the shape itself."
                                ),
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "color": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL color for the center point. Valid values: "
                                            "'red', 'blue', 'green', 'black', 'gray', 'orange', "
                                            "'purple', 'brown', 'pink', 'yellow', 'cyan', "
                                            "'magenta', or hex codes like '#FF0000'. NEVER use "
                                            "empty string. Omit this property to use default black."
                                        )
                                    },
                                    "label": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL text label for the center point. Omit this "
                                            "property to use no label. If you label the center "
                                            "point, ensure the label matches the correct value of "
                                            "the center point as used elsewhere in the content, "
                                            "and ESPECIALLY ensure the label matches any labels "
                                            "used on other center points elsewhere in the content."
                                        )
                                    },
                                    "show_center_point": {
                                        "type": "boolean",
                                        "description": (
                                            "Whether to show the center point marker. Defaults to "
                                            "false. Set to true when illustrating geometric "
                                            "concepts related to circles or ellipses, such as "
                                            "showing a radius, diameter, or axis. If false, the "
                                            "center point dot will be hidden but labels (both "
                                            "center label and shape label) will still be shown "
                                            "(if specified). If you only wish to illustrate "
                                            "circles without geometric features like radii or "
                                            "diameters, hide the center point marker."
                                        ),
                                        "default": False
                                    }
                                },
                                "required": ["x", "y"]
                            },
                            "x_axis": {
                                "type": "object",
                                "description": (
                                    "X-axis (horizontal) definition for ellipse shapes. Specify "
                                    "the x-axis of the ellipse when you wish to create a "
                                    "non-circular ellipse."
                                ),
                                "properties": {
                                    "magnitude": {"type": "number"},
                                    "label": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL text label for the x-axis. Omit this "
                                            "property to use no label."
                                        )
                                    },
                                    "color": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL color for the x-axis line and label. Valid "
                                            "values: 'red', 'blue', 'green', 'black', 'gray', "
                                            "'orange', 'purple', 'brown', 'pink', 'yellow', "
                                            "'cyan', 'magenta', or hex codes like '#FF0000'. "
                                            "NEVER use empty string. Omit this property to use "
                                            "default black."
                                        )
                                    }
                                },
                                "required": ["magnitude"]
                            },
                            "y_axis": {
                                "type": "object",
                                "description": (
                                    "Y-axis (vertical) definition for ellipse shapes. Specify "
                                    "the y-axis of the ellipse when you wish to create a "
                                    "non-circular ellipse."
                                ),
                                "properties": {
                                    "magnitude": {"type": "number"},
                                    "label": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL text label for the y-axis. Omit this "
                                            "property to use no label."
                                        )
                                    },
                                    "color": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL color for the y-axis line and label. Valid "
                                            "values: 'red', 'blue', 'green', 'black', 'gray', "
                                            "'orange', 'purple', 'brown', 'pink', 'yellow', "
                                            "'cyan', 'magenta', or hex codes like '#FF0000'. "
                                            "NEVER use empty string. Omit this property to use "
                                            "default black."
                                        )
                                    }
                                },
                                "required": ["magnitude"]
                            },
                            "radius": {
                                "type": "object",
                                "description": (
                                    "Radius definition for circle shapes (alternative to x/y "
                                    "axes). Specify the radius of the circle when you wish to "
                                    "create a circle by radius."
                                ),
                                "properties": {
                                    "magnitude": {"type": "number"},
                                    "label": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL text label for the radius. Omit this "
                                            "property to use no label."
                                        )
                                    },
                                    "color": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL color for the radius line and label. Valid "
                                            "values: 'red', 'blue', 'green', 'black', 'gray', "
                                            "'orange', 'purple', 'brown', 'pink', 'yellow', "
                                            "'cyan', 'magenta', or hex codes like '#FF0000'. "
                                            "NEVER use empty string. Omit this property to use "
                                            "default black."
                                        )
                                    }
                                },
                                "required": ["magnitude"]
                            },
                            "diameter": {
                                "type": "object",
                                "description": (
                                    "Diameter definition for circle shapes (alternative to "
                                    "radius). Specify the diameter of the circle when you wish "
                                    "to create a circle by diameter. The magnitude should be "
                                    "the full diameter distance (e.g., if you want a 10m "
                                    "diameter circle, use magnitude: 10). This will draw both "
                                    "the circle outline AND a diameter line through the center "
                                    "with the label."
                                ),
                                "properties": {
                                    "magnitude": {
                                        "type": "number",
                                        "description": (
                                            "The full diameter of the circle (not radius). "
                                            "Must be greater than 0."
                                        ),
                                        "minimum": 0.1
                                    },
                                    "label": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL text label for the diameter. Omit this "
                                            "property to use no label."
                                        )
                                    },
                                    "color": {
                                        "type": "string",
                                        "description": (
                                            "OPTIONAL color for the diameter line and label. Valid "
                                            "values: 'red', 'blue', 'green', 'black', 'gray', "
                                            "'orange', 'purple', 'brown', 'pink', 'yellow', "
                                            "'cyan', 'magenta', or hex codes like '#FF0000'. "
                                            "NEVER use empty string. Omit this property to use "
                                            "default black."
                                        )
                                    }
                                },
                                "required": ["magnitude"]
                            },
                            "ellipse_edge_color": {
                                "type": "string",
                                "description": (
                                    "OPTIONAL color for ellipse edge (ellipses only). Valid "
                                    "values: 'red', 'blue', 'green', 'black', 'gray', 'orange', "
                                    "'purple', 'brown', 'pink', 'yellow', 'cyan', 'magenta', "
                                    "or hex codes like '#FF0000'. NEVER use empty string. Omit "
                                    "this property to use default black."
                                )
                            },
                            "fill_color": {
                                "type": "string",
                                "description": (
                                    "OPTIONAL color to fill the shape with. **CRITICAL: This "
                                    "property must be specified for EACH individual shape that "
                                    "should be colored.** Colors are NOT shared between shapes - "
                                    "if you want 10 green circles, you must specify "
                                    "\"fill_color\": \"green\" for ALL 10 circle objects. Valid "
                                    "values: 'red', 'blue', 'green', 'black', 'gray', 'orange', "
                                    "'purple', 'brown', 'pink', 'yellow', 'cyan', 'magenta', "
                                    "'lightblue', 'lightgreen', 'lightcoral', 'lightgray', or hex "
                                    "codes like '#FF0000'. Use 'transparent' for no fill. NEVER "
                                    "use empty string. Omit this property for no fill. Default "
                                    "is no fill, but choose among a variety of colors for "
                                    "aesthetic variety."
                                )
                            },
                            "label": {
                                "type": "string",
                                "description": "Label for the entire shape."
                            },
                            "group_id": {
                                "type": "string",
                                "description": (
                                    "Identifier for grouping shapes together visually when "
                                    "relevant to the content being generated. You MUST ALWAYS use "
                                    "a group_id to group objects any time that the grouping of "
                                    "objects is academically relevant to the content being "
                                    "produced (e.g., when teaching concepts like equal groups, "
                                    "arrays, or set partitioning) because shapes with the same "
                                    "group_id will have a dashed black rectangle drawn around to "
                                    "make it clear how the objects are grouped. Groups with only "
                                    "one shape and shapes with no group_id will not have an "
                                    "outline drawn. This capability can ONLY draw rectangular "
                                    "groups, so ensure you arrange shapes such that a rectangle "
                                    "can contain exactly the set of shapes in the group. DO NOT "
                                    "FAIL TO SET THE GROUP_ID WHEN YOU EXPECT STUDENTS TO "
                                    "UNDERSTAND HOW YOU HAVE GROUPED THE SHAPES! Only omit this "
                                    "property to when you want to leave shapes ungrouped, for "
                                    "example when the grouping of shapes is not relevant to the "
                                    "content."
                                )
                            }
                        },
                        "required": ["shape_type"],
                        "if": {
                            "properties": {
                                "shape_type": {"const": "ellipse"}
                            }
                        },
                        "then": {
                            "required": ["center"],
                            "anyOf": [
                                {"required": ["radius"]},
                                {"required": ["diameter"]},
                                {"required": ["x_axis", "y_axis"]}
                            ]
                        }
                    }
                },
                "background_color": {
                    "type": "string",
                    "description": (
                        "The background color behind the shapes. Use 'transparent' for "
                        "transparent background, or any valid matplotlib color name or hex "
                        "code. The shapes retain their specified colors. Defaults to "
                        "'transparent'."
                    )
                }
            },
            "required": ["shapes", "background_color"]
        }
    }
    return spec, generate_2d_shape_image 