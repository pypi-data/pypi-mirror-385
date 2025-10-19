# Simple DOT interpreter + force-directed layout + SVG renderer
# This script is self-contained and uses only Python standard libraries.
# It supports a small DOT subset: graph/digraph, node IDs, edges like A -> B or A -- B,
# simple attributes in brackets (label="...", color=...), and node/edge statements.
#
# Run and it will produce /mnt/data/output_graph.svg which you can download.
import os
from math import sqrt, cos, sin, pi
import random
import re
from xml.sax.saxutils import escape


# ------------------ Parser ------------------
def parse_dot(dot_text):
    dot_text = re.sub(r"//.*", "", dot_text)  # strip single-line comments
    dot_text = re.sub(r"/\*.*?\*/", "", dot_text, flags=re.S)  # strip block comments
    header = re.match(
        r'\s*(strict\s+)?(digraph|graph)\s+([\w"-]+)?\s*\{', dot_text, flags=re.I
    )
    directed = False
    if header:
        directed = header.group(2).lower() == "digraph"
    # Extract body inside outermost braces
    body_match = re.search(r"\{(.*)\}\s*$", dot_text, flags=re.S)
    body = body_match.group(1) if body_match else dot_text
    # Tokenize by semicolons (not perfect but fine for simple DOT)
    statements = [s.strip() for s in re.split(r";\s*(?![^[]*\])", body) if s.strip()]
    nodes = {}
    edges = []
    for stmt in statements:
        # Edge: A -> B  or A -- B (with optional attributes)
        m = re.match(
            r"(?P<src>[^->\[\;]+?)(\s*(->|--)\s*)(?P<dst>[^;\[]+)(\s*\[(?P<attr>[^\]]*)\])?",
            stmt,
        )
        if m:
            src = m.group("src").strip().strip('"')
            dst = m.group("dst").strip().strip('"')
            attr = parse_attrs(m.group("attr") or "")
            nodes.setdefault(src, {})
            nodes.setdefault(dst, {})
            edges.append({"src": src, "dst": dst, "attr": attr})
            continue
        # Node with attributes: A [label="Hi"]
        m2 = re.match(r"(?P<id>[^ \t\[]+)\s*\[(?P<attr>[^\]]*)\]", stmt)
        if m2:
            nid = m2.group("id").strip().strip('"')
            attr = parse_attrs(m2.group("attr") or "")
            nodes.setdefault(nid, {}).update(attr)
            continue
        # Node alone: A
        m3 = re.match(r'^[\w"\-\.]+$', stmt)
        if m3:
            nid = stmt.strip().strip('"')
            nodes.setdefault(nid, {})
            continue
        # fallback: try to parse any id tokens
        tokens = re.findall(r"[\w\-\.]+", stmt)
        for t in tokens[:1]:
            nodes.setdefault(t, {})
    return {"directed": directed, "nodes": nodes, "edges": edges}


def parse_attrs(attr_text):
    attrs = {}
    # split on commas but allow commas inside quotes
    parts = re.findall(r'(\w+)\s*=\s*("[^"]*"|\'[^\']*\'|[^,]+)', attr_text)
    for k, v in parts:
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (
            v.startswith("'") and v.endswith("'")
        ):
            v = v[1:-1]
        attrs[k.strip()] = v
    return attrs


# ------------------ Simple Force-Directed Layout ------------------
def layout_force_directed(nodes, edges, width=1200, height=800, iterations=500):
    # nodes: dict of id -> attr
    # edges: list of {'src','dst'}
    n = len(nodes)
    if n == 0:
        return {}
    # initial positions random in box
    positions = {
        nid: (random.uniform(50, width - 50), random.uniform(50, height - 50))
        for nid in nodes
    }
    disp = {nid: [0.0, 0.0] for nid in nodes}
    area = width * height
    k = sqrt(area / n)
    # constants
    t = max(width, height) / 10.0  # initial "temperature"
    dt = t / (iterations + 1.0)
    # adjacency for attractive forces
    adj = {nid: set() for nid in nodes}
    for e in edges:
        adj[e["src"]].add(e["dst"])
        adj[e["dst"]].add(e["src"])
    for iter_count in range(iterations):
        for v in nodes:
            disp[v][0] = 0.0
            disp[v][1] = 0.0
        # repulsive
        for v in nodes:
            for u in nodes:
                if u == v:
                    continue
                dx = positions[v][0] - positions[u][0]
                dy = positions[v][1] - positions[u][1]
                dist = sqrt(dx * dx + dy * dy) + 1e-9
                force = (k * k) / dist
                disp[v][0] += (dx / dist) * force
                disp[v][1] += (dy / dist) * force
        # attractive (edges)
        for v in nodes:
            for u in adj[v]:
                dx = positions[v][0] - positions[u][0]
                dy = positions[v][1] - positions[u][1]
                dist = sqrt(dx * dx + dy * dy) + 1e-9
                force = (dist * dist) / k
                disp[v][0] -= (dx / dist) * force
                disp[v][1] -= (dy / dist) * force
        # limit max displacement by temperature and apply
        for v in nodes:
            dx, dy = disp[v]
            disp_len = sqrt(dx * dx + dy * dy)
            if disp_len > 1e-9:
                x = positions[v][0] + (dx / disp_len) * min(disp_len, t)
                y = positions[v][1] + (dy / disp_len) * min(disp_len, t)
            else:
                x, y = positions[v]
            # keep inside box margins
            margin = 40
            x = min(width - margin, max(margin, x))
            y = min(height - margin, max(margin, y))
            positions[v] = (x, y)
        t -= dt
    return positions


# ------------------ SVG Renderer ------------------
ARROW_DEF = """
<marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto" markerUnits="strokeWidth">
  <path d="M0,0 L10,5 L0,10 z" />
</marker>
"""


def render_svg(
    graph,
    positions,
    filename=os.path.expanduser("~/Documents/output_graph.svg"),
    width=1200,
    height=800,
):
    nodes = graph["nodes"]
    edges = graph["edges"]
    directed = graph["directed"]
    node_radius = 18
    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )
    svg.append("<defs>" + ARROW_DEF + "</defs>")
    # background
    svg.append(f'<rect width="100%" height="100%" fill="#ffffff"/>')
    # edges
    for e in edges:
        src = e["src"]
        dst = e["dst"]
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        # line offset to avoid overlapping node circle centers
        dx = x2 - x1
        dy = y2 - y1
        dist = sqrt(dx * dx + dy * dy) + 1e-9
        ox = (dx / dist) * node_radius
        oy = (dy / dist) * node_radius
        sx, sy = x1 + ox, y1 + oy
        ex, ey = x2 - ox, y2 - oy
        # simple straight line; could add bezier for curved edges later
        marker = ' marker-end="url(#arrow)"' if directed else ""
        label = e.get("attr", {}).get("label", None)
        svg.append(
            f'<line x1="{sx:.2f}" y1="{sy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}" stroke="#333" stroke-width="1.6"{marker} />'
        )
        if label:
            lx, ly = (sx + ex) / 2, (sy + ey) / 2
            svg.append(
                f'<text x="{lx:.2f}" y="{ly - 6:.2f}" font-size="12" text-anchor="middle">{escape(label)}</text>'
            )
    # nodes (circles + labels)
    for nid, attr in nodes.items():
        x, y = positions[nid]
        label = attr.get("label", nid)
        title = attr.get("title", "")
        svg.append(f'<g class="node">')
        svg.append(
            f'  <circle cx="{x:.2f}" cy="{y:.2f}" r="{node_radius}" fill="#f2f2f9" stroke="#333" stroke-width="1.4"/>'
        )
        svg.append(
            f'  <text x="{x:.2f}" y="{y + 4:.2f}" font-size="12" text-anchor="middle">{escape(label)}</text>'
        )
        if title:
            svg.append(f"  <title>{escape(title)}</title>")
        svg.append(f"</g>")
    svg.append("</svg>")
    svg_text = "\n".join(svg)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg_text)
    return filename


# ------------------ Example usage ------------------
example_dot = r"""
digraph G {
  node [shape=circle];
  rankdir=LR;
  A [label="Start"];
  B [label="Check"];
  C [label="Process"];
  D [label="End"];
  A -> B [label="ok"];
  B -> C [label="yes"];
  B -> D [label="no"];
  C -> D;
  E; // isolated node
}
"""

graph = parse_dot(example_dot)
positions = layout_force_directed(
    graph["nodes"], graph["edges"], width=1200, height=800, iterations=400
)
out_path = render_svg(
    graph,
    positions,
    filename=os.path.expanduser("~/Documents/output_graph.svg"),
    width=1200,
    height=800,
)

out_path
