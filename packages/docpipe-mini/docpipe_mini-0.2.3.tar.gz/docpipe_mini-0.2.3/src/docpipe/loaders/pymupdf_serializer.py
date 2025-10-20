"""
独立的 PyMuPDF 序列器实现

基于 Protocol-oriented 设计，提供高性能 PDF 处理能力，支持：
- 准确的文本提取和坐标定位
- 高质量图像提取和元数据
- 表格结构识别和解析
- 可配置的处理选项
- 完整的结构化日志记录
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator, Optional, Dict, Any, Union

from .._types import DocumentChunk, BBox, ContentType, estimate_tokens, generate_doc_id
from .._protocols import DocumentSerializer, LoggingMixin, SerializerMixin

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# 处理配置常量
DEFAULT_MIN_CHUNK_LENGTH = 10
DEFAULT_IMAGE_MIN_RELATIVE_SIZE = 0.01
DEFAULT_FONT_SIZE_THRESHOLD = 6
DEFAULT_COORDINATE_PRECISION = 3

# 内容检测阈值
DEFAULT_HEADING_MAX_LENGTH = 100
DEFAULT_TABLE_MIN_ROWS = 2
DEFAULT_TABLE_MIN_COLS = 2

logger = logging.getLogger(__name__)


class PyMuPDFLoader(LoggingMixin, SerializerMixin, DocumentSerializer):
    """
    基于 PyMuPDF 的高性能 PDF 序列器

    特性：
    - AGPL 3.0 许可证（PyMuPDF 的要求）
    - 准确的文本块提取和坐标定位
    - 高质量图像提取，支持多种格式
    - 表格自动检测和结构化提取
    - 字体信息和元数据保留
    - 内存优化和错误处理
    """

    def __init__(
        self,
        *,
        min_chunk_length: int = DEFAULT_MIN_CHUNK_LENGTH,
        extract_images: bool = True,
        extract_tables: bool = True,
        image_min_relative_size: float = DEFAULT_IMAGE_MIN_RELATIVE_SIZE,
        coordinate_precision: int = DEFAULT_COORDINATE_PRECISION,
        enable_performance_logging: bool = True
    ):
        """
        初始化 PyMuPDF 序列器

        Args:
            min_chunk_length: 文本块最小长度
            extract_images: 是否提取图像
            extract_tables: 是否提取表格
            image_min_relative_size: 图像最小相对尺寸（占页面面积的比例）
            coordinate_precision: 坐标精度（小数位数）
            enable_performance_logging: 是否启用性能日志
        """
        super().__init__()  # 初始化所有 mixin

        if not PYMUPDF_AVAILABLE:
            self.log_error("PyMuPDF not available", error="ImportError")
            raise ImportError(
                "PyMuPDF is required for this PDF processor. "
                "Install with: pip install PyMuPDF"
            )

        # 验证参数
        if min_chunk_length < 1:
            raise ValueError("min_chunk_length must be positive")
        if not 0 < image_min_relative_size <= 1:
            raise ValueError("image_min_relative_size must be between 0 and 1")
        if coordinate_precision < 0:
            raise ValueError("coordinate_precision must be non-negative")

        # 存储配置
        self.min_chunk_length = min_chunk_length
        self.extract_images = extract_images
        self.extract_tables = extract_tables
        self.image_min_relative_size = image_min_relative_size
        self.coordinate_precision = coordinate_precision

        # 配置日志
        self.configure_logging(enable_performance_logging=enable_performance_logging)

        self.log_debug(
            "PyMuPDF Loader initialized",
            min_chunk_length=min_chunk_length,
            extract_images=extract_images,
            extract_tables=extract_tables,
            image_min_relative_size=image_min_relative_size,
            coordinate_precision=coordinate_precision
        )

    def can_serialize(self, file_path: Path | str) -> bool:
        """
        检查文件是否为可处理的 PDF

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否为 PDF 文件
        """
        # 标准化路径
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # 检查扩展名和文件存在性
        is_pdf = file_path.suffix.lower() == '.pdf'

        if is_pdf and file_path.exists():
            # 额外检查：尝试打开文件验证是否为有效 PDF
            try:
                with fitz.open(file_path) as pdf:
                    return len(pdf) > 0
            except Exception as e:
                self.log_debug(f"PDF validation failed", file_path=str(file_path), error=str(e))
                return False

        return is_pdf

    def serialize(
        self,
        file_path: Path | str,
        *,
        max_mem_mb: Optional[int] = None
    ) -> Iterator[DocumentChunk]:
        """
        序列化 PDF 文档为坐标感知的文档块

        Args:
            file_path: PDF 文件路径
            max_mem_mb: 内存限制（PyMuPDF 中暂未实现）

        Yields:
            DocumentChunk: 文档块，包含文本、图像和表格
        """
        # 标准化文件路径
        file_path = self._normalize_file_path(file_path)

        # 验证文件
        if not self.can_serialize(file_path):
            raise ValueError(f"Cannot serialize file: {file_path}")

        # 解析配置
        config = self._resolve_serialization_config(max_mem_mb)

        self.log_operation_start(
            "PDF serialization",
            file_path=str(file_path),
            file_size=file_path.stat().st_size if file_path.exists() else 0,
            config=config
        )

        try:
            with self.log_timing("PDF document processing"):
                with fitz.open(file_path) as pdf:
                    # 准备文档元数据
                    document_metadata = self._build_document_metadata(file_path, config)

                    # 处理所有页面
                    total_pages = len(pdf)
                    processed_chunks = 0
                    text_chunks_count = 0
                    image_chunks_count = 0
                    table_chunks_count = 0

                    for page_num in range(total_pages):
                        with self.log_timing(
                            f"page_{page_num + 1}_processing",
                            page_num=page_num + 1
                        ):
                            # 获取页面
                            page = pdf[page_num]

                            # 生成页面级文档ID
                            page_doc_id = generate_doc_id()

                            # 提取文本块
                            text_chunks = self._extract_text_chunks(
                                page, page_num + 1, page_doc_id, document_metadata
                            )
                            text_chunks_count += len(text_chunks)

                            # 提取图像块
                            image_chunks = []
                            if self.extract_images:
                                image_chunks = self._extract_images(
                                    page, page_num + 1, page_doc_id, document_metadata
                                )
                                image_chunks_count += len(image_chunks)

                            # 提取表格块
                            table_chunks = []
                            if self.extract_tables:
                                table_chunks = self._extract_tables(
                                    page, page_num + 1, page_doc_id, document_metadata
                                )
                                table_chunks_count += len(table_chunks)

                            # 按坐标排序并产出所有块
                            all_chunks = text_chunks + image_chunks + table_chunks
                            all_chunks.sort(key=lambda chunk: (chunk.y, chunk.x))

                            for chunk in all_chunks:
                                yield chunk
                                processed_chunks += 1

                        # 大文档进度日志
                        if total_pages > 10 and (page_num + 1) % 10 == 0:
                            self.log_progress(
                                page_num + 1, total_pages, "Processing pages"
                            )

                    # 最终统计
                    final_stats = {
                        "total_pages": total_pages,
                        "total_chunks": processed_chunks,
                        "text_chunks": text_chunks_count,
                        "image_chunks": image_chunks_count,
                        "table_chunks": table_chunks_count,
                        "file_size_mb": file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0,
                        "avg_chunks_per_page": round(processed_chunks / total_pages, 2) if total_pages > 0 else 0
                    }

                    self.log_processing_stats(final_stats, file_path=str(file_path))

            self.log_operation_success("PDF serialization", file_path=str(file_path))

        except Exception as e:
            self.log_operation_error("PDF serialization", e, file_path=str(file_path))
            raise

    def _extract_text_chunks(
        self,
        page,
        page_num: int,
        doc_id: str,
        document_metadata: Dict[str, Any]
    ) -> list[DocumentChunk]:
        """
        从 PyMuPDF 页面提取文本块

        使用 PyMuPDF 的文本块检测以获得更好的准确性

        Args:
            page: PyMuPDF 页面对象
            page_num: 页码（1-based）
            doc_id: 文档ID
            document_metadata: 文档元数据

        Returns:
            List[DocumentChunk]: 文本块列表
        """
        chunks = []

        try:
            with self.log_timing("text_extraction", page_num=page_num):
                # 获取文本块
                text_dict = page.get_text("dict")

                if "blocks" not in text_dict:
                    self.log_debug("No text blocks found", page_num=page_num)
                    return chunks

                for block_idx, block in enumerate(text_dict["blocks"]):
                    if block["type"] != 0:  # 跳过非文本块
                        continue

                    # 提取块文本
                    block_text = self._extract_block_text(block)

                    if len(block_text) < self.min_chunk_length:
                        continue

                    # 获取边界框
                    bbox = block.get("bbox", [0, 0, 0, 0])
                    norm_bbox = self._normalize_bbox(bbox, page)

                    # 提取字体信息
                    font_info = self._extract_font_info(block)

                    # 检测内容类型
                    content_type = self._detect_text_content_type(block_text)

                    # 创建文档块
                    chunk = DocumentChunk(
                        doc_id=doc_id,
                        page=page_num,
                        x=norm_bbox.x,
                        y=norm_bbox.y,
                        w=norm_bbox.w,
                        h=norm_bbox.h,
                        type=content_type,
                        text=block_text,
                        tokens=estimate_tokens(block_text),
                        metadata={
                            **document_metadata,
                            **font_info,
                            "block_type": "text_block",
                            "char_count": len(block_text),
                            "extraction_method": "pymupdf_block",
                            "block_index": block_idx
                        }
                    )
                    chunks.append(chunk)

                self.log_debug(
                    f"Text extraction completed",
                    page_num=page_num,
                    chunks_found=len(chunks)
                )

        except Exception as e:
            self.log_warning(
                f"Error in text extraction",
                page_num=page_num,
                error=str(e)
            )

        return chunks

    def _extract_images(
        self,
        page,
        page_num: int,
        doc_id: str,
        document_metadata: Dict[str, Any]
    ) -> list[DocumentChunk]:
        """
        从 PyMuPDF 页面提取图像

        Args:
            page: PyMuPDF 页面对象
            page_num: 页码（1-based）
            doc_id: 文档ID
            document_metadata: 文档元数据

        Returns:
            List[DocumentChunk]: 图像块列表
        """
        if not self.extract_images:
            return []

        image_chunks = []

        try:
            with self.log_timing("image_extraction", page_num=page_num):
                # 获取图像列表
                image_list = page.get_images()

                if not image_list:
                    return image_chunks

                page_rect = page.rect
                page_area = page_rect.width * page_rect.height

                for img_index, img in enumerate(image_list):
                    try:
                        # 提取图像
                        chunk = self._extract_single_image(
                            page, img, img_index, page_num, doc_id,
                            document_metadata, page_area
                        )
                        if chunk:
                            image_chunks.append(chunk)

                    except Exception as img_error:
                        self.log_debug(
                            f"Error processing image",
                            page_num=page_num,
                            img_index=img_index,
                            error=str(img_error)
                        )
                        continue

                self.log_debug(
                    f"Image extraction completed",
                    page_num=page_num,
                    images_processed=len(image_chunks),
                    total_images_found=len(image_list)
                )

        except Exception as e:
            self.log_warning(
                f"Error in image extraction",
                page_num=page_num,
                error=str(e)
            )

        return image_chunks

    def _extract_tables(
        self,
        page,
        page_num: int,
        doc_id: str,
        document_metadata: Dict[str, Any]
    ) -> list[DocumentChunk]:
        """
        从 PyMuPDF 页面提取表格

        Args:
            page: PyMuPDF 页面对象
            page_num: 页码（1-based）
            doc_id: 文档ID
            document_metadata: 文档元数据

        Returns:
            List[DocumentChunk]: 表格块列表
        """
        if not self.extract_tables:
            return []

        table_chunks = []

        try:
            with self.log_timing("table_extraction", page_num=page_num):
                # 查找表格
                tables = page.find_tables()

                for table_index, table in enumerate(tables):
                    try:
                        # 提取表格数据
                        chunk = self._extract_single_table(
                            table, table_index, page_num, doc_id, document_metadata, page
                        )
                        if chunk:
                            table_chunks.append(chunk)

                    except Exception as table_error:
                        self.log_debug(
                            f"Error processing table",
                            page_num=page_num,
                            table_index=table_index,
                            error=str(table_error)
                        )
                        continue

                self.log_debug(
                    f"Table extraction completed",
                    page_num=page_num,
                    tables_processed=len(table_chunks)
                )

        except Exception as e:
            self.log_warning(
                f"Error in table extraction",
                page_num=page_num,
                error=str(e)
            )

        return table_chunks

    # 辅助方法
    def _extract_block_text(self, block: Dict[str, Any]) -> str:
        """从文本块中提取文本"""
        text_parts = []

        for line in block.get("lines", []):
            line_text = ""
            for span in line.get("spans", []):
                span_text = span.get("text", "")
                if span_text:
                    line_text += span_text

            if line_text.strip():
                text_parts.append(line_text.strip())

        return " ".join(text_parts)

    def _extract_font_info(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """提取字体信息"""
        font_counts = {}
        total_chars = 0

        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font_name = span.get("font", "")
                font_size = span.get("size", 0)
                text = span.get("text", "")

                if text and font_name:
                    key = f"{font_name}_{font_size}"
                    font_counts[key] = font_counts.get(key, 0) + len(text)
                    total_chars += len(text)

        # 找到最常用的字体
        if font_counts:
            primary_font = max(font_counts.items(), key=lambda x: x[1])[0]
            font_name, font_size = primary_font.split("_", 1)

            return {
                "primary_font": font_name,
                "primary_font_size": float(font_size),
                "font_consistency": max(font_counts.values()) / total_chars if total_chars > 0 else 0
            }

        return {"primary_font": "", "primary_font_size": 0, "font_consistency": 0}

    def _detect_text_content_type(self, text: str) -> str:
        """检测文本内容类型"""
        text = text.strip()

        # 标题检测
        if (len(text) <= DEFAULT_HEADING_MAX_LENGTH and
            (text.isupper() or text.endswith(':') or
             any(text.startswith(prefix) for prefix in ['Chapter', 'Section', 'Abstract']))):
            return ContentType.TEXT

        return ContentType.TEXT

    def _extract_single_image(
        self,
        page,
        img: tuple,
        img_index: int,
        page_num: int,
        doc_id: str,
        document_metadata: Dict[str, Any],
        page_area: float
    ) -> Optional[DocumentChunk]:
        """提取单个图像"""
        xref = img[0]

        try:
            # 获取图像数据
            img_data = page.parent.extract_image(xref)
            binary_data = img_data["image"]

            # 创建 pixmap 获取尺寸信息
            pix = fitz.Pixmap(page.parent, xref)

            # 获取边界框
            try:
                img_rect = page.get_image_bbox(img)
                bbox = [img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1]
            except:
                # 如果无法获取边界框，创建默认位置
                img_w, img_h = pix.width, pix.height
                scale_factor = min(0.2, min(600 / img_w, 400 / img_h))
                bbox = [50, 50, 50 + img_w * scale_factor, 50 + img_h * scale_factor]

            # 检查图像尺寸
            norm_bbox = self._normalize_bbox(bbox, page)
            relative_size = norm_bbox.w * norm_bbox.h

            if relative_size < self.image_min_relative_size:
                self.log_debug(
                    f"Skipping small image",
                    page_num=page_num,
                    img_index=img_index,
                    relative_size=relative_size
                )
                return None

            # 创建图像块
            chunk = DocumentChunk(
                doc_id=doc_id,
                page=page_num,
                x=norm_bbox.x,
                y=norm_bbox.y,
                w=norm_bbox.w,
                h=norm_bbox.h,
                type=ContentType.IMAGE,
                text=None,
                tokens=None,
                binary_data=binary_data,
                metadata={
                    **document_metadata,
                    "width": pix.width,
                    "height": pix.height,
                    "colorspace": str(pix.colorspace) if pix.colorspace else "unknown",
                    "xref": xref,
                    "format": img_data.get("ext", "unknown"),
                    "image_index": img_index,
                    "relative_size": relative_size,
                    "extraction_method": "pymupdf"
                }
            )

            # 清理 pixmap
            pix = None

            return chunk

        except Exception as e:
            self.log_debug(
                f"Failed to extract image",
                page_num=page_num,
                img_index=img_index,
                error=str(e)
            )
            return None

    def _extract_single_table(
        self,
        table,
        table_index: int,
        page_num: int,
        doc_id: str,
        document_metadata: Dict[str, Any],
        page
    ) -> Optional[DocumentChunk]:
        """提取单个表格"""
        try:
            # 获取边界框
            bbox = table.bbox
            norm_bbox = self._normalize_bbox(
                [bbox.x0, bbox.y0, bbox.x1, bbox.y1], page
            )

            # 提取表格数据
            table_data = []
            for row_idx in range(table.row_count):
                row_data = []
                for col_idx in range(table.col_count):
                    try:
                        cell = table.extract_cell(row_idx, col_idx)
                        row_data.append(cell or "")
                    except:
                        row_data.append("")
                table_data.append(row_data)

            # 检查表格有效性
            if len(table_data) < DEFAULT_TABLE_MIN_ROWS or table.col_count < DEFAULT_TABLE_MIN_COLS:
                self.log_debug(
                    f"Skipping small table",
                    page_num=page_num,
                    table_index=table_index,
                    rows=len(table_data),
                    cols=table.col_count
                )
                return None

            # 创建表格结构
            table_structure = {
                "rows": [
                    {"cells": row, "cell_count": len(row)}
                    for row in table_data
                ],
                "row_count": len(table_data),
                "col_count": table.col_count,
                "has_header": len(table_data) > 1,
                "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1]
            }

            # 创建表格文本
            table_text = "\n".join(["\t".join(row) for row in table_data])

            # 创建表格块
            chunk = DocumentChunk(
                doc_id=doc_id,
                page=page_num,
                x=norm_bbox.x,
                y=norm_bbox.y,
                w=norm_bbox.w,
                h=norm_bbox.h,
                type=ContentType.TABLE,
                text=table_text,
                tokens=estimate_tokens(table_text),
                metadata={
                    **document_metadata,
                    "table_structure": table_structure,
                    "table_index": table_index,
                    "extraction_method": "pymupdf"
                }
            )

            return chunk

        except Exception as e:
            self.log_debug(
                f"Failed to extract table",
                page_num=page_num,
                table_index=table_index,
                error=str(e)
            )
            return None

    def _normalize_bbox(self, bbox: list, page) -> BBox:
        """标准化边界框坐标"""
        x1, y1, x2, y2 = bbox
        page_rect = page.rect

        # 确保坐标有效
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # 限制在页面范围内
        x1 = max(0, min(x1, page_rect.width))
        x2 = max(0, min(x2, page_rect.width))
        y1 = max(0, min(y1, page_rect.height))
        y2 = max(0, min(y2, page_rect.height))

        # 创建标准化边界框
        norm_bbox = BBox.from_points(
            round(x1, self.coordinate_precision),
            round(y1, self.coordinate_precision),
            round(x2, self.coordinate_precision),
            round(y2, self.coordinate_precision),
            page_rect.width,
            page_rect.height
        )

        return norm_bbox

    def _normalize_file_path(self, file_path: Path | str) -> Path:
        """标准化文件路径"""
        return Path(file_path) if isinstance(file_path, str) else file_path

    def _resolve_serialization_config(self, max_mem_mb: Optional[int]) -> Dict[str, Any]:
        """解析序列化配置"""
        return {
            'max_mem_mb': max_mem_mb,
            'min_chunk_length': self.min_chunk_length,
            'extract_images': self.extract_images,
            'extract_tables': self.extract_tables,
            'image_min_relative_size': self.image_min_relative_size,
            'coordinate_precision': self.coordinate_precision
        }

    def _build_document_metadata(self, file_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """构建文档元数据"""
        metadata = {
            "source_file": str(file_path),
            "file_name": file_path.name,
            "file_extension": file_path.suffix,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "serializer": "pymupdf",
            "extraction_config": {
                k: v for k, v in config.items()
                if k != 'max_mem_mb' and v is not None
            }
        }

        # 尝试获取 PDF 元数据
        try:
            with fitz.open(file_path) as pdf:
                if pdf.metadata:
                    metadata.update({
                        "pdf_title": pdf.metadata.get('title', ''),
                        "pdf_author": pdf.metadata.get('author', ''),
                        "pdf_subject": pdf.metadata.get('subject', ''),
                        "pdf_creator": pdf.metadata.get('creator', ''),
                        "pdf_producer": pdf.metadata.get('producer', ''),
                        "pdf_creation_date": pdf.metadata.get('creationDate', ''),
                        "pdf_modification_date": pdf.metadata.get('modDate', '')
                    })

                metadata["pdf_page_count"] = len(pdf)

                # 计算页面尺寸统计
                if len(pdf) > 0:
                    first_page = pdf[0]
                    metadata["pdf_page_size"] = {
                        "width": first_page.rect.width,
                        "height": first_page.rect.height
                    }

        except Exception as e:
            self.log_debug(f"Could not extract PDF metadata", error=str(e))

        return metadata

    @property
    def supported_extensions(self) -> list[str]:
        """返回支持的文件扩展名"""
        return [".pdf"]

    # 公共配置方法
    def configure_extraction(
        self,
        *,
        extract_images: Optional[bool] = None,
        extract_tables: Optional[bool] = None,
        min_chunk_length: Optional[int] = None,
        image_min_relative_size: Optional[float] = None
    ) -> 'PyMuPDFLoader':
        """
        配置提取选项

        Args:
            extract_images: 是否提取图像
            extract_tables: 是否提取表格
            min_chunk_length: 最小文本块长度
            image_min_relative_size: 图像最小相对尺寸

        Returns:
            Self for method chaining
        """
        if extract_images is not None:
            self.extract_images = extract_images
        if extract_tables is not None:
            self.extract_tables = extract_tables
        if min_chunk_length is not None:
            if min_chunk_length < 1:
                raise ValueError("min_chunk_length must be positive")
            self.min_chunk_length = min_chunk_length
        if image_min_relative_size is not None:
            if not 0 < image_min_relative_size <= 1:
                raise ValueError("image_min_relative_size must be between 0 and 1")
            self.image_min_relative_size = image_min_relative_size

        self.log_debug(
            "Extraction configuration updated",
            extract_images=self.extract_images,
            extract_tables=self.extract_tables,
            min_chunk_length=self.min_chunk_length,
            image_min_relative_size=self.image_min_relative_size
        )

        return self

    def get_processing_stats(self, file_path: Path | str) -> Dict[str, Any]:
        """
        获取文件的预处理统计信息（不实际处理内容）

        Args:
            file_path: PDF 文件路径

        Returns:
            Dict[str, Any]: 统计信息
        """
        file_path = self._normalize_file_path(file_path)

        if not self.can_serialize(file_path):
            raise ValueError(f"Cannot process file: {file_path}")

        stats = {
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "can_process": True
        }

        try:
            with fitz.open(file_path) as pdf:
                stats.update({
                    "page_count": len(pdf),
                    "has_images": any(len(page.get_images()) > 0 for page in pdf),
                    "has_tables": any(len(page.find_tables()) > 0 for page in pdf),
                    "pdf_metadata": pdf.metadata or {}
                })

                # 快速文本统计（前几页）
                sample_text = ""
                for page_num in range(min(3, len(pdf))):
                    page_text = pdf[page_num].get_text()
                    sample_text += page_text

                if sample_text:
                    stats.update({
                        "estimated_total_chunks": len(pdf) * 5,  # 粗略估计
                        "sample_text_length": len(sample_text),
                        "sample_tokens": estimate_tokens(sample_text)
                    })

        except Exception as e:
            stats["error"] = str(e)
            stats["can_process"] = False

        return stats

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
        统一的迭代器方法，可产出 DocumentChunks 或 RAG JSONL 字符串。

        这是迭代文档内容的首选方法，支持内部配置和参数覆盖。

        Args:
            file_path: PDF 文件路径
            rag_format: 如果为 True，产出 RAG JSONL 字符串；如果为 False，产出 DocumentChunks
            enable_backward_compatible: RAG 格式兼容性设置（PDF 中未使用）
            max_mem_mb: 内存限制设置
            header_row: 标题行覆盖（PDF 中未使用）
            custom_headers: 自定义标题覆盖（PDF 中未使用）

        Yields:
            DocumentChunk 对象或 JSONL 字符串，取决于 rag_format 设置
        """
        if rag_format:
            # 对于 PDF，实现 RAG 格式输出
            import json
            for chunk in self.serialize(file_path, max_mem_mb=max_mem_mb):
                # 构建 RAG 格式的块
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
            # 默认产出 DocumentChunk 对象
            yield from self.serialize(file_path, max_mem_mb=max_mem_mb)