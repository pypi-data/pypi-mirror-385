"""
Tests for core functionality.
"""

import pytest
from ..core.interpreter import DotInterpreter
from ..core.models import NodeShape  # , Direction
from ..utils.exceptions import NodeNotFoundError, ValidationError
from ..core.themes import Theme


class TestDotInterpreter:
    def test_basic_creation(self):
        flow = DotInterpreter("test_flow")
        assert flow.name == "test_flow"
        assert flow.theme == Theme.DEFAULT

    def test_node_creation(self):
        flow = DotInterpreter()
        flow.start("A")
        assert "A" in flow.nodes
        assert flow.nodes["A"].shape == NodeShape.ELLIPSE

    def test_connection(self):
        flow = DotInterpreter()
        flow.start("A").process("B").connect("A", "B")
        assert len(flow.edges) == 1
        assert flow.edges[0].from_node == "A"
        assert flow.edges[0].to_node == "B"

    def test_node_not_found(self):
        flow = DotInterpreter()
        flow.start("A")
        with pytest.raises(NodeNotFoundError):
            flow.connect("A", "Nonexistent")

    def test_invalid_node_id(self):
        flow = DotInterpreter()
        with pytest.raises(ValidationError):
            flow.start("invalid-node")
