"""
Base exporter classes.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class Exporter(ABC):
    """Base exporter class."""

    @abstractmethod
    def export(self, dot_content: str, output_path: str) -> str:
        """Export DOT content to specified format."""
        pass


class FileExporter(Exporter):
    """Base class for file-based exporters."""

    def _ensure_directory(self, file_path: str) -> None:
        """Ensure the directory for the file exists."""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
