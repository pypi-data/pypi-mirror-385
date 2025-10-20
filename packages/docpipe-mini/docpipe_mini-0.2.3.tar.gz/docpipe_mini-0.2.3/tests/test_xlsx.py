"""Test XLSX serializer functionality."""

import pytest
from pathlib import Path
from docpipe.loaders._xlsx import XlsxSerializer, CellData
from docpipe._types import ContentType


def test_xlsx_serializer_creation():
    """Test XLSX serializer can be created."""
    serializer = XlsxSerializer()
    assert serializer is not None
    assert serializer.min_cell_length == 1
    assert '.xlsx' in serializer.supported_extensions
    assert '.xls' in serializer.supported_extensions


def test_xlsx_serializer_file_detection():
    """Test file type detection."""
    serializer = XlsxSerializer()

    assert serializer.can_serialize(Path("test.xlsx"))
    assert serializer.can_serialize(Path("test.xls"))
    assert serializer.can_serialize(Path("test.xlsm"))
    assert not serializer.can_serialize(Path("test.pdf"))
    assert not serializer.can_serialize(Path("test.docx"))


def test_cell_reference_parsing():
    """Test Excel cell reference parsing."""
    serializer = XlsxSerializer()

    # Test basic references
    assert serializer._parse_cell_reference("A1") == (1, 1)
    assert serializer._parse_cell_reference("B1") == (2, 1)
    assert serializer._parse_cell_reference("A2") == (1, 2)

    # Test multi-letter columns
    assert serializer._parse_cell_reference("AA1") == (27, 1)
    assert serializer._parse_cell_reference("AB1") == (28, 1)
    assert serializer._parse_cell_reference("ZZ1") == (702, 1)

    # Test case insensitivity
    assert serializer._parse_cell_reference("a1") == (1, 1)
    assert serializer._parse_cell_reference("B10") == (2, 10)


def test_cell_data_creation():
    """Test CellData creation."""
    cell = CellData(row=1, col=1, value="Test", cell_type="string")
    assert cell.row == 1
    assert cell.col == 1
    assert cell.value == "Test"
    assert cell.cell_type == "string"
    assert cell.style is None


def test_content_type_detection():
    """Test content type detection for rows."""
    serializer = XlsxSerializer()

    # Single cell - should be text
    assert serializer._detect_content_type("Single value", 1) == ContentType.TEXT

    # Multiple cells with tabs - should be table
    assert serializer._detect_content_type("Value1\tValue2\tValue3", 3) == ContentType.TABLE

    # Header-like text
    assert serializer._detect_content_type("TITLE:", 1) == ContentType.TEXT
    assert serializer._detect_content_type("TOTAL", 1) == ContentType.TEXT


def test_coordinate_estimation():
    """Test coordinate estimation for rows."""
    serializer = XlsxSerializer()

    # First row in a 10-row sheet
    bbox = serializer._estimate_row_coordinates(1, 10, 3)
    assert 0.05 <= bbox.y <= 0.15  # Should be near top
    assert 0.05 <= bbox.x <= 0.1   # Should have left margin
    assert bbox.w == 0.9           # Should use most of width

    # Middle row
    bbox = serializer._estimate_row_coordinates(5, 10, 3)
    assert 0.45 <= bbox.y <= 0.55  # Should be in middle

    # Last row
    bbox = serializer._estimate_row_coordinates(10, 10, 3)
    assert 0.85 <= bbox.y <= 0.96  # Should be near bottom (allowing for float precision)


def test_invalid_cell_reference():
    """Test handling of invalid cell references."""
    serializer = XlsxSerializer()

    # Should default to A1 for invalid references
    assert serializer._parse_cell_reference("") == (1, 1)
    assert serializer._parse_cell_reference("invalid") == (1, 1)
    assert serializer._parse_cell_reference("123") == (1, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])