"""
Image exporter using Graphviz.
"""

import tempfile
import subprocess
from pathlib import Path
from typing import Optional
from ..utils.exceptions import ExportError, SystemValidationError
from .base import FileExporter
from ..utils.validators import SystemValidator


class ImageExporter(FileExporter):
    """Exporter for image formats using Graphviz."""

    SUPPORTED_FORMATS = {"png", "svg", "pdf", "jpg", "gif"}

    def __enter__():
        """Validate Graphviz existence on enter"""

        check, error = SystemValidator().validate_graphviz_existense()
        if not check:
            raise SystemValidationError(error)

    def export(
        self, dot_content: str, output_path: str, format: Optional[str] = None
    ) -> str:
        """Export DOT content to an image file."""
        if format is None:
            format = Path(output_path).suffix[1:].lower()

        if format not in self.SUPPORTED_FORMATS:
            raise ExportError(f"Unsupported format: {format}")

        self._ensure_directory(output_path)

        # Write DOT code to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dot", delete=False, encoding="utf-8"
        ) as f:
            f.write(dot_content)
            dot_file = f.name

        try:
            # Use Graphviz to render
            result = subprocess.run(
                ["dot", f"-T{format}", dot_file, "-o", output_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise ExportError(f"Graphviz error: {result.stderr}")

            return output_path
        except subprocess.TimeoutExpired:
            raise ExportError("Graphviz rendering timed out")
        except FileNotFoundError:
            raise ExportError(
                "Graphviz not found. Please install Graphviz: "
                "https://graphviz.org/download/"
            )
        finally:
            Path(dot_file).unlink(missing_ok=True)
