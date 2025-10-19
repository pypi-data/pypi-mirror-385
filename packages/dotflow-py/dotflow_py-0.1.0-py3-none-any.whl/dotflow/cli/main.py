"""
Main CLI entry point for DotFlow.
"""

import os
import click
import sys
from pathlib import Path
from typing import Optional

from ..core.interpreter import DotInterpreter
from ..core.themes import Theme
from ..core.models import Direction, NodeShape
from ..exporters.image import ImageExporter
from ..exporters.dot import DotExporter
from ..utils.exceptions import DotFlowError
from ..utils.colors import fg, bg, rs
from ..utils.validators import node_id_validator
from ..utils.screen import clear_screen

RESET = rs


@click.group()
@click.version_option()
def cli():
    """DotFlow - Python-based DOT language interpreter with multiple API styles."""
    pass


@cli.command()
@click.argument("output", type=click.Path(), default=os.path.curdir)
@click.option("--name", "-n", default="flow", help="Name of the flow diagram")
@click.option(
    "--theme",
    "-t",
    type=click.Choice([t.value for t in Theme]),
    default="default",
    help="Color theme for the diagram",
)
@click.option(
    "--direction",
    "-d",
    type=click.Choice([d.value for d in Direction]),
    default="TB",
    help="Layout direction",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["png", "svg", "pdf", "dot"]),
    default="png",
    help="Output format",
)
@click.option("--dsl-file", "-i", type=click.File("r"), help="Input DSL file")
@click.option("--dsl-text", "-s", help="DSL text directly from command line")
def generate(
    output: str,
    name: str,
    theme: str,
    direction: str,
    format: str,
    dsl_file: Optional[click.File],
    dsl_text: Optional[str],
):
    """Generate a flow diagram from DSL input."""

    try:
        # Create interpreter
        flow = DotInterpreter(
            name=name, theme=Theme(theme), direction=Direction(direction)
        )

        # Get DSL content
        dsl_content = ""
        if dsl_file:
            dsl_content = dsl_file.read()
        elif dsl_text:
            dsl_content = dsl_text
        else:
            click.echo(
                "Error: Either --dsl-file or --dsl-text must be provided", err=True
            )
            sys.exit(1)

        # Parse DSL and generate diagram
        flow.parse_dsl(dsl_content)

        # Remove initial extension
        output = f"{output.split('.', 1)[0]}.{format}"
        # Export based on format
        if format == "dot":
            exporter = DotExporter()
            exporter.export(flow.to_dot(), output)
        else:
            exporter = ImageExporter()
            exporter.export(flow.to_dot(), output, format)

        click.echo(f"Successfully generated {format.upper()} diagram: {output}")

    except DotFlowError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("output", type=click.Path())
@click.option("--name", "-n", default="flow", help="Name of the flow diagram")
@click.option(
    "--theme",
    "-t",
    type=click.Choice([t.value for t in Theme]),
    default="default",
    help="Color theme for the diagram",
)
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
def wizard(output: str, name: str, theme: str, interactive: bool):
    """Interactive wizard for creating flow diagrams."""

    try:
        flow = DotInterpreter(name=name, theme=Theme(theme))

        if interactive:
            InterractiveSession(flow, output=output)._run_wizard()
        else:
            _run_quick_wizard(flow)

        # Always generate both DOT and PNG
        dot_exporter = DotExporter()
        image_exporter = ImageExporter()

        dot_path = Path(output).with_suffix(".dot")
        png_path = Path(output).with_suffix(".png")

        dot_exporter.export(flow.to_dot(), str(dot_path))
        image_exporter.export(flow.to_dot(), str(png_path))

        click.echo(f"{fg.GREEN}Successfully generated{RESET}:")
        click.echo(f"  - DOT file: {fg.BLUE}{dot_path}{RESET}")
        click.echo(f"  - PNG file: {fg.BLUE}{png_path}{RESET}")

    except KeyboardInterrupt:
        click.echo("\nQuit")
        sys.exist(1)
    except DotFlowError as e:
        click.echo(f"{fg.RED}Error: {fg.YELLOW}{e}{RESET}", err=True)
        # sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {fg.RED}{e}{RESET}", err=True)
        # sys.exit(1)


class InterractiveSession:
    """Run interactive wizard for building flows."""

    def __init__(self, flow: DotInterpreter, output=click.Path()):
        self.flow = flow
        self.output = output
        click.echo("🐍 DotFlow Interactive Wizard")
        click.echo("=" * 40)

        self.nodes = []
        self.current_node = None
        self.method_map = {
            1: self.add_node,
            2: self.add_process,
            3: self.add_decision,
            4: self.add_end,
            5: self.connect_nodes,
            6: self.add_cluster,
            # 7: exit subgraph
            # 8: self.all_options,
            # 9: exit
            10: self.save_progress,
            11: self.preview_diagram,
            12: self.show_flow,
            13: self.clear_screen,
        }
        self.cluster_nodes = []
        self.current_cluster = None
        self.all_options = False

    def add_node(self):
        node_id = click.prompt("Enter node ID")
        self.flow.start(node_id)
        self.nodes.append(node_id)
        self.current_node = node_id
        click.echo(f"{fg.GREEN}✓{RESET} Added start node: {node_id}")

    def add_process(self):
        node_id = click.prompt("Enter node ID")
        label = click.prompt("Enter label (optional)", default=node_id)
        self.flow.process(node_id, label)
        self.nodes.append(node_id)
        self.current_node = node_id
        click.echo(f"{fg.GREEN}✓{RESET} Added process node: {node_id}")

    def add_decision(self):
        node_id = click.prompt("Enter node ID")
        question = click.prompt("Enter question", default=node_id)
        self.flow.decision(node_id, question)
        self.nodes.append(node_id)
        self.current_node = node_id
        click.echo(f"{fg.GREEN}✓{RESET} Added decision node: {node_id}")

    def add_end(self):
        node_id = click.prompt("Enter node ID")
        self.flow.end(node_id)
        self.nodes.append(node_id)
        self.current_node = node_id
        click.echo(f"{fg.GREEN}✓{RESET} Added end node: {node_id}")

    def connect_nodes(self):
        if len(self.nodes) < 2:
            click.echo(f"{fg.RED}Need at least 2 nodes to connect{RESET}")
            return

        click.echo("Available nodes: " + f"{RESET}, {fg.CYAN}".join(self.nodes))
        from_node = click.prompt("From node", default=self.current_node)
        to_node = click.prompt("To node")
        label = click.prompt("Label (optional)", default="")

        if from_node not in self.nodes:
            click.echo(f"Node {fg.YELLOW}{from_node}{fg.YELLOW} not found")
            return
        if to_node not in self.nodes:
            click.echo(f"Node {fg.YELLOW}{to_node}{fg.YELLOW} not found")
            return

        self.flow.connect(from_node, to_node, label if label else None)
        click.echo(
            f"{fg.GREEN}✓{fg.BBLUE} Connected {fg.DWHITE}{from_node}{fg.BWHITE} -> {fg.DWHITE}{to_node}{RESET}"
        )

    def add_cluster(self):
        cluster_name = click.prompt("Enter cluster/subgraph name")
        cluster_label = click.prompt(
            "Enter cluster/subgraph label", default=cluster_name
        )
        self.cluster_nodes = []
        self.subgraph = True
        with self.flow.cluster(cluster_name, cluster_label):
            click.echo(
                f"{bg.BLACK}Now adding nodes to cluster/subgraph '{bg.GREEN}{fg.DWHITE}{cluster_name}{RESET}'..."
            )
            while self._run_wizard(is_subgraph=True) != 0:
                node_id = click.prompt("Enter node ID for cluster/subgraph")
                while not node_id_validator(node_id):
                    click.echo(
                        f"{fg.RED}Invalid node id. {fg.MAGENTA}Must start with a letter or underscore{RESET}"
                    )
                    node_id = click.prompt(
                        f"Enter node ID for cluster/subgraph eg({fg.LWHITE}cluster1{RESET})"
                    )
                self.flow.process(node_id)
                self.nodes.append(node_id)
                self.cluster_nodes.append(node_id)
                self.current_node = node_id
            click.echo(f"{fg.FYELLOW}Exited subgraph{RESET}")

    def show_flow(self):
        click.echo(f"\n{fg.DWHITE}Current flow:{RESET}")
        click.echo(rf"{fg.GREEN}{self.flow.to_dot()}{RESET}")
        click.echo()

    def save_progress(self):
        # Always generate both DOT and PNG
        dot_exporter = DotExporter()
        image_exporter = ImageExporter()

        dot_path = Path(f"{self.output.split('.')[0]}_checkpoint").with_suffix(".dot")
        png_path = Path(f"{self.output.split('.')[0]}_preview").with_suffix(".png")

        dot_exporter.export(self.flow.to_dot(), str(dot_path))
        image_exporter.export(self.flow.to_dot(), str(png_path))

        click.echo(f"{fg.GREEN}Progess saved{RESET}:")
        click.echo(f"  - DOT file: {fg.BLUE}{dot_path}{RESET}")

    def preview_diagram(self):
        # Always generate both DOT and PNG
        image_exporter = ImageExporter()

        png_path = Path(f"{self.output.split('.')[0]}_preview").with_suffix(".png")

        image_exporter.export(self.flow.to_dot(), str(png_path))

        click.echo(f"{fg.GREEN}Previe saved{RESET}:")
        click.echo(f"  - PNG file: {fg.BLUE}{png_path}{RESET}")

    def clear_screen(self):
        clear_screen()

    def show_all_options(self):
        click.echo("  10. Save Progess")
        click.echo("  11. Preview diagram")
        click.echo("  12. View flow")
        click.echo("  13. Clear Screen")

    def _run_wizard(self, is_subgraph=False):
        """Run interactive wizard for building flows."""

        while True:
            try:
                click.echo(f"{fg.DWHITE}Options:{RESET}")

                if not is_subgraph:
                    click.echo("  1. Add start node (ellipse)")
                    click.echo("  2. Add process node (rect)")
                    click.echo("  3. Add decision node (diamond)")
                    click.echo("  4. Add end node")
                    click.echo("  5. Connect nodes")
                    click.echo(f"  6. Add cluster({fg.LBLUE}subgraph{RESET})")
                    click.echo("  7. Finish and generate")
                else:
                    click.echo("  1. Add subgraph start node (ellipse)")
                    click.echo("  2. Add subgraph process node (rect)")
                    click.echo("  3. Add subgraph decision node (diamond)")
                    click.echo("  4. Add subgraph end node")
                    click.echo("  5. Connect subgraph nodes")
                    click.echo(f"  6. Add sub-cluster({fg.LBLUE}sub-subgraph{RESET})")
                    click.echo("  7. Exit subgraph")

                click.echo(f"  8. {fg.LBLUE}More Options{RESET}")
                click.echo("  9. Exit session")
                if self.all_options:
                    self.show_all_options()

                choice = click.prompt(f"{fg.DWHITE}Choose an option{RESET}", type=int)

                self.all_options = choice == 8

                if choice == 7:
                    return 0

                if choice == 9:
                    click.echo("\nQuit")
                    sys.exit(1)

                action = self.method_map.get(choice, None)

                if not action:
                    if choice != 8:
                        click.echo(f"{fg.YELLOW} Invalid option{RESET}")
                    else:
                        self.clear_screen()
                    continue

                action()

            except click.ClickException:
                click.echo("\nQuit")
                sys.exist(1)
            except Exception as e:
                click.echo(f"{fg.RED}Wizard Error: {fg.YELLOW}{e}{RESET}", err=True)
                continue

    def load_file(self):
        """TODO: Implement loading of dot file to resume editing"""
        pass


def _run_quick_wizard(flow: DotInterpreter):
    """Run quick wizard with predefined flow."""
    click.echo("🚀 DotFlow Quick Wizard")
    click.echo("Creating a sample workflow...")

    # Create a sample flow
    (
        flow.start("Start")
        .process("Process Data")
        .decision("Data Valid?")
        .connect("Data Valid?", "End", label="Yes")
        .connect("Data Valid?", "Process Data", label="No")
    )


@cli.command()
@click.argument("dsl_file", type=click.File("r"))
def validate(dsl_file: click.File):
    """Validate DSL syntax without generating output."""

    try:
        flow = DotInterpreter()
        dsl_content = dsl_file.read()
        flow.parse_dsl(dsl_content)

        click.echo(f"{fg.GREEN}✓{RESET}DSL syntax is valid!")
        click.echo(f"Found {len(flow.nodes)} nodes and {len(flow.edges)} edges")

        # Show summary
        if flow.nodes:
            click.echo("\nNodes:")
            for node_id, node in flow.nodes.items():
                click.echo(f"  - {node_id} ({node.shape.value}): {node.label}")

        if flow.edges:
            click.echo("\nEdges:")
            for edge in flow.edges:
                label_info = f" : {edge.label}" if edge.label else ""
                click.echo(f"  - {edge.from_node} -> {edge.to_node}{label_info}")

    except DotFlowError as e:
        click.echo(f"{fg.RED}❌{RESET} DSL validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def themes():
    """List available color themes."""
    click.echo("🎨 Available Themes:")
    click.echo("")

    for theme in Theme:
        flow = DotInterpreter(theme=theme)
        flow.start("Sample").process("Node").end("End")

        click.echo(f"  {theme.value:<12} - {_get_theme_description(theme)}")

    click.echo("")
    click.echo("Use: dotflow generate --theme THEME_NAME")


def _get_theme_description(theme: Theme) -> str:
    """Get description for a theme."""
    descriptions = {
        Theme.DEFAULT: "Clean black and white",
        Theme.DARK: "Dark mode with light text",
        Theme.COLORFUL: "Bright yellow nodes",
        Theme.BLUE: "Blue color scheme",
        Theme.GREEN: "Green color scheme",
        Theme.MONOCHROME: "Simple monochrome",
    }
    return descriptions.get(theme, "Custom theme")


@cli.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["png", "svg", "pdf", "dot"]),
    default="png",
    help="Output format",
)
@click.option(
    "--theme",
    "-t",
    type=click.Choice([t.value for t in Theme]),
    default="default",
    help="Color theme",
)
def examples(format: str, theme: str):
    """Generate example diagrams."""

    examples_dir = Path("dotflow_examples")
    examples_dir.mkdir(exist_ok=True)

    examples_data = [
        ("simple_flow", _create_simple_flow),
        ("decision_tree", _create_decision_tree),
        ("with_clusters", _create_clustered_flow),
        ("complex_workflow", _create_complex_workflow),
    ]

    for example_name, creator_func in examples_data:
        try:
            flow = DotInterpreter(example_name, Theme(theme))
            creator_func(flow)

            if format == "dot":
                output_path = examples_dir / f"{example_name}.dot"
                DotExporter().export(flow.to_dot(), str(output_path))
            else:
                output_path = examples_dir / f"{example_name}.{format}"
                ImageExporter().export(flow.to_dot(), str(output_path), format)

            click.echo(f"✓ Generated {example_name}: {output_path}")

        except Exception as e:
            click.echo(f"✗ Failed to generate {example_name}: {e}", err=True)


def _create_simple_flow(flow: DotInterpreter):
    """Create a simple linear flow."""
    (flow.start("Start").process("Step 1").process("Step 2").end("End"))


def _create_decision_tree(flow: DotInterpreter):
    """Create a decision tree flow."""
    (
        flow.start("Start")
        .process("Input Data")
        .decision("Valid")
        .process("Process Data")
        .decision("Success")
        .process("Error Handling")
        .end("End")
        .connect("Start", "Input Data", "Initialize")
        .connect("Input Data", "Valid", "Data In")
        .connect("Valid", "ProcessData", label="Yes")
        .connect("Valid", "Error Handling", label="No")
        .connect("ProcessData", "Error Handling", label="Processing Error")
        .connect("ProcessData", "Success", label="Yes")
        .connect("Success", "End", label="Yes")
        .connect("Success", "Error Handling", label="No")
    )


def _create_clustered_flow(flow: DotInterpreter):
    """Create a flow with clusters."""
    with flow.cluster("input", "Input Processing"):
        flow.start("Read Input").process("Validate Input", "Validate Input")

    with flow.cluster("processing", "Data Processing"):
        flow.process("Transform").process("Analyze")

    with flow.cluster("output", "Output"):
        flow.process("Generate Report").end("Finish")
    (
        flow.connect("Read Input", "Validate Input")
        .connect("Validate Input", "Transform")
        .connect("Transform", "Analyze")
        .connect("Analyze", "Generate Report")
        .connect("Generate Report", "Finish")
    )


def _create_complex_workflow(flow: DotInterpreter):
    """Create a complex workflow with multiple paths."""
    (
        flow.start("Init")
        .process("Load Config")
        .decision("Config Valid")
        .process("Read Data")
        .decision("Data Available")
        .process("Process Records")
        .decision("All Processed")
        .process("Generate Output")
        .decision("Output Valid")
        .process("Save Results")
        .end("End")
        .connect("Config Valid", "Read Data", label="Yes")
        .connect("Config Valid", "Init", label="No")
        .connect("Data Available", "End", label="No")
        .connect("Data Available", "Process Records", label="Yes")
        .connect("All Processed", "Generate Output", label="Yes")
        .connect("All Processed", "Process Records", label="No")
        .connect("Output Valid", "Save Results", label="Yes")
        .connect("Output Valid", "Process Records", label="No")
    )


@cli.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["png", "svg", "pdf", "dot"]),
    default="png",
    help="Output format",
)
def cheat_sheet(format: str):
    """Generate a DSL cheat sheet diagram."""

    flow = DotInterpreter("cheat_sheet", Theme.DEFAULT)

    dsl_examples = [
        "A -> B",
        "A -> B : Label",
        "A {decision} -> B : Yes",
        "A [shape=rect]",
        "A [shape=diamond, label='Check?']",
        "# This is a comment",
    ]

    # Create nodes for each example
    y_pos = 0
    for i, example in enumerate(dsl_examples):
        node_id = f"example_{i}"
        flow.node(node_id, example, NodeShape.RECTANGLE)
        # Simple vertical layout
        flow.set_graph_attr(f"{node_id}.pos", f"0,{y_pos}")
        y_pos -= 100

    output_path = f"dotflow_cheat_sheet.{format}"

    try:
        if format == "dot":
            DotExporter().export(flow.to_dot(), output_path)
        else:
            ImageExporter().export(flow.to_dot(), output_path, format)
    except Exception as e:
        sys.exit(f"{fg.RED}{e}{RESET}")
    click.echo(f"{fg.GREEN}✓{fg.GREEN} Generated cheat sheet{RESET}: {output_path}")


if __name__ == "__main__":
    cli()

"""
# Pythonic API
flow.py.node("A", "Label", shape=NodeShape.DIAMOND)
flow.py.dashed_connect("A", "B")

# Natural Language API
flow >> "A" >> "B" | "Label"
flow // "C"  # Dashed connection

# DSL API
flow.parse_dsl("A -> B : Label")

# Mixed usage
flow.start("A").py.diamond("B") >> "C" | "Label"
"""
