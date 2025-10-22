"""
Rows & Columns Spreadsheet - Python Implementation

A Python library for spreadsheet operations, providing data manipulation
capabilities similar to the TypeScript version.
"""

from .types import (
    CellData,
    GridRange,
    SelectionArea,
    Sheet,
    CellInterface,
    Direction,
    SpreadsheetState,
    ExtendedValue,
    ErrorValue,
)
from .spreadsheet import Spreadsheet
from .operations import insert_row, delete_row, insert_column, delete_column
from .interface import SpreadsheetInterface
from .immer_interface import ImmerSpreadsheetInterface, produce_with_patches, apply_patches
from .patches import SpreadsheetPatch, JSONPatch, PatchGenerator
from .sheet_cell import SheetCell, DEFAULT_SHEET_ID, DEFAULT_CELL_COORDS
from .sheet_cell_helpers import (
    create_row_data_from_array,
    is_cell_range,
    combine_map_iterators,
    get_next_table_column_name,
    get_conflicting_table,
    hash_object,
    AWAITING_CALCULATION,
)
from .datatype import (
    detect_value_type_and_pattern,
    detect_value_type,
    detect_number_format_type,
    detect_number_format_pattern,
    detect_decimal_pattern,
    is_currency,
    is_boolean,
    is_percentage,
    is_number,
    is_formula,
    is_valid_url_or_email,
    is_multiline,
    convert_to_number,
    create_formatted_value,
    PATTERN_NUMBER,
    PATTERN_NUMBER_THOUSANDS,
    PATTERN_PERCENT,
    PATTERN_CURRENCY,
)

__version__ = "0.1.0"
__all__ = [
    "CellData",
    "GridRange",
    "SelectionArea",
    "Sheet",
    "CellInterface",
    "Direction",
    "SpreadsheetState",
    "ExtendedValue",
    "ErrorValue",
    "Spreadsheet",
    "SpreadsheetInterface",
    "ImmerSpreadsheetInterface",
    "produce_with_patches",
    "apply_patches",
    "SpreadsheetPatch",
    "JSONPatch",
    "PatchGenerator",
    "insert_row",
    "delete_row",
    "insert_column",
    "delete_column",
    "SheetCell",
    "DEFAULT_SHEET_ID",
    "DEFAULT_CELL_COORDS",
    "create_row_data_from_array",
    "is_cell_range",
    "combine_map_iterators",
    "get_next_table_column_name",
    "get_conflicting_table",
    "hash_object",
    "AWAITING_CALCULATION",
    "detect_value_type_and_pattern",
    "detect_value_type",
    "detect_number_format_type",
    "detect_number_format_pattern",
    "detect_decimal_pattern",
    "is_currency",
    "is_boolean",
    "is_percentage",
    "is_number",
    "is_formula",
    "is_valid_url_or_email",
    "is_multiline",
    "convert_to_number",
    "create_formatted_value",
    "PATTERN_NUMBER",
    "PATTERN_NUMBER_THOUSANDS",
    "PATTERN_PERCENT",
    "PATTERN_CURRENCY",
]