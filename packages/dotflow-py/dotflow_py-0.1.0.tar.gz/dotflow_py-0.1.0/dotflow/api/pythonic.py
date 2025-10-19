"""
Pythonic API implementation.
"""

from typing import Optional
from ..core.models import NodeShape, EdgeStyle
from ..utils.validators import validate_node_id, validate_label


class PythonicAPI:
    """Pythonic API methods for DotInterpreter."""

    def __init__(self, interpreter: "DotInterpreter"):
        self._interpreter = interpreter

    def node(
        self,
        node_id: str,
        label: Optional[str] = None,
        shape: NodeShape = NodeShape.RECTANGLE,
        **style_kwargs,
    ) -> "DotInterpreter":
        """Explicit node creation with custom shape and style."""
        label = label or node_id
        self._interpreter._create_node(node_id, label, shape, **style_kwargs)
        return self._interpreter

    def rectangle(self, node_id: str, label: Optional[str] = None) -> "DotInterpreter":
        """Create a rectangle node."""
        return self.node(node_id, label, NodeShape.RECTANGLE)

    def diamond(self, node_id: str, label: Optional[str] = None) -> "DotInterpreter":
        """Create a diamond node."""
        return self.node(node_id, label, NodeShape.DIAMOND)

    def circle(self, node_id: str, label: Optional[str] = None) -> "DotInterpreter":
        """Create a circle node."""
        return self.node(node_id, label, NodeShape.CIRCLE)

    def ellipse(self, node_id: str, label: Optional[str] = None) -> "DotInterpreter":
        """Create an ellipse node."""
        return self.node(node_id, label, NodeShape.ELLIPSE)

    def rounded_rect(
        self, node_id: str, label: Optional[str] = None
    ) -> "DotInterpreter":
        """Create a rounded rectangle node."""
        return self.node(node_id, label, NodeShape.ROUNDED_RECTANGLE)

    def dashed_connect(
        self, from_node: str, to_node: str, label: Optional[str] = None
    ) -> "DotInterpreter":
        """Create a dashed connection."""
        return self._interpreter.connect(from_node, to_node, label, EdgeStyle.DASHED)

    def dotted_connect(
        self, from_node: str, to_node: str, label: Optional[str] = None
    ) -> "DotInterpreter":
        """Create a dotted connection."""
        return self._interpreter.connect(from_node, to_node, label, EdgeStyle.DOTTED)

    def bold_connect(
        self, from_node: str, to_node: str, label: Optional[str] = None
    ) -> "DotInterpreter":
        """Create a bold connection."""
        return self._interpreter.connect(from_node, to_node, label, EdgeStyle.BOLD)
