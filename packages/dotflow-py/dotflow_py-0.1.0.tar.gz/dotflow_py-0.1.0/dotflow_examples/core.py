from dotflow import create_flow, Theme
import warnings

warnings.filterwarnings(
    action="ignore",
    category=SyntaxWarning,
    message="str indices must be integers or slices, not str; perhaps you missed a comma?",
)


def demo_pythonic_api():
    # Demo Pythonic API.
    print("=== Pythonic API Demo ===")
    flow = create_flow("pythonic_demo", Theme.COLORFUL)

    # Method chaining style
    (
        flow.start(node_id="Start")
        .process(node_id="Load Data")
        .decision(node_id="Data Valid", question="Data Valid?")
        .process(node_id="Process Data")
        .process(node_id="Storage")
        .process(node_id="Error Handler")
        .connect(from_node="Start", to_node="Load Data")
        .connect(from_node="Load Data", to_node="Data Valid")
        .connect(from_node="Data Valid", to_node="Process Data", label="Yes")
        .connect(from_node="Data Valid", to_node="Error Handler", label="No")
        .connect(
            from_node="Process Data", to_node="Error Handler", label="Processing Error"
        )
        .decision(node_id="retryHandler", question="retry<max_retries?")
        .connect(from_node="Error Handler", to_node="retryHandler")
        .connect(from_node="Process Data", to_node="Storage", label="data storage")
        .end(node_id="End")
        .connect(from_node="Storage", to_node="End")
        .connect(from_node="retryHandler", to_node="End", label="No(end)")
    )

    # Using explicit Pythonic API
    flow.py.dashed_connect("retryHandler", "Load Data", "Yes(retry)")

    # print(flow.to_dot())
    flow.render("png", "pythonic_demo.png")
    print("Generated pythonic_demo.png\n")


def demo_natural_language_api():
    # Demo Natural Language API.
    print("=== Natural Language API Demo ===")
    flow = create_flow("natural_demo", Theme.BLUE)

    # Operator-based style
    (
        flow.start(node_id="Start")
        .process(node_id="Process")
        .decision(node_id="decision", question="Proccessable?")
        .process(node_id="Success")
        .py.circle(node_id="Retry")
        .process(node_id="validate")
        .end(node_id="End")
    )

    flow >> "Start" >> "validate" >> "decision" >> "Process" >> "Success" >> "End"
    flow.connect("decision", "End", label="No")
    flow.py.bold_connect("Process", "Retry", label="Reprocess")
    flow.py.dashed_connect("Retry", "Process")

    # Alternative path with dashed connection
    # flow >> "Decision" // "Retry" | "No"

    # Conditional label
    # flow >> "Retry" >> "Process"
    # flow["After retry"]

    # print(flow.to_dot())
    flow.render("png", "natural_demo.png")
    print("Generated natural_demo.png\n")


def demo_dsl_api():
    # Demo Textual DSL API.
    print("=== Textual DSL API Demo ===")
    flow = create_flow("dsl_demo", Theme.GREEN)

    dsl_text = """
    A [shape=rect, label='Custom']
    B [shape=rect, label="decision"]
    C [shape=diamond, label=process]
    A->B:Input Data
    B{decison}->C:Valid
    # End of of diagram
    """

    flow.parse_dsl(dsl_text)

    print(flow.to_dot())
    flow.render("png", "dsl_demo.png")
    print("Generated dsl_demo.png\n")


def demo_mixed_apis():
    # Demo mixing different APIs.
    print("=== Mixed APIs Demo ===")
    flow = create_flow("mixed_demo", Theme.DARK)

    # Start with Pythonic API
    flow.start("Start").process("Initial Setup").process("Check Requirements").process(
        "Requirements Met", label="Requirements Met?"
    )

    # Switch to natural language
    flow >> "Check Requirements" >> "Requirements Met"

    # Use Pythonic API for complex logic
    with flow.cluster("processing", "Data Processing"):
        flow.py.rectangle("Transform Data")
        flow.py.diamond("Validation Check")

    # Back to natural language
    flow >> "Generate Output" >> "End"

    # Use DSL for additional connections
    flow.parse_dsl("""
    Requirements Met -> Transform Data : Yes
    Requirements Met -> End : No
    Validation Check -> Generate Output : Valid
    Validation Check -> Transform Data : Invalid
    """)

    print(flow.to_dot())
    flow.render("png", "mixed_demo.png")
    print("Generated mixed_demo.png")


if __name__ == "__main__":
    # demo_pythonic_api()
    demo_natural_language_api()
    # demo_dsl_api()
    # demo_mixed_apis()
