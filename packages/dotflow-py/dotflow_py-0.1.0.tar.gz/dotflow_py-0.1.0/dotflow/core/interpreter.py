"""
Main interpreter class that orchestrates all functionality.
"""

from typing import Dict, Union, List, Optional, Any, TYPE_CHECKING
from contextlib import contextmanager
from pathlib import Path
from .models import (
    Node,
    Edge,
    Cluster,
    NodeShape,
    EdgeStyle,
    EdgeStyleConfig,
    Direction,
)
from .themes import Theme, ThemeManager
from ..utils.validators import validate_node_id, validate_label
from ..utils.exceptions import (
    NodeNotFoundError,
)
from ..exporters.dot import DotExporter
from ..exporters.image import ImageExporter
from ..core.models import NodeStyle

if TYPE_CHECKING:
    from ..api.pythonic import PythonicAPI
    from ..api.natural import NaturalLanguageAPI
    from ..api.dsl import TextualDSL


class DotInterpreter:
    """
    Main interpreter for creating DOT diagrams with multiple API styles.
    """

    def __init__(
        self,
        name: str = "flow",
        theme: Theme = Theme.DEFAULT,
        direction: Direction = Direction.TOP_DOWN,
    ):
        self.name = name
        self.theme = theme
        self.direction = direction
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.clusters: Dict[str, Cluster] = {}
        self._current_cluster: Optional[str] = None
        self._theme_config = ThemeManager.get_theme_config(theme)
        # API instances (lazy-loaded)
        self._pythonic_api: Optional["PythonicAPI"] = None
        self._natural_api: Optional["NaturalLanguageAPI"] = None
        self._dsl_api: Optional["TextualDSL"] = None

        # Natural language API state
        self._last_node: Optional[str] = None
        self._pending_label: Optional[str] = None

        # Initialize default graph attributes
        self._graph_attrs = {
            "bgcolor": self._theme_config["bg_color"],
            "rankdir": direction.value.replace('"', "").replace("'", ""),
        }

    @property
    def py(self) -> "PythonicAPI":
        """Access Pythonic API methods."""
        if self._pythonic_api is None:
            from ..api.pythonic import PythonicAPI

            self._pythonic_api = PythonicAPI(self)
        return self._pythonic_api

    @property
    def nl(self) -> "NaturalLanguageAPI":
        """Access natural language API."""
        if self._natural_api is None:
            from ..api.natural import NaturalLanguageAPI

            self._natural_api = NaturalLanguageAPI(self)
        return self._natural_api

    @property
    def dsl(self) -> "TextualDSL":
        """Access textual DSL parser."""
        if self._dsl_api is None:
            from ..api.dsl import TextualDSL

            self._dsl_api = TextualDSL(self)
        return self._dsl_api

    # Natural language API operators
    def __rshift__(self, other: Union[str, "DotInterpreter"]) -> "DotInterpreter":
        """Override >> operator for flow creation: flow >> "A" >> "B" """

        return self.nl.__rshift__(other)

    def __or__(self, other: str) -> "DotInterpreter":
        """Override | operator for labels: flow >> "A" >> "B" | "Label" """
        return self.nl.__or__(other)

    def __getitem__(self, key: str) -> "DotInterpreter":
        """Override [] for conditional flows: flow >> "A" >> "B"["Label"]"""
        return self.nl.__getitem__(key)

    def __floordiv__(self, other: str) -> "DotInterpreter":
        """Override // for dashed connections: flow >> "A" // "B" """
        return self.nl.__floordiv__(other)

    def __divmod__(self, other: str) -> "DotInterpreter":
        """Override // for dashed connections: flow >> "A" // "B" """
        return self.nl.__divmod__(other)

    # Textual DSL methods
    def parse_dsl(self, dsl_text: str) -> "DotInterpreter":
        """Parse DSL text (convenience method)."""
        return self.dsl.parse_dsl(dsl_text)

    def _create_node(
        self, node_id: str, label: str, shape: NodeShape, **kwargs
    ) -> Node:
        """Create a node with theme-appropriate styling."""
        # Remove whitespaces
        node_id = node_id.replace(" ", "")
        # Validate id and label
        validate_node_id(node_id)
        validate_label(label)

        # Merge theme style with any custom styles
        theme_style = self._theme_config["node_style"]
        custom_style = theme_style.__dict__.copy()
        custom_style.update(kwargs)

        style = NodeStyle(**custom_style)
        node = Node(node_id, label, shape, style)

        if self._current_cluster and self._current_cluster in self.clusters:
            self.clusters[self._current_cluster].add_node(node)
        else:
            self.nodes[node_id] = node

        return node

    def _create_edge(
        self,
        from_node: str,
        to_node: str,
        label: Optional[str] = None,
        style: EdgeStyle = EdgeStyle.SOLID,
        **kwargs,
    ) -> Edge:
        """Create an edge with theme-appropriate styling."""
        # remove whitespaces
        from_node = from_node.replace(" ", "")
        to_node = to_node.replace(" ", "")
        # Validate nodes exist
        if from_node not in self.nodes and not any(
            from_node in [node.id for node in cluster.nodes]
            for cluster in self.clusters.values()
        ):
            raise NodeNotFoundError(f"Source node '{from_node}' not found")

        if to_node not in self.nodes and not any(
            to_node in [node.id for node in cluster.nodes]
            for cluster in self.clusters.values()
        ):
            raise NodeNotFoundError(f"Target node '{to_node}' not found")

        if label:
            validate_label(label)

        # Merge theme style with any custom styles
        theme_style = self._theme_config["edge_style"]
        custom_style = theme_style.__dict__.copy()
        custom_style.update({"style": style, **kwargs})

        edge_style = EdgeStyleConfig(**custom_style)
        edge = Edge(from_node, to_node, label, edge_style)

        if self._current_cluster and self._current_cluster in self.clusters:
            self.clusters[self._current_cluster].add_edge(edge)
        else:
            self.edges.append(edge)

        return edge

    def node(self, *args, **kwargs):
        return self._create_node(*args, **kwargs)

    def edge(self, *args, **kwargs):
        return self._create_edge(*args, **kwargs)

    # Core API methods
    def start(self, node_id: str, label: Optional[str] = None) -> "DotInterpreter":
        """Start a flow with an initial node (ellipse shape)."""
        label = label or node_id
        self._create_node(node_id, label, NodeShape.ELLIPSE)
        return self

    def process(self, node_id: str, label: Optional[str] = None) -> "DotInterpreter":
        """Create a process node (rectangle shape)."""
        label = label or node_id
        self._create_node(node_id, label, NodeShape.RECTANGLE)
        return self

    def decision(
        self, node_id: str, question: Optional[str] = None
    ) -> "DotInterpreter":
        """Create a decision node (diamond shape)."""
        label = question or node_id
        self._create_node(node_id, label, NodeShape.DIAMOND)
        return self

    def end(self, node_id: str, label: Optional[str] = None) -> "DotInterpreter":
        """Create an end node (ellipse shape)."""
        label = label or node_id
        self._create_node(
            node_id, label, NodeShape.ELLIPSE, style="filled", fillcolor="#ffcccc"
        )
        return self

    def input_output(
        self, node_id: str, label: Optional[str] = None
    ) -> "DotInterpreter":
        """Create an input/output node (parallelogram shape)."""
        label = label or node_id
        self._create_node(node_id, label, NodeShape.PARALLELOGRAM)
        return self

    def connect(
        self,
        from_node: str,
        to_node: str,
        label: Optional[str] = None,
        style: EdgeStyle = EdgeStyle.SOLID,
    ) -> "DotInterpreter":
        """Connect two nodes with an optional label."""
        self._create_edge(from_node, to_node, label, style)
        return self

    @contextmanager
    def cluster(self, name: str, label: str, **style_kwargs):
        """Context manager for creating clusters."""
        previous_cluster = self._current_cluster
        self._current_cluster = name

        cluster_style = {
            "style": "filled",
            "color": "lightgrey",
            "fillcolor": "lightgrey:white",
            "gradientangle": "90",
            **style_kwargs,
        }
        self.clusters[name] = Cluster(name, label, cluster_style)

        try:
            yield self
        finally:
            self._current_cluster = previous_cluster

    def set_graph_attr(self, key: str, value: Any):
        """Set a graph-level attribute."""
        self._graph_attrs[key] = value

    def to_dot(self) -> str:
        """Generate DOT language code."""
        lines = [f"digraph {self.name} {{"]

        # Add graph attributes
        for key, value in self._graph_attrs.items():
            lines.append(f'  {key}="{value}";')

        lines.append('  node [fontname="Arial", fontsize=12];')
        lines.append('  edge [fontname="Arial", fontsize=10];')
        lines.append("")

        # Add nodes
        for node in self.nodes.values():
            lines.append(f"  {node.to_dot()}")

        # Add edges
        for edge in self.edges:
            lines.append(f"  {edge.to_dot()}")

        # Add clusters
        for cluster in self.clusters.values():
            lines.extend([f"  {line}" for line in cluster.to_dot()])

        lines.append("}")
        return "\n".join(lines)

    def get_cluster(self):
        """Returns cached clusters for the active instance"""
        return self.clusters

    def get_nodes(self):
        """Returns cached nodes for the active instance"""
        return self.nodes

    def render(self, format: str, output):
        output_path = Path(f"{output.split('.', 1)[0]}.{format}")

        if format == "dot":
            DotExporter().export(self.to_dot(), str(output_path))
        else:
            ImageExporter().export(self.to_dot(), str(output_path), format)

    def __str__(self) -> str:
        return self.to_dot()


class FlowExpr:
    def __init__(self, flow, expr):
        self.flow = flow
        self.expr = expr

    def __str__(self):
        return f"{self.flow} // {self.expr}"
