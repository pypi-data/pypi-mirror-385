"""
XLSX serializer using Python standard library.

Zero-dependency Excel parser using zipfile and xml.etree.
Extracts cell data with basic coordinate estimation for AI consumption.

Features:
- Stream-based processing for memory efficiency
- RAG-optimized JSONL output format
- Header injection and custom table parsing
- Context manager support
- Row-level chunking for better granularity
"""

from __future__ import annotations

import logging
import re
import zipfile
import xml.etree.ElementTree as ET
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass

from .._types import DocumentChunk, BBox, ContentType, estimate_tokens, generate_doc_id
from .._protocols import DocumentSerializer, SerializerMixin, LoggingMixin
from ..utils._table_parser import TableHeaderParser
from ..formatters._rag_jsonl import format_chunks_as_rag_jsonl

# Constants for Excel processing
EXCEL_NAMESPACES = {
    'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'chart': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
    'drawing': 'http://schemas.openxmlformats.org/drawingml/2006/main'
}

# File paths within XLSX structure
WORKBOOK_PATH = 'xl/workbook.xml'
SHARED_STRINGS_PATH = 'xl/sharedStrings.xml'
WORKSHEET_PREFIX = 'xl/worksheets/sheet'
MEDIA_PREFIX = 'xl/media/'
CHART_PREFIX = 'xl/charts/'

# Excel date constants
EXCEL_EPOCH = datetime(1899, 12, 30)
EXCEL_LEAP_YEAR_BUG_DAY = 60
BUSINESS_DATE_START = 36526  # 2000-01-01
BUSINESS_DATE_END = 54878    # 2050-12-31
HISTORICAL_DATE_START = 32874  # 1990-01-01
HISTORICAL_DATE_END = 36525    # 1999-12-31

# Processing constants
NULL_VALUE = "NULL"
MAX_CELL_LENGTH = 50
MIN_TABLE_ROWS = 3
MEANINGFUL_DATA_THRESHOLD = 0.3
HEADER_INDICATOR_THRESHOLD = 0.5


@dataclass
class CellData:
    """
    Represents a single Excel cell with position and content.

    Attributes:
        row: Row number (1-based)
        col: Column number (1-based, A=1, B=2, etc.)
        value: Cell value as string
        cell_type: Excel cell type ("string", "number", "boolean", "date")
        style: Optional style information
    """
    row: int
    col: int
    value: str
    cell_type: str
    style: Optional[str] = None


class XlsxSerializer(LoggingMixin, SerializerMixin, DocumentSerializer):
    """
    XLSX serializer using Python standard library only.

    This serializer parses XLSX files by extracting cell data from worksheet XML files
    and estimating coordinates based on cell positions. It supports:

    - Row-level table chunking for RAG optimization
    - Header injection (row-based or custom)
    - Memory-efficient streaming processing
    - Context manager support
    - RAG-optimized JSONL output
    - Image and chart extraction

    The serializer works entirely with Python's standard library (zipfile + xml.etree),
    making it lightweight and dependency-free.
    """

    def __init__(self, *, min_cell_length: int = 1):
        """
        Initialize the XLSX serializer.

        Args:
            min_cell_length: Minimum cell content length for inclusion in output.
                           Cells with content shorter than this may be filtered out
                           to reduce noise in the output.
        """
        super().__init__()  # Initialize both mixin attributes
        self.min_cell_length = min_cell_length
        self.log_debug("XLSX serializer initialized", min_cell_length=min_cell_length)

    def can_serialize(self, file_path: Path | str) -> bool:
        """Check if file is an XLSX."""
        # Convert to Path object for consistent handling
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        return file_path.suffix.lower() in ['.xlsx', '.xls', '.xlsm']

    def serialize(
        self,
        file_path: Path | str,
        *,
        max_mem_mb: Optional[int] = None,
        header_row: Optional[Union[int, List[int]]] = None,
        custom_headers: Optional[Union[List[str], List[List[str]]]] = None
    ) -> Iterator[DocumentChunk]:
        """
        Serialize XLSX document into coordinate-aware chunks.

        This method processes XLSX files in a streaming fashion, yielding chunks
        as they are processed to maintain memory efficiency.

        Args:
            file_path: Path to XLSX file
            max_mem_mb: Memory limit (not implemented for stdlib version)
            header_row: Optional row number to use as header (1-based)
            custom_headers: Optional list of custom headers to inject

        Yields:
            DocumentChunk objects with cell data and estimated coordinates

        Raises:
            ValueError: If file is invalid or parameters are invalid
            zipfile.BadZipFile: If file is not a valid ZIP archive
        """
        # Normalize and validate inputs
        file_path = self._normalize_file_path(file_path)
        config = self._resolve_serialization_config(max_mem_mb, header_row, custom_headers)

        self.log_operation_start(
            "XLSX serialization",
            file_path=str(file_path),
            file_size=file_path.stat().st_size if file_path.exists() else 0
        )
        self._log_header_injection_config(config)

        try:
            with self.log_timing("XLSX file processing"):
                with zipfile.ZipFile(file_path, 'r') as xlsx:
                    self._validate_xlsx_structure(xlsx)

                    # Prepare processing context
                    document_metadata = self._build_document_metadata(file_path, config)
                    processing_context = self._build_processing_context(xlsx, document_metadata)

                    # Process content in order: tables, images, charts
                    yield from self._process_worksheets(xlsx, processing_context)
                    yield from self._process_images(xlsx, processing_context)
                    yield from self._process_charts(xlsx, processing_context)

                    # Log processing statistics
                    total_chunks = self._count_total_chunks(processing_context)
                    self.log_processing_stats(
                        {
                            "total_chunks": total_chunks,
                            "file_size_mb": file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0
                        },
                        file_path=str(file_path)
                    )

            self.log_operation_success(
                "XLSX serialization",
                file_path=str(file_path)
            )

        except Exception as e:
            self.log_operation_error(
                "XLSX serialization",
                e,
                file_path=str(file_path)
            )
            raise

    # === Input normalization and validation ===

    def _normalize_file_path(self, file_path: Path | str) -> Path:
        """Normalize file path to Path object."""
        return Path(file_path) if isinstance(file_path, str) else file_path

    def _resolve_serialization_config(
        self,
        max_mem_mb: Optional[int],
        header_row: Optional[Union[int, List[int]]],
        custom_headers: Optional[Union[List[str], List[List[str]]]]
    ) -> Dict[str, Any]:
        """Resolve effective configuration from parameters and internal state."""
        effective_max_mem = max_mem_mb if max_mem_mb is not None else self._max_mem_mb
        effective_header_row = header_row if header_row is not None else self._header_row
        effective_custom_headers = custom_headers if custom_headers is not None else self._custom_headers

        # Validate header injection parameters
        if effective_header_row is not None and effective_custom_headers is not None:
            raise ValueError("Cannot specify both header_row and custom_headers")

        # Validate header_row (can be int or list of ints)
        if effective_header_row is not None:
            if isinstance(effective_header_row, int):
                if effective_header_row < 1:
                    raise ValueError("header_row must be a positive integer (1-based)")
            elif isinstance(effective_header_row, list):
                for i, hr in enumerate(effective_header_row):
                    if hr is not None and hr < 1:
                        raise ValueError(f"header_row[{i}] must be a positive integer (1-based) or None")
            else:
                raise ValueError("header_row must be an int or list of ints")

        # Validate custom_headers (can be list of strings or list of lists)
        if effective_custom_headers is not None:
            if isinstance(effective_custom_headers, list):
                if effective_custom_headers and isinstance(effective_custom_headers[0], list):
                    # Multi-sheet custom headers
                    for i, headers in enumerate(effective_custom_headers):
                        if headers is not None and not headers:
                            raise ValueError(f"custom_headers[{i}] cannot be an empty list")
                else:
                    # Single-sheet custom headers
                    if not effective_custom_headers:
                        raise ValueError("custom_headers cannot be empty")
            else:
                raise ValueError("custom_headers must be a list of strings or list of lists")

        return {
            'max_mem_mb': effective_max_mem,
            'header_row': effective_header_row,
            'custom_headers': effective_custom_headers,
            'header_injection': self._build_header_injection_metadata(effective_header_row, effective_custom_headers)
        }

    def _build_header_injection_metadata(
        self,
        header_row: Optional[Union[int, List[int]]],
        custom_headers: Optional[Union[List[str], List[List[str]]]]
    ) -> Dict[str, Any]:
        """
        Build header injection metadata dictionary.

        Supports both single-sheet and multi-sheet header configuration:
        - header_row=1: All sheets use row 1 as header
        - header_row=[1, 2, None]: Sheet 1 uses row 1, sheet 2 uses row 2, sheet 3 has no header
        - custom_headers=["A", "B"]: All sheets use these headers
        - custom_headers=[["A", "B"], ["C", "D"], None]: Each sheet has its own headers
        """
        if header_row is not None:
            if isinstance(header_row, list):
                return {
                    "type": "multi_sheet_row_based",
                    "header_rows": header_row,
                    "is_multi_sheet": True
                }
            else:
                return {"type": "row_based", "header_row": header_row}
        elif custom_headers is not None:
            if isinstance(custom_headers, list) and custom_headers and isinstance(custom_headers[0], list):
                return {
                    "type": "multi_sheet_custom",
                    "headers": custom_headers,
                    "is_multi_sheet": True
                }
            else:
                return {"type": "custom", "headers": custom_headers}
        return {}

    def _log_header_injection_config(self, config: Dict[str, Any]) -> None:
        """Log header injection configuration for debugging."""
        header_row = config['header_row']
        custom_headers = config['custom_headers']

        if header_row is not None:
            if isinstance(header_row, list):
                self.log_info(
                    "Using multi-sheet header row injection",
                    header_rows=header_row,
                    sheet_count=len(header_row)
                )
            else:
                self.log_info("Using header row injection", header_row=header_row)
        elif custom_headers is not None:
            if isinstance(custom_headers, list) and custom_headers and isinstance(custom_headers[0], list):
                self.log_info(
                    "Using multi-sheet custom headers injection",
                    sheets_with_headers=len([h for h in custom_headers if h]),
                    total_sheets=len(custom_headers),
                    first_sheet_headers=custom_headers[0][:3] if custom_headers and custom_headers[0] else []
                )
            else:
                preview_headers = custom_headers[:3]
                self.log_info(
                    "Using custom headers injection",
                    headers_preview=preview_headers,
                    total_headers=len(custom_headers)
                )

    def _count_total_chunks(self, context: Dict[str, Any]) -> int:
        """Count total chunks that will be generated (estimate)."""
        try:
            # Count worksheet chunks (this is an approximation)
            worksheet_files = self._get_worksheet_files(context['xlsx'])
            estimated_chunks = len(worksheet_files) * 10  # Rough estimate

            # Add image chunks
            media_files = [f for f in context['xlsx'].namelist() if f.startswith(MEDIA_PREFIX)]
            estimated_chunks += len(media_files)

            # Add chart chunks
            chart_files = [f for f in context['xlsx'].namelist() if f.startswith(CHART_PREFIX)]
            estimated_chunks += len(chart_files)

            return estimated_chunks
        except Exception:
            return 0

    # === XLSX structure validation and preparation ===

    def _validate_xlsx_structure(self, xlsx: zipfile.ZipFile) -> None:
        """Validate that the ZIP file contains valid XLSX structure."""
        if WORKBOOK_PATH not in xlsx.namelist():
            raise ValueError("Invalid XLSX file: no workbook.xml found")

    def _build_document_metadata(self, file_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build document metadata dictionary."""
        base_metadata = {
            "source_file": str(file_path),
            "file_name": file_path.name,
            "file_extension": file_path.suffix,
            "file_size": file_path.stat().st_size if file_path.exists() else 0
        }

        # Add header injection metadata if configured
        if config['header_injection']:
            base_metadata["header_injection"] = config['header_injection']

        return base_metadata

    def _build_processing_context(self, xlsx: zipfile.ZipFile, document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build processing context with shared resources."""
        return {
            'xlsx': xlsx,
            'document_metadata': document_metadata,
            'sheet_names': self._extract_sheet_names(xlsx),
            'shared_strings': self._extract_shared_strings_from_file(xlsx)
        }

    # === Content processing methods ===

    def _process_worksheets(self, xlsx: zipfile.ZipFile, context: Dict[str, Any]) -> Iterator[DocumentChunk]:
        """Process all worksheets and yield table chunks."""
        worksheet_files = self._get_worksheet_files(xlsx)
        if not worksheet_files:
            raise ValueError("No worksheets found in XLSX file")

        sheet_names = context['sheet_names']
        document_metadata = context['document_metadata']
        shared_strings = context['shared_strings']

        for sheet_index, worksheet_file in enumerate(worksheet_files):
            sheet_name = sheet_names[sheet_index] if sheet_index < len(sheet_names) else f"Sheet{sheet_index + 1}"

            with self.log_timing(f"worksheet_{sheet_index + 1}_processing",
                                worksheet_file=worksheet_file, sheet_name=sheet_name):
                try:
                    self.log_debug(f"Processing worksheet: {worksheet_file} ({sheet_name})")
                    worksheet_data = xlsx.read(worksheet_file)
                    chunks = self._extract_worksheet_chunks(
                        worksheet_data, sheet_index + 1, sheet_name, document_metadata, shared_strings
                    )
                    yield from chunks
                except Exception as sheet_error:
                    self.log_warning(f"Error processing worksheet {worksheet_file}: {sheet_error}",
                                    worksheet_file=worksheet_file, sheet_name=sheet_name)
                    continue

    def _process_images(self, xlsx: zipfile.ZipFile, context: Dict[str, Any]) -> Iterator[DocumentChunk]:
        """Process embedded images and yield image chunks."""
        image_chunks = self._extract_images(xlsx, context['document_metadata'])
        yield from image_chunks

    def _process_charts(self, xlsx: zipfile.ZipFile, context: Dict[str, Any]) -> Iterator[DocumentChunk]:
        """Process charts and yield chart chunks."""
        chart_chunks = self._extract_charts(xlsx, context['document_metadata'])
        yield from chart_chunks

    def _get_worksheet_files(self, xlsx: zipfile.ZipFile) -> List[str]:
        """Get and sort worksheet file paths."""
        worksheet_files = [f for f in xlsx.namelist()
                         if f.startswith(WORKSHEET_PREFIX) and f.endswith('.xml')]
        worksheet_files.sort()
        return worksheet_files

    def _extract_worksheet_chunks(
        self,
        worksheet_data: bytes,
        sheet_num: int,
        sheet_name: str,
        document_metadata: Dict[str, Any],
        shared_strings: List[str] = None
    ) -> List[DocumentChunk]:
        """
        Extract chunks from a worksheet.

        Args:
            worksheet_data: XML data for the worksheet
            sheet_num: Worksheet number (1-based)
            document_metadata: Document metadata to include

        Returns:
            List of DocumentChunk objects
        """
        chunks = []

        try:
            root = ET.fromstring(worksheet_data)

            # Define namespace
            namespaces = {
                '': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
            }

            # Use the shared strings passed in
            if shared_strings is None:
                shared_strings = []

            # Extract all cells
            cells = self._extract_cells(root, namespaces, shared_strings)

            if not cells:
                self.log_debug(f"No cells found in worksheet {sheet_num}", sheet_num=sheet_num, sheet_name=sheet_name)
                return chunks

            # Organize cells by rows
            rows_data = {}
            for cell in cells:
                if cell.row not in rows_data:
                    rows_data[cell.row] = []
                rows_data[cell.row].append(cell)

            # Sort cells within each row by column
            for row_num in rows_data:
                rows_data[row_num].sort(key=lambda c: c.col)

            # Create structured table chunks for contiguous data ranges only
            # Skip individual row chunks to avoid duplication
            table_chunks = self._create_table_chunks(rows_data, sheet_num, sheet_name, document_metadata)
            chunks.extend(table_chunks)

        except Exception as e:
            self.log_warning(f"Error extracting worksheet chunks: {e}", sheet_num=sheet_num, sheet_name=sheet_name)

        return chunks

    def _extract_shared_strings(self, root: ET.Element, namespaces: Dict[str, str]) -> List[str]:
        """
        Extract shared strings from the worksheet.

        Note: In a full implementation, we'd read from xl/sharedStrings.xml,
        but for this stdlib version, we'll extract from inline elements.
        """
        shared_strings = []

        try:
            # Look for inline rich text elements that might contain shared strings
            for is_elem in root.findall('.//is', namespaces):
                for text_elem in is_elem.findall('.//t', namespaces):
                    if text_elem.text:
                        # Try to handle encoding issues
                        text_value = text_elem.text
                        try:
                            # Ensure proper UTF-8 encoding
                            if isinstance(text_value, bytes):
                                text_value = text_value.decode('utf-8')
                            shared_strings.append(text_value)
                        except (UnicodeDecodeError, UnicodeEncodeError):
                            # If encoding fails, try to decode with error handling
                            try:
                                text_value = text_value.encode('ascii', errors='ignore').decode('ascii')
                                shared_strings.append(text_value)
                            except:
                                # As last resort, use repr
                                shared_strings.append(repr(text_value))
        except Exception as e:
            self.log_debug(f"Error extracting shared strings: {e}")

        return shared_strings

    def _extract_cells(
        self,
        root: ET.Element,
        namespaces: Dict[str, str],
        shared_strings: List[str]
    ) -> List[CellData]:
        """
        Extract all cells from the worksheet.

        Args:
            root: Worksheet XML root element
            namespaces: XML namespaces
            shared_strings: List of shared strings (not used in stdlib version)

        Returns:
            List of CellData objects
        """
        cells = []

        try:
            # Find all cells
            cell_elements = root.findall('.//c', namespaces)

            for cell_elem in cell_elements:
                try:
                    # Parse cell reference (e.g., "A1", "B2")
                    cell_ref = cell_elem.get('r', '')
                    if not cell_ref:
                        continue

                    # Extract row and column numbers
                    col_num, row_num = self._parse_cell_reference(cell_ref)

                    # Get cell value
                    cell_value = self._get_cell_value(cell_elem, namespaces, shared_strings)

                    # Skip empty cells
                    if not cell_value or not cell_value.strip():
                        continue

                    # Determine cell type
                    cell_type = cell_elem.get('t', 'string')  # Default to string

                    # Create cell data
                    cell_data = CellData(
                        row=row_num,
                        col=col_num,
                        value=cell_value,
                        cell_type=cell_type
                    )

                    cells.append(cell_data)

                except Exception as cell_error:
                    self.log_debug(f"Error processing cell {cell_ref}: {cell_error}", cell_ref=cell_ref)
                    continue

        except Exception as e:
            self.log_warning(f"Error extracting cells: {e}")

        return cells

    def _parse_cell_reference(self, cell_ref: str) -> Tuple[int, int]:
        """
        Parse Excel cell reference (e.g., "A1", "B2") into column and row numbers.

        Args:
            cell_ref: Cell reference string

        Returns:
            Tuple of (column_number, row_number)
        """
        # Separate letters (column) from numbers (row)
        import re
        match = re.match(r'([A-Za-z]+)(\d+)', cell_ref)
        if not match:
            return 1, 1  # Default to A1

        col_letters, row_str = match.groups()

        # Convert column letters to number (A=1, B=2, ..., AA=27, etc.)
        col_num = 0
        for char in col_letters.upper():
            col_num = col_num * 26 + (ord(char) - ord('A') + 1)

        # Convert row string to number
        row_num = int(row_str)

        return col_num, row_num

    def _get_cell_value(self, cell_elem: ET.Element, namespaces: Dict[str, str], shared_strings: List[str] = None) -> str:
        """
        Extract the actual value from a cell element.

        Args:
            cell_elem: Cell XML element
            namespaces: XML namespaces
            shared_strings: List of shared strings from the workbook

        Returns:
            Cell value as string
        """
        try:
            # Check for inline string (is element)
            is_elem = cell_elem.find('is', namespaces)
            if is_elem is not None:
                # Extract text from inline string
                text_elem = is_elem.find('.//t', namespaces)
                if text_elem is not None and text_elem.text:
                    return self._fix_encoding(text_elem.text)

            # Check for shared string reference (cell type 's')
            cell_type = cell_elem.get('t', '')
            if cell_type == 's':
                value_elem = cell_elem.find('v', namespaces)
                if value_elem is not None and value_elem.text:
                    try:
                        # The value is an index into the shared strings array
                        string_index = int(value_elem.text)
                        if shared_strings and 0 <= string_index < len(shared_strings):
                            return self._fix_encoding(shared_strings[string_index])
                        else:
                            # Shared strings not available or index out of range
                            # This is the bug - we're returning the index instead of handling it properly
                            self.log_debug(
                                f"Shared string not available for index {string_index}",
                                cell_type=cell_type,
                                available_shared_strings=len(shared_strings) if shared_strings else 0
                            )
                            # Fall through to return the raw index for now, but this should be fixed
                    except (ValueError, IndexError):
                        # Fall through to regular value processing
                        pass

            # Check for regular value element
            value_elem = cell_elem.find('v', namespaces)
            if value_elem is not None and value_elem.text:
                value_text = value_elem.text

                # Check if this might be a date value
                cell_type = cell_elem.get('t', '')
                if cell_type != 's' and self._is_likely_date(value_text):
                    # Try to convert Excel date number to readable date
                    date_value = self._convert_excel_date(value_text)
                    if date_value:
                        return date_value

                return value_text

            # No value found
            return ""

        except Exception as e:
            self.log_debug(f"Error getting cell value: {e}")
            return ""

    def _extract_shared_strings_from_file(self, xlsx: zipfile.ZipFile) -> List[str]:
        """
        Extract shared strings from xl/sharedStrings.xml file.

        Shared strings are used to optimize XLSX file size by storing
        repeated strings once and referencing them by index.

        Args:
            xlsx: Opened XLSX zipfile

        Returns:
            List of shared strings in order of appearance
        """
        shared_strings = []

        try:
            if SHARED_STRINGS_PATH not in xlsx.namelist():
                self.log_debug("No shared strings file found")
                return shared_strings

            shared_strings_data = xlsx.read(SHARED_STRINGS_PATH)
            root = ET.fromstring(shared_strings_data)

            # Extract all text elements from shared strings using direct namespace
            direct_namespace = f"{{{EXCEL_NAMESPACES['main']}}}"
            for si_elem in root.findall(f"{direct_namespace}si"):
                text_parts = []

                # Extract text from t elements (handle multiple t elements for rich text)
                for t_elem in si_elem.findall(f"{direct_namespace}t"):
                    if t_elem.text:
                        text_parts.append(t_elem.text)

                # Combine text parts and fix encoding
                if text_parts:
                    combined_text = ''.join(text_parts)
                    fixed_text = self._fix_encoding(combined_text)
                    shared_strings.append(fixed_text)

            self.log_debug(f"Extracted {len(shared_strings)} shared strings", shared_strings_count=len(shared_strings))

        except Exception as e:
            self.log_warning(f"Error extracting shared strings: {e}")

        return shared_strings

    def _extract_sheet_names(self, xlsx: zipfile.ZipFile) -> List[str]:
        """
        Extract sheet names from workbook.xml file.

        Args:
            xlsx: Opened XLSX zipfile

        Returns:
            List of sheet names in order
        """
        sheet_names = []

        try:
            if WORKBOOK_PATH not in xlsx.namelist():
                self.log_debug("No workbook.xml file found")
                return sheet_names

            workbook_data = xlsx.read(WORKBOOK_PATH)
            root = ET.fromstring(workbook_data)

            # Extract sheet names using main namespace
            for sheet_elem in root.findall('.//sheet', {None: EXCEL_NAMESPACES['main']}):
                sheet_name = sheet_elem.get('name', f'Sheet{len(sheet_names) + 1}')
                sheet_names.append(sheet_name)

            self.log_debug(f"Extracted {len(sheet_names)} sheet names", sheet_count=len(sheet_names), sheet_names=sheet_names)

        except Exception as e:
            self.log_warning(f"Error extracting sheet names: {e}")

        return sheet_names

    def _fix_encoding(self, text: str) -> str:
        """
        Fix encoding issues in extracted text.

        Args:
            text: Raw text from XML

        Returns:
            Text with proper encoding
        """
        if not text:
            return ""

        try:
            # Try to ensure proper UTF-8 encoding
            if isinstance(text, bytes):
                return text.decode('utf-8')

            # If it's already a string, ensure it's proper UTF-8
            return text.encode('utf-8', errors='ignore').decode('utf-8')

        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            self.log_debug(f"Encoding issue: {e}, trying fallback", encoding_error=str(e))

            # Fallback: try to encode/decode with error handling
            try:
                return text.encode('ascii', errors='ignore').decode('ascii')
            except:
                # Last resort: return a safe representation
                return repr(text)

    def _is_likely_date(self, value: str) -> bool:
        """
        Determine if a cell value might be an Excel date.

        Uses conservative heuristics to avoid misidentifying regular numbers as dates.
        Checks both business date ranges (2000-2050) and historical ranges (1990-1999).

        Args:
            value: Cell value as string

        Returns:
            True if likely an Excel date value
        """
        try:
            num_value = float(value)

            # Check business date range: 2000-01-01 to 2050-12-31
            if BUSINESS_DATE_START <= num_value <= BUSINESS_DATE_END:
                return True

            # Check historical date range: 1990-01-01 to 1999-12-31
            if HISTORICAL_DATE_START <= num_value <= HISTORICAL_DATE_END:
                return True

        except ValueError:
            # Not a number, so not an Excel date
            pass

        return False

    def _convert_excel_date(self, excel_date: str) -> Optional[str]:
        """
        Convert Excel date number to readable date string.

        Handles Excel's leap year bug where 1900 is incorrectly treated as a leap year.
        The bug affects dates from March 1, 1900 onwards.

        Args:
            excel_date: Excel date number as string

        Returns:
            Formatted date string (YYYY-MM-DD) or None if conversion fails
        """
        try:
            date_num = float(excel_date)

            if date_num < 1:
                return None

            # Handle Excel's leap year bug
            # Dates before the bug (before 1900-03-01) use different epoch
            if date_num >= EXCEL_LEAP_YEAR_BUG_DAY:
                excel_epoch = EXCEL_EPOCH
            else:
                excel_epoch = datetime(1899, 12, 31)

            # Calculate the actual date
            delta_days = timedelta(days=date_num)
            actual_date = excel_epoch + delta_days

            return actual_date.strftime("%Y-%m-%d")

        except (ValueError, OverflowError) as e:
            self.log_debug(f"Could not convert Excel date '{excel_date}': {e}", excel_date=excel_date, error_type=type(e).__name__)
            return None

    def _detect_content_type(self, text: str, cell_count: int) -> str:
        """
        Detect content type based on text patterns and structure.

        Args:
            text: Row text content
            cell_count: Number of cells in the row

        Returns:
            Content type identifier
        """
        text = text.strip()

        # If it has multiple cells with tabs, it's likely table content
        if cell_count > 1 and '\t' in text:
            return ContentType.TABLE

        # Header detection (short text, might be title)
        if len(text) < 50 and (
            text.isupper() or
            text.endswith(':') or
            any(text.startswith(prefix) for prefix in ['Title', 'Name', 'Date', 'Summary', 'Total'])
        ):
            return ContentType.TEXT

        # Default to text
        return ContentType.TEXT

    def _estimate_row_coordinates(
        self,
        row_num: int,
        total_rows: int,
        cell_count: int
    ) -> BBox:
        """
        Estimate coordinates for a row based on its position.

        Args:
            row_num: Row number in worksheet
            total_rows: Total number of rows
            cell_count: Number of cells in the row

        Returns:
            Estimated bounding box
        """
        # Estimate vertical position (y) based on row order
        y_pos = (row_num / max(total_rows, 1)) * 0.9 + 0.05  # 5% to 95%

        # Estimate height based on content
        if cell_count <= 3:
            height = 0.02  # Single row
        elif cell_count <= 10:
            height = 0.03  # Standard row
        else:
            height = 0.05  # Wide row

        # Standard width and position for table content
        x_pos = 0.05  # 5% margin
        width = 0.9   # 90% of page width

        return BBox(x=x_pos, y=y_pos, w=width, h=height)

    def _create_table_chunks(
        self,
        rows_data: Dict[int, List[CellData]],
        sheet_num: int,
        sheet_name: str,
        document_metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Create row-level table chunks for contiguous data ranges.
        Only generates row-level chunks for better RAG granularity.
        Supports header injection via document metadata.

        Args:
            rows_data: Dictionary mapping row numbers to cell data
            sheet_num: Worksheet number
            sheet_name: Worksheet name
            document_metadata: Document metadata

        Returns:
            List of table DocumentChunk objects (row-level only)
        """
        table_chunks = []

        try:
            # Extract header injection configuration
            header_injection = document_metadata.get("header_injection", {})
            injected_headers = None
            header_row_num = None

            # Process header injection
            header_injection_type = header_injection.get("type")

            # Get effective headers for this specific sheet
            injected_headers, header_row_num = self._get_effective_headers_for_sheet(
                header_injection, rows_data, sheet_num, sheet_name
            )

            # Detect separate tables based on empty rows and structural changes
            table_groups = self._detect_table_groups(rows_data)

            for table_start, table_end, table_rows in table_groups:
                # Generate a unique doc_id for this table group
                table_doc_id = generate_doc_id()

                # Determine headers to use
                effective_headers = injected_headers
                if effective_headers is None:
                    # Use auto-detection: first row as header
                    first_row = table_rows[0] if table_rows else []
                    first_row_sorted = sorted(first_row, key=lambda c: c.col)
                    effective_headers = [cell.value for cell in first_row_sorted]

                # Auto-detect header row if not using injected headers
                is_header_row = injected_headers is None and self._is_likely_header_row(table_rows[0] if table_rows else [])

                # Estimate table coordinates for row positioning
                y_min = (table_start / max(len(rows_data), 1)) * 0.9 + 0.05
                y_max = (table_end / max(len(rows_data), 1)) * 0.9 + 0.05
                height = y_max - y_min + 0.05  # Add some padding
                row_height = height / len(table_rows)

                # Create row-level chunks only (skip full table chunk)
                for row_idx, row_cells in enumerate(table_rows):
                    actual_row_num = table_start + row_idx

                    # For header injection, skip the header row if it's in the table data
                    if header_row_num is not None and actual_row_num == header_row_num:
                        self.log_debug(f"Skipping header row from chunk generation", header_row=actual_row_num)
                        continue

                    # Ensure row has same column count as headers, fill missing with NULL
                    expected_col_count = len(effective_headers)
                    padded_row_cells = self._pad_row_to_match_columns(row_cells, expected_col_count)

                    # Format row text
                    row_text = self._format_table_text([padded_row_cells], actual_row_num, actual_row_num, is_row_level=True)

                    # Note: Headers are stored in metadata, not added to text to avoid duplication
                    # The headers are accessible via chunk.metadata['headers']

                    # Calculate row-level coordinates (approximate)
                    row_y = y_min + (row_idx * row_height)

                    # Create metadata for the row
                    row_metadata = {
                        **document_metadata,
                        "sheet_name": sheet_name,
                        "sheet_number": sheet_num,
                        "table_type": "structured_row",
                        "row_count": 1,
                        "column_count": expected_col_count,
                        "table_start_row": actual_row_num,
                        "table_end_row": actual_row_num,
                        "parent_table_doc_id": table_doc_id,
                        "has_header": is_header_row and row_idx == 0,  # Mark header row for auto-detection
                        "extraction_method": f"xlsx_stdlib|row={actual_row_num}",
                        "headers": effective_headers if injected_headers is not None else None,  # Store injected headers
                        "header_injection_type": header_injection.get("type") if header_injection else None
                    }

                    # Remove header_injection from row metadata to avoid duplication
                    row_metadata.pop("header_injection", None)

                    row_chunk = DocumentChunk(
                        doc_id=table_doc_id,  # Same doc_id to group rows from same table
                        page=sheet_num,
                        x=0.05,  # Left margin
                        y=row_y,
                        w=0.9,   # Most of page width
                        h=row_height,
                        type=ContentType.TABLE,
                        text=row_text,
                        tokens=estimate_tokens(row_text),
                        metadata=row_metadata
                    )

                    table_chunks.append(row_chunk)

                self.log_debug(f"Created row-level chunks for worksheet", sheet_num=sheet_num, sheet_name=sheet_name,
                        table_start=table_start, table_end=table_end, row_chunks_count=len(table_rows))

        except Exception as e:
            self.log_warning(f"Error creating table chunks: {e}", sheet_num=sheet_num, sheet_name=sheet_name)

        return table_chunks

    def _pad_row_to_match_columns(self, row_cells: List[CellData], expected_count: int) -> List[CellData]:
        """
        Pad row cells to match expected column count by adding NULL cells.

        Args:
            row_cells: List of cell data in the row
            expected_count: Expected number of columns

        Returns:
            Padded list of cell data
        """
        if len(row_cells) >= expected_count:
            return row_cells[:expected_count]  # Trim if too long

        # Pad with NULL cells
        padded_cells = row_cells.copy()
        current_max_col = max((cell.col for cell in row_cells), default=0)

        for i in range(len(row_cells), expected_count):
            # Create NULL cell for missing columns
            null_cell = CellData(
                row=row_cells[0].row if row_cells else 1,
                col=current_max_col + i + 1,
                value="NULL",
                cell_type="string"
            )
            padded_cells.append(null_cell)

        return padded_cells

    def _detect_table_groups(
        self,
        rows_data: Dict[int, List[CellData]]
    ) -> List[Tuple[int, int, List[List[CellData]]]]:
        """
        Detect separate table groups based on content patterns and structure.

        Uses a sliding window approach to identify contiguous groups of rows
        that form meaningful tables. Groups are detected based on:
        - Consecutive row numbers (allowing small gaps)
        - Consistent column structure
        - Sufficient row count for meaningful analysis

        Args:
            rows_data: Dictionary mapping row numbers to cell data

        Returns:
            List of tuples: (start_row, end_row, table_rows)
        """
        table_groups = []
        sorted_rows = sorted(rows_data.keys())

        if not sorted_rows:
            return table_groups

        # Prepare sorted row data for analysis
        sorted_row_data = []
        for row_num in sorted_rows:
            row_cells = rows_data[row_num]
            row_cells.sort(key=lambda c: c.col)  # Ensure column order
            sorted_row_data.append((row_num, row_cells))

        # Detect table groups using sliding window
        i = 0
        while i < len(sorted_row_data):
            row_num, row_cells = sorted_row_data[i]

            # Skip rows with insufficient data
            if len(row_cells) < 2:
                i += 1
                continue

            # Initialize potential table group
            current_table = [row_cells]
            current_start = row_num
            expected_cols = len(row_cells)
            prev_row = row_num
            i += 1

            # Extend table group while structure is consistent
            while i < len(sorted_row_data):
                next_row_num, next_row_cells = sorted_row_data[i]

                if self._should_continue_table_group(
                    next_row_num, next_row_cells, prev_row, expected_cols,
                    current_table, sorted_row_data, i
                ):
                    current_table.append(next_row_cells)
                    prev_row = next_row_num
                    i += 1
                else:
                    break

            # Add group if it meets criteria
            if self._is_valid_table_group(current_table):
                table_groups.append((current_start, prev_row, current_table))

        return table_groups

    def _should_continue_table_group(
        self,
        next_row_num: int,
        next_row_cells: List[CellData],
        prev_row: int,
        expected_cols: int,
        current_table: List[List[CellData]],
        all_rows: List[Tuple[int, List[CellData]]],
        current_index: int
    ) -> bool:
        """
        Determine if the next row should be included in the current table group.
        """
        # Check row proximity (allow small gaps)
        if next_row_num > prev_row + 3:
            return False

        # Check column count similarity (allow some variation)
        if abs(len(next_row_cells) - expected_cols) > 2:
            return False

        # Avoid single outlier rows
        if len(current_table) == 1:
            # Look ahead to see if next row matches
            if current_index + 1 < len(all_rows):
                future_row_cells = all_rows[current_index + 1][1]
                if abs(len(future_row_cells) - expected_cols) <= 2:
                    return False

        return True

    def _is_valid_table_group(self, table_rows: List[List[CellData]]) -> bool:
        """
        Determine if a table group is valid and should be kept.
        """
        if len(table_rows) >= MIN_TABLE_ROWS:
            return True

        # For smaller tables, check if they contain meaningful data
        if len(table_rows) == 2:
            return self._has_meaningful_data(table_rows)

        return False

    def _has_meaningful_data(self, table_rows: List[List[CellData]]) -> bool:
        """
        Check if table contains meaningful data (not just numbers or formulas).

        Uses a threshold-based approach to determine if the table has sufficient
        meaningful content to be worth processing.

        Args:
            table_rows: List of table rows

        Returns:
            True if contains meaningful data
        """
        if not table_rows:
            return False

        meaningful_cells = 0
        total_cells = 0

        # Keywords that indicate meaningful content
        meaningful_keywords = [
            '名称', '类型', '状态', '总计', '合计', '日期', '时间',
            'name', 'type', 'status', 'total', 'date', 'time'
        ]

        for row_cells in table_rows:
            for cell in row_cells:
                total_cells += 1
                cell_value = cell.value.strip() if cell.value else ""

                # Check for meaningful content indicators
                is_meaningful = (
                    # Text content with reasonable length
                    (cell.cell_type == 'string' and len(cell_value) > 1) or
                    # Numbers with reasonable length (exclude large Excel IDs)
                    (cell.cell_type == 'number' and len(cell_value) < 10) or
                    # Contains meaningful keywords
                    any(keyword in cell_value.lower() for keyword in meaningful_keywords)
                )

                if is_meaningful:
                    meaningful_cells += 1

        # Use constant threshold for meaningful data percentage
        return (meaningful_cells / max(total_cells, 1)) > MEANINGFUL_DATA_THRESHOLD

    def _is_likely_header_row(self, row_cells: List[CellData]) -> bool:
        """
        Determine if a row is likely a header row.

        Uses pattern matching to identify header characteristics such as:
        - Common header keywords
        - Non-numeric values
        - Short, descriptive text

        Args:
            row_cells: List of cell data in the row

        Returns:
            True if likely header row
        """
        if not row_cells:
            return False

        header_indicators = 0
        total_cells = len(row_cells)

        # Keywords commonly found in headers
        header_keywords = [
            'name', 'date', 'time', 'id', 'code', 'type', 'status',
            '总计', '合计', '名称', '日期', '时间', '编号', '类型', '状态'
        ]

        for cell in row_cells:
            cell_value = cell.value.strip().lower() if cell.value else ""

            # Check for header keywords
            if any(keyword in cell_value for keyword in header_keywords):
                header_indicators += 1

            # Non-numeric values are more likely headers
            if cell.cell_type != 'number' and cell_value:
                header_indicators += 1

        # Use constant threshold for header detection
        return (header_indicators / max(total_cells, 1)) > HEADER_INDICATOR_THRESHOLD

    def _format_table_text(
        self,
        table_rows: List[List[CellData]],
        start_row: int,
        end_row: int,
        is_row_level: bool = False
    ) -> str:
        """
        Format table data into clean, parsable text format.
        Optimized for RAG consumption and downstream processing.

        Args:
            table_rows: List of rows, each containing cell data
            start_row: Starting row number
            end_row: Ending row number
            is_row_level: Whether this is a row-level chunk (affects header format)

        Returns:
            Clean formatted table text
        """
        if not table_rows:
            return ""

        # Convert cell data to values, filtering out problematic content
        table_values = []
        for row_cells in table_rows:
            row_values = []
            for cell in row_cells:
                cell_value = cell.value if cell.value else ""
                # Skip problematic Excel formulas and IDs
                if (
                    not cell_value.startswith("=DISPIMG") and
                    not cell_value.startswith("ID_") and
                    len(cell_value) < 50  # Skip very long strings
                ):
                    # Fix broken text: merge broken numbers and Chinese names
                    fixed_value = self._fix_broken_text(cell_value)
                    row_values.append(fixed_value)
            table_values.append(row_values)

        if not table_values or not any(table_values):
            return ""

        # Build clean table format without decoration
        lines = []

        # Add appropriate header based on chunk type
        if is_row_level:
            # Row-level format: use row=N instead of [HEADER]
            lines.append(f"row={start_row}")
        else:
            # Full table format: use [HEADER] for clarity
            lines.append(f"[HEADER] {start_row}-{end_row}")

        # Format each row with single pipe separator and no extra spacing
        for i, row in enumerate(table_values):
            if not row:  # Skip empty rows
                continue

            # Handle empty cells with NULL placeholder
            formatted_cells = []
            for j, cell_value in enumerate(row):
                # Use NULL for empty values
                cell_str = str(cell_value) if cell_value.strip() else "NULL"
                formatted_cells.append(cell_str)

            if formatted_cells:  # Only add if there are cells to display
                row_line = "|".join(formatted_cells)
                lines.append(row_line)

        return "\n".join(lines)

    def _fix_broken_text(self, text: str) -> str:
        """
        Fix broken text patterns like "8 .7", "黄 伟", dates, and product names split across lines.
        Implements enhanced regex patterns from Issue #6.

        Args:
            text: Original text that might be broken

        Returns:
            Fixed text with merged broken parts
        """
        if not text or not isinstance(text, str):
            return text

        import re

        # Fix decimal numbers split with spaces: "8 .7" -> "8.7"
        text = re.sub(r'(\d+)\s+\.\s*(\d+)', r'\1.\2', text)

        # Fix Chinese names with unwanted spaces: "黄 伟" -> "黄伟"
        # Merge consecutive Chinese characters separated by spaces
        text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)

        # Fix cross-line broken dates: "2024-05\n15" -> "2024-05-15"
        text = re.sub(r'(\d{4}-\d{2})\s*\n\s*(\d{2})', r'\1-\2', text)

        # Fix cross-line broken month dates: "5月\n15日" -> "5月15日"
        text = re.sub(r'(\d{1,2}月)\s*\n\s*(\d{1,2}日)', r'\1\2', text)

        # Fix cross-line broken Chinese words/product names: "产品\n名称" -> "产品名称"
        text = re.sub(r'([\u4e00-\u9fa5])\s*\n\s*([\u4e00-\u9fa5])', r'\1\2', text)

        # Fix cross-line broken Chinese phrases (3+ characters): "高级\n产品经理" -> "高级产品经理"
        text = re.sub(r'([\u4e00-\u9fa5]{2,})\s*\n\s*([\u4e00-\u9fa5]{2,})', r'\1\2', text)

        # Remove spaces between Chinese characters and English letters/numbers when appropriate
        text = re.sub(r'([\u4e00-\u9fff])\s+([a-zA-Z0-9])', r'\1\2', text)
        text = re.sub(r'([a-zA-Z0-9])\s+([\u4e00-\u9fff])', r'\1\2', text)

        # Remove excessive whitespace (multiple spaces -> single space)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _extract_images(
        self,
        xlsx: zipfile.ZipFile,
        document_metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Extract embedded images from XLSX file.

        Args:
            xlsx: Opened XLSX zipfile
            document_metadata: Document metadata to include

        Returns:
            List of DocumentChunk objects representing images
        """
        image_chunks = []

        try:
            # Check for media folder with images
            media_files = [f for f in xlsx.namelist() if f.startswith('xl/media/')]
            self.log_debug(f"Found media files", media_files_count=len(media_files), media_files=media_files[:5])

            # Sort media files to maintain order
            media_files.sort()

            # Extract drawing relationships to map images to worksheets
            drawing_rels = self._extract_drawing_relationships(xlsx)

            for media_path in media_files:
                try:
                    # Extract image data
                    image_data = xlsx.read(media_path)

                    # Skip empty files
                    if not image_data:
                        continue

                    # Determine image format from file extension
                    filename = media_path.split('/')[-1]
                    image_format = 'unknown'
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                        image_format = filename.split('.')[-1].lower()

                    # Create binary data (base64 encoded)
                    binary_data = base64.b64encode(image_data).decode('utf-8')

                    # Estimate coordinates for images
                    image_index = len(image_chunks)
                    y_pos = 0.1 + (image_index * 0.15)  # Spread images vertically
                    if y_pos > 0.8:  # Reset if too far down
                        y_pos = 0.1 + ((image_index % 5) * 0.15)

                    # Estimate size based on image data length
                    data_size = len(image_data)
                    if data_size < 50000:  # Small image
                        width, height = 0.2, 0.1
                    elif data_size < 200000:  # Medium image
                        width, height = 0.3, 0.2
                    else:  # Large image
                        width, height = 0.4, 0.3

                    # Find associated worksheet if possible
                    worksheet_num = 1  # Default to first worksheet
                    for drawing_path, rel_info in drawing_rels.items():
                        if media_path in rel_info.get('image_targets', []):
                            worksheet_num = rel_info.get('worksheet_num', 1)
                            break

                    # Create image chunk
                    chunk = DocumentChunk(
                        doc_id=generate_doc_id(),
                        page=worksheet_num,
                        x=0.1,  # Left margin
                        y=y_pos,
                        w=width,
                        h=height,
                        type=ContentType.IMAGE,
                        text=None,
                        tokens=None,
                        binary_data=binary_data,
                        metadata={
                            **document_metadata,
                            "image_format": image_format,
                            "image_size_bytes": len(image_data),
                            "original_path": media_path,
                            "content_type": "embedded_image",
                            "extraction_method": "xlsx_stdlib|image"
                        }
                    )
                    image_chunks.append(chunk)

                except Exception as img_error:
                    self.log_debug(f"Error extracting image", media_path=media_path, error=str(img_error))
                    continue

            self.log_debug(f"Extracted images from XLSX", images_count=len(image_chunks))

        except Exception as e:
            self.log_debug(f"Error extracting images from XLSX", error=str(e))

        return image_chunks

    def _extract_charts(
        self,
        xlsx: zipfile.ZipFile,
        document_metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Extract chart information from XLSX file.

        Args:
            xlsx: Opened XLSX zipfile
            document_metadata: Document metadata to include

        Returns:
            List of DocumentChunk objects representing charts
        """
        chart_chunks = []

        try:
            # Look for chart files
            chart_files = [f for f in xlsx.namelist() if f.startswith('xl/charts/') and f.endswith('.xml')]
            self.log_debug(f"Found chart files", chart_files_count=len(chart_files), chart_files=chart_files[:3])

            for chart_index, chart_file in enumerate(chart_files):
                try:
                    # Read chart XML
                    chart_data = xlsx.read(chart_file)
                    root = ET.fromstring(chart_data)

                    # Extract basic chart information
                    chart_info = self._parse_chart_xml(root)

                    # Estimate coordinates for charts
                    y_pos = 0.2 + (chart_index * 0.25)  # Spread charts vertically
                    if y_pos > 0.8:  # Reset if too far down
                        y_pos = 0.2 + ((chart_index % 3) * 0.25)

                    # Format chart information in standardized key=value format
                    chart_title = chart_info.get('title', f'Chart {chart_index + 1}')
                    chart_type = chart_info.get('chart_type', 'unknown')
                    series_count = chart_info.get('series_count', 0)
                    source_file = document_metadata.get('file_name', 'unknown')

                    # Create standardized chart description in key=value format
                    chart_parts = [
                        f"chart_id={chart_index + 1}",
                        f"type={chart_type}",
                        f"series_count={series_count}",
                        f"file={source_file}",
                        f"chart_file={chart_file.split('/')[-1]}"
                    ]
                    if chart_title != f'Chart {chart_index + 1}':
                        chart_parts.append(f"title={chart_title}")

                    chart_text = "|".join(chart_parts)

                    chunk = DocumentChunk(
                        doc_id=generate_doc_id(),
                        page=1,  # Charts don't have specific sheet assignment in this simple version
                        x=0.1,  # Left margin
                        y=y_pos,
                        w=0.6,  # Charts are typically wider
                        h=0.25,  # Charts are typically taller
                        type=ContentType.TEXT,  # Charts are represented as text descriptions
                        text=chart_text,
                        tokens=estimate_tokens(chart_text),
                        metadata={
                            **document_metadata,
                            "content_type": "chart",
                            "chart_title": chart_title,
                            "chart_type": chart_type,
                            "series_count": series_count,
                            "source_file": source_file,
                            "chart_index": chart_index + 1,
                            "chart_file": chart_file,
                            "extraction_method": "xlsx_stdlib|chart"
                        }
                    )
                    chart_chunks.append(chunk)

                except Exception as chart_error:
                    self.log_debug(f"Error extracting chart", chart_file=chart_file, error=str(chart_error))
                    continue

            self.log_debug(f"Extracted charts from XLSX", charts_count=len(chart_chunks))

        except Exception as e:
            self.log_debug(f"Error extracting charts from XLSX", error=str(e))

        return chart_chunks

    def _extract_drawing_relationships(
        self,
        xlsx: zipfile.ZipFile
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract drawing relationships to map images to worksheets.

        Args:
            xlsx: Opened XLSX zipfile

        Returns:
            Dictionary mapping drawing files to relationship info
        """
        drawing_rels = {}

        try:
            # Look for drawing relationship files
            rel_files = [f for f in xlsx.namelist() if f.endswith('.rels') and 'drawings' in f]

            for rel_file in rel_files:
                try:
                    rel_data = xlsx.read(rel_file)
                    root = ET.fromstring(rel_data)

                    # Parse relationships
                    relationships = {}
                    for child in root:
                        target = child.get('Target', '')
                        rel_type = child.get('Type', '')
                        rel_id = child.get('Id', '')

                        if 'image' in rel_type.lower():
                            relationships.setdefault('image_targets', []).append(target)

                    drawing_rels[rel_file] = {
                        'relationships': relationships,
                        'worksheet_num': 1  # Would need more complex logic to determine actual worksheet
                    }

                except Exception as rel_error:
                    self.log_debug(f"Error parsing relationships", rel_file=rel_file, error=str(rel_error))
                    continue

        except Exception as e:
            self.log_debug(f"Error extracting drawing relationships", error=str(e))

        return drawing_rels

    def _parse_chart_xml(self, root: ET.Element) -> Dict[str, Any]:
        """
        Parse chart XML to extract basic information.

        Args:
            root: Chart XML root element

        Returns:
            Dictionary with chart information
        """
        chart_info = {}

        try:
            # Define namespaces
            namespaces = {
                'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
            }

            # Try to find chart title
            title_elem = root.find('.//c:title/c:tx/c:rich/a:p/a:r/a:t', namespaces)
            if title_elem is not None and title_elem.text:
                chart_info['title'] = title_elem.text

            # Try to determine chart type
            if root.find('.//c:barChart', namespaces) is not None:
                chart_info['chart_type'] = 'bar'
            elif root.find('.//c:lineChart', namespaces) is not None:
                chart_info['chart_type'] = 'line'
            elif root.find('.//c:pieChart', namespaces) is not None:
                chart_info['chart_type'] = 'pie'
            elif root.find('.//c:scatterChart', namespaces) is not None:
                chart_info['chart_type'] = 'scatter'
            elif root.find('.//c:areaChart', namespaces) is not None:
                chart_info['chart_type'] = 'area'

            # Count data series
            series_elements = root.findall('.//c:ser', namespaces)
            chart_info['series_count'] = len(series_elements)

        except Exception as e:
            self.log_debug(f"Error parsing chart XML", error=str(e))

        return chart_info

    def serialize_as_rag_jsonl(
        self,
        file_path: Path | str,
        *,
        enable_backward_compatible: Optional[bool] = None,
        max_mem_mb: Optional[int] = None,
        header_row: Optional[Union[int, List[int]]] = None,
        custom_headers: Optional[Union[List[str], List[List[str]]]] = None
    ) -> Iterator[str]:
        """
        Serialize XLSX document into RAG-optimized JSONL format.

        This method converts pipe-delimited table strings into flattened JSON key-value pairs
        optimized for Retrieval-Augmented Generation applications.

        Args:
            file_path: Path to XLSX file
            enable_backward_compatible: Whether to maintain backward compatible pipe format for non-tables
            max_mem_mb: Memory limit (not implemented for stdlib version)
            header_row: Optional row number to use as header (1-based)
            custom_headers: Optional list of custom headers to inject

        Yields:
            RAG-optimized JSONL strings, one per line
        """
        # Use internal config if parameters not provided
        effective_max_mem = max_mem_mb if max_mem_mb is not None else self._max_mem_mb
        effective_header_row = header_row if header_row is not None else self._header_row
        effective_custom_headers = custom_headers if custom_headers is not None else self._custom_headers
        effective_backward_compatible = (
            enable_backward_compatible if enable_backward_compatible is not None
            else self._enable_backward_compatible
        )

        self.log_info(f"Processing XLSX with RAG format", file_path=str(file_path))

        # Collect all chunks first to enable table parsing
        all_chunks = list(self.serialize(
            file_path,
            max_mem_mb=effective_max_mem,
            header_row=effective_header_row,
            custom_headers=effective_custom_headers
        ))

        # Use table parser to extract headers and structure
        table_parser = TableHeaderParser()
        for chunk in all_chunks:
            table_parser.add_chunk(chunk)

        # Parse all tables to get header information
        table_results = table_parser.parse_all_tables()

        # Format chunks as RAG JSONL
        rag_jsonl_lines = format_chunks_as_rag_jsonl(
            all_chunks,
            enable_backward_compatible=effective_backward_compatible,
            table_parser=table_parser
        )

        # Yield each JSONL line
        for line in rag_jsonl_lines:
            yield line

    def iterate_chunks(
        self,
        file_path: Path | str,
        *,
        rag_format: bool = False,
        enable_backward_compatible: Optional[bool] = None,
        max_mem_mb: Optional[int] = None,
        header_row: Optional[Union[int, List[int]]] = None,
        custom_headers: Optional[Union[List[str], List[List[str]]]] = None
    ) -> Iterator[Union[DocumentChunk, str]]:
        """
        Unified iterator method that can yield either DocumentChunks or RAG JSONL strings.

        This is the preferred method for iterating through document content,
        supporting both internal configuration and parameter override.

        Args:
            file_path: Path to XLSX file
            rag_format: If True, yield RAG JSONL strings; if False, yield DocumentChunks
            enable_backward_compatible: RAG format compatibility setting
            max_mem_mb: Memory limit setting
            header_row: Header row override
            custom_headers: Custom headers override

        Yields:
            DocumentChunk objects or JSONL strings depending on rag_format
        """
        if rag_format:
            yield from self.serialize_as_rag_jsonl(
                file_path,
                enable_backward_compatible=enable_backward_compatible,
                max_mem_mb=max_mem_mb,
                header_row=header_row,
                custom_headers=custom_headers
            )
        else:
            yield from self.serialize(
                file_path,
                max_mem_mb=max_mem_mb,
                header_row=header_row,
                custom_headers=custom_headers
            )

    def _get_effective_headers_for_sheet(
        self,
        header_injection: Dict[str, Any],
        rows_data: Dict[int, List[CellData]],
        sheet_num: int,
        sheet_name: str
    ) -> tuple[Optional[List[str]], Optional[int]]:
        """
        Get effective headers for a specific sheet based on header injection configuration.

        Args:
            header_injection: Header injection configuration metadata
            rows_data: Sheet row data mapping
            sheet_num: Sheet number (1-based)
            sheet_name: Sheet name

        Returns:
            Tuple of (effective_headers_list, header_row_number_if_extracted)
        """
        header_injection_type = header_injection.get("type")
        injected_headers = None
        header_row_num = None

        if header_injection_type == "custom":
            # Global custom headers (same for all sheets)
            injected_headers = header_injection.get("headers", [])
            self.log_debug(
                f"Using global custom headers",
                sheet_num=sheet_num,
                sheet_name=sheet_name,
                headers_count=len(injected_headers),
                headers_preview=injected_headers[:3] if injected_headers else []
            )

        elif header_injection_type == "row_based":
            # Global header row (same for all sheets)
            global_header_row = header_injection.get("header_row")
            self.log_debug(
                f"Using global header row",
                sheet_num=sheet_num,
                sheet_name=sheet_name,
                header_row=global_header_row
            )
            if global_header_row in rows_data:
                header_row_num = global_header_row
                header_cells = rows_data[header_row_num]
                header_cells.sort(key=lambda c: c.col)
                injected_headers = [cell.value for cell in header_cells]
                self.log_debug(
                    f"Extracted headers from global row",
                    sheet_num=sheet_num,
                    header_row=header_row_num,
                    headers_count=len(injected_headers),
                    headers_preview=injected_headers[:3] if injected_headers else []
                )

        elif header_injection_type == "multi_sheet_custom":
            # Per-sheet custom headers
            headers_list = header_injection.get("headers", [])
            if (sheet_num <= len(headers_list) and
                headers_list[sheet_num - 1] is not None and
                headers_list[sheet_num - 1]):
                injected_headers = headers_list[sheet_num - 1]
                self.log_debug(
                    f"Using sheet-specific custom headers",
                    sheet_num=sheet_num,
                    sheet_name=sheet_name,
                    headers_count=len(injected_headers),
                    headers_preview=injected_headers[:3] if injected_headers else []
                )
            else:
                self.log_debug(
                    f"No custom headers for sheet",
                    sheet_num=sheet_num,
                    sheet_name=sheet_name,
                    headers_available=len(headers_list),
                    sheet_index=sheet_num - 1
                )

        elif header_injection_type == "multi_sheet_row_based":
            # Per-sheet header rows
            header_rows = header_injection.get("header_rows", [])
            if sheet_num <= len(header_rows) and header_rows[sheet_num - 1]:
                sheet_header_row = header_rows[sheet_num - 1]
                self.log_debug(
                    f"Using sheet-specific header row",
                    sheet_num=sheet_num,
                    sheet_name=sheet_name,
                    header_row=sheet_header_row
                )
                if sheet_header_row in rows_data:
                    header_row_num = sheet_header_row
                    header_cells = rows_data[header_row_num]
                    header_cells.sort(key=lambda c: c.col)
                    injected_headers = [cell.value for cell in header_cells]
                    self.log_debug(
                        f"Extracted headers from sheet-specific row",
                        sheet_num=sheet_num,
                        sheet_name=sheet_name,
                        header_row=header_row_num,
                        headers_count=len(injected_headers),
                        headers_preview=injected_headers[:3] if injected_headers else []
                    )

        return injected_headers, header_row_num

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".xlsx", ".xls", ".xlsm"]