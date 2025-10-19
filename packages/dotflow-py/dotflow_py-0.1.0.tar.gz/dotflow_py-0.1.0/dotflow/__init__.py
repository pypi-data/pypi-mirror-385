"""
A Python-based DOT language interpreter with multiple API styles.

---
Demo showing all three API styles provided by dotflow.


from dotflow import create_flow, Theme


def demo_pythonic_api():
    # Demo Pythonic API.
    print("=== Pythonic API Demo ===")
    flow = create_flow("pythonic_demo", Theme.COLORFUL)

    # Method chaining style
    (
        flow.start("Start")
        .process("Load Data")
        .decision("Data Valid?")
        .connect("Data Valid?", "Process Data", label="Yes")
        .connect("Data Valid?", "Error Handler", label="No")
        .process("Process Data")
        .end("End")
    )

    # Using explicit Pythonic API
    flow.py.dashed_connect("Error Handler", "Load Data", "Retry")

    print(flow.to_dot())
    flow.render("png", "pythonic_demo.png")
    print("Generated pythonic_demo.png\n")


def demo_natural_language_api():
    # Demo Natural Language API.
    print("=== Natural Language API Demo ===")
    flow = create_flow("natural_demo", Theme.BLUE)

    # Operator-based style
    (flow >> "Start" >> "Process" >> "Decision" >> "Success" | "Yes" >> "End")

    # Alternative path with dashed connection
    flow >> "Decision" // "Retry" | "No"

    # Conditional label
    flow >> "Retry" >> "Process"["After retry"]

    print(flow.to_dot())
    flow.render("png", "natural_demo.png")
    print("Generated natural_demo.png\n")


def demo_dsl_api():
    #Demo Textual DSL API.
    print("=== Textual DSL API Demo ===")
    flow = create_flow("dsl_demo", Theme.GREEN)

    dsl_text = \"\"\"
    # Simple workflow DSL
    Start -> Process -> Decision
    Decision -> Success : Yes
    Decision -> Retry : No
    Retry -> Process : After retry
    Success -> End
    \"\"\"

    flow.parse_dsl(dsl_text)

    print(flow.to_dot())
    flow.render("png", "dsl_demo.png")
    print("Generated dsl_demo.png\n")


def demo_mixed_apis():
    # Demo mixing different APIs.
    print("=== Mixed APIs Demo ===")
    flow = create_flow("mixed_demo", Theme.DARK)

    # Start with Pythonic API
    flow.start("Start").process("Initial Setup")

    # Switch to natural language
    flow >> "Check Requirements" >> "Requirements Met?"

    # Use Pythonic API for complex logic
    with flow.cluster("processing", "Data Processing"):
        flow.py.rectangle("Transform Data")
        flow.py.diamond("Validation Check")

    # Back to natural language
    flow >> "Generate Output" >> "End"

    # Use DSL for additional connections
    flow.parse_dsl(\"\"\"
    Requirements Met? -> Transform Data : Yes
    Requirements Met? -> End : No
    Validation Check -> Generate Output : Valid
    Validation Check -> Transform Data : Invalid
    \"\"\")

    print(flow.to_dot())
    flow.render("png", "mixed_demo.png")
    print("Generated mixed_demo.png")


if __name__ == "__main__":
    demo_pythonic_api()
    demo_natural_language_api()
    demo_dsl_api()
    demo_mixed_apis()
"""

from .core.interpreter import DotInterpreter
from .core.themes import Theme
from .api.pythonic import PythonicAPI
from .api.natural import NaturalLanguageAPI
from .api.dsl import TextualDSL

try:
    from .cli import cli
except ImportError:
    cli = None

__version__ = "0.1.0"
__all__ = [
    "DotInterpreter",
    "Flow",
    "Theme",
    "PythonicAPI",
    "NaturalLanguageAPI",
    "TextualDSL",
    "create_flow",
    "cli",
]


# Convenience function
def create_flow(name: str = "flow", theme: Theme = Theme.DEFAULT) -> "DotInterpreter":
    """Create a new flow diagram."""
    return DotInterpreter(name, theme)


# Alias for backward compatibility
Flow = DotInterpreter
