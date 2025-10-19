"""
DOT file exporter.
"""

from .base import FileExporter


class DotExporter(FileExporter):
    """Exporter for DOT files."""

    def export(self, dot_content: str, output_path: str) -> str:
        """Export DOT content to a .dot file."""
        self._ensure_directory(output_path)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dot_content)

        return output_path
