"""
File I/O utilities and abstractions for splurge_sql_generator.

This module provides testable abstractions for file operations and configuration
reading to reduce coupling and improve testability.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import splurge_safe_io.exceptions as safe_io_exc
import yaml  # type: ignore[import-untyped]
from splurge_safe_io.safe_text_file_reader import SafeTextFileReader
from splurge_safe_io.safe_text_file_writer import open_safe_text_writer

from splurge_sql_generator.exceptions import ConfigurationError, FileError

DOMAINS = ["file", "utilities"]


class FileIoAdapter(ABC):
    """Abstract interface for file I/O operations."""

    @abstractmethod
    def read_text(self, path: str | Path, *, encoding: str = "utf-8") -> str:
        """
        Read file as text.

        Args:
            path: File path to read
            encoding: Text encoding (default: utf-8)

        Returns:
            File contents as string

        Raises:
            FileError: If file cannot be read
        """

    @abstractmethod
    def write_text(self, path: str | Path, content: str, *, encoding: str = "utf-8") -> None:
        """
        Write text to file.

        Args:
            path: File path to write to
            content: Text content to write
            encoding: Text encoding (default: utf-8)

        Raises:
            FileError: If file cannot be written
        """

    @abstractmethod
    def exists(self, path: str | Path) -> bool:
        """
        Check if file exists.

        Args:
            path: File path to check

        Returns:
            True if file exists, False otherwise
        """


class SafeTextFileIoAdapter(FileIoAdapter):
    """Adapter wrapping SafeTextFileReader/Writer with error translation."""

    def __init__(self) -> None:
        """Initialize the adapter."""
        self._logger = logging.getLogger(__name__)

    def read_text(self, path: str | Path, *, encoding: str = "utf-8") -> str:
        """
        Read file as text using SafeTextFileReader.

        Args:
            path: File path to read
            encoding: Text encoding (default: utf-8)

        Returns:
            File contents as string

        Raises:
            FileError: If file cannot be read
        """
        try:
            reader = SafeTextFileReader(path, encoding=encoding)
            content = reader.read()
            if not isinstance(content, str):
                raise FileError(f"Unexpected return type from SafeTextFileReader: {type(content)}")
            return content
        except safe_io_exc.SplurgeSafeIoPathValidationError as e:
            raise FileError(f"Invalid file path: {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoFileNotFoundError as e:
            raise FileError(f"File not found: {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoFilePermissionError as e:
            raise FileError(f"Permission denied reading {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoFileDecodingError as e:
            raise FileError(f"Encoding error reading {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoOsError as e:
            raise FileError(f"OS error reading {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoUnknownError as e:
            raise FileError(f"Unknown error reading {path}", details=str(e.message)) from e

    def write_text(self, path: str | Path, content: str, *, encoding: str = "utf-8") -> None:
        """
        Write text to file using SafeTextFileWriter.

        Args:
            path: File path to write to
            content: Text content to write
            encoding: Text encoding (default: utf-8)

        Raises:
            FileError: If file cannot be written
        """
        try:
            with open_safe_text_writer(path, encoding=encoding) as writer:
                writer.write(content)
        except safe_io_exc.SplurgeSafeIoPathValidationError as e:
            raise FileError(f"Invalid file path: {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoFileEncodingError as e:
            raise FileError(f"Encoding error writing to {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoFilePermissionError as e:
            raise FileError(f"Permission denied writing to {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoOsError as e:
            raise FileError(f"OS error writing to {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoFileOperationError as e:
            raise FileError(f"File operation error writing to {path}", details=str(e.message)) from e
        except safe_io_exc.SplurgeSafeIoUnknownError as e:
            raise FileError(f"Unknown error writing to {path}", details=str(e.message)) from e

    def exists(self, path: str | Path) -> bool:
        """
        Check if file exists.

        Args:
            path: File path to check

        Returns:
            True if file exists, False otherwise
        """
        return Path(path).exists()


class YamlConfigReader:
    """Read and parse YAML configuration files."""

    def __init__(self, file_io: FileIoAdapter | None = None) -> None:
        """
        Initialize the YAML config reader.

        Args:
            file_io: Optional FileIoAdapter. If None, uses SafeTextFileIoAdapter.
        """
        self._file_io = file_io or SafeTextFileIoAdapter()
        self._logger = logging.getLogger(__name__)

    def read(self, path: str | Path) -> dict[str, Any]:
        """
        Read and parse YAML file.

        Args:
            path: Path to YAML file

        Returns:
            Parsed YAML content as dictionary

        Raises:
            FileError: If file cannot be read
            ConfigurationError: If YAML is invalid or not a dictionary
        """
        try:
            content = self._file_io.read_text(path)
            parsed = yaml.safe_load(content)

            if not isinstance(parsed, dict):
                self._logger.warning(
                    f"YAML file {path} must contain a dictionary, got {type(parsed).__name__}. "
                    "Returning empty dictionary."
                )
                return {}

            self._logger.debug(f"Successfully loaded {len(parsed)} entries from YAML file: {path}")
            return parsed

        except FileError:
            # Re-raise file errors as-is
            raise
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML syntax in {path}", details=str(e)) from e
        except Exception as e:
            raise ConfigurationError(f"Error reading YAML from {path}", details=str(e)) from e
