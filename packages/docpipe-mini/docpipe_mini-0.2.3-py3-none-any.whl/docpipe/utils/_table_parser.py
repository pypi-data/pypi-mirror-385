"""
表格解析工具

提供表格数据的解析和格式化功能，支持RAG优化的输出格式。
"""

from __future__ import annotations

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from .._types import DocumentChunk


class TableHeaderParser:
    """
    表格头部解析器

    用于从表格chunks中提取表头信息，并建立表头与数据的映射关系。
    """

    def __init__(self):
        """初始化表格头部解析器"""
        self.table_groups: Dict[str, List[DocumentChunk]] = defaultdict(list)
        self.headers_cache: Dict[str, List[str]] = {}

    def add_chunk(self, chunk: DocumentChunk):
        """
        添加表格chunk到解析器

        Args:
            chunk: DocumentChunk对象
        """
        if chunk.type != "table":
            return

        metadata = chunk.metadata or {}
        table_type = metadata.get("table_type", "")

        if table_type in ["structured_table", "structured_row"]:
            doc_id = chunk.doc_id
            self.table_groups[doc_id].append(chunk)

    def parse_all_tables(self) -> Dict[str, Dict[str, Any]]:
        """
        解析所有表格组，提取表头和结构信息

        Returns:
            表格解析结果字典
        """
        results = {}

        for doc_id, chunks in self.table_groups.items():
            if doc_id in self.headers_cache:
                # 使用缓存的表头
                headers = self.headers_cache[doc_id]
            else:
                # 解析表头
                headers = self._extract_headers_from_chunks(chunks)
                self.headers_cache[doc_id] = headers

            # 分析表格结构
            table_info = self._analyze_table_structure(chunks, headers)

            results[doc_id] = {
                "headers": headers,
                "structure": table_info,
                "chunks": chunks
            }

        return results

    def _extract_headers_from_chunks(self, chunks: List[DocumentChunk]) -> List[str]:
        """
        从chunks中提取表头信息

        Args:
            chunks: DocumentChunk列表

        Returns:
            表头列表
        """
        # 查找主表chunk（structured_table类型）
        main_table = None
        for chunk in chunks:
            metadata = chunk.metadata or {}
            if metadata.get("table_type") == "structured_table":
                main_table = chunk
                break

        if not main_table:
            return []

        text = main_table.text or ""
        return self._parse_header_text(text)

    def _parse_header_text(self, text: str) -> List[str]:
        """
        解析表头文本

        Args:
            text: 表头文本

        Returns:
            清理后的表头列表
        """
        lines = text.split('\n')

        for line in lines:
            if line.startswith("[HEADER]"):
                continue  # 跳过[HEADER]行

            if "|" in line:
                # 找到包含管道符的行，解析为表头
                headers = [col.strip() for col in line.split('|')]
                return self._clean_headers(headers)

        return []

    def _clean_headers(self, headers: List[str]) -> List[str]:
        """
        清理表头，移除空值和无效字符

        Args:
            headers: 原始表头列表

        Returns:
            清理后的表头列表
        """
        cleaned = []
        for header in headers:
            if header and header.strip():
                # 移除多余的空格和特殊字符
                clean_header = re.sub(r'\s+', ' ', header.strip())
                cleaned.append(clean_header)

        return cleaned

    def _analyze_table_structure(self, chunks: List[DocumentChunk], headers: List[str]) -> Dict[str, Any]:
        """
        分析表格结构

        Args:
            chunks: DocumentChunk列表
            headers: 表头列表

        Returns:
            表格结构信息
        """
        structure = {
            "headers": headers,
            "column_count": len(headers),
            "row_count": 0,
            "main_table": None,
            "row_chunks": []
        }

        main_table = None
        row_chunks = []

        for chunk in chunks:
            metadata = chunk.metadata or {}
            table_type = metadata.get("table_type", "")

            if table_type == "structured_table":
                main_table = chunk
            elif table_type == "structured_row":
                row_chunks.append(chunk)
                structure["row_count"] += 1

        structure["main_table"] = main_table
        structure["row_chunks"] = row_chunks

        return structure

    def get_headers_for_chunk(self, chunk: DocumentChunk) -> Optional[List[str]]:
        """
        获取指定chunk对应的表头

        Args:
            chunk: DocumentChunk对象

        Returns:
            表头列表，如果无法获取则返回None
        """
        if chunk.type != "table":
            return None

        metadata = chunk.metadata or {}
        parent_doc_id = metadata.get("parent_table_doc_id")
        doc_id = chunk.doc_id

        # 尝试使用父表的doc_id获取表头
        target_doc_id = parent_doc_id or doc_id

        if target_doc_id in self.headers_cache:
            return self.headers_cache[target_doc_id]

        # 如果缓存中没有，实时解析
        if target_doc_id in self.table_groups:
            chunks = self.table_groups[target_doc_id]
            headers = self._extract_headers_from_chunks(chunks)
            self.headers_cache[target_doc_id] = headers
            return headers

        return None


class TableRowParser:
    """
    表格行解析器

    用于解析表格行数据，并进行类型转换和格式化。
    """

    def __init__(self, headers: List[str]):
        """
        初始化表格行解析器

        Args:
            headers: 表头列表
        """
        self.headers = headers
        self.column_count = len(headers)

    def parse_row_text(self, text: str) -> Dict[str, Any]:
        """
        解析行文本数据

        Args:
            text: 行文本内容

        Returns:
            解析后的键值对字典
        """
        lines = text.split('\n')

        # 跳过行号标识
        data_line = None
        for line in lines:
            if not line.startswith("row=") and "|" in line:
                data_line = line
                break

        if not data_line:
            return self._create_empty_row()

        # 解析数据值
        values = [val.strip() for val in data_line.split('|')]
        return self._parse_values(values)

    def _parse_values(self, values: List[str]) -> Dict[str, Any]:
        """
        解析数据值，进行类型转换

        Args:
            values: 原始值列表

        Returns:
            解析后的键值对字典
        """
        row_data = {}

        for i, header in enumerate(self.headers):
            if i < len(values):
                parsed_value = self._parse_single_value(values[i])
                row_data[header] = parsed_value
            else:
                # 缺失值设为null
                row_data[header] = None

        return row_data

    def _parse_single_value(self, value: str) -> Any:
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

        # 整数检测
        if re.match(r'^-?\d+$', value):
            try:
                return int(value)
            except ValueError:
                pass

        # 浮点数检测
        if re.match(r'^-?\d*\.\d+$', value):
            try:
                return float(value)
            except ValueError:
                pass

        # 科学计数法检测
        if re.match(r'^-?\d+\.?\d*[eE][-+]?\d+$', value):
            try:
                return float(value)
            except ValueError:
                pass

        # 日期格式检测（ISO 8601）
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            return value  # 保持字符串格式的日期

        # 时间格式检测
        if re.match(r'^\d{2}:\d{2}:\d{2}$', value):
            return value  # 保持字符串格式的时间

        # 布尔值检测
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'

        # 其他情况返回字符串
        return value

    def _create_empty_row(self) -> Dict[str, Any]:
        """
        创建空行数据

        Returns:
            空行数据的字典
        """
        return {header: None for header in self.headers}


def create_table_parser() -> TableHeaderParser:
    """
    创建表格头部解析器的便捷函数

    Returns:
        TableHeaderParser实例
    """
    return TableHeaderParser()


def create_row_parser(headers: List[str]) -> TableRowParser:
    """
    创建表格行解析器的便捷函数

    Args:
        headers: 表头列表

    Returns:
        TableRowParser实例
    """
    return TableRowParser(headers)