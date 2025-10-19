"""
Data models for DOT elements.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import html


class NodeShape(Enum):
    RECTANGLE = "rect"
    ELLIPSE = "ellipse"
    DIAMOND = "diamond"
    CIRCLE = "circle"
    TRIANGLE = "triangle"
    HEXAGON = "hexagon"
    PARALLELOGRAM = "parallelogram"
    ROUNDED_RECTANGLE = "rounded"


class EdgeStyle(Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"
    BOLD = "bold"


class Direction(Enum):
    TOP_DOWN = "TB"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"
    BOTTOM_UP = "BT"


@dataclass
class NodeStyle:
    color: str = "black"
    fillcolor: str = "white"
    fontcolor: str = "black"
    fontsize: int = 12
    fontname: str = "Arial"
    style: str = "filled"
    width: float = 0.75
    height: float = 0.5


@dataclass
class EdgeStyleConfig:
    color: str = "black"
    fontcolor: str = "black"
    fontsize: int = 10
    style: EdgeStyle = EdgeStyle.SOLID


@dataclass
class Node:
    id: str
    label: str
    shape: NodeShape
    style: NodeStyle

    def to_dot(self) -> str:
        attrs = [
            f'label="{html.escape(self.label)}"',
            f"shape={self.shape.value}",
            f'color="{self.style.color}"',
            f'fillcolor="{self.style.fillcolor}"',
            f'fontcolor="{self.style.fontcolor}"',
            f"fontsize={self.style.fontsize}",
            f'fontname="{self.style.fontname}"',
            f'style="{self.style.style}"',
            f"width={self.style.width}",
            f"height={self.style.height}",
        ]
        return f"{self.id} [{' '.join(attrs)}];"


@dataclass
class Edge:
    from_node: str
    to_node: str
    label: Optional[str] = None
    style: EdgeStyleConfig = None

    def __post_init__(self):
        if self.style is None:
            self.style = EdgeStyleConfig()

    def to_dot(self) -> str:
        attrs = [f"style={self.style.style.value}"]
        if self.label:
            attrs.append(f'label="{html.escape(self.label)}"')
        attrs.extend(
            [
                f'color="{self.style.color}"',
                f'fontcolor="{self.style.fontcolor}"',
                f"fontsize={self.style.fontsize}",
            ]
        )
        return f"{self.from_node} -> {self.to_node} [{' '.join(attrs)}];"


class Cluster:
    def __init__(self, name: str, label: str, style: Optional[Dict[str, Any]] = None):
        self.name = f"cluster_{name}"
        self.label = label
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.style = style or {
            "style": "filled",
            "color": "lightgrey",
            "fillcolor": "lightgrey:white",
            "gradientangle": "90",
        }

    def add_node(self, node: Node):
        self.nodes.append(node)

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def to_dot(self) -> List[str]:
        lines = [f"subgraph {self.name} {{"]
        lines.append(f'  label="{self.label}";')
        for key, value in self.style.items():
            lines.append(f'  {key}="{value}";')

        for node in self.nodes:
            lines.append(f"  {node.to_dot()}")
        for edge in self.edges:
            lines.append(f"  {edge.to_dot()}")
        lines.append("}")
        return lines
