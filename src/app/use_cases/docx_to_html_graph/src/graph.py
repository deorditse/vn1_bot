from typing import TypedDict, Annotated
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.channels import LastValue
from langgraph.graph import StateGraph, START, END
from app.policies.policies_loader import load_prompt
from app.policies.prompts.md_to_html.examples import menu_example, md_example, content_example
from infrastructure.llm.llm import LLMService

_llm_validation = None
_llm_content = None


def get_llm_validation():
    global _llm_validation
    if _llm_validation is None:
        _llm_validation = LLMService().openai()
    return _llm_validation


def get_llm_content():
    global _llm_content
    if _llm_content is None:
        _llm_content = LLMService().openai()
    return _llm_content


# =======================================================
# Graph state
# =======================================================


class GraphState(TypedDict, total=False):
    # mdFile: str
    mdFile: Annotated[str, LastValue]
    html_menu: str
    html_content: str
    validation_attempts: Annotated[int, LastValue]
    validation_errors: list[str]

    # validation
    html_content_is_valid: bool


DOC_TO_CONTENT_HTML_PROMPT = load_prompt('md_to_html/content_prompt.md').format(markdown_example=md_example,
                                                                                html_content_example=content_example)


async def generate_content_html(state: GraphState) -> GraphState:
    _log()
    is_valid = state.get("html_content_is_valid", True)
    llm = get_llm_content()
    response = await llm.ainvoke([
        SystemMessage(content=DOC_TO_CONTENT_HTML_PROMPT),
        HumanMessage(content=state.get('mdFile') if state.get("html_content") is None else state.get("html_content")),
    ])

    return {'html_content': response.content}


def validate_content_html(state: GraphState) -> GraphState:
    _log()
    errors: list[str] = []

    html = state["html_content"]

    # TODO: add validation

    if not errors:
        return {
            "html_content_is_valid": True,
            "validation_errors": []
        }

    return {
        "html_content_is_valid": False,
        "validation_errors": errors,
        "validation_attempts": state.get("validation_attempts", 0) + 1,
    }


DOC_TO_MENU_HTML_PROMPT = load_prompt('md_to_html/menu_prompt.md').format(html_menu_example=menu_example,
                                                                          html_input_example=content_example,
                                                                          )


async def generate_menu_html(state: GraphState) -> GraphState:
    _log()

    llm = get_llm_content()
    # чтобы anchor_id были одинковыми - берем сгенерированный html и работаем с ним
    response = await llm.ainvoke(
        [SystemMessage(content=DOC_TO_MENU_HTML_PROMPT),
         HumanMessage(content=state.get("html_content")),
         ]
    )

    return {
        "html_menu": response.content,
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
            return "generate_menu_html"

        if attempts >= self.max_attempts:
            return "generate_menu_html"  # или END / error-node

        return "generate_content_html"


def build_graph() -> StateGraph:
    # convert file to MD
    graph = StateGraph(GraphState)

    graph.add_node("generate_content_html", generate_content_html)
    graph.add_node("validate_content_html", validate_content_html)
    graph.add_node("generate_menu_html", generate_menu_html)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "generate_content_html")
    graph.add_edge("generate_content_html", "validate_content_html")

    graph.add_conditional_edges(
        "validate_content_html",
        ValidationRouter(),
        {
            "generate_content_html": "generate_content_html",
            "generate_menu_html": "generate_menu_html",
        },
    )

    graph.add_edge("generate_menu_html", "summarize")

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
