"""
Validation utilities.
"""

import re
import subprocess
from typing import Any, Tuple
from pathlib import Path
from .exceptions import ValidationError


def validate_node_id(node_id: str) -> None:
    """Validate node ID format."""
    if "[" in node_id:
        node_id = node_id.split("[")[0]
    if not node_id:
        raise ValidationError("Node ID cannot be empty")

    if not re.match(r"^[a-zA-Z_]\w*$", node_id):
        raise ValidationError(
            f"Invalid node ID: '{node_id}'. "
            "Must start with a letter or underscore and contain only "
            "alphanumeric characters and underscores."
        )


def node_id_validator(node_id: str) -> bool:
    """Validate node ID format."""
    if not node_id:
        return False

    if not re.match(r"^[a-zA-Z_]\w*$", node_id):
        return False
    return True


def validate_label(label: str) -> None:
    """Validate label content."""
    if not label:
        return

    if len(label) > 1000:
        raise ValidationError("Label too long (max 1000 characters)")

    # Check for potentially dangerous characters
    if "\x00" in label:
        raise ValidationError("Label contains null character")


def validate_style_value(value: Any) -> None:
    """Validate style value."""
    if value is None:
        raise ValidationError("Style value cannot be None")

    if isinstance(value, str) and len(value) > 100:
        raise ValidationError("Style value too long")


class SystemValidator:
    """Validates system requirements and dependencies."""

    @staticmethod
    def validate_graphviz_existense() -> Tuple[bool, str]:
        """Check if Mermaid CLI is installed and accessible."""
        try:
            result = subprocess.run(
                ["dot", "-V"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Graphviz detected"
            else:
                return False, "Graphviz not properly installed"

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            return False, f"Graphviz check failed: {str(e)}"

    @staticmethod
    def validate_file_permissions(temp_dir: Path) -> Tuple[bool, str]:
        """Validate write permissions in temporary directory."""
        try:
            test_file = temp_dir / "permission_test.txt"
            test_file.write_text("test")
            test_file.unlink()
            return True, "Write permissions verified"
        except (OSError, IOError) as e:
            return False, f"Insufficient permissions: {str(e)}"
