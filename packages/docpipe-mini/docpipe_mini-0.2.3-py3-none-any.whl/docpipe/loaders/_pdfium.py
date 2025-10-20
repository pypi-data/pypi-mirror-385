"""
Zero-dependency PDF serializer using pypdfium2.

BSD license fallback for PDF processing when PyMuPDF is not available.
Focus: coordinate extraction + text serialization for AI consumption.

Enhanced with LoggingMixin and SerializerMixin for structured logging,
context management, and unified configuration.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator, Optional, Dict, Any, Union

try:
    import pypdfium2  # BSD license
    PYPDFIUM2_AVAILABLE = True
except ImportError:
    PYPDFIUM2_AVAILABLE = False

from .._types import DocumentChunk, BBox, ContentType, estimate_tokens, generate_doc_id
from .._protocols import DocumentSerializer, LoggingMixin, SerializerMixin

# Constants for PDF processing
MIN_CHUNK_LENGTH = 10
COORDINATE_NORMALIZATION_MARGIN = 72  # 1 inch in points
MIN_IMAGE_RELATIVE_SIZE = 0.01  # 1% of page area
POSITION_ROUNDING_PRECISION = 1
COORDINATE_PRECISION = 3

# Content detection thresholds
MAX_HEADING_LENGTH = 100
MAX_PARAGRAPH_HEIGHT_FACTOR = 0.1
MIN_TABLE_LINES = 3
TEXT_BASED_HEIGHT_FACTOR = 0.05

# Table parsing delimiters
TABLE_DELIMITERS = ['|', '\t']
CELL_CLEANUP_EMPTY = ""

# PDF object types (as defined in PDF spec)
PDF_OBJ_TEXT = 1
PDF_OBJ_IMAGE = 2
PDF_OBJ_PATH = 3
PDF_OBJ_SHADING = 4
PDF_OBJ_FORM = 5


class PdfiumSerializer(LoggingMixin, SerializerMixin, DocumentSerializer):
    """
    PDF serializer using pypdfium2 (BSD license).

    Extracts text with coordinates using pypdfium2's native text extraction.
    Provides good performance for most PDFs without AGPL dependencies.

    Enhanced with structured logging, context management, and unified configuration.
    """

    def __init__(self, *, min_chunk_length: int = MIN_CHUNK_LENGTH):
        """
        Initialize the PDF serializer.

        Args:
            min_chunk_length: Minimum text length for a chunk
        """
        super().__init__()  # Initialize both mixin attributes

        if not PYPDFIUM2_AVAILABLE:
            self.log_error("pypdfium2 not available", error="ImportError")
            raise ImportError(
                "pypdfium2 is required for PDF processing. "
                "Install with: pip install pypdfium2"
            )

        self.min_chunk_length = min_chunk_length
        self.log_debug("PDF serializer initialized", min_chunk_length=min_chunk_length)

    def can_serialize(self, file_path: Path | str) -> bool:
        """Check if file is a PDF."""
        # Convert to Path object for consistent handling
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        return file_path.suffix.lower() == '.pdf'

    def serialize(
        self,
        file_path: Path | str,
        *,
        max_mem_mb: Optional[int] = None
    ) -> Iterator[DocumentChunk]:
        """
        Serialize PDF document into coordinate-aware chunks.

        Args:
            file_path: Path to PDF file
            max_mem_mb: Memory limit (not implemented for pypdfium2)

        Yields:
            DocumentChunk objects with text and coordinates
        """
        # Normalize file path
        file_path = self._normalize_file_path(file_path)

        # Resolve configuration
        config = self._resolve_serialization_config(max_mem_mb, None, None)

        self.log_operation_start(
            "PDF serialization",
            file_path=str(file_path),
            file_size=file_path.stat().st_size if file_path.exists() else 0
        )

        try:
            with self.log_timing("PDF file processing"):
                pdf = pypdfium2.PdfDocument(file_path)
                try:
                    self._validate_pdf_structure(pdf)

                    # Prepare processing context
                    document_metadata = self._build_document_metadata(file_path, config)

                    # Process all pages
                    total_pages = len(pdf)
                    processed_chunks = 0

                    for page_num in range(total_pages):
                        with self.log_timing(f"page_{page_num + 1}_processing", page_num=page_num + 1):
                            page_chunks = list(self._process_page(
                                pdf[page_num], page_num + 1, document_metadata
                            ))

                            # Set doc_id for all chunks from this page
                            page_doc_id = generate_doc_id()
                            for chunk in page_chunks:
                                chunk.doc_id = page_doc_id
                                yield chunk

                            processed_chunks += len(page_chunks)

                        # Log progress for large documents
                        if total_pages > 10:
                            self.log_progress(page_num + 1, total_pages, "Processing pages")
                finally:
                    # Explicitly close the PDF document
                    pdf.close()

                # Log final statistics
                self.log_processing_stats(
                    {
                        "total_pages": total_pages,
                        "total_chunks": processed_chunks,
                        "file_size_mb": file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0
                    },
                    file_path=str(file_path)
                )

            self.log_operation_success("PDF serialization", file_path=str(file_path))

        except Exception as e:
            self.log_operation_error("PDF serialization", e, file_path=str(file_path))
            raise

    def _extract_text_chunks(
        self,
        text_page,
        page_num: int,
        page_width: float,
        page_height: float,
        document_metadata: Dict[str, Any]
    ) -> list[DocumentChunk]:
        """
        Extract text chunks with improved coordinates from a PDF text page.

        Uses pypdfium2's text block extraction for better coordinate accuracy.

        Args:
            text_page: pypdfium2 text page object
            page_num: Page number (1-based)
            page_width: Page width in points
            page_height: Page height in points
            document_metadata: Document metadata to include

        Returns:
            List of DocumentChunk objects
        """
        chunks = []

        try:
            # Try to get text blocks first (better coordinates)
            text_blocks = []
            try:
                # pypdfium2 4+ supports get_text_blocks
                text_blocks = text_page.get_text_blocks()
                self.log_debug(
                    f"Extracted text blocks using native method",
                    page_num=page_num,
                    blocks_count=len(text_blocks)
                )
            except AttributeError:
                # Fallback to manual block detection
                self.log_debug("Using manual block extraction", page_num=page_num)
                text_blocks = self._extract_blocks_manually(text_page, page_width, page_height)

            # Process each text block
            for block_idx, block in enumerate(text_blocks):
                if isinstance(block, (list, tuple)) and len(block) >= 5:
                    # Format: (text, x1, y1, x2, y2, ...) - coordinates in points
                    text = str(block[0]) if block[0] else ""
                    if len(text.strip()) < self.min_chunk_length:
                        continue

                    x1, y1, x2, y2 = float(block[1]), float(block[2]), float(block[3]), float(block[4])

                    # Validate coordinates
                    if not (0 <= x1 < x2 <= page_width and 0 <= y1 < y2 <= page_height):
                        self.log_debug(
                            f"Skipping block with invalid coordinates",
                            page_num=page_num,
                            block_idx=block_idx,
                            coordinates=(x1, y1, x2, y2)
                        )
                        continue

                    # Normalize coordinates
                    norm_bbox = BBox.from_points(
                        x1, y1, x2, y2, page_width, page_height
                    )

                    # Detect content type
                    content_type = self._detect_content_type(text)

                    # Prepare metadata for tables
                    metadata = {**document_metadata}
                    if content_type == ContentType.TABLE:
                        # Try to parse table structure
                        try:
                            table_data = self._parse_table_structure(text.strip())
                            metadata.update({
                                "table_structure": table_data,
                                "extraction_method": "text_based"
                            })
                            self.log_debug(
                                f"Parsed table structure",
                                page_num=page_num,
                                rows=table_data.get("row_count", 0),
                                columns=table_data.get("max_columns", 0)
                            )
                        except Exception as table_error:
                            self.log_debug(
                                f"Could not parse table structure",
                                page_num=page_num,
                                block_idx=block_idx,
                                error=str(table_error)
                            )
                            metadata["parsing_error"] = str(table_error)

                    # Create chunk
                    chunk = DocumentChunk(
                        doc_id="",  # Will be set by serialize()
                        page=page_num,
                        x=norm_bbox.x,
                        y=norm_bbox.y,
                        w=norm_bbox.w,
                        h=norm_bbox.h,
                        type=content_type,
                        text=text.strip(),
                        tokens=estimate_tokens(text.strip()),
                        metadata=metadata
                    )
                    chunks.append(chunk)

                elif isinstance(block, str):
                    # Simple text without coordinates - estimate position
                    if len(block.strip()) < self.min_chunk_length:
                        continue

                    # Estimate position based on block order
                    estimated_bbox = BBox(
                        x=0.1,
                        y=0.1 + (block_idx * TEXT_BASED_HEIGHT_FACTOR),  # Stack vertically
                        w=0.8,
                        h=min(TEXT_BASED_HEIGHT_FACTOR, len(block) / 1000)  # Height based on length
                    )

                    chunk = DocumentChunk(
                        doc_id="",  # Will be set by serialize()
                        page=page_num,
                        x=estimated_bbox.x,
                        y=estimated_bbox.y,
                        w=estimated_bbox.w,
                        h=estimated_bbox.h,
                        type=ContentType.TEXT,
                        text=block.strip(),
                        tokens=estimate_tokens(block.strip()),
                        metadata=document_metadata
                    )
                    chunks.append(chunk)

        except Exception as e:
            self.log_warning(
                f"Error in advanced coordinate extraction",
                page_num=page_num,
                error=str(e)
            )

            # Ultimate fallback: full page text
            try:
                full_text = text_page.get_text_range()
                if full_text.strip():
                    # Split into reasonable chunks
                    paragraphs = full_text.split('\n\n')
                    for i, para in enumerate(paragraphs):
                        if len(para.strip()) < self.min_chunk_length:
                            continue

                        # Estimate position
                        y_pos = 0.1 + (i / len(paragraphs)) * 0.8
                        estimated_bbox = BBox(
                            x=0.1, y=y_pos, w=0.8,
                            h=min(MAX_PARAGRAPH_HEIGHT_FACTOR, len(para) / 500)
                        )

                        chunk = DocumentChunk(
                            doc_id="",  # Will be set by serialize()
                            page=page_num,
                            x=estimated_bbox.x,
                            y=estimated_bbox.y,
                            w=estimated_bbox.w,
                            h=estimated_bbox.h,
                            type=ContentType.TEXT,
                            text=para.strip(),
                            tokens=estimate_tokens(para.strip()),
                            metadata={**document_metadata, "extraction_method": "fallback"}
                        )
                        chunks.append(chunk)

            except Exception as fallback_error:
                self.log_error(
                    f"Failed to extract page text",
                    page_num=page_num,
                    error=str(fallback_error)
                )

        return chunks

    def _extract_blocks_manually(self, text_page, page_width: float, page_height: float) -> list:
        """
        Manually extract text blocks when get_text_blocks is not available.

        Args:
            text_page: pypdfium2 text page object
            page_width: Page width in points
            page_height: Page height in points

        Returns:
            List of text blocks with estimated coordinates
        """
        blocks = []
        try:
            # Get full text and split into paragraphs
            full_text = text_page.get_text_range()
            paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]

            self.log_debug(
                f"Manual block extraction",
                paragraphs_count=len(paragraphs),
                text_length=len(full_text)
            )

            # Estimate coordinates for each paragraph
            for i, paragraph in enumerate(paragraphs):
                # Simple vertical stacking estimation
                y_pos = 0.1 + (i / len(paragraphs)) * 0.8 if paragraphs else 0.5
                height = min(MAX_PARAGRAPH_HEIGHT_FACTOR, len(paragraph) / 1000)

                blocks.append((
                    paragraph,
                    COORDINATE_NORMALIZATION_MARGIN,  # x1 in points (1 inch)
                    y_pos * page_height,  # y1 in points
                    page_width - COORDINATE_NORMALIZATION_MARGIN,  # x2 in points
                    (y_pos + height) * page_height  # y2 in points
                ))

        except Exception as e:
            self.log_debug(
                f"Manual block extraction failed",
                error=str(e),
                page_width=page_width,
                page_height=page_height
            )

        return blocks

    def _detect_content_type(self, text: str) -> str:
        """
        Detect content type based on text patterns.

        Args:
            text: Text content

        Returns:
            Content type identifier
        """
        text = text.strip()

        # Heading detection
        if len(text) < MAX_HEADING_LENGTH and (
            text.isupper() or
            text.endswith(':') or
            any(text.startswith(prefix) for prefix in ['Chapter', 'Section', 'Part', 'Abstract'])
        ):
            return ContentType.TEXT

        # Table detection
        lines = text.split('\n')
        if len(lines) >= MIN_TABLE_LINES:
            # Check for consistent column patterns
            has_delimiters = any(any(delimiter in line for delimiter in TABLE_DELIMITERS) for line in lines[:5])
            has_pipes = any('|' in line for line in lines[:5])
            if (has_delimiters or has_pipes) and all(len(line.strip()) > 0 for line in lines[:3]):
                return ContentType.TABLE

        # List detection
        if any(text.startswith(prefix) for prefix in ['•', '-', '*', '1.', '2.', '3.']):
            return ContentType.TEXT

        return ContentType.TEXT

    def _extract_images(
        self,
        page,
        page_num: int,
        page_width: float,
        page_height: float,
        document_metadata: Dict[str, Any]
    ) -> list[DocumentChunk]:
        """
        Extract images from a PDF page.

        Args:
            page: pypdfium2 page object
            page_num: Page number (1-based)
            page_width: Page width in points
            page_height: Page height in points
            document_metadata: Document metadata to include

        Returns:
            List of DocumentChunk objects representing images
        """
        image_chunks = []

        try:
            # Get page objects and look for images
            page_objects = page.get_objects()
            self.log_debug(
                f"Processing page objects for images",
                page_num=page_num,
                objects_count=len(page_objects)
            )

            # Use a set to track unique image positions and avoid duplicates
            seen_positions = set()
            processed_images = 0

            for obj_idx, obj in enumerate(page_objects):
                try:
                    # Check if this is an image object
                    if hasattr(obj, 'type'):
                        obj_type = obj.type
                        if obj_type == PDF_OBJ_IMAGE:  # Image object
                            # Try to get image bounds
                            if hasattr(obj, 'get_pos'):
                                try:
                                    x, y, w, h = obj.get_pos()
                                    if w > 0 and h > 0:
                                        # Filter out very small images (likely icons or decorative elements)
                                        page_area = page_width * page_height
                                        image_area = w * h
                                        relative_size = image_area / page_area

                                        if relative_size > MIN_IMAGE_RELATIVE_SIZE:
                                            # Round coordinates to avoid near-duplicates
                                            pos_key = (
                                                round(x, POSITION_ROUNDING_PRECISION),
                                                round(y, POSITION_ROUNDING_PRECISION),
                                                round(w, POSITION_ROUNDING_PRECISION),
                                                round(h, POSITION_ROUNDING_PRECISION)
                                            )

                                            if pos_key not in seen_positions:
                                                seen_positions.add(pos_key)

                                                # Normalize coordinates
                                                norm_bbox = BBox(
                                                    x=x / page_width,
                                                    y=y / page_height,
                                                    w=w / page_width,
                                                    h=h / page_height
                                                )

                                                # Try to extract actual image data
                                                binary_data = None
                                                metadata = {
                                                    **document_metadata,
                                                    "source": "pypdfium2",
                                                    "format": "unknown",
                                                    "relative_size": relative_size
                                                }

                                                try:
                                                    # Try to get bitmap data from the image object
                                                    if hasattr(obj, 'get_bitmap'):
                                                        bitmap = obj.get_bitmap()
                                                        if bitmap:
                                                            # Convert bitmap to bytes
                                                            binary_data = bitmap.to_bytes()

                                                            # Try to determine image format
                                                            if hasattr(bitmap, 'get_width') and hasattr(bitmap, 'get_height'):
                                                                metadata.update({
                                                                    "width": bitmap.get_width(),
                                                                    "height": bitmap.get_height(),
                                                                    "format": "bitmap"
                                                                })

                                                            metadata["extraction_method"] = "bitmap"
                                                            processed_images += 1

                                                except Exception as bitmap_error:
                                                    self.log_debug(
                                                        f"Could not extract bitmap",
                                                        page_num=page_num,
                                                        obj_idx=obj_idx,
                                                        error=str(bitmap_error)
                                                    )
                                                    metadata["extraction_error"] = str(bitmap_error)

                                                # Create image chunk with binary data
                                                chunk = DocumentChunk(
                                                    doc_id="",  # Will be set by serialize()
                                                    page=page_num,
                                                    x=norm_bbox.x,
                                                    y=norm_bbox.y,
                                                    w=norm_bbox.w,
                                                    h=norm_bbox.h,
                                                    type=ContentType.IMAGE,
                                                    text=None,  # Pure image has no text
                                                    tokens=None,
                                                    binary_data=binary_data,
                                                    metadata=metadata
                                                )
                                                image_chunks.append(chunk)

                                except Exception as pos_error:
                                    self.log_debug(
                                        f"Could not get image position",
                                        page_num=page_num,
                                        obj_idx=obj_idx,
                                        error=str(pos_error)
                                    )

                except Exception as obj_error:
                    self.log_debug(
                        f"Error processing page object",
                        page_num=page_num,
                        obj_idx=obj_idx,
                        error=str(obj_error)
                    )
                    continue

            self.log_debug(
                f"Image extraction completed",
                page_num=page_num,
                images_processed=processed_images,
                total_chunks=len(image_chunks)
            )

        except Exception as e:
            self.log_debug(
                f"Error extracting images from page",
                page_num=page_num,
                error=str(e)
            )

        return image_chunks

    def _parse_table_structure(self, text: str) -> Dict[str, Any]:
        """
        Parse table structure from text content.

        Args:
            text: Table text content

        Returns:
            Dictionary with table structure information
        """
        lines = text.strip().split('\n')
        rows = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try different delimiters
            cells = []
            for delimiter in TABLE_DELIMITERS:
                if delimiter in line:
                    if delimiter == '|':
                        # Pipe-delimited table
                        cells = [cell.strip() for cell in line.split(delimiter) if cell.strip() != CELL_CLEANUP_EMPTY]
                    else:
                        # Tab-delimited table
                        cells = line.split(delimiter)
                    break

            # If no delimiters found, treat as simple table
            if not cells:
                cells = [line]

            if cells:
                rows.append({
                    "cells": cells,
                    "cell_count": len(cells)
                })

        return {
            "rows": rows,
            "row_count": len(rows),
            "has_header": len(rows) > 1,
            "max_columns": max([r["cell_count"] for r in rows]) if rows else 0
        }

    def _normalize_file_path(self, file_path: Path | str) -> Path:
        """Normalize file path to Path object."""
        return Path(file_path) if isinstance(file_path, str) else file_path

    def _resolve_serialization_config(
        self,
        max_mem_mb: Optional[int],
        header_row: Optional[int],
        custom_headers: Optional[list]
    ) -> Dict[str, Any]:
        """Resolve effective configuration from parameters and internal state."""
        effective_max_mem = max_mem_mb if max_mem_mb is not None else self._max_mem_mb
        # PDF doesn't use header injection, but we maintain the interface for consistency

        return {
            'max_mem_mb': effective_max_mem,
            'min_chunk_length': self.min_chunk_length
        }

    def _validate_pdf_structure(self, pdf: pypdfium2.PdfDocument) -> None:
        """Validate that the PDF document is properly structured."""
        if len(pdf) == 0:
            raise ValueError("PDF document has no pages")

    def _build_document_metadata(self, file_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build document metadata dictionary."""
        return {
            "source_file": str(file_path),
            "file_name": file_path.name,
            "file_extension": file_path.suffix,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "min_chunk_length": config['min_chunk_length'],
            "serializer": "pypdfium2"
        }

    def _process_page(
        self,
        page,
        page_num: int,
        document_metadata: Dict[str, Any]
    ) -> list[DocumentChunk]:
        """
        Process a single PDF page and extract all chunks.

        Args:
            page: pypdfium2 page object
            page_num: Page number (1-based)
            document_metadata: Document metadata to include

        Returns:
            List of DocumentChunk objects from this page
        """
        chunks = []

        try:
            # Get page dimensions
            page_width = page.get_width()
            page_height = page.get_height()

            self.log_debug(
                f"Processing page dimensions",
                page_num=page_num,
                width=page_width,
                height=page_height
            )

            # Extract text with coordinates
            text_page = page.get_textpage()
            try:
                text_chunks = self._extract_text_chunks(
                    text_page, page_num, page_width, page_height, document_metadata
                )
                chunks.extend(text_chunks)
            finally:
                text_page.close()

            # Extract images
            image_chunks = self._extract_images(
                page, page_num, page_width, page_height, document_metadata
            )
            chunks.extend(image_chunks)

            self.log_debug(
                f"Page processing completed",
                page_num=page_num,
                text_chunks=len(text_chunks),
                image_chunks=len(image_chunks),
                total_chunks=len(chunks)
            )

        except Exception as e:
            self.log_warning(
                f"Error processing page {page_num}",
                page_num=page_num,
                error=str(e)
            )

        return chunks

    def iterate_chunks(
        self,
        file_path: Path | str,
        *,
        rag_format: bool = False,
        enable_backward_compatible: Optional[bool] = None,
        max_mem_mb: Optional[int] = None,
        header_row: Optional[int] = None,
        custom_headers: Optional[list] = None
    ) -> Iterator[Union[DocumentChunk, str]]:
        """
        Unified iterator method that can yield either DocumentChunks or RAG JSONL strings.

        This is the preferred method for iterating through document content,
        supporting both internal configuration and parameter override.

        Args:
            file_path: Path to PDF file
            rag_format: If True, yield RAG JSONL strings; if False, yield DocumentChunks
            enable_backward_compatible: RAG format compatibility setting (not used for PDF)
            max_mem_mb: Memory limit setting
            header_row: Header row override (not used for PDF)
            custom_headers: Custom headers override (not used for PDF)

        Yields:
            DocumentChunk objects or JSONL strings depending on rag_format
        """
        if rag_format:
            # For PDF, we can implement RAG format if needed in the future
            # For now, just return the regular chunks
            for chunk in self.serialize(file_path, max_mem_mb=max_mem_mb):
                # Simple RAG format conversion
                import json
                rag_chunk = {
                    "doc_id": chunk.doc_id,
                    "page": chunk.page,
                    "type": chunk.type,
                    "text": chunk.text,
                    "tokens": chunk.tokens,
                    "coordinates": {
                        "x": chunk.x,
                        "y": chunk.y,
                        "w": chunk.w,
                        "h": chunk.h
                    },
                    "metadata": chunk.metadata
                }
                yield json.dumps(rag_chunk, ensure_ascii=False)
        else:
            yield from self.serialize(file_path, max_mem_mb=max_mem_mb)

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".pdf"]