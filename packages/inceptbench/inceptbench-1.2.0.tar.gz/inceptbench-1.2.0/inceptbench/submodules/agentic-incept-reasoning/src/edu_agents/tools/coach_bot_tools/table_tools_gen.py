from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional

from .coach_bot_utils import (
    create_dynamic_tool_spec,
    log_tool_generation,
    setup_coach_bot_imports,
    upload_coach_bot_image,
)

# Setup coach-bot imports
setup_coach_bot_imports()

from content_generators.additional_content.stimulus_image.drawing_functions.table import (  # noqa: E402
    create_probability_diagram,
    draw_data_table,
    draw_data_table_group,
    draw_table_two_way,
    generate_horizontal_table,
    generate_table,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.probability_diagrams import (  # noqa: E402, E501
    DataItem,
    ProbabilityDiagram,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.table import (  # noqa: E402
    DataTable,
    DataTableGroup,
    Table,
    TableColumn,
    TableRow,
)
from content_generators.additional_content.stimulus_image.stimulus_descriptions.table_two_way import (  # noqa: E402, E501
    TableTwoWay,
)

logger = logging.getLogger("coach_bot_tools.table_tools_gen")


def generate_coach_bot_simple_table_image(
    columns: List[str],
    rows: List[List[str]],
    horizontal: bool = False
) -> str:
    """
    Generate simple data tables for educational content.
    
    Creates clean, well-formatted tables for displaying structured data. 
    Supports both vertical (traditional) and horizontal layouts. Perfect 
    for showing data sets, comparison charts, and organizing information 
    for mathematical analysis and interpretation.
    
    Parameters
    ----------
    columns : List[str]
        Column headers for the table (exactly 2 headers required)
    rows : List[List[str]]
        Table data rows, each row must have 2 values matching column count (max 15 rows)
    horizontal : bool
        If True, creates horizontal layout; if False, creates vertical layout
        
    Returns
    -------
    str
        The URL of the generated simple table image
    """
    
    logger.info(f"Generating simple table with {len(rows)} rows, horizontal={horizontal}")
    
    # Create column objects
    column_objects = [TableColumn(label=str(col)) for col in columns]
    
    # Create row objects
    row_objects = []
    for row in rows:
        row_obj = TableRow(field_1=str(row[0]), field_2=str(row[1]))
        row_objects.append(row_obj)
    
    # Create the Table stimulus (Pydantic handles validation automatically)
    table_stimulus = Table(columns=column_objects, rows=row_objects)
    
    # Generate the image using appropriate function
    if horizontal:
        image_file_path = generate_horizontal_table(table_stimulus)
    else:
        image_file_path = generate_table(table_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_two_way_table_image(
    table_title: str,
    row_titles: List[str],
    column_titles: List[str],
    data: List[List[int]]
) -> str:
    """
    Generate two-way tables for cross-tabulation and statistical analysis.
    
    Creates formatted two-way tables with row and column headers for displaying 
    cross-tabulated data. Essential for teaching statistical concepts, data 
    organization, and analysis of relationships between categorical variables.
    
    VALIDATION REQUIREMENTS:
    - Table title cannot be empty
    - 2-5 row titles and 2-5 column titles required
    - Data matrix dimensions must match header counts exactly
    - All data values must be non-negative integers
    - Row and column titles cannot be empty strings
    
    Parameters
    ----------
    table_title : str
        Main title for the table (cannot be empty)
    row_titles : List[str]
        Row header labels (2-5 non-empty strings)
        Example: ["Elementary", "Middle School", "High School"]
    column_titles : List[str]
        Column header labels (2-5 non-empty strings)  
        Example: ["Math", "Science", "English"]
    data : List[List[int]]
        Data matrix where each inner list represents a row of non-negative integers
        Must have same number of rows as row_titles and columns as column_titles
        Example: [[45, 38, 42], [52, 41, 39], [48, 45, 44]]
        
    Returns
    -------
    str
        The URL of the generated two-way table image
    """
    
    logger.info(f"Generating two-way table: {table_title}")
    
    # Validate table title
    if not table_title or not str(table_title).strip():
        raise ValueError("Table title cannot be empty")
    
    # Validate input dimensions
    if not (2 <= len(row_titles) <= 5):
        raise ValueError("Row titles must have 2-5 items")
    if not (2 <= len(column_titles) <= 5):
        raise ValueError("Column titles must have 2-5 items")
    if len(data) != len(row_titles):
        raise ValueError(f"Data must have {len(row_titles)} rows to match row titles")
    
    # Validate titles are not empty
    for i, title in enumerate(row_titles):
        if not title or not str(title).strip():
            raise ValueError(f"Row title {i+1} cannot be empty")
    for i, title in enumerate(column_titles):
        if not title or not str(title).strip():
            raise ValueError(f"Column title {i+1} cannot be empty")
    
    # Validate data structure
    for i, row in enumerate(data):
        if not isinstance(row, list) or len(row) != len(column_titles):
            raise ValueError(
                f"Data row {i+1} must have {len(column_titles)} values to match column titles"
            )
        
        # Ensure all values are non-negative integers
        for j, val in enumerate(row):
            if not isinstance(val, int):
                raise ValueError(f"Data value at row {i+1}, column {j+1} must be an integer")
            if val < 0:
                raise ValueError(f"Data value at row {i+1}, column {j+1} must be non-negative")
    
    # Create formatted row and column titles
    formatted_row_titles = [
        {f"label_{i+1}": str(title)} for i, title in enumerate(row_titles)
    ]
    formatted_column_titles = [
        {f"label_{i+1}": str(title)} for i, title in enumerate(column_titles)
    ]
    
    # Create formatted data
    formatted_data = []
    for row in data:
        row_dict = {str(i+1): val for i, val in enumerate(row)}
        formatted_data.append(row_dict)
    
    # Create the TableTwoWay stimulus
    two_way_stimulus = TableTwoWay(
        table_title=str(table_title),
        rows_title=formatted_row_titles,
        columns_title=formatted_column_titles,
        data=formatted_data
    )
    
    # Generate the image using the two-way table function
    image_file_path = draw_table_two_way(two_way_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_probability_table_image(
    row_labels: List[str],
    column_labels: List[str],
    data_values: List[List[int]]
) -> str:
    """
    Generate probability tables for statistical education.
    
    Creates specialized probability tables with automatic total validation 
    for teaching probability concepts, contingency tables, and statistical 
    analysis. Enforces strict mathematical validation of totals.
    
    CRITICAL VALIDATION REQUIREMENTS:
    - Exactly 3 rows and 4 columns required
    - Last row must contain column totals (sum of first 2 rows for each column)
    - Last column must contain row totals (sum of first 3 columns for each row)
    - All values must be non-negative integers
    - Row and column labels cannot be empty
    
    Parameters
    ----------
    row_labels : List[str]
        Labels for exactly 3 rows [data_row_1, data_row_2, total_row]
        Example: ["Boys", "Girls", "Total"]
    column_labels : List[str]
        Labels for exactly 4 columns [data_col_1, data_col_2, data_col_3, total_col]
        Example: ["Basketball", "Soccer", "Tennis", "Total"]
    data_values : List[List[int]]
        3x4 integer matrix where:
        - Rows 1-2: Actual data values
        - Row 3: Column totals (must equal sum of rows 1-2 for each column)
        - Columns 1-3: Actual data values  
        - Column 4: Row totals (must equal sum of columns 1-3 for each row)
        Example: [[12, 8, 5, 25], [18, 10, 7, 35], [30, 18, 12, 60]]
        
    Returns
    -------
    str
        The URL of the generated probability table image
        
    Examples
    --------
    Sports preference by gender:
    row_labels = ["Boys", "Girls", "Total"]
    column_labels = ["Basketball", "Soccer", "Tennis", "Total"] 
    data_values = [
        [12, 8, 5, 25],   # Boys: 12+8+5=25 ✓
        [18, 10, 7, 35],  # Girls: 18+10+7=35 ✓  
        [30, 18, 12, 60]  # Totals: 12+18=30, 8+10=18, 5+7=12, 25+35=60 ✓
    ]
    """
    
    log_tool_generation("generate_coach_bot_probability_table_image", 
                        rows_count=len(row_labels), columns_count=len(column_labels))
    
    # Validate dimensions
    if len(row_labels) != 3:
        raise ValueError("Probability tables require exactly 3 row labels")
    if len(column_labels) != 4:
        raise ValueError("Probability tables require exactly 4 column labels")
    if len(data_values) != 3:
        raise ValueError("Data must have exactly 3 rows")
    
    # Validate labels are not empty
    for i, label in enumerate(row_labels):
        if not label or not str(label).strip():
            raise ValueError(f"Row label {i+1} cannot be empty")
    for i, label in enumerate(column_labels):
        if not label or not str(label).strip():
            raise ValueError(f"Column label {i+1} cannot be empty")
    
    # Validate data structure and values
    for i, row in enumerate(data_values):
        if len(row) != 4:
            raise ValueError(f"Data row {i+1} must have exactly 4 values")
        for j, val in enumerate(row):
            if not isinstance(val, int):
                raise ValueError(f"Data value at row {i+1}, column {j+1} must be an integer")
            if val < 0:
                raise ValueError(f"Data value at row {i+1}, column {j+1} must be non-negative")
    
    # Validate totals are mathematically correct
    # Check column totals (last row should equal sum of first 2 rows for each column)
    for col in range(3):  # Only check first 3 columns (data columns)
        expected_total = data_values[0][col] + data_values[1][col]
        actual_total = data_values[2][col]
        if actual_total != expected_total:
            raise ValueError(
                f"Column {col+1} total is incorrect. "
                f"Expected {expected_total} (sum of {data_values[0][col]} + "
                f"{data_values[1][col]}), got {actual_total}. Please ensure totals are calculated "
                "correctly."
            )
    
    # Check row totals (last column should equal sum of first 3 columns for each row)
    for row in range(3):  # Check all 3 rows
        expected_total = sum(data_values[row][:3])  # Sum first 3 columns
        actual_total = data_values[row][3]  # Last column value
        if actual_total != expected_total:
            row_name = ["first", "second", "total"][row]
            raise ValueError(
                f"Row {row+1} ({row_name}) total is incorrect. "
                f"Expected {expected_total} (sum of {data_values[row][:3]}), "
                f"got {actual_total}. Please ensure totals are calculated correctly."
            )
    
    # Create formatted titles
    formatted_row_titles = [
        {f"label_{i+1}": str(label)} for i, label in enumerate(row_labels)
    ]
    formatted_column_titles = [
        {f"label_{i+1}": str(label)} for i, label in enumerate(column_labels)
    ]
    
    # Create data items (probability table format using field aliases)
    data_items = []
    for row in data_values:
        # DataItem uses field aliases "1", "2", "3", "4" not field names
        data_item = DataItem(**{
            "1": row[0],  # col1 field alias
            "2": row[1],  # col2 field alias
            "3": row[2],  # col3 field alias
            "4": row[3]   # row_total field alias
        })
        data_items.append(data_item)
    
    # Create the ProbabilityDiagram stimulus
    prob_stimulus = ProbabilityDiagram(
        rows_title=formatted_row_titles,
        columns_title=formatted_column_titles,
        data=data_items
    )
    
    # Generate the image using the probability diagram function
    image_file_path = create_probability_diagram(prob_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_data_table_image(
    headers: List[str],
    data: List[List[str]],
    title: Optional[str] = None,
    metadata: Optional[str] = None
) -> str:
    """
    Generate enhanced data tables with titles and metadata.
    
    Creates professional data tables with optional titles and footer metadata. 
    Supports flexible column layouts and automatic text wrapping. Perfect for 
    presenting datasets, survey results, and structured information with 
    context and descriptions.
    
    Parameters
    ----------
    headers : List[str]
        Column headers (1-8 columns)
    data : List[List[str]]
        Table data rows (2-15 rows), each row must match header count
    title : Optional[str]
        Optional table title (max 40 characters)
    metadata : Optional[str]
        Optional footer metadata (max 40 characters)
        
    Returns
    -------
    str
        The URL of the generated data table image
    """
    
    log_tool_generation("generate_coach_bot_data_table_image", 
                        headers_count=len(headers), rows_count=len(data), 
                        title=title, has_metadata=metadata is not None)
    
    # Create the DataTable stimulus (Pydantic handles all validation automatically)
    data_table_stimulus = DataTable(
        headers=headers,
        data=data,
        title=title,
        metadata=metadata
    )
    
    # Generate the image using the data table function
    image_file_path = draw_data_table(data_table_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_table_group_image(
    tables: List[Dict[str, any]],
    group_title: Optional[str] = None,
    layout: str = "auto"
) -> str:
    """
    Generate groups of data tables arranged in organized layouts.
    
    Creates collections of related data tables arranged in grids or rows/columns. 
    Perfect for comparative analysis, showing multiple datasets, or creating 
    comprehensive data presentations with unified styling and organization.
    
    Parameters
    ----------
    tables : List[Dict[str, any]]
        List of table specifications (1-6 tables), each containing:
        - headers: List of column headers (1-8 columns)
        - data: List of data rows (2-15 rows)
        - title: Optional table title (max 40 characters)
        - metadata: Optional footer metadata (max 40 characters)
    group_title : Optional[str]
        Overall title for the group of tables (max 60 characters)
    layout : str
        Layout arrangement: 'auto' (automatic grid), 'horizontal' (single row), 'vertical' (single
        column)
        
    Returns
    -------
    str
        The URL of the generated table group image
    """
    
    log_tool_generation("generate_coach_bot_table_group_image", 
                        tables_count=len(tables), layout=layout, 
                        group_title=group_title)
    
    # Validate tables list
    if not isinstance(tables, list) or not (1 <= len(tables) <= 6):
        raise ValueError("Tables must be a list with 1-6 items")
    
    # Validate group title
    if group_title and len(str(group_title)) > 60:
        raise ValueError("Group title must not exceed 60 characters")
    
    # Validate layout
    if layout not in ['auto', 'horizontal', 'vertical']:
        raise ValueError("Layout must be 'auto', 'horizontal', or 'vertical'")
    
    # Create DataTable objects
    data_table_objects = []
    for i, table_data in enumerate(tables):
        # Validate required fields
        if 'headers' not in table_data or 'data' not in table_data:
            raise ValueError(f"Table {i+1} must have 'headers' and 'data' fields")
        
        headers = table_data['headers']
        data = table_data['data']
        
        # Validate table structure
        if not isinstance(headers, list) or not (1 <= len(headers) <= 8):
            raise ValueError(f"Table {i+1} headers must be a list with 1-8 items")
        
        if not isinstance(data, list) or not (2 <= len(data) <= 15):
            raise ValueError(f"Table {i+1} data must be a list with 2-15 rows")
        
        for j, row in enumerate(data):
            if not isinstance(row, list) or len(row) != len(headers):
                raise ValueError(
                    f"Table {i+1}, row {j+1} must have {len(headers)} values to match headers"
                )
        
        # Validate optional fields
        title = table_data.get('title')
        metadata = table_data.get('metadata')
        
        if title and len(str(title)) > 40:
            raise ValueError(f"Table {i+1} title must not exceed 40 characters")
        if metadata and len(str(metadata)) > 40:
            raise ValueError(f"Table {i+1} metadata must not exceed 40 characters")
        
        # Create DataTable object
        data_table_obj = DataTable(
            headers=[str(h) for h in headers],
            data=[[str(cell) for cell in row] for row in data],
            title=str(title) if title else None,
            metadata=str(metadata) if metadata else None
        )
        data_table_objects.append(data_table_obj)
    
    # Create the DataTableGroup stimulus
    table_group_stimulus = DataTableGroup(
        tables=data_table_objects,
        group_title=str(group_title) if group_title else None,
        layout=layout
    )
    
    # Generate the image using the table group function
    image_file_path = draw_data_table_group(table_group_stimulus)
    
    # Upload and return URL using shared utility
    return upload_coach_bot_image(image_file_path)


def generate_coach_bot_simple_table_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for simple table generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_simple_table_image",
        "description": (
            "Generate simple data tables for educational content. Creates clean, "
            "well-formatted tables for displaying structured data. Supports both "
            "vertical (traditional) and horizontal layouts. Perfect for showing "
            "data sets, comparison charts, and organizing information for "
            "mathematical analysis and interpretation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "columns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Column headers for the table (exactly 2 required)"
                },
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Row data (exactly 2 values per row matching column "
                                       "structure)"
                    },
                    "minItems": 1,
                    "maxItems": 15,
                    "description": "Educational data rows for simple analysis (1-15 rows). Each "
                                   "row contains exactly 2 values for basic data literacy "
                                   "instruction."
                },
                "horizontal": {
                    "type": "boolean",
                    "description": "Whether to use horizontal layout",
                    "default": False
                }
            },
            "required": ["columns", "rows"]
        }
    }
    return spec, generate_coach_bot_simple_table_image


def generate_coach_bot_two_way_table_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for two-way table generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_two_way_table_image",
        "description": (
            "Generate two-way tables for cross-tabulation and statistical analysis. "
            "Creates formatted tables with row and column headers for displaying "
            "cross-tabulated data. REQUIREMENTS: Non-empty table title, 2-5 non-empty "
            "row/column titles, data matrix dimensions must match header counts exactly, "
            "and all values must be non-negative integers."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "table_title": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Main title for the table (cannot be empty)"
                },
                "row_titles": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1
                    },
                    "minItems": 2,
                    "maxItems": 5,
                    "description": "Row header labels (2-5 non-empty strings)"
                },
                "column_titles": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1
                    },
                    "minItems": 2,
                    "maxItems": 5,
                    "description": "Column header labels (2-5 non-empty strings)"
                },
                "data": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "integer",
                            "minimum": 0
                        },
                        "description": "Row of non-negative integers"
                    },
                    "description": (
                        "Data matrix where each inner list represents a row. Must have same "
                        "number of rows as row_titles and same number of columns as column_titles"
                    )
                }
            },
            "required": ["table_title", "row_titles", "column_titles", "data"]
        }
    }
    return spec, generate_coach_bot_two_way_table_image


def generate_coach_bot_probability_table_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for probability table generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_probability_table_image",
        "description": (
            "Generate probability tables for statistical education with strict total "
            "validation. CRITICAL: Requires exactly 3 rows and 4 columns. Last row must "
            "contain column totals (sum of first 2 rows). Last column must contain row "
            "totals (sum of first 3 columns). All totals are automatically validated for "
            "mathematical correctness. Perfect for contingency tables and probability analysis."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "row_labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 3,
                    "description": (
                        "Exactly 3 row labels [data_row_1, data_row_2, total_row]. "
                        "Example: ['Boys', 'Girls', 'Total']"
                    )
                },
                "column_labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                    "maxItems": 4,
                    "description": (
                        "Exactly 4 column labels [data_col_1, data_col_2, data_col_3, total_col]. "
                        "Example: ['Basketball', 'Soccer', 'Tennis', 'Total']"
                    )
                },
                "data_values": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "integer",
                            "minimum": 0
                        },
                        "minItems": 4,
                        "maxItems": 4,
                        "description": "Row with 4 non-negative integers"
                    },
                    "minItems": 3,
                    "maxItems": 3,
                    "description": (
                        "3x4 matrix where last row contains column totals and last column "
                        "contains row totals. Example: [[12,8,5,25], [18,10,7,35], [30,18,12,60]] "
                        "where 30=12+18, 18=8+10, 12=5+7, 25=12+8+5, 35=18+10+7, 60=25+35"
                    )
                }
            },
            "required": ["row_labels", "column_labels", "data_values"]
        }
    }
    return spec, generate_coach_bot_probability_table_image


def generate_coach_bot_data_table_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for data table generation."""
    spec = create_dynamic_tool_spec(
        name="generate_coach_bot_data_table_image",
        description=(
            "Generate enhanced data tables with titles and metadata for educational content. "
            "Creates professional data tables with optional titles and footer metadata, automatic "
            "text wrapping, and flexible column layouts. Perfect for presenting datasets, survey "
            "results, structured information, and educational data analysis with context and "
            "descriptions. Supports comprehensive data visualization for mathematics, science, and "
            "social studies instruction."
        ),
        pydantic_model=DataTable,
        custom_descriptions={
            "headers": (
                "Column headers for the data table (1-8 columns supported). Each header provides "
                "context for the data column and helps organize information for educational "
                "analysis and interpretation. Essential for data literacy and mathematical "
                "reasoning instruction."
            ),
            "data": (
                "Table data rows containing educational content (2-15 rows supported). Each row "
                "must contain the same number of values as headers. Perfect for displaying "
                "datasets, experimental results, survey data, and structured information for "
                "student analysis."
            ),
            "title": (
                "Optional descriptive title for the data table (max 40 characters). Provides "
                "context and educational purpose for the dataset. Useful for organizing "
                "educational materials and creating clear, labeled content for instruction and "
                "assessment."
            ),
            "metadata": (
                "Optional footer metadata or additional information (max 40 characters). Useful "
                "for data source attribution, units of measurement, or explanatory notes that "
                "enhance educational understanding and provide context for data interpretation."
            )
        }
    )
    return spec, generate_coach_bot_data_table_image


def generate_coach_bot_table_group_image_tool() -> tuple[dict, Callable]:
    """Generate the tool specification and callable for table group generation."""
    spec = {
        "type": "function",
        "name": "generate_coach_bot_table_group_image",
        "description": (
            "Generate groups of data tables arranged in organized layouts. "
            "Creates collections of related data tables arranged in grids or "
            "rows/columns. Perfect for comparative analysis, showing multiple "
            "datasets, or creating comprehensive data presentations with "
            "unified styling and organization."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "tables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "headers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 1,
                                "maxItems": 8,
                                "description": "Column headers"
                            },
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Row data"
                                },
                                "minItems": 2,
                                "maxItems": 15,
                                "description": "Table data rows"
                            },
                            "title": {
                                "type": "string",
                                "maxLength": 40,
                                "description": "Optional table title"
                            },
                            "metadata": {
                                "type": "string",
                                "maxLength": 40,
                                "description": "Optional footer metadata"
                            }
                        },
                        "required": ["headers", "data"]
                    },
                    "minItems": 1,
                    "maxItems": 6,
                    "description": "List of table specifications"
                },
                "group_title": {
                    "type": "string",
                    "maxLength": 60,
                    "description": "Overall title for the group of tables"
                },
                "layout": {
                    "type": "string",
                    "enum": ["auto", "horizontal", "vertical"],
                    "description": "Layout arrangement",
                    "default": "auto"
                }
            },
            "required": ["tables"]
        }
    }
    return spec, generate_coach_bot_table_group_image
