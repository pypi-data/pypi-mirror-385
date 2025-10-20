"""
Minimal protocols for docpipe document-to-jsonl serializer.

Focus: simple serialize() interface with zero dependency core.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, Optional, List, Dict, Any, Union, Protocol
from contextlib import contextmanager

from ._types import DocumentChunk


class LoggingMixin:
    """
    Mixin class providing structured logging functionality for serializers.

    This mixin provides consistent logging patterns across all serializer implementations,
    including timing information, structured context, and configurable log levels.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._timing_contexts: Dict[str, float] = {}
        self._enable_performance_logging: bool = True

    def configure_logging(
        self,
        *,
        enable_performance_logging: bool = True,
        log_level: str = "INFO"
    ) -> 'LoggingMixin':
        """
        Configure logging settings.

        Args:
            enable_performance_logging: Whether to log timing information
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

        Returns:
            Self for method chaining
        """
        self._enable_performance_logging = enable_performance_logging
        self._logger.setLevel(getattr(logging, log_level.upper()))
        return self

    @contextmanager
    def log_timing(self, operation: str, *, level: str = "info", **extra_context):
        """
        Context manager for timing operations and logging performance metrics.

        Args:
            operation: Description of the operation being timed
            level: Log level for the timing message
            **extra_context: Additional context to include in log message

        Yields:
            None
        """
        if not self._enable_performance_logging:
            yield
            return

        start_time = time.time()
        operation_id = f"{operation}_{int(start_time * 1000)}"

        try:
            self._log_with_context(
                f"Starting {operation}",
                level=level,
                operation_id=operation_id,
                operation=operation,
                **extra_context
            )
            yield
        finally:
            duration = time.time() - start_time
            self._log_with_context(
                f"Completed {operation} in {duration:.2f}s",
                level=level,
                operation_id=operation_id,
                operation=operation,
                duration=duration,
                **extra_context
            )

    def _log_with_context(self, message: str, level: str = "info", **context) -> None:
        """
        Log a message with structured context information.

        Args:
            message: The log message
            level: Log level (debug, info, warning, error)
            **context: Additional context information
        """
        log_method = getattr(self._logger, level.lower())
        if context:
            # Format context values for better readability
            formatted_context = []
            for k, v in context.items():
                if isinstance(v, (list, tuple)):
                    if len(v) <= 3:
                        formatted_context.append(f"{k}={v}")
                    else:
                        formatted_context.append(f"{k}={v[:3]}...({len(v)} total)")
                elif isinstance(v, str) and len(v) > 50:
                    formatted_context.append(f"{k}={v[:47]}...")
                else:
                    formatted_context.append(f"{k}={v}")

            context_str = " | ".join(formatted_context)
            log_method(f"{message} | {context_str}")
        else:
            log_method(message)

    def log_operation_start(self, operation: str, **context) -> None:
        """Log the start of an operation."""
        self._log_with_context(f"Starting {operation}", level="info", **context)

    def log_operation_success(self, operation: str, **context) -> None:
        """Log successful completion of an operation."""
        self._log_with_context(f"Successfully completed {operation}", level="info", **context)

    def log_operation_error(self, operation: str, error: Exception, **context) -> None:
        """Log an error during operation execution."""
        self._log_with_context(
            f"Error in {operation}: {str(error)}",
            level="error",
            error_type=type(error).__name__,
            **context
        )

    def log_processing_stats(self, stats: Dict[str, Any], **context) -> None:
        """
        Log processing statistics and metrics.

        Args:
            stats: Dictionary of processing statistics
            **context: Additional context information
        """
        stats_str = ", ".join(f"{k}: {v}" for k, v in stats.items())
        self._log_with_context(
            f"Processing stats: {stats_str}",
            level="info",
            **context
        )

    def log_configuration(self, **config) -> None:
        """Log current configuration settings."""
        config_items = [f"{k}={v}" for k, v in config.items() if v is not None]
        if config_items:
            self._log_with_context(
                f"Configuration: {', '.join(config_items)}",
                level="debug"
            )

    def log_debug(self, message: str, **context) -> None:
        """Log debug message with context."""
        self._log_with_context(message, level="debug", **context)

    def log_info(self, message: str, **context) -> None:
        """Log info message with context."""
        self._log_with_context(message, level="info", **context)

    def log_warning(self, message: str, **context) -> None:
        """Log warning message with context."""
        self._log_with_context(message, level="warning", **context)

    def log_error(self, message: str, **context) -> None:
        """Log error message with context."""
        self._log_with_context(message, level="error", **context)

    def log_progress(self, current: int, total: int, operation: str = "Processing", **context) -> None:
        """
        Log progress information for long-running operations.

        Args:
            current: Current progress count
            total: Total items to process
            operation: Description of the operation
            **context: Additional context information
        """
        percentage = (current / total * 100) if total > 0 else 0
        self._log_with_context(
            f"{operation} progress: {current}/{total} ({percentage:.1f}%)",
            level="info",
            current=current,
            total=total,
            percentage=percentage,
            **context
        )

    def log_performance_metric(self, metric_name: str, value: float, unit: str = "", **context) -> None:
        """
        Log a performance metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement (optional)
            **context: Additional context information
        """
        metric_str = f"{metric_name}={value:.3f}"
        if unit:
            metric_str += f" {unit}"

        self._log_with_context(
            f"Performance metric: {metric_str}",
            level="info",
            metric_name=metric_name,
            value=value,
            unit=unit,
            **context
        )

    def log_data_summary(self, data_description: str, count: int, **context) -> None:
        """
        Log a summary of processed data.

        Args:
            data_description: Description of the data type
            count: Number of items processed
            **context: Additional context information
        """
        self._log_with_context(
            f"Data summary: {count} {data_description}",
            level="info",
            data_type=data_description,
            count=count,
            **context
        )


class SerializerMixin:
    """
    Mixin class providing common serializer functionality.

    Provides context manager support and internal configuration management
    for document serializers. This ensures consistent behavior across all
    serializer implementations in the docpipe project.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._header_row: Optional[int] = None
        self._custom_headers: Optional[List[str]] = None
        self._rag_format: bool = False
        self._enable_backward_compatible: bool = True
        self._max_mem_mb: Optional[int] = None

    def configure_header_injection(
        self,
        *,
        header_row: Optional[int] = None,
        custom_headers: Optional[List[str]] = None
    ) -> 'SerializerMixin':
        """
        Configure header injection settings internally.

        Args:
            header_row: Row number to use as headers (1-based)
            custom_headers: Custom list of headers to use

        Returns:
            Self for method chaining
        """
        if header_row is not None and custom_headers is not None:
            raise ValueError("Cannot specify both header_row and custom_headers")
        if header_row is not None and header_row < 1:
            raise ValueError("header_row must be a positive integer (1-based)")
        if custom_headers is not None and not custom_headers:
            raise ValueError("custom_headers cannot be empty")

        self._header_row = header_row
        self._custom_headers = custom_headers
        return self

    def configure_rag_format(
        self,
        *,
        enable_backward_compatible: bool = True
    ) -> 'SerializerMixin':
        """
        Configure RAG output format settings.

        Args:
            enable_backward_compatible: Whether to maintain pipe format for non-tables

        Returns:
            Self for method chaining
        """
        self._rag_format = True
        self._enable_backward_compatible = enable_backward_compatible
        return self

    def configure_memory_limit(self, max_mem_mb: Optional[int]) -> 'SerializerMixin':
        """
        Configure memory limit for processing.

        Args:
            max_mem_mb: Maximum memory in MB to use

        Returns:
            Self for method chaining
        """
        self._max_mem_mb = max_mem_mb
        return self

    def __enter__(self) -> 'SerializerMixin':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        # Reset configuration on exit
        self._header_row = None
        self._custom_headers = None
        self._rag_format = False
        self._enable_backward_compatible = True
        self._max_mem_mb = None

    @contextmanager
    def with_config(
        self,
        *,
        header_row: Optional[int] = None,
        custom_headers: Optional[List[str]] = None,
        rag_format: bool = False,
        enable_backward_compatible: bool = True,
        max_mem_mb: Optional[int] = None
    ):
        """
        Temporary configuration context manager.

        Args:
            header_row: Row number to use as headers (1-based)
            custom_headers: Custom list of headers to use
            rag_format: Whether to output RAG format
            enable_backward_compatible: Whether to maintain pipe format for non-tables
            max_mem_mb: Maximum memory in MB to use
        """
        # Store current config
        original_config = {
            'header_row': self._header_row,
            'custom_headers': self._custom_headers,
            'rag_format': self._rag_format,
            'enable_backward_compatible': self._enable_backward_compatible,
            'max_mem_mb': self._max_mem_mb
        }

        try:
            # Apply temporary config
            if header_row is not None or custom_headers is not None:
                self.configure_header_injection(header_row=header_row, custom_headers=custom_headers)
            if rag_format:
                self.configure_rag_format(enable_backward_compatible=enable_backward_compatible)
            if max_mem_mb is not None:
                self.configure_memory_limit(max_mem_mb)

            yield self
        finally:
            # Restore original config
            self._header_row = original_config['header_row']
            self._custom_headers = original_config['custom_headers']
            self._rag_format = original_config['rag_format']
            self._enable_backward_compatible = original_config['enable_backward_compatible']
            self._max_mem_mb = original_config['max_mem_mb']


class DocumentSerializer(ABC):
    """
    Abstract base class for document serializers.

    This is the primary interface - all document processing flows through
    this simple, type-safe interface.
    """

    @abstractmethod
    def can_serialize(self, file_path: Path) -> bool:
        """
        Check if this serializer can handle the given file.

        Args:
            file_path: Path to the document file

        Returns:
            True if the file format is supported
        """
        ...

    @abstractmethod
    def serialize(
        self,
        file_path: Path,
        *,
        max_mem_mb: Optional[int] = None
    ) -> Iterator[DocumentChunk]:
        """
        Serialize document into coordinate-aware chunks.

        Args:
            file_path: Path to the document file
            max_mem_mb: Optional memory limit

        Yields:
            DocumentChunk objects with coordinates and text
        """
        ...

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """List of supported file extensions."""
        ...


class SerializerRegistry:
    """
    Registry for document serializers with plugin support.
    """

    def __init__(self):
        self._serializers: list[DocumentSerializer] = []

    def register(self, serializer: DocumentSerializer) -> None:
        """Register a new serializer."""
        self._serializers.append(serializer)

    def get_serializer(self, file_path: Path) -> Optional[DocumentSerializer]:
        """Get appropriate serializer for file."""
        for serializer in self._serializers:
            if serializer.can_serialize(file_path):
                return serializer
        return None

    def list_supported_formats(self) -> dict[str, list[str]]:
        """Get all supported formats."""
        return {
            serializer.__class__.__name__: serializer.supported_extensions
            for serializer in self._serializers
        }


# Global registry instance
_registry = SerializerRegistry()


def get_serializer(file_path: Path) -> Optional[DocumentSerializer]:
    """Get serializer for file from global registry."""
    return _registry.get_serializer(file_path)


def register_serializer(serializer: DocumentSerializer) -> None:
    """Register serializer in global registry."""
    _registry.register(serializer)


def list_supported_formats() -> dict[str, list[str]]:
    """List all supported formats from global registry."""
    return _registry.list_supported_formats()