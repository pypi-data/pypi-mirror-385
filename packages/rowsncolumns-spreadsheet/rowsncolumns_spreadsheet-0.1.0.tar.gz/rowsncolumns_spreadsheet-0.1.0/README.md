# Rows & Columns Spreadsheet - Python Library

A Python implementation of spreadsheet operations, providing data manipulation capabilities similar to the TypeScript version used in the main Rows & Columns spreadsheet application.

## Features

- **Core Data Types**: Pydantic models for sheets, cells, ranges, and selections
- **Row Operations**: Insert and delete rows with proper data shifting
- **Column Operations**: Insert and delete columns with proper data shifting
- **Cell Operations**: Get and set cell values, work with ranges
- **Table Support**: Automatic table range updates during row/column operations
- **Filter Support**: Basic filter range updates
- **Merge Support**: Merged cell range updates
- **History**: Operation history for undo/redo functionality

## Installation

```bash
cd python
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from rowsncolumns_spreadsheet import Spreadsheet, GridRange

# Create a new spreadsheet
spreadsheet = Spreadsheet()

# Set some cell values
spreadsheet.set_cell_value(0, 0, 0, "Hello")  # Sheet 0, Row 0, Col 0
spreadsheet.set_cell_value(0, 0, 1, "World")  # Sheet 0, Row 0, Col 1

# Get cell values
value = spreadsheet.get_cell_value(0, 0, 0)  # Returns "Hello"

# Insert rows
spreadsheet.insert_rows(sheet_id=0, reference_row_index=1, num_rows=2)

# Insert columns
spreadsheet.insert_columns(sheet_id=0, reference_column_index=1, num_columns=1)

# Work with ranges
range_values = spreadsheet.get_range_values(
    sheet_id=0,
    range_spec=GridRange(
        start_row_index=0,
        end_row_index=2,
        start_column_index=0,
        end_column_index=2,
    )
)

# Set range values
spreadsheet.set_range_values(
    sheet_id=0,
    range_spec=GridRange(start_row_index=0, end_row_index=1, start_column_index=0, end_column_index=1),
    values=[["A1", "B1"], ["A2", "B2"]]
)
```

## Architecture

The library is structured around these core concepts:

### Data Types (`types.py`)
- **CellData**: Individual cell with value, formula, and formatting
- **GridRange**: Rectangular cell range specification
- **Sheet**: Worksheet with metadata, dimensions, and features
- **SpreadsheetState**: Complete spreadsheet state including all sheets and data

### Operations (`operations.py`)
- **insert_row()**: Insert rows with proper data shifting and metadata updates
- **delete_row()**: Delete rows with proper cleanup
- **insert_column()**: Insert columns with proper data shifting
- **delete_column()**: Delete columns with proper cleanup

### High-Level Interface (`spreadsheet.py`)
- **Spreadsheet**: Main class providing convenient methods for common operations
- Manages state internally and provides intuitive APIs

### Utilities (`utils.py`)
- Helper functions for moving ranges, cloning formatting, etc.

## Compatibility with TypeScript Version

This Python implementation mirrors the core functionality of the TypeScript version:

1. **Data Structures**: Similar models using Pydantic instead of TypeScript interfaces
2. **Operation Logic**: Same algorithms for row/column insertion with proper shifting
3. **Metadata Handling**: Proper updates to tables, filters, merges, and frozen areas
4. **History Support**: Operation tracking for undo/redo functionality

Key differences:
- Uses Python/Pydantic conventions (snake_case, etc.)
- Simplified callback system (no React-specific patterns)
- Immutable state updates using model copying instead of Immer

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=rowsncolumns_spreadsheet tests/
```

## Development

Format code:
```bash
black rowsncolumns_spreadsheet/ tests/
```

Type checking:
```bash
mypy rowsncolumns_spreadsheet/
```

## Example: Advanced Usage

```python
from rowsncolumns_spreadsheet import (
    Spreadsheet,
    Sheet,
    GridRange,
    Table,
    FilterView,
    MergedCell
)

# Create a spreadsheet with custom configuration
custom_sheet = Sheet(
    sheet_id=1,
    name="Sales Data",
    index=0,
    row_count=5000,
    column_count=50,
    frozen_row_count=1,  # Freeze header row
    frozen_column_count=2,  # Freeze first two columns
)

spreadsheet = Spreadsheet()
spreadsheet._state.sheets.append(custom_sheet)

# Add a table
table = Table(
    sheet_id=1,
    range=GridRange(
        start_row_index=0,
        end_row_index=100,
        start_column_index=0,
        end_column_index=10,
    ),
    name="SalesTable"
)
spreadsheet._state.tables.append(table)

# Insert rows - table will automatically expand
spreadsheet.insert_rows(sheet_id=1, reference_row_index=50, num_rows=10)

# The table range will now include the new rows
updated_table = spreadsheet._state.tables[0]
print(f"Table now spans rows {updated_table.range.start_row_index}-{updated_table.range.end_row_index}")
```

This Python library provides a solid foundation for building spreadsheet applications or integrating spreadsheet functionality into Python applications, while maintaining compatibility with the existing TypeScript ecosystem.