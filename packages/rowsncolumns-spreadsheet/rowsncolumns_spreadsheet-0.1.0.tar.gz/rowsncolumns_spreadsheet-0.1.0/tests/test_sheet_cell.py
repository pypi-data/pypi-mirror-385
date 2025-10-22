"""
Tests for SheetCell class and helpers.

This test module covers the core functionality of SheetCell including:
- Initialization and assignment
- Value setting and getting
- Formatting operations
- Formula handling
- Data validation
- Helper functions
"""

import pytest
from rowsncolumns_spreadsheet import (
    SheetCell,
    CellData,
    ExtendedValue,
    ErrorValue,
    CellInterface,
    DEFAULT_SHEET_ID,
    DEFAULT_CELL_COORDS,
    create_row_data_from_array,
    is_cell_range,
    get_next_table_column_name,
    hash_object,
)


class TestSheetCellInitialization:
    """Test SheetCell initialization and basic properties."""

    def test_default_initialization(self):
        """Test creating a SheetCell with default values."""
        cell = SheetCell()

        assert cell.sheet_id == DEFAULT_SHEET_ID
        assert cell.coords.row_index == DEFAULT_CELL_COORDS.row_index
        assert cell.coords.column_index == DEFAULT_CELL_COORDS.column_index
        assert cell.user_entered_value is None
        assert cell.effective_value is None
        assert cell.formatted_value is None

    def test_initialization_with_coords(self):
        """Test creating a SheetCell with custom coordinates."""
        coords = CellInterface(row_index=5, column_index=10)
        cell = SheetCell(sheet_id=2, coords=coords)

        assert cell.sheet_id == 2
        assert cell.coords.row_index == 5
        assert cell.coords.column_index == 10

    def test_initialization_with_cell_data(self):
        """Test creating a SheetCell with initial cell data."""
        cell_data = CellData(
            user_entered_value=ExtendedValue(stringValue="Hello"),
            effective_value=ExtendedValue(stringValue="Hello"),
            formatted_value="Hello"
        )
        cell = SheetCell(cell_data=cell_data)

        assert cell.user_entered_value is not None
        assert cell.user_entered_value.stringValue == "Hello"
        assert cell.effective_value is not None
        assert cell.effective_value.stringValue == "Hello"
        assert cell.formatted_value == "Hello"

    def test_cell_key_generation(self):
        """Test unique cell key generation."""
        cell = SheetCell(sheet_id=1, coords=CellInterface(row_index=0, column_index=0))
        assert cell.key == "1!A1"

        cell2 = SheetCell(sheet_id=2, coords=CellInterface(row_index=5, column_index=3))
        assert cell2.key == "2!D6"

    def test_static_generate_cell_key(self):
        """Test static cell key generation method."""
        key = SheetCell.generate_cell_key(1, 0, 0)
        assert key == "1!A1"

        key2 = SheetCell.generate_cell_key(3, 10, 25)
        assert key2 == "3!Z11"


class TestSheetCellValueSetting:
    """Test setting different value types."""

    def test_set_string_value(self):
        """Test setting a string value."""
        cell = SheetCell()
        cell.set_user_entered_value("Hello World")

        assert cell.user_entered_value.stringValue == "Hello World"
        assert cell.effective_value.stringValue == "Hello World"
        assert cell.formatted_value == "Hello World"
        assert cell.effective_format is not None
        assert cell.effective_format.get('horizontalAlignment') == 'left'

    def test_set_number_value(self):
        """Test setting a number value."""
        cell = SheetCell()
        cell.set_user_entered_value(42)

        assert cell.user_entered_value.stringValue == "42.0"
        assert cell.effective_value.numberValue == 42.0
        assert cell.formatted_value == "42"
        assert cell.effective_format.get('horizontalAlignment') == 'right'

    def test_set_float_value(self):
        """Test setting a float value."""
        cell = SheetCell()
        cell.set_user_entered_value(3.14159)

        assert cell.effective_value.numberValue == 3.14159
        assert cell.effective_format.get('horizontalAlignment') == 'right'

    def test_set_boolean_value(self):
        """Test setting a boolean value."""
        cell = SheetCell()
        cell.set_user_entered_value(True)

        assert cell.user_entered_value.boolValue is True
        assert cell.effective_value.boolValue is True
        assert cell.formatted_value == "TRUE"
        assert cell.effective_format.get('horizontalAlignment') == 'center'

        cell2 = SheetCell()
        cell2.set_user_entered_value(False)
        assert cell2.formatted_value == "FALSE"

    def test_set_formula_value(self):
        """Test setting a formula value."""
        cell = SheetCell()
        cell.set_user_entered_value("=SUM(A1:A10)")

        assert cell.user_entered_value.formulaValue == "=SUM(A1:A10)"
        assert cell.is_formula() is True
        assert cell.formula == "=SUM(A1:A10)"

    def test_set_formula_with_plus_prefix(self):
        """Test setting a formula with + prefix."""
        cell = SheetCell()
        cell.set_user_entered_value("+A1+B1")

        assert cell.user_entered_value.formulaValue == "=A1+B1"
        assert cell.is_formula() is True

    def test_formula_clears_number_format(self):
        """Test that entering a formula clears number format from previous value."""
        cell = SheetCell()

        # First, set a number with format
        cell.set_user_entered_value("12.12")
        cell_data_1 = cell.get_cell_data()

        # Verify number format exists
        assert 'numberFormat' in cell_data_1.get('uf', {})
        assert 'numberFormat' in cell_data_1.get('ef', {})

        # Then set a formula
        cell.set_user_entered_value("=SUM(4,4)")
        cell_data_2 = cell.get_cell_data()

        # Verify number format was cleared
        assert 'numberFormat' not in cell_data_2.get('uf', {})
        assert 'numberFormat' not in cell_data_2.get('ef', {})
        assert cell.user_entered_value.formulaValue == "=SUM(4,4)"

    def test_set_empty_value(self):
        """Test setting empty/None value."""
        cell = SheetCell()
        cell.set_user_entered_value("Test")
        cell.set_user_entered_value(None)

        assert cell.user_entered_value is None
        assert cell.effective_value is None
        assert cell.formatted_value is None

    def test_set_effective_value(self):
        """Test setting effective value directly."""
        cell = SheetCell()
        cell.set_effective_value(100)

        assert cell.effective_value.numberValue == 100.0
        assert cell.formatted_value == "100"

    def test_set_error_value(self):
        """Test setting an error value."""
        cell = SheetCell()
        error = ErrorValue(type="Error", message="Division by zero")
        cell.set_effective_value(error)

        assert cell.effective_value.errorValue is not None
        assert cell.effective_value.errorValue.message == "Division by zero"


class TestSheetCellFormatting:
    """Test cell formatting operations."""

    def test_set_user_entered_format(self):
        """Test setting user-entered format."""
        cell = SheetCell()
        cell.set_user_entered_format('textFormat', {'bold': True, 'italic': True})

        assert cell.user_entered_format is not None
        assert cell.user_entered_format['textFormat']['bold'] is True
        assert cell.user_entered_format['textFormat']['italic'] is True

    def test_set_effective_format(self):
        """Test setting effective format."""
        cell = SheetCell()
        cell.set_effective_format('backgroundColor', {'red': 255, 'green': 0, 'blue': 0})

        assert cell.effective_format is not None
        assert cell.effective_format['backgroundColor']['red'] == 255

    def test_set_border(self):
        """Test setting cell borders."""
        cell = SheetCell()
        border = {'style': 'SOLID', 'color': {'red': 0, 'green': 0, 'blue': 0}}
        cell.set_border('top', border)

        assert cell.user_entered_format is not None
        assert cell.user_entered_format['borders']['top'] == border

    def test_set_all_borders(self):
        """Test setting all borders at once."""
        cell = SheetCell()
        border = {'style': 'SOLID', 'color': {'red': 0, 'green': 0, 'blue': 0}}
        cell.set_all_borders(border)

        assert cell.user_entered_format['borders']['top'] == border
        assert cell.user_entered_format['borders']['bottom'] == border
        assert cell.user_entered_format['borders']['left'] == border
        assert cell.user_entered_format['borders']['right'] == border

    def test_clear_all_borders(self):
        """Test clearing all borders."""
        cell = SheetCell()
        border = {'style': 'SOLID', 'color': {'red': 0, 'green': 0, 'blue': 0}}
        cell.set_all_borders(border)
        cell.clear_all_borders()

        assert cell.user_entered_format.get('borders') is None

    def test_clear_formatting(self):
        """Test clearing all formatting."""
        cell = SheetCell()
        cell.set_user_entered_format('textFormat', {'bold': True})
        cell.clear_formatting()

        assert cell.user_entered_format is None
        assert cell.effective_format is None

    def test_change_indent(self):
        """Test changing cell indent."""
        cell = SheetCell()
        cell.increase_indent()

        assert cell.user_entered_format['indent'] == 2

        cell.increase_indent()
        assert cell.user_entered_format['indent'] == 4

        cell.decrease_indent()
        assert cell.user_entered_format['indent'] == 2

    def test_set_text_format_color(self):
        """Test setting text format color."""
        cell = SheetCell()
        cell.set_effective_text_format_color('#FF0000')

        assert cell.effective_format['textFormat']['color'] == '#FF0000'

        cell.set_effective_text_format_color(None)
        assert cell.effective_format['textFormat'].get('color') is None


class TestSheetCellHelpers:
    """Test helper methods and utilities."""

    def test_is_empty(self):
        """Test checking if cell is empty."""
        cell = SheetCell()
        assert cell.is_empty() is True

        cell.set_user_entered_value("Test")
        assert cell.is_empty() is False

    def test_is_multiline(self):
        """Test checking for multiline text."""
        cell = SheetCell()
        cell.set_user_entered_value("Line 1\nLine 2")

        assert cell.is_multiline() is True

        cell2 = SheetCell()
        cell2.set_user_entered_value("Single line")
        assert cell2.is_multiline() is False

    def test_is_formula(self):
        """Test checking if cell contains formula."""
        cell = SheetCell()
        assert cell.is_formula() is False

        cell.set_user_entered_value("=A1+B1")
        assert cell.is_formula() is True

    def test_is_structured_reference_formula(self):
        """Test checking for structured reference formulas."""
        cell = SheetCell()
        cell.set_formula_value("=Table1[@Column1]")

        assert cell.is_structured_reference_formula() is True

        cell2 = SheetCell()
        cell2.set_formula_value("=A1+B1")
        assert cell2.is_structured_reference_formula() is False

    def test_ephemeral(self):
        """Test checking for ephemeral formulas."""
        cell = SheetCell()
        cell.set_formula_value("=$A$1")

        assert cell.ephemeral() is True

    def test_delete_contents(self):
        """Test deleting cell contents."""
        cell = SheetCell()
        cell.set_user_entered_value("Test")
        cell.set_user_entered_format('textFormat', {'bold': True})

        cell.delete_contents()

        assert cell.user_entered_value is None
        assert cell.effective_value is None
        # Format should be preserved
        assert cell.user_entered_format is not None

    def test_clone_with_formatting(self):
        """Test cloning cell while preserving formatting."""
        cell = SheetCell()
        cell.set_user_entered_value("Test")
        cell.set_user_entered_format('textFormat', {'bold': True})

        cloned = cell.clone_with_formatting()

        assert cloned.user_entered_value is None
        assert cloned.user_entered_format is not None


class TestSheetCellDataValidation:
    """Test data validation functionality."""

    def test_set_data_validation(self):
        """Test setting data validation rule."""
        cell = SheetCell()
        validation = {
            'condition': {
                'type': 'NUMBER_GREATER',
                'values': [{'userEnteredValue': '0'}]
            }
        }
        cell.set_data_validation(validation)

        assert cell.data_validation is not None
        assert cell.data_validation['condition']['type'] == 'NUMBER_GREATER'

    def test_delete_data_validation(self):
        """Test deleting data validation."""
        cell = SheetCell()
        validation = {'condition': {'type': 'NUMBER_GREATER', 'values': []}}
        cell.set_data_validation(validation)
        cell.delete_data_validation()

        assert cell.data_validation is None

    def test_set_conditional_format_result(self):
        """Test setting conditional format result."""
        cell = SheetCell()
        cell.set_conditional_format_result(1, {'backgroundColor': 'red'})

        assert cell.conditional_formatting_result_by_id is not None
        assert cell.conditional_formatting_result_by_id[1] == {'backgroundColor': 'red'}


class TestSheetCellHyperlinks:
    """Test hyperlink functionality."""

    def test_set_url(self):
        """Test setting URL."""
        cell = SheetCell()
        cell.set_url("https://example.com")

        assert cell.hyperlink == "https://example.com"
        assert cell.formatted_value == "https://example.com"

    def test_set_url_with_title(self):
        """Test setting URL with custom title."""
        cell = SheetCell()
        cell.set_url("https://example.com", "Example Site")

        assert cell.hyperlink == "https://example.com"
        assert cell.formatted_value == "Example Site"

    def test_delete_url(self):
        """Test deleting URL."""
        cell = SheetCell()
        cell.set_url("https://example.com")
        cell.delete_url()

        assert cell.hyperlink is None


class TestSheetCellImages:
    """Test image functionality."""

    def test_set_image(self):
        """Test setting image URL."""
        cell = SheetCell()
        cell.set_image("https://example.com/image.png")

        assert cell.image_url == "https://example.com/image.png"
        assert cell.formatted_value == ""


class TestSheetCellGetters:
    """Test getter methods."""

    def test_get_effective_value(self):
        """Test getting effective value."""
        cell = SheetCell()
        cell.set_user_entered_value(42)

        assert cell.get_effective_value() == 42.0

    def test_get_user_entered_value(self):
        """Test getting user-entered value."""
        cell = SheetCell()
        cell.set_user_entered_value("Test")

        assert cell.get_user_entered_value() == "Test"

    def test_get_cell_data(self):
        """Test getting complete cell data."""
        cell = SheetCell()
        cell.set_user_entered_value(42)

        cell_data = cell.get_cell_data()

        assert cell_data is not None
        assert 'ue' in cell_data
        assert 'ev' in cell_data
        assert 'fv' in cell_data

    def test_get_number_format(self):
        """Test getting number format."""
        cell = SheetCell()
        cell.set_user_entered_value(42)

        # Initially might not have number format
        num_format = cell.get_number_format()
        # Could be None or a dict depending on implementation


class TestSheetCellTypeChecks:
    """Test type checking methods."""

    def test_is_date(self):
        """Test checking if format is DATE."""
        cell = SheetCell()
        assert cell.is_date() is False

        # With date format
        date_format = {'type': 'DATE', 'pattern': 'MM/DD/YYYY'}
        assert cell.is_date(date_format) is True

    def test_is_date_time(self):
        """Test checking if format is DATE_TIME."""
        cell = SheetCell()
        assert cell.is_date_time() is False

        datetime_format = {'type': 'DATE_TIME', 'pattern': 'MM/DD/YYYY HH:MM'}
        assert cell.is_date_time(datetime_format) is True

    def test_is_text(self):
        """Test checking if format is TEXT."""
        cell = SheetCell()
        assert cell.is_text() is False

        text_format = {'type': 'TEXT'}
        assert cell.is_text(text_format) is True

    def test_is_number_type(self):
        """Test checking if format type is numeric."""
        cell = SheetCell()

        assert cell.is_number_type('NUMBER') is True
        assert cell.is_number_type('CURRENCY') is True
        assert cell.is_number_type('PERCENT') is True
        assert cell.is_number_type('TEXT') is False


class TestSheetCellHelperFunctions:
    """Test helper functions from sheet_cell_helpers module."""

    def test_create_row_data_from_array(self):
        """Test creating row data from array."""
        rows = [
            ["Name", "Age", "Score"],
            ["Alice", 25, 95.5],
            ["Bob", 30, 88.0],
        ]

        row_data = create_row_data_from_array(rows)

        assert len(row_data) == 3
        assert len(row_data[0]['values']) == 3
        # First cell should have string value
        assert row_data[0]['values'][0] is not None

    def test_is_cell_range(self):
        """Test checking if coordinates are a range."""
        assert is_cell_range({"from": {"row": 0, "col": 0}}) is True
        assert is_cell_range({"row": 0, "col": 0}) is False

    def test_get_next_table_column_name(self):
        """Test getting next table column name."""
        columns = [{"name": "Column1"}, {"name": "Column2"}]
        next_name = get_next_table_column_name(columns)

        assert next_name == "Column3"

        # With no columns
        assert get_next_table_column_name(None) == "Column1"
        assert get_next_table_column_name([]) == "Column1"

    def test_hash_object(self):
        """Test object hashing."""
        obj1 = {"key": "value", "num": 123}
        obj2 = {"key": "value", "num": 123}
        obj3 = {"key": "different", "num": 456}

        hash1 = hash_object(obj1)
        hash2 = hash_object(obj2)
        hash3 = hash_object(obj3)

        # Same objects should hash to same value
        assert hash1 == hash2
        # Different objects should hash to different values
        assert hash1 != hash3

        # None should hash to 0
        assert hash_object(None) == 0


class TestSheetCellNotes:
    """Test cell note functionality."""

    def test_update_note(self):
        """Test updating cell note."""
        cell = SheetCell()
        cell.update_note("This is a note")

        assert cell.note == "This is a note"

        cell.update_note(None)
        assert cell.note is None


class TestSheetCellLoading:
    """Test loading state functionality."""

    def test_set_loading(self):
        """Test setting loading state."""
        cell = SheetCell()
        cell.set_loading()

        assert cell.is_loading is True
        assert cell.effective_value is None

    def test_hide_loading(self):
        """Test hiding loading state."""
        cell = SheetCell()
        cell.set_loading()
        cell.hide_loading()

        assert cell.is_loading is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
