from typing import TypedDict, Annotated

from langgraph.channels import LastValue
from langgraph.graph import StateGraph, START, END
from starlette.responses import JSONResponse

from domain.services.converter import Converter
from infrastructure.llm.llm import LLMService

llm = LLMService().openai()


# =======================================================
# Graph state
# =======================================================


class GraphState(TypedDict, total=False):
    # mdFile: str
    mdFile: Annotated[str, LastValue]
    html_menu: str
    html_content: str
    validation_attempts: Annotated[int, LastValue]

    # validation
    html_content_is_valid: bool


def generate_menu_html(state: GraphState) -> GraphState:
    _log()

    md = state["mdFile"]

    return {
        "html_menu": "html_menu",
    }


def generate_content_html(state: GraphState) -> GraphState:
    _log()

    md = state["mdFile"]

    return {'html_content': "html_content"}


def validate_content_html(state: GraphState) -> GraphState:
    _log()

    html = state["html_content"]

    is_valid = False  # допустим, иногда false
    return {
        "html_content_is_valid": is_valid,
        "validation_attempts": state.get("validation_attempts", 0) + 1
    }


def summarize(state: GraphState) -> GraphState:
    _log()
    return state

    # =======================================================
    # Graph builder
    # =======================================================


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


def build_graph() -> StateGraph:
    # convert file to MD
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

    return graph


md_to_html_graph = build_graph()
compile_md_to_html_graph = md_to_html_graph.compile()

import sys
import logging
logger = logging.getLogger(__name__)
def _log():
    fn = sys._getframe(1).f_code.co_name
    print("call: def", fn)
