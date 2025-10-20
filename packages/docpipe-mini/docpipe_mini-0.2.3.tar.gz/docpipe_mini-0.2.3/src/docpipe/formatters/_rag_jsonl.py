"""
RAG优化的JSONL格式化器

将表格数据转换为平铺的JSON键值对格式，实现"开箱即用"的RAG兼容性。
"""

from __future__ import annotations

import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict

from .._types import DocumentChunk, ContentType

logger = logging.getLogger(__name__)


class RAGJsonlFormatter:
    """
    RAG优化的JSONL格式化器

    将管道符格式的表格数据转换为平铺的JSON键值对格式，
    实现向量化友好和检索友好的输出结构。
    """

    def __init__(self, *, enable_backward_compatible: bool = True):
        """
        初始化RAG JSONL格式化器

        Args:
            enable_backward_compatible: 是否保持向后兼容的管道符格式
        """
        self.enable_backward_compatible = enable_backward_compatible

    def format_chunk(self, chunk: DocumentChunk) -> str:
        """
        格式化单个DocumentChunk为RAG优化的JSONL格式

        Args:
            chunk: DocumentChunk对象

        Returns:
            RAG优化的JSONL字符串
        """
        if chunk.type != ContentType.TABLE:
            # 非表格内容保持原样
            return chunk.to_jsonl()

        metadata = chunk.metadata or {}
        table_type = metadata.get("table_type", "")

        if table_type == "structured_row":
            return self._format_table_row_chunk(chunk)
        elif table_type == "structured_table":
            return self._format_table_header_chunk(chunk)
        else:
            # 未知表格类型，保持原样
            return chunk.to_jsonl()

    def _format_table_row_chunk(self, chunk: DocumentChunk) -> str:
        """
        格式化表格行级chunk为平铺JSON格式

        Args:
            chunk: 表格行级DocumentChunk

        Returns:
            平铺JSON格式的字符串
        """
        metadata = chunk.metadata or {}
        text = chunk.text or ""

        # 解析text内容
        lines = text.split('\n')
        row_line = None
        for line in lines:
            if line.startswith("row="):
                # 找到行号标识，跳过
                continue
            elif "|" in line:
                # 找到数据行
                row_line = line
                break

        if not row_line:
            # 如果没有找到数据行，返回空格式
            return self._create_empty_row_format(chunk)

        # 获取列名（需要从父表获取）
        headers = self._extract_headers_from_chunk(chunk)
        if not headers:
            # 如果无法获取列名，返回管道符格式（向后兼容）
            return chunk.to_jsonl() if self.enable_backward_compatible else self._create_empty_row_format(chunk)

        # 解析数据行
        values = row_line.split('|')
        row_data = self._parse_row_values(values, headers)

        # 构建RAG格式数据
        rag_data = self._build_rag_format(chunk, headers, row_data)

        return json.dumps(rag_data, ensure_ascii=False)

    def _format_table_header_chunk(self, chunk: DocumentChunk) -> str:
        """
        格式化表格头部chunk（保持原样或提供结构化信息）

        Args:
            chunk: 表格头部DocumentChunk

        Returns:
            格式化的JSONL字符串
        """
        if self.enable_backward_compatible:
            return chunk.to_jsonl()
        else:
            # 为RAG提供结构化的表头信息
            metadata = chunk.metadata or {}
            text = chunk.text or ""

            # 解析表头
            headers = []
            if text.startswith("[HEADER]"):
                # 查找数据行来提取表头
                lines = text.split('\n')
                for line in lines[1:]:  # 跳过[HEADER]行
                    if "|" in line:
                        headers = [col.strip() for col in line.split('|')]
                        break

            rag_data = {
                "_doc_id": chunk.doc_id,
                "_type": "table_header",
                "_page": chunk.page,
                "_src": self._build_source_path(metadata),
                "_headers": headers,
                "_column_count": len(headers),
                "_row_count": metadata.get("row_count", 0),
                "table_info": {
                    "sheet_name": metadata.get("sheet_name", ""),
                    "has_header": metadata.get("has_header", False),
                    "extraction_method": metadata.get("extraction_method", "")
                }
            }

            return json.dumps(rag_data, ensure_ascii=False)

    def _format_table_chunk_with_parser(self, chunk: DocumentChunk, table_parser: 'TableHeaderParser', all_chunks: Optional[List[DocumentChunk]] = None) -> str:
        """
        使用table_parser格式化表格chunk

        Args:
            chunk: DocumentChunk对象
            table_parser: 表格解析器
            all_chunks: 所有chunk列表，用于跨chunk表头提取

        Returns:
            RAG优化的JSONL字符串
        """
        metadata = chunk.metadata or {}
        table_type = metadata.get("table_type", "")

        if table_type == "structured_row":
            return self._format_table_row_chunk_with_parser(chunk, table_parser, all_chunks)
        elif table_type == "structured_table":
            return self._format_table_header_chunk(chunk)
        else:
            # 未知表格类型，保持原样
            return chunk.to_jsonl() if self.enable_backward_compatible else self._create_empty_row_format(chunk)

    def _format_table_row_chunk_with_parser(self, chunk: DocumentChunk, table_parser: 'TableHeaderParser', all_chunks: Optional[List[DocumentChunk]] = None) -> str:
        """
        使用table_parser格式化表格行级chunk为平铺JSON格式

        Args:
            chunk: 表格行级DocumentChunk
            table_parser: 表格解析器
            all_chunks: 所有chunk列表，用于跨chunk表头提取

        Returns:
            平铺JSON格式的字符串
        """
        metadata = chunk.metadata or {}
        text = chunk.text or ""

        # 解析text内容
        lines = text.split('\n')
        row_line = None
        for line in lines:
            if line.startswith("row="):
                # 找到行号标识，跳过
                continue
            elif "|" in line:
                # 找到数据行
                row_line = line
                break

        if not row_line:
            # 如果没有找到数据行，返回空格式
            return self._create_empty_row_format(chunk)

        # 使用table_parser获取准确的列名
        headers = table_parser.get_headers_for_chunk(chunk)

        # 如果table_parser无法获取表头，尝试从行级chunk中提取
        if not headers:
            headers = self._extract_headers_from_row_chunk(chunk, all_chunks)

        if not headers:
            # 如果仍然无法获取列名，返回管道符格式（向后兼容）
            return chunk.to_jsonl() if self.enable_backward_compatible else self._create_empty_row_format(chunk)

        # 解析数据行
        values = row_line.split('|')
        row_data = self._parse_row_values(values, headers)

        # 构建RAG格式数据
        rag_data = self._build_rag_format(chunk, headers, row_data)

        return json.dumps(rag_data, ensure_ascii=False)

    def _extract_headers_from_row_chunk(self, chunk: DocumentChunk, all_chunks: Optional[List[DocumentChunk]] = None) -> Optional[List[str]]:
        """
        从行级chunk中提取表头信息

        优先级：
        1. 从chunk metadata中的injected_headers获取
        2. 从header行的text内容提取表头
        3. 从同一表的其他header行中提取表头

        Args:
            chunk: 行级DocumentChunk
            all_chunks: 所有chunk列表，用于查找header行

        Returns:
            表头列表，如果无法提取则返回None
        """
        metadata = chunk.metadata or {}

        # 优先检查是否有注入的headers
        injected_headers = metadata.get("headers")
        if injected_headers:
            logger.debug(f"Using injected headers: {injected_headers}")
            return injected_headers

        # 如果当前chunk是header行，直接提取
        if metadata.get("has_header", False):
            text = chunk.text or ""
            lines = text.split('\n')

            # 查找包含管道符的数据行
            for line in lines:
                if line.startswith("row="):
                    continue  # 跳过行号标识
                elif "|" in line:
                    # 提取表头
                    headers = [col.strip() for col in line.split('|') if col.strip()]
                    return headers if headers else None

        # 如果当前chunk不是header行，查找同一表的header行
        elif all_chunks:
            parent_table_doc_id = metadata.get("parent_table_doc_id")
            if parent_table_doc_id:
                for other_chunk in all_chunks:
                    other_metadata = other_chunk.metadata or {}
                    if (other_metadata.get("parent_table_doc_id") == parent_table_doc_id and
                        other_metadata.get("has_header", False)):
                        # 从header行提取表头
                        return self._extract_headers_from_row_chunk(other_chunk)

        return None

    def _extract_headers_from_chunk(self, chunk: DocumentChunk, table_parser: Optional['TableHeaderParser'] = None) -> Optional[List[str]]:
        """
        从chunk中提取表头信息

        使用table_parser获取准确的表头信息，而不是生成通用列名。
        """
        metadata = chunk.metadata or {}

        # 如果有table_parser，使用它来获取准确的表头
        if table_parser:
            headers = table_parser.get_headers_for_chunk(chunk)
            if headers:
                return headers

        # 回退到从metadata中尝试获取列信息
        column_count = metadata.get("column_count", 0)

        # 生成通用列名（最后的选择）
        if column_count > 0:
            return [f"列{i+1}" for i in range(column_count)]

        return None

    def _parse_row_values(self, values: List[str], headers: List[str]) -> Dict[str, Any]:
        """
        解析行数据值，进行类型转换

        Args:
            values: 原始值列表
            headers: 表头列表

        Returns:
            解析后的键值对字典
        """
        row_data = {}

        for i, (header, value) in enumerate(zip(headers, values)):
            if i < len(values):
                parsed_value = self._parse_value(values[i].strip())
                row_data[header] = parsed_value
            else:
                # 缺失值设为null
                row_data[header] = None

        return row_data

    def _parse_value(self, value: str) -> Any:
        """
        解析单个值，进行类型转换

        Args:
            value: 原始字符串值

        Returns:
            转换后的值（int/float/str/null）
        """
        value = value.strip()

        # NULL 处理
        if value == "NULL" or value == "":
            return None

        # 数值类型检测
        if re.match(r'^-?\d+$', value):
            return int(value)

        if re.match(r'^-?\d*\.\d+$', value):
            return float(value)

        # 日期格式检测（ISO 8601）
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            return value  # 保持字符串格式的日期

        # 其他情况返回字符串
        return value

    def _build_rag_format(self, chunk: DocumentChunk, headers: List[str], row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建RAG格式的数据结构

        Args:
            chunk: DocumentChunk对象
            headers: 表头列表
            row_data: 解析后的行数据

        Returns:
            RAG格式的字典
        """
        metadata = chunk.metadata or {}

        rag_data = {
            # 公共元数据（带_前缀）
            "_doc_id": chunk.doc_id,
            "_row_id": metadata.get("table_start_row", 0),
            "_type": "table_row",
            "_page": chunk.page,
            "_src": self._build_source_path(metadata),

            # 业务数据（无前缀，直接使用中文列名）
            **row_data
        }

        return rag_data

    def _build_source_path(self, metadata: Dict[str, Any]) -> str:
        """
        构建数据源路径

        Args:
            metadata: 元数据字典

        Returns:
            数据源路径字符串
        """
        file_name = metadata.get("file_name", "")
        sheet_name = metadata.get("sheet_name", "")
        table_type = metadata.get("table_type", "")

        if file_name and sheet_name:
            if table_type == "structured_row":
                return f"{file_name}#{sheet_name}"
            else:
                return f"{file_name}"

        return "unknown_source"

    def _create_empty_row_format(self, chunk: DocumentChunk) -> str:
        """
        创建空行格式的RAG数据

        Args:
            chunk: DocumentChunk对象

        Returns:
            空行格式的JSONL字符串
        """
        metadata = chunk.metadata or {}

        rag_data = {
            "_doc_id": chunk.doc_id,
            "_row_id": metadata.get("table_start_row", 0),
            "_type": "table_row",
            "_page": chunk.page,
            "_src": self._build_source_path(metadata),
            "_empty": True,
            "_raw_text": chunk.text or ""
        }

        return json.dumps(rag_data, ensure_ascii=False)


def format_chunks_as_rag_jsonl(
    chunks: List[DocumentChunk],
    *,
    enable_backward_compatible: bool = True,
    table_parser: Optional['TableHeaderParser'] = None
) -> List[str]:
    """
    将DocumentChunk列表格式化为RAG优化的JSONL格式

    Args:
        chunks: DocumentChunk列表
        enable_backward_compatible: 是否保持向后兼容
        table_parser: 表格解析器，用于提取准确的表头信息

    Returns:
        RAG优化的JSONL字符串列表
    """
    formatter = RAGJsonlFormatter(enable_backward_compatible=enable_backward_compatible)

    results = []
    for chunk in chunks:
        if chunk.type == ContentType.TABLE and table_parser:
            # For table chunks, pass the table_parser and all chunks for better header extraction
            formatted_chunk = formatter._format_table_chunk_with_parser(chunk, table_parser, chunks)
        else:
            formatted_chunk = formatter.format_chunk(chunk)
        results.append(formatted_chunk)

    return results


# 便捷函数
def to_rag_jsonl(chunk: DocumentChunk, *, enable_backward_compatible: bool = True) -> str:
    """
    将单个DocumentChunk转换为RAG优化的JSONL格式

    Args:
        chunk: DocumentChunk对象
        enable_backward_compatible: 是否保持向后兼容

    Returns:
        RAG优化的JSONL字符串
    """
    formatter = RAGJsonlFormatter(enable_backward_compatible=enable_backward_compatible)
    return formatter.format_chunk(chunk)