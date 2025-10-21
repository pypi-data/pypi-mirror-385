from __future__ import annotations

import logging
from typing import Callable, List, Union

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports using centralized utility
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.polygon_scales import (  # noqa: E402
    draw_polygon_scale,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.polygon_scale import (  # noqa: E402, E501
    PolygonScale,
)

logger = logging.getLogger("coach_bot_tools.polygon_scales")


def generate_coach_bot_polygon_scale_image(
    polygon_type: str,
    original_polygon_label: str,
    scaled_polygon_label: str,
    scale_factor: float,
    original_vertex_labels: List[str],
    scaled_vertex_labels: List[str],
    original_visible_sides: List[str],
    scaled_visible_sides: List[str],
    original_measurements: List[Union[int, float]],
    scaled_measurements: List[Union[int, float]],
    measurement_unit: str = "units"
) -> str:
    """
    Generate a polygon scaling comparison image showing original and scaled polygons.
    
    Creates a visual comparison of two polygons side by side - an original polygon and
    its scaled version. Shows measurements on specified sides for teaching scale factor
    concepts, proportional reasoning, and geometric similarity.
    
    Parameters
    ----------
    polygon_type : str
        Type of polygon ('triangle', 'quadrilateral', 'pentagon', 'hexagon', 'irregular')
    original_polygon_label : str
        Label for the original polygon (e.g., 'Polygon P')
    scaled_polygon_label : str
        Label for the scaled polygon (e.g., 'Polygon Q')
    scale_factor : float
        Scale factor used to transform the original polygon (0 < scale_factor <= 5)
    original_vertex_labels : List[str]
        Vertex labels for the original polygon (e.g., ['A', 'B', 'C', 'D'])
    scaled_vertex_labels : List[str]
        Vertex labels for the scaled polygon (e.g., ['A\'', 'B\'', 'C\'', 'D\''])
    original_visible_sides : List[str]
        Names of sides to show measurements on original polygon (e.g., ['AB', 'BC'])
    scaled_visible_sides : List[str]
        Names of sides to show measurements on scaled polygon (e.g., ['A\'B\'', 'B\'C\''])
    original_measurements : List[Union[int, float]]
        All side measurements for original polygon in vertex order
    scaled_measurements : List[Union[int, float]]
        All side measurements for scaled polygon in vertex order
    measurement_unit : str
        Unit of measurement (default: 'units')
        
    Returns
    -------
    str
        The URL of the generated polygon scale comparison image
    """
    
    # Use standardized logging
    log_tool_generation("polygon_scale_image", polygon_type=polygon_type, 
                       scale_factor=scale_factor, measurement_unit=measurement_unit)
    
    # Create and validate the PolygonScale using Pydantic
    # This handles all validation: scale factor range (0 < factor <= 5), 
    # array length consistency, measurement count validation, and side names
    polygon_scale = PolygonScale(
        polygon_type=polygon_type,
        original_polygon_label=original_polygon_label,
        scaled_polygon_label=scaled_polygon_label,
        scale_factor=scale_factor,
        original_vertex_labels=original_vertex_labels,
        scaled_vertex_labels=scaled_vertex_labels,
        original_visible_sides=original_visible_sides,
        scaled_visible_sides=scaled_visible_sides,
        original_measurements=original_measurements,
        scaled_measurements=scaled_measurements,
        measurement_unit=measurement_unit
    )
    
    # Generate the image using the polygon scale function
    image_file_path = draw_polygon_scale(polygon_scale)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_polygon_scale_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for polygon scale generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_polygon_scale_image",
        description=(
            "Generate polygon scaling comparison visualizations for geometry and mathematics "
            "education. Creates side-by-side comparisons of original and scaled polygons with "
            "precise measurements displayed on specified sides. Perfect for teaching scale factor "
            "concepts, proportional reasoning, geometric similarity, mathematical transformations, "
            "and ratio relationships. Supports triangles, quadrilaterals, pentagons, hexagons, and "
            "irregular polygons with customizable vertex labeling, selective measurement display, "
            "and educational scaling exercises. Scale factors range from 0 to 5 for comprehensive "
            "mathematical exploration. Ideal for geometry lessons, similarity studies, proportion "
            "problems, scale drawing activities, and mathematical modeling exercises. Each polygon "
            "shows clear vertex labels and measurements to enhance student understanding of "
            "scaling relationships and geometric transformations. Excellent for assessment "
            "questions, worksheets, and interactive mathematical problem-solving activities."
        ),
        pydantic_model=PolygonScale,
        custom_descriptions={
            "polygon_type": (
                "Type of polygon for the scaling exercise. Choose from educational polygon types: "
                "'triangle' for basic similarity concepts, 'quadrilateral' for rectangle/square "
                "scaling, 'pentagon' and 'hexagon' for advanced geometry, or 'irregular' for "
                "complex shape analysis. Each type provides different educational opportunities "
                "for teaching scaling, proportional reasoning, and geometric similarity principles."
            ),
            "original_polygon_label": (
                "Educational label for the original polygon that enhances learning context. Use "
                "clear, descriptive labels like 'Polygon P', 'Original Shape', 'Figure A', or "
                "contextual names like 'Garden Plot', 'Building Floor Plan'. Good labeling helps "
                "students distinguish between the original and scaled versions in mathematical "
                "discussions."
            ),
            "scaled_polygon_label": (
                "Educational label for the scaled polygon that shows the transformation "
                "relationship. Use labels that indicate scaling like 'Polygon Q', 'Scaled Shape', "
                "'Figure B', or prime notation like 'Figure A\\''. Clear labeling reinforces the "
                "concept that this is the mathematically transformed version of the original "
                "polygon."
            ),
            "scale_factor": (
                "Mathematical scale factor for the geometric transformation (0 < factor ≤ 5). This "
                "value determines how the original polygon is scaled: values < 1 create smaller "
                "polygons (reduction), values > 1 create larger polygons (enlargement), value = 1 "
                "creates congruent polygons (same size). Examples: 0.5 (half size), 2.0 (double "
                "size), 1.5 (50% larger). Perfect for teaching proportional relationships and "
                "similarity concepts."
            ),
            "original_vertex_labels": (
                "Vertex labels for the original polygon that establish mathematical reference "
                "points. Use alphabetical sequence like ['A', 'B', 'C', 'D'] for systematic "
                "vertex identification. These labels are essential for referencing specific sides, "
                "angles, and measurements in mathematical discussions and problem-solving "
                "activities."
            ),
            "scaled_vertex_labels": (
                "Vertex labels for the scaled polygon using mathematical notation conventions. "
                "Typically use prime notation like ['A\\'', 'B\\'', 'C\\'', 'D\\''] to show "
                "correspondence with original vertices. This notation reinforces the mathematical "
                "relationship between original and transformed shapes, helping students understand "
                "geometric transformations."
            ),
            "original_visible_sides": (
                "Names of sides to display measurements on the original polygon for educational "
                "focus. Use vertex notation like ['AB', 'BC', 'CD'] to specify which sides show "
                "measurements. Strategic selection helps focus student attention on key "
                "measurements for scale factor calculations and proportional reasoning exercises."
            ),
            "scaled_visible_sides": (
                "Names of sides to display measurements on the scaled polygon for mathematical "
                "comparison. Use corresponding prime notation like ['A\\'B\\'', 'B\\'C\\''] to "
                "match original sides. Can show fewer measurements than the original for "
                "progressive learning or assessment purposes, allowing students to calculate "
                "missing scaled measurements.measurements."
            ),
            "original_measurements": (
                "Complete list of all side measurements for the original polygon in vertex order. "
                "Provide measurements for ALL sides (not just visible ones) as this data is used "
                "for accurate polygon generation. Example for quadrilateral: [30, 20, 30, 20] "
                "represents sides AB, BC, CD, DA. Use realistic educational values for practical "
                "learning applications."
            ),
            "scaled_measurements": (
                "Complete list of all side measurements for the scaled polygon in corresponding "
                "vertex order. These should reflect the scale factor transformation of original "
                "measurements. Example: if original is [30, 20, 30, 20] with scale factor 1.5, "
                "then scaled should be [45, 30, 45, 30]. Provides mathematical consistency for "
                "scale factor verification exercises."
            ),
            "measurement_unit": (
                "Unit of measurement for educational context and real-world application. Use "
                "appropriate units like 'feet', 'meters', 'cm', 'inches', or generic 'units' for "
                "abstract problems. Proper units enhance the educational value by connecting "
                "geometric concepts to practical measurement scenarios and real-world "
                "mathematical applications."
            )
        }
    )
    return spec, generate_coach_bot_polygon_scale_image
