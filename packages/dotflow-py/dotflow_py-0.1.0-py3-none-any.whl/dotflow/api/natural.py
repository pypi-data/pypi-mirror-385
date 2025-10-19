"""
Natural language API implementation using operator overloading.
"""

from typing import Union, Optional
from ..core.models import EdgeStyle
from ..utils.validators import validate_node_id


class NaturalLanguageAPI:
    """Natural language API using operator overloading."""

    def __init__(self, interpreter: "DotInterpreter"):
        self._interpreter = interpreter
        self._last_node: Optional[str] = None
        self._pending_label: Optional[str] = None

    def __rshift__(
        self, other: Union[str, "NaturalLanguageAPI"]
    ) -> "NaturalLanguageAPI":
        """Override >> operator for flow creation: flow >> "A" >> "B" """
        if isinstance(other, str):
            validate_node_id(other)
            if self._last_node:
                # Create connection from last node to new node
                self._interpreter.connect(self._last_node, other, self._pending_label)
                self._pending_label = None
            else:
                # Start new flow
                self._interpreter.start(other)

            self._last_node = other
            return self

        return self

    def __or__(self, other: str) -> "NaturalLanguageAPI":
        """Override | operator for labels: flow >> "A" >> "B" | "Label" """
        if isinstance(other, str):
            self._pending_label = other
            # self._last_node = other
        return self

    def __getitem__(self, key: str) -> "NaturalLanguageAPI":
        """Override [] for conditional flows: flow >> "A" >> "B"["Label"]"""
        if isinstance(key, str) and self._last_node and self._interpreter.edges:
            # Find the most recent edge and update its label
            for edge in reversed(self._interpreter.edges):
                if edge.to_node == self._last_node:
                    edge.label = key
                    break
        return self

    def __floordiv__(self, other: str) -> "NaturalLanguageAPI":
        """Override // for dashed connections: flow >> "A" // "B" """
        if isinstance(other, str) and self._last_node:
            self._interpreter.connect(self._last_node, other, style=EdgeStyle.DASHED)
            self._last_node = other
        return self

    def reset(self):
        """Reset the state for a new flow."""
        self._last_node = None
        self._pending_label = None
