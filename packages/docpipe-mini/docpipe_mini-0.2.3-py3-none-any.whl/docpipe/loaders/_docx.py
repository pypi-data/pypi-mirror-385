"""
DOCX serializer using Python standard library.

Zero-dependency Word document parser using zipfile and xml.etree.
Extracts text with basic coordinate estimation for AI consumption.

Enhanced with LoggingMixin and SerializerMixin for structured logging,
context management, and unified configuration.
"""

from __future__ import annotations

import logging
import time
import zipfile
import xml.etree.ElementTree as ET
import base64
from pathlib import Path
from typing import Iterator, Optional, Dict, Any, Union, List
from dataclasses import dataclass

from .._types import DocumentChunk, BBox, ContentType, estimate_tokens, generate_doc_id
from .._protocols import DocumentSerializer, LoggingMixin, SerializerMixin

# Constants for DOCX processing
MIN_CHUNK_LENGTH = 10
COORDINATE_MARGIN = 0.1  # 10% margin for text content
CONTENT_WIDTH = 0.8  # 80% of page width for content
MIN_IMAGE_Y_SPACING = 0.15  # Minimum vertical spacing between images
MAX_IMAGE_Y_POSITION = 0.8  # Maximum y position for images
MAX_SINGLE_LINE_HEIGHT = 0.02  # Height for single line content
MAX_SHORT_PARAGRAPH_HEIGHT = 0.04  # Height for short paragraphs
MAX_PARAGRAPH_HEIGHT = 0.15  # Maximum paragraph height

# Image size estimation based on data length
SMALL_IMAGE_MAX_SIZE = 50000  # bytes
MEDIUM_IMAGE_MAX_SIZE = 200000  # bytes

# Content detection thresholds
MAX_HEADING_LENGTH = 100
HEADING_PREFIXES = ['Chapter', 'Section', 'Part', 'Figure', 'Table']
LIST_PREFIXES = ['•', '-', '*', '1.', '2.', '3.']

# DOCX XML namespaces
DOCX_NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships'  # Package relationships namespace
}

# File paths in DOCX structure
DOCUMENT_XML_PATH = 'word/document.xml'
MEDIA_FOLDER_PREFIX = 'word/media/'

# Font size conversion (half-points to points)
FONT_SIZE_HALF_POINT_TO_POINT = 2.0


@dataclass
class TextRun:
    """Represents a text run with formatting information."""
    text: str
    font_size: Optional[float] = None
    is_bold: bool = False
    is_italic: bool = False


class DocxSerializer(LoggingMixin, SerializerMixin, DocumentSerializer):
    """
    DOCX serializer using Python standard library only.

    Parses DOCX files by extracting text from document.xml and estimating
    coordinates based on document structure and formatting.

    Enhanced with structured logging, context management, and unified configuration.
    """

    def __init__(self, *, min_chunk_length: int = MIN_CHUNK_LENGTH):
        """
        Initialize the DOCX serializer.

        Args:
            min_chunk_length: Minimum text length for a chunk
        """
        super().__init__()  # Initialize both mixin attributes

        self.min_chunk_length = min_chunk_length
        self.log_debug("DOCX serializer initialized", min_chunk_length=min_chunk_length)

    def can_serialize(self, file_path: Path | str) -> bool:
        """Check if file is a DOCX."""
        # Convert to Path object for consistent handling
        file_path = self._normalize_file_path(file_path)
        return file_path.suffix.lower() in ['.docx', '.docm']

    def _normalize_file_path(self, file_path: Path | str) -> Path:
        """Normalize file path to Path object."""
        return Path(file_path) if isinstance(file_path, str) else file_path

    def _resolve_serialization_config(
        self,
        max_mem_mb: Optional[int],
        header_row: Optional[int],  # DOCX doesn't use header injection but keeping interface consistent
        custom_headers: Optional[List[str]]  # DOCX doesn't use custom headers but keeping interface consistent
    ) -> Dict[str, Any]:
        """Resolve effective configuration from parameters and internal state."""
        return {
            "max_mem_mb": max_mem_mb or self._max_mem_mb,
            "header_row": None,  # Not applicable to DOCX
            "custom_headers": None,  # Not applicable to DOCX
            "rag_format": self._rag_format,
            "enable_backward_compatible": self._enable_backward_compatible
        }

    def _build_document_metadata(self, file_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build document metadata for chunks."""
        return {
            "source_file": str(file_path),
            "file_extension": file_path.suffix.lower(),
            "serializer": "DocxSerializer",
            "extraction_method": "docx_stdlib",
            "chunk_creation_time": time.time(),
            "rag_format": config["rag_format"],
            "enable_backward_compatible": config["enable_backward_compatible"]
        }

    def serialize(
        self,
        file_path: Path | str,
        *,
        max_mem_mb: Optional[int] = None
    ) -> Iterator[DocumentChunk]:
        """
        Serialize DOCX document into coordinate-aware chunks.

        Args:
            file_path: Path to DOCX file
            max_mem_mb: Memory limit (not implemented for stdlib version)

        Yields:
            DocumentChunk objects with text and estimated coordinates
        """
        # Normalize file path
        file_path = self._normalize_file_path(file_path)

        # Resolve configuration
        config = self._resolve_serialization_config(max_mem_mb, None, None)

        self.log_operation_start(
            "DOCX serialization",
            file_path=str(file_path),
            file_size=file_path.stat().st_size if file_path.exists() else 0
        )

        try:
            with self.log_timing("DOCX file processing"):
                with zipfile.ZipFile(file_path, 'r') as docx:
                    # Extract document structure
                    if DOCUMENT_XML_PATH not in docx.namelist():
                        raise ValueError(f"Invalid DOCX file: no {DOCUMENT_XML_PATH} found")

                    # Parse main document
                    document_xml = docx.read(DOCUMENT_XML_PATH)
                    root = ET.fromstring(document_xml)

                    # Prepare document metadata
                    document_metadata = self._build_document_metadata(file_path, config)

                    # Process document in proper order - parse document structure to maintain text-image order
                    all_chunks = []
                    chunk_num = 0

                    # Extract images first to get their relationship IDs
                    image_mapping = self._build_image_mapping(docx)
                    self.log_debug(f"Built image mapping with {len(image_mapping)} images")

                    # Process document in document order
                    all_chunks = self._process_document_in_order(root, docx, image_mapping, document_metadata)
                    self.log_debug(f"Processed document, got {len(all_chunks)} chunks")

                    chunk_num = len(all_chunks)

                    # Set doc_id for all chunks and yield in proper order
                    chunk_count = 0
                    for chunk in all_chunks:
                        chunk.doc_id = generate_doc_id()
                        yield chunk
                        chunk_count += 1

                    # Log final statistics
                    self.log_processing_stats(
                        {
                            "total_chunks": chunk_count,
                            "text_chunks": chunk_count,  # For now, use total count
                            "image_chunks": 0,  # For now, assume no images
                            "file_size_mb": file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0
                        },
                        file_path=str(file_path)
                    )

            self.log_operation_success("DOCX serialization", file_path=str(file_path))

        except Exception as e:
            self.log_operation_error("DOCX serialization", e, file_path=str(file_path))
            raise

    def _process_text_chunks(self, root: ET.Element, document_metadata: Dict[str, Any]) -> list[DocumentChunk]:
        """
        Process text chunks from document XML.

        Args:
            root: Root XML element of document.xml
            document_metadata: Document metadata to include in chunks

        Returns:
            List of DocumentChunk objects containing text
        """
        chunks = []
        paragraph_idx = 0

        # Find all paragraphs
        paragraphs = self._find_with_namespace(root, ".//w:p")
        total_paragraphs = len(paragraphs)

        for paragraph in paragraphs:
            paragraph_idx += 1

            # Extract text runs
            text_runs = self._extract_text_runs(paragraph)
            if not text_runs:
                continue

            # Combine text from all runs
            combined_text = ''.join(run.text for run in text_runs).strip()
            if not combined_text or len(combined_text) < self.min_chunk_length:
                continue

            # Estimate coordinates
            coords = self._estimate_coordinates(paragraph_idx, total_paragraphs, len(text_runs))

            # Detect content type
            content_type = self._detect_content_type(combined_text)

            # Estimate tokens
            tokens = estimate_tokens(combined_text)

            # Create text chunk
            chunk = DocumentChunk(
                doc_id="",
                page=1,
                x=coords.x,
                y=coords.y,
                w=coords.w,
                h=coords.h,
                type=content_type,
                text=combined_text,
                tokens=tokens,
                binary_data=None,
                metadata={
                    **document_metadata,
                    "paragraph_index": paragraph_idx,
                    "text_runs_count": len(text_runs),
                    "extraction_method": "docx_stdlib",
                    "has_formatting": any(run.is_bold or run.is_italic for run in text_runs),
                    "font_sizes": [run.font_size for run in text_runs if run.font_size]
                }
            )
            chunks.append(chunk)

        return chunks

    def _find_with_namespace(self, element: ET.Element, xpath: str) -> list[ET.Element]:
        """Helper method to find elements with proper namespace handling."""
        return element.findall(xpath, DOCX_NAMESPACES)

    def _find_one_with_namespace(self, element: ET.Element, xpath: str) -> Optional[ET.Element]:
        """Helper method to find one element with proper namespace handling."""
        return element.find(xpath, DOCX_NAMESPACES)

    def _build_image_mapping(self, docx: zipfile.ZipFile) -> Dict[str, Dict[str, Any]]:
        """
        Build a mapping of relationship IDs to image data.

        Args:
            docx: Opened DOCX zipfile

        Returns:
            Dictionary mapping relationship IDs to image information
        """
        image_mapping = {}

        try:
            # Read relationships file to find image relationships
            rels_path = 'word/_rels/document.xml.rels'
            if rels_path in docx.namelist():
                rels_xml = docx.read(rels_path)
                rels_root = ET.fromstring(rels_xml)

                # Find all relationships that point to images
                for rel in rels_root.findall(".//pr:Relationship", DOCX_NAMESPACES):
                    rel_id = rel.get('Id')
                    rel_target = rel.get('Target')
                    rel_type = rel.get('Type')

                    # Check if this is an image relationship
                    if (rel_type and 'image' in rel_type.lower() and
                        rel_target and rel_target.startswith('media/')):

                        # Extract the actual image data
                        full_image_path = f"word/{rel_target}"
                        if full_image_path in docx.namelist():
                            image_data = docx.read(full_image_path)
                            if image_data:
                                # Determine image format
                                filename = rel_target.split('/')[-1]
                                image_format = 'unknown'
                                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                                    image_format = filename.split('.')[-1].lower()

                                image_mapping[rel_id] = {
                                    'data': image_data,
                                    'format': image_format,
                                    'original_path': full_image_path,
                                    'filename': filename
                                }

                                self.log_debug(
                                    f"Found image mapping",
                                    rel_id=rel_id,
                                    image_format=image_format,
                                    image_size=len(image_data)
                                )

        except Exception as e:
            self.log_debug(f"Error building image mapping: {e}")

        return image_mapping

    def _process_document_in_order(
        self,
        root: ET.Element,
        docx: zipfile.ZipFile,
        image_mapping: Dict[str, Dict[str, Any]],
        document_metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Process document elements in their natural order to maintain text-image sequence.

        Args:
            root: Root XML element of document.xml
            docx: Opened DOCX zipfile
            image_mapping: Mapping of relationship IDs to image data
            document_metadata: Document metadata to include in chunks

        Returns:
            List of DocumentChunk objects in document order
        """
        chunks = []
        element_count = 0

        try:
            # Get all paragraphs in document order
            paragraphs = self._find_with_namespace(root, ".//w:p")
            total_paragraphs = len(paragraphs)

            self.log_debug(f"Processing {total_paragraphs} paragraphs in order")

            for para_idx, paragraph in enumerate(paragraphs, 1):
                element_count += 1

                # Check if paragraph contains an image
                image_element = self._find_one_with_namespace(paragraph, ".//w:drawing//a:blip")

                if image_element is not None:
                    # This paragraph contains an image
                    rel_id = image_element.get(f"{{{DOCX_NAMESPACES['r']}}}embed")

                    if rel_id and rel_id in image_mapping:
                        # Create image chunk
                        image_info = image_mapping[rel_id]

                        # Estimate coordinates based on paragraph position
                        coords = self._estimate_coordinates(para_idx, total_paragraphs, 1)

                        # Adjust image coordinates slightly to be distinct from text
                        image_y = coords.y + 0.01  # Slightly below the text position
                        if image_y > 0.95:
                            image_y = coords.y - 0.01

                        # Estimate image size based on data
                        data_size = len(image_info['data'])
                        if data_size < SMALL_IMAGE_MAX_SIZE:
                            width, height = 0.3, 0.15
                        elif data_size < MEDIUM_IMAGE_MAX_SIZE:
                            width, height = 0.4, 0.25
                        else:
                            width, height = 0.5, 0.35

                        # Create image chunk
                        binary_data = base64.b64encode(image_info['data']).decode('utf-8')

                        chunk = DocumentChunk(
                            doc_id="",
                            page=1,
                            x=coords.x,
                            y=image_y,
                            w=width,
                            h=height,
                            type=ContentType.IMAGE,
                            text=None,
                            tokens=None,
                            binary_data=binary_data,
                            metadata={
                                **document_metadata,
                                "image_format": image_info['format'],
                                "image_size_bytes": len(image_info['data']),
                                "original_path": image_info['original_path'],
                                "extraction_method": "docx_stdlib_ordered",
                                "paragraph_index": para_idx,
                                "relationship_id": rel_id
                            }
                        )

                        chunks.append(chunk)

                        self.log_debug(
                            f"Created image chunk in order",
                            paragraph_index=para_idx,
                            image_format=image_info['format'],
                            image_size=len(image_info['data'])
                        )
                    else:
                        self.log_debug(
                            f"Found image element but no matching image data",
                            rel_id=rel_id,
                            paragraph_index=para_idx
                        )

                # Process text content in this paragraph
                text_runs = self._extract_text_runs(paragraph)
                if text_runs:
                    # Combine text from all runs
                    combined_text = ''.join(run.text for run in text_runs).strip()
                    if combined_text and len(combined_text) >= self.min_chunk_length:
                        # Estimate coordinates
                        coords = self._estimate_coordinates(para_idx, total_paragraphs, len(text_runs))

                        # Detect content type
                        content_type = self._detect_content_type(combined_text)

                        # Estimate tokens
                        tokens = estimate_tokens(combined_text)

                        # Create text chunk
                        chunk = DocumentChunk(
                            doc_id="",
                            page=1,
                            x=coords.x,
                            y=coords.y,
                            w=coords.w,
                            h=coords.h,
                            type=content_type,
                            text=combined_text,
                            tokens=tokens,
                            binary_data=None,
                            metadata={
                                **document_metadata,
                                "paragraph_index": para_idx,
                                "text_runs_count": len(text_runs),
                                "extraction_method": "docx_stdlib_ordered",
                                "has_formatting": any(run.is_bold or run.is_italic for run in text_runs),
                                "font_sizes": [run.font_size for run in text_runs if run.font_size],
                                "has_image_in_paragraph": image_element is not None
                            }
                        )

                        chunks.append(chunk)

                        self.log_debug(
                            f"Created text chunk in order",
                            paragraph_index=para_idx,
                            text_length=len(chunk.text),
                            content_type=chunk.type,
                            has_image=image_element is not None
                        )

            self.log_debug(
                f"Document processing completed",
                total_elements=element_count,
                total_chunks=len(chunks),
                text_chunks=len([c for c in chunks if c.type == ContentType.TEXT]),
                image_chunks=len([c for c in chunks if c.type == ContentType.IMAGE])
            )

        except Exception as e:
            self.log_debug(f"Error processing document in order: {e}")
            # Fall back to the old method if ordered processing fails
            self.log_debug("Falling back to separate text and image processing")
            text_chunks = self._process_text_chunks(root, document_metadata)
            image_chunks = self._extract_images(docx, document_metadata)
            chunks = text_chunks + image_chunks
            chunks.sort(key=lambda c: (c.y, c.x))

        return chunks

    def _extract_text_runs(self, paragraph: ET.Element) -> list[TextRun]:
        """
        Extract text runs from a paragraph with formatting information.

        Args:
            paragraph: Paragraph XML element

        Returns:
            List of TextRun objects
        """
        runs = []

        for run in self._find_with_namespace(paragraph, ".//w:r"):
            # Extract text
            text_elements = self._find_with_namespace(run, ".//w:t")
            run_text = ''.join(elem.text or '' for elem in text_elements)

            if not run_text.strip():
                continue

            # Extract formatting
            run_props = self._find_one_with_namespace(run, ".//w:rPr")
            font_size = None
            is_bold = False
            is_italic = False

            if run_props is not None:
                # Font size
                sz_elem = self._find_one_with_namespace(run_props, ".//w:sz")
                if sz_elem is not None and sz_elem.get('val'):
                    try:
                        font_size = float(sz_elem.get('val')) / FONT_SIZE_HALF_POINT_TO_POINT
                    except (ValueError, TypeError):
                        self.log_debug(
                            f"Invalid font size value",
                            sz_value=sz_elem.get('val'),
                            run_text_preview=run_text[:20]
                        )

                # Bold
                b_elem = self._find_one_with_namespace(run_props, ".//w:b")
                if b_elem is not None:
                    is_bold = True

                # Italic
                i_elem = self._find_one_with_namespace(run_props, ".//w:i")
                if i_elem is not None:
                    is_italic = True

            runs.append(TextRun(
                text=run_text,
                font_size=font_size,
                is_bold=is_bold,
                is_italic=is_italic
            ))

        return runs

    def _estimate_coordinates(
        self,
        paragraph_idx: int,
        total_paragraphs: int,
        text_runs_count: int
    ) -> BBox:
        """
        Estimate coordinates for a paragraph based on its position.

        Since DOCX doesn't store absolute coordinates without complex layout
        calculation, we estimate based on document structure.

        Args:
            paragraph_idx: Paragraph index in document
            total_paragraphs: Total number of paragraphs
            text_runs_count: Number of text runs in paragraph

        Returns:
            Estimated bounding box
        """
        # Estimate vertical position (y) based on paragraph order
        y_pos = (paragraph_idx / max(total_paragraphs, 1)) * 0.9 + 0.05  # 5% to 95%

        # Estimate height based on content length and runs using constants
        if text_runs_count == 1:
            height = MAX_SINGLE_LINE_HEIGHT
        elif text_runs_count <= 3:
            height = MAX_SHORT_PARAGRAPH_HEIGHT
        else:
            height = min(MAX_SINGLE_LINE_HEIGHT * text_runs_count, MAX_PARAGRAPH_HEIGHT)

        # Use constants for standard width and position
        x_pos = COORDINATE_MARGIN  # 10% margin
        width = CONTENT_WIDTH  # 80% of page width

        return BBox(x=x_pos, y=y_pos, w=width, h=height)

    def _detect_content_type(self, text: str) -> str:
        """
        Detect content type based on text patterns.

        Args:
            text: Text content

        Returns:
            Content type identifier
        """
        text = text.strip()

        # Heading detection using constants
        if len(text) < MAX_HEADING_LENGTH and (
            text.isupper() or
            text.endswith(':') or
            any(text.startswith(prefix) for prefix in HEADING_PREFIXES)
        ):
            return ContentType.TEXT  # Still text, but could be used for styling

        # List detection using constants
        if any(text.startswith(prefix) for prefix in LIST_PREFIXES):
            return ContentType.TEXT

        # Table detection (simple)
        if '\t' in text or '|' in text:
            lines = text.split('\n')
            if len(lines) > 1 and all('|' in line or '\t' in line for line in lines[:3]):
                return ContentType.TABLE

        # Default to text
        return ContentType.TEXT

    def _extract_images(self, docx: zipfile.ZipFile, document_metadata: Dict[str, Any]) -> list[DocumentChunk]:
        """
        Extract images from DOCX file.

        Args:
            docx: Opened DOCX zipfile
            document_metadata: Document metadata to include

        Returns:
            List of DocumentChunk objects representing images
        """
        image_chunks = []

        try:
            # Check if there's a media folder with images using constant
            media_files = [f for f in docx.namelist() if f.startswith(MEDIA_FOLDER_PREFIX)]
            self.log_debug(f"Found media files", media_files_count=len(media_files))

            # Sort media files to maintain order
            media_files.sort()

            for media_path in media_files:
                try:
                    # Extract image data
                    image_data = docx.read(media_path)

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

                    # Estimate coordinates using constants
                    image_index = len(image_chunks)
                    y_pos = COORDINATE_MARGIN + (image_index * MIN_IMAGE_Y_SPACING)
                    if y_pos > MAX_IMAGE_Y_POSITION:  # Reset if too far down
                        y_pos = COORDINATE_MARGIN + ((image_index % 5) * MIN_IMAGE_Y_SPACING)

                    # Estimate size based on image data length using constants
                    data_size = len(image_data)
                    if data_size < SMALL_IMAGE_MAX_SIZE:  # Small image
                        width, height = 0.2, 0.1
                    elif data_size < MEDIUM_IMAGE_MAX_SIZE:  # Medium image
                        width, height = 0.3, 0.2
                    else:  # Large image
                        width, height = 0.4, 0.3

                    # Create image chunk
                    chunk = DocumentChunk(
                        doc_id="",
                        page=1,
                        x=COORDINATE_MARGIN,  # Left margin
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
                            "extraction_method": "docx_stdlib"
                        }
                    )
                    image_chunks.append(chunk)

                except Exception as img_error:
                    self.log_debug(
                        f"Error extracting image",
                        media_path=media_path,
                        error=str(img_error)
                    )
                    continue

            self.log_debug(
                f"Extracted images from DOCX",
                images_count=len(image_chunks),
                total_image_size=sum(len(chunk.binary_data or '') for chunk in image_chunks)
            )

        except Exception as e:
            self.log_debug(
                f"Error extracting images from DOCX",
                error=str(e)
            )

        return image_chunks

    def iterate_chunks(
        self,
        file_path: Path | str,
        *,
        max_mem_mb: Optional[int] = None
    ) -> Iterator[DocumentChunk]:
        """
        Iterate over DOCX document chunks with memory-efficient processing.

        This method provides a memory-efficient iterator interface for processing
        large DOCX files without loading all chunks into memory at once.

        Args:
            file_path: Path to DOCX file
            max_mem_mb: Memory limit (not implemented for stdlib version)

        Yields:
            DocumentChunk objects one at a time

        Example:
            >>> serializer = DocxSerializer()
            >>> with serializer:
            ...     for chunk in serializer.iterate_chunks("document.docx"):
            ...         print(f"Processing: {chunk.type}")
        """
        # Normalize file path and store for context manager
        file_path = self._normalize_file_path(file_path)
        self._current_file = file_path

        # Resolve configuration
        config = self._resolve_serialization_config(max_mem_mb, None, None)

        self.log_operation_start(
            "DOCX chunk iteration",
            file_path=str(file_path),
            file_size=file_path.stat().st_size if file_path.exists() else 0
        )

        try:
            with self.log_timing("DOCX file iteration"):
                with zipfile.ZipFile(file_path, 'r') as docx:
                    # Extract document structure
                    if DOCUMENT_XML_PATH not in docx.namelist():
                        raise ValueError(f"Invalid DOCX file: no {DOCUMENT_XML_PATH} found")

                    # Parse main document
                    document_xml = docx.read(DOCUMENT_XML_PATH)
                    root = ET.fromstring(document_xml)

                    # Prepare document metadata
                    document_metadata = self._build_document_metadata(file_path, config)

                    # Process document in proper order - similar to serialize() but yielding chunks immediately
                    chunk_count = 0

                    # Extract images first to get their relationship IDs
                    image_mapping = self._build_image_mapping(docx)
                    self.log_debug(f"Built image mapping with {len(image_mapping)} images for iteration")

                    # Get all paragraphs in document order
                    paragraphs = self._find_with_namespace(root, ".//w:p")
                    total_paragraphs = len(paragraphs)

                    self.log_debug(f"Iterating through {total_paragraphs} paragraphs in order")

                    for para_idx, paragraph in enumerate(paragraphs, 1):
                        # Check if paragraph contains an image
                        image_element = self._find_one_with_namespace(paragraph, ".//w:drawing//a:blip")

                        if image_element is not None:
                            # This paragraph contains an image
                            rel_id = image_element.get(f"{{{DOCX_NAMESPACES['r']}}}embed")

                            if rel_id and rel_id in image_mapping:
                                # Create image chunk
                                image_info = image_mapping[rel_id]

                                # Estimate coordinates based on paragraph position
                                coords = self._estimate_coordinates(para_idx, total_paragraphs, 1)

                                # Adjust image coordinates slightly to be distinct from text
                                image_y = coords.y + 0.01  # Slightly below the text position
                                if image_y > 0.95:
                                    image_y = coords.y - 0.01

                                # Estimate image size based on data
                                data_size = len(image_info['data'])
                                if data_size < SMALL_IMAGE_MAX_SIZE:
                                    width, height = 0.3, 0.15
                                elif data_size < MEDIUM_IMAGE_MAX_SIZE:
                                    width, height = 0.4, 0.25
                                else:
                                    width, height = 0.5, 0.35

                                # Create image chunk
                                binary_data = base64.b64encode(image_info['data']).decode('utf-8')

                                chunk = DocumentChunk(
                                    doc_id=generate_doc_id(),
                                    page=1,
                                    x=coords.x,
                                    y=image_y,
                                    w=width,
                                    h=height,
                                    type=ContentType.IMAGE,
                                    text=None,
                                    tokens=None,
                                    binary_data=binary_data,
                                    metadata={
                                        **document_metadata,
                                        "image_format": image_info['format'],
                                        "image_size_bytes": len(image_info['data']),
                                        "original_path": image_info['original_path'],
                                        "extraction_method": "docx_stdlib_iterative_ordered",
                                        "paragraph_index": para_idx,
                                        "relationship_id": rel_id
                                    }
                                )

                                chunk_count += 1

                                self.log_debug(
                                    f"Yielded image chunk in order",
                                    chunk_num=chunk_count,
                                    paragraph_index=para_idx,
                                    image_format=image_info['format'],
                                    image_size=len(image_info['data'])
                                )

                                yield chunk
                            else:
                                self.log_debug(
                                    f"Found image element but no matching image data during iteration",
                                    rel_id=rel_id,
                                    paragraph_index=para_idx
                                )

                        # Process text content in this paragraph
                        text_runs = self._extract_text_runs(paragraph)
                        if text_runs:
                            # Combine text from all runs
                            combined_text = ''.join(run.text for run in text_runs).strip()
                            if combined_text and len(combined_text) >= self.min_chunk_length:
                                # Estimate coordinates
                                coords = self._estimate_coordinates(para_idx, total_paragraphs, len(text_runs))

                                # Detect content type
                                content_type = self._detect_content_type(combined_text)

                                # Estimate tokens
                                tokens = estimate_tokens(combined_text)

                                # Create text chunk
                                chunk = DocumentChunk(
                                    doc_id=generate_doc_id(),
                                    page=1,
                                    x=coords.x,
                                    y=coords.y,
                                    w=coords.w,
                                    h=coords.h,
                                    type=content_type,
                                    text=combined_text,
                                    tokens=tokens,
                                    binary_data=None,
                                    metadata={
                                        **document_metadata,
                                        "paragraph_index": para_idx,
                                        "text_runs_count": len(text_runs),
                                        "extraction_method": "docx_stdlib_iterative_ordered",
                                        "has_formatting": any(run.is_bold or run.is_italic for run in text_runs),
                                        "font_sizes": [run.font_size for run in text_runs if run.font_size],
                                        "has_image_in_paragraph": image_element is not None
                                    }
                                )

                                chunk_count += 1

                                self.log_debug(
                                    f"Yielded text chunk in order",
                                    chunk_num=chunk_count,
                                    paragraph_index=para_idx,
                                    text_length=len(chunk.text),
                                    content_type=chunk.type,
                                    has_image=image_element is not None
                                )

                                yield chunk

                    # Log final statistics
                    self.log_processing_stats(
                        {
                            "total_chunks": chunk_count,
                            "file_size_mb": file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0,
                            "processing_mode": "iterative_ordered"
                        },
                        file_path=str(file_path)
                    )

            self.log_operation_success("DOCX chunk iteration", file_path=str(file_path))

        except Exception as e:
            self.log_operation_error("DOCX chunk iteration", e, file_path=str(file_path))
            raise
        finally:
            # Clean up context manager state
            if hasattr(self, '_current_file'):
                delattr(self, '_current_file')

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        if exc_type is not None:
            self.log_operation_error("DOCX context manager", exc_val, file_path=str(getattr(self, '_current_file', 'unknown')))
        else:
            self.log_debug("DOCX context manager completed successfully")
        return False  # Don't suppress exceptions

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".docx", ".docm"]