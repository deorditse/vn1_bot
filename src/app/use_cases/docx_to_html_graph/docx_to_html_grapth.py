from typing import Any, TypedDict, Dict, Annotated

from langgraph.channels import LastValue
from langgraph.graph import StateGraph, START, END

from infrastructure.llm.llm import LLMService


# =======================================================
# Graph state
# =======================================================


class GraphState(TypedDict, total=False):
    # mdFile: str
    mdFile: Annotated[str, LastValue]
    html_menu: str
    html_content: str
    validation_attempts: Annotated[str, LastValue]

    # validation
    html_content_is_valid: bool


def generate_menu_html(state: GraphState) -> GraphState:
    # md = state["mdFile"]
    print(f"generate_menu_html: {state}")

    return {
        "mdFile": state["mdFile"],
        "html_menu": "html_menu",
    }


def generate_content_html(state: GraphState) -> GraphState:
    md = state["mdFile"]
    print(f"generate_content_html: {state}")

    return {'html_content': "html_content"}


def validate_content_html(state: GraphState) -> GraphState:
    is_valid = False  # допустим, иногда false

    return {
        "html_content_is_valid": is_valid,
        "validation_attempts": state.get("validation_attempts", 0) + 1
    }


def summarize(state: GraphState) -> GraphState:
    print(state)
    return state

    # =======================================================
    # Graph builder
    # =======================================================


llm = LLMService().openai()


class ValidationRouter:
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def __call__(self, state: GraphState) -> str:
        attempts = state.get("validation_attempts", 0)

        if state.get("html_content_is_valid"):
            return "summarize"

        if attempts >= self.max_attempts:
            return "summarize"  # или END / error-node

        return "generate_content_html"


async def build_docx_to_html_graph(file: bytes) -> Dict:
    # convert file to MD
    md = '''create todo: MD convert'''
    initState = {
        "mdFile": md,
    }
    graph = StateGraph(GraphState)

    graph.add_node("generate_menu_html", generate_menu_html)
    graph.add_node("generate_content_html", generate_content_html)
    graph.add_node("validate_content_html", validate_content_html)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "generate_menu_html")
    graph.add_edge('generate_menu_html', "summarize")

    graph.add_edge(START, "generate_content_html")
    graph.add_edge("generate_content_html", "validate_content_html")

    graph.add_conditional_edges(
        "validate_content_html",
        ValidationRouter(),
        {
            "generate_content_html": "generate_content_html",
            "summarize": "summarize",
        },
    )

    graph.add_edge("summarize", END)

    graph.set_entry_point("generate_menu_html")
    graph.set_finish_point("summarize")
    app = graph.compile()
    result_generated = await app.ainvoke(initState)
    return result_generated
