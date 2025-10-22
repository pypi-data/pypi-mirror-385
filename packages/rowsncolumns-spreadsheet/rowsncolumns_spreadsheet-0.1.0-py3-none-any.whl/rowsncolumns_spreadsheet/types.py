"""
Core data types for the spreadsheet library.

These types mirror the TypeScript definitions but use Python/Pydantic conventions.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field


class Direction(Enum):
    """Direction for operations like moving cells."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class CellInterface(BaseModel):
    """Represents a single cell coordinate."""
    row_index: int = Field(ge=0, description="Row index (0-based)")
    column_index: int = Field(ge=0, description="Column index (0-based)")


class GridRange(BaseModel):
    """Represents a rectangular range of cells."""
    start_row_index: int = Field(ge=0)
    end_row_index: int = Field(ge=0)
    start_column_index: int = Field(ge=0)
    end_column_index: int = Field(ge=0)

    def model_post_init(self, __context: Any) -> None:
        """Validate that start indices are <= end indices."""
        if self.start_row_index > self.end_row_index:
            raise ValueError("start_row_index must be <= end_row_index")
        if self.start_column_index > self.end_column_index:
            raise ValueError("start_column_index must be <= end_column_index")


class SelectionAttributes(BaseModel):
    """Attributes for a selection area."""
    in_progress: bool = False
    is_filling: bool = False


class SelectionArea(BaseModel):
    """Represents a selected area in the spreadsheet."""
    range: GridRange
    attributes: Optional[SelectionAttributes] = None


class Color(BaseModel):
    """Color specification - can be theme-based or custom."""
    theme: Optional[int] = Field(None, ge=0, le=10)
    red: Optional[int] = Field(None, ge=0, le=255)
    green: Optional[int] = Field(None, ge=0, le=255)
    blue: Optional[int] = Field(None, ge=0, le=255)
    alpha: Optional[float] = Field(None, ge=0.0, le=1.0)


class FilterView(BaseModel):
    """Represents a filter view on a range."""
    range: GridRange
    title: Optional[str] = None


class MergedCell(BaseModel):
    """Represents a merged cell range."""
    range: GridRange


class RowMetadata(BaseModel):
    """Metadata for a row."""
    size: Optional[float] = None  # Row height
    hidden: bool = False


class ColumnMetadata(BaseModel):
    """Metadata for a column."""
    size: Optional[float] = None  # Column width
    hidden: bool = False


class Sheet(BaseModel):
    """Represents a worksheet."""
    sheet_id: int = Field(ge=0)
    name: str
    index: int = Field(ge=0)
    row_count: int = Field(default=1000, ge=1)
    column_count: int = Field(default=26, ge=1)
    frozen_row_count: Optional[int] = Field(default=None, ge=0)
    frozen_column_count: Optional[int] = Field(default=None, ge=0)
    tab_color: Optional[Color] = None
    hidden: bool = False
    basic_filter: Optional[FilterView] = None
    merges: Optional[List[MergedCell]] = None
    row_metadata: Optional[Dict[int, RowMetadata]] = None
    column_metadata: Optional[Dict[int, ColumnMetadata]] = None


class ErrorValue(BaseModel):
    """Represents an error value for cells, aligning with TypeScript ErrorValue."""
    type: Literal["Error", "Invalid"]
    message: str


class ExtendedValue(BaseModel):
    """Represents the possible primitive values in a cell, similar to TS ExtendedValue.

    Note: Uses camelCase field names (matching TypeScript) as primary names.
    Snake_case aliases are provided for Python convention compatibility.
    """
    numberValue: Optional[float] = Field(default=None, alias="number_value")
    stringValue: Optional[str] = Field(default=None, alias="string_value")
    boolValue: Optional[bool] = Field(default=None, alias="bool_value")
    formulaValue: Optional[str] = Field(default=None, alias="formula_value")
    errorValue: Optional[ErrorValue] = Field(default=None, alias="error_value")
    structuredValue: Optional[Dict[str, Any]] = Field(default=None, alias="structured_value")

    model_config = {
        "populate_by_name": True
    }


class CellData(BaseModel):
    """
    Cell data model broadly aligned with the TypeScript `CellData` shape.

    Notes:
    - Keeps legacy fields (value, formula, format) for backward compatibility with
      existing helpers while adding TS-like fields with proper aliases.
    - Additional fields are intentionally loosely typed (Dict/Any) to avoid
      over-constraining server-side usage.
    """
    # Legacy/simple fields used by current python helpers
    value: Any = None
    formula: Optional[str] = None
    format: Optional[Dict[str, Any]] = None

    # TS-aligned fields (aliased to camelCase)
    user_entered_value: Optional[ExtendedValue] = Field(default=None, alias="userEnteredValue")
    effective_value: Optional[ExtendedValue] = Field(default=None, alias="effectiveValue")
    formatted_value: Optional[str] = Field(default=None, alias="formattedValue")
    text_format_runs: Optional[List[Dict[str, Any]]] = Field(default=None, alias="textFormatRuns")
    note: Optional[str] = None
    hyperlink: Optional[str] = None
    data_validation: Optional[Dict[str, Any]] = Field(default=None, alias="dataValidation")
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    meta_type: Optional[Literal["people"]] = Field(default=None, alias="metaType")
    user_entered_format: Optional[Dict[str, Any]] = Field(default=None, alias="userEnteredFormat")
    effective_format: Optional[Dict[str, Any]] = Field(default=None, alias="effectiveFormat")
    collapsible: Optional[bool] = None
    is_collapsed: Optional[bool] = Field(default=None, alias="isCollapsed")

    model_config = {
        "populate_by_name": True
    }


class RowData(BaseModel):
    """
    RowData mirrors the TypeScript row shape used in SheetData where a row is an
    object that may or may not contain a `values` array.
    """
    values: Optional[List[Optional[CellData]]] = None


class Table(BaseModel):
    """Represents a table within a sheet."""
    sheet_id: int = Field(ge=0)
    range: GridRange
    name: Optional[str] = None


class HistoryEntry(BaseModel):
    """Represents an entry in the operation history for undo/redo."""
    operation: str
    timestamp: float
    data: Dict[str, Any]


class SpreadsheetState(BaseModel):
    """Complete state of a spreadsheet."""
    sheets: List[Sheet] = Field(default_factory=list)
    # SheetData<CellData>: Map of sheetId -> array of (RowData | null)
    sheet_data: Dict[int, List[Optional[RowData]]] = Field(default_factory=dict)
    tables: List[Table] = Field(default_factory=list)
    active_sheet_id: Optional[int] = None
    selections: Dict[int, List[SelectionArea]] = Field(default_factory=dict)
    history: List[HistoryEntry] = Field(default_factory=list)
