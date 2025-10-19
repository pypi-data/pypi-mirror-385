"""
Textual DSL parser implementation.
"""

import re
from typing import Optional
from ..core.models import NodeShape, EdgeStyle, Direction
from ..utils.exceptions import DSLParseError


class TextualDSL:
    """Textual Domain Specific Language parser."""

    def __init__(self, interpreter: "DotInterpreter"):
        self._interpreter = interpreter

    def parse_dsl(self, dsl_text: str) -> "DotInterpreter":
        """
        Parse textual DSL input.

        Supported syntax:
        - Node connections: "A -> B : Label"
        - Node definitions: "A [shape=rect, label='Custom']"
        - Decisions: "A {decision} -> B : Yes"
        - Comments: "# This is a comment"
        """
        lines = dsl_text.strip().split("\n")
        line_number = 0

        for line in lines:
            line_number += 1
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            try:
                self._parse_line(line, line_number)
            except Exception as e:
                raise DSLParseError(f"Error parsing line {line_number}: {line}") from e

        return self._interpreter

    def _parse_line(self, line: str, line_number: int):
        """Parse a single line of DSL text."""
        # Try node connection first: "A -> B : Label"
        connection_match = re.match(
            r"(\w+)\s*(?:\{([^}]+)\})?\s*->\s*(\w+)\s*(?::\s*(.+))?", line
        )
        if connection_match:
            from_node, modifiers, to_node, label = connection_match.groups()
            self._parse_connection(from_node, to_node, label, modifiers)
            return

        # Try node definition: "A [shape=rect, label='Custom']"
        node_match = re.match(r"(\w+)\s*\[(.+)\]", line)
        if node_match:
            node_id, attrs_str = node_match.groups()
            self._parse_node_definition(node_id, attrs_str)
            return

        # Try standalone node: "A"
        if re.match(r"^\w+$", line):
            self._interpreter.process(line)
            return

        # Try dg attributes deirection=LR
        # if re.match(r"^\w+=\s", line):
        #  return

        raise DSLParseError(f"Unrecognized DSL syntax at line {line_number}")

    def _parse_connection(
        self,
        from_node: str,
        to_node: str,
        label: Optional[str],
        modifiers: Optional[str],
    ):
        """Parse a connection between nodes."""
        style = EdgeStyle.SOLID

        if modifiers:
            if "dashed" in modifiers:
                style = EdgeStyle.DASHED
            elif "dotted" in modifiers:
                style = EdgeStyle.DOTTED
            elif "bold" in modifiers:
                style = EdgeStyle.BOLD

        self._interpreter.connect(from_node, to_node, label, style)

    def _parse_node_definition(self, node_id: str, attrs_str: str):
        """Parse node attributes definition."""
        attrs = {}

        # Simple attribute parsing
        for attr_match in re.finditer(r"(\w+)\s*=\s*([^,]+)", attrs_str):
            key, value = attr_match.groups()
            attrs[key.strip()] = value.strip().strip("'\"")

        shape = NodeShape.RECTANGLE
        label = node_id

        if "shape" in attrs:
            shape_name = attrs["shape"].upper()
            try:
                shape = NodeShape[shape_name]
            except KeyError:
                shape = NodeShape.RECTANGLE

        if "label" in attrs:
            label = attrs["label"]

        self._interpreter._create_node(node_id, label, shape)

    def _parse_dg_attrs(self, node_id: str, attrs_str: str):
        """Parse node attributes definition."""
        attrs = {}

        # Simple attribute parsing
        for attr_match in re.finditer(r"(\w+)\s*=\s+", attrs_str):
            key, value = attr_match.groups()
            attrs[key.strip()] = value.strip().strip("'\"")

        if "direction" in attrs:
            dg_direction = attrs["direction"].upper()
            try:
                dg_dict = Direction.__dict__.copy()
                if dg_direction in dg_dict.values():
                    direction = dg_dict[dg_direction]
                    direction = self._interpreter.direction = direction
                    print(direction)
            except KeyError:
                pass

        # self._interpreter._create_node(node_id, label, shape)
