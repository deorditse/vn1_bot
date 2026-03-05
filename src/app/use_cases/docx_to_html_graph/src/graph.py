import inspect
from typing import Any
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from pydantic import Field
from pydantic.v1 import BaseModel

from app.policies.policies_loader import load_prompt
from app.policies.prompts.md_to_html.examples import menu_example, md_example, content_example
from common import ApiMode, env
from infrastructure.llm.llm import LLMService

mode: ApiMode = env.api_mode()


# =======================================================
# Graph state
# =======================================================


class GraphState(BaseModel):
    mdFile: str = Field("", description="mdFile")
    html_menu: str = Field("", description="HTML menu")
    html_content: str = Field('', description="HTML content")
    validation_attempts: int = Field(0, description="Validation attempts")
    validation_errors: list[str] = Field(default_factory=list, description="Validation errors")
    html_content_is_valid: bool = Field(False, description="HTML content is_valid")


# =======================================================
# Node base class
# =======================================================

class BaseNode:
    """Node base class"""
    step: str
    title: str

    def __init__(self, step: str, title: str):
        self.step = step
        self.title = title

    def __call__(self, state: GraphState) -> dict:
        raise NotImplementedError


# =======================================================
# Nodes
# =======================================================

class GenerateContentHtmlNode(BaseNode):
    """Генерация HTML структуры из Markdown"""

    def __init__(self, llm: Any):
        super().__init__(
            step="generateContentHtml", title="Генерация HTML структуры"
        )
        self.llm = llm

    async def __call__(self, state: GraphState) -> dict:
        _log()

        messages = [
            SystemMessage(content=DOC_TO_CONTENT_HTML_PROMPT.strip()),
            HumanMessage(content=state.mdFile)
        ]

        errors = state.validation_errors

        if not isinstance(errors, list):
            errors = []

        if errors:
            messages.append(
                HumanMessage(
                    content="Fix the following validation errors:\n"
                            + "\n".join(errors)
                )
            )

        response = await self.llm.ainvoke(messages)
        _print(response.content)

        return {'html_content': response.content}


_llm_menu = None
_llm_content = None


def get_llm_menu():
    global _llm_menu
    if _llm_menu is None:
        _llm_menu = LLMService().openai()
    return _llm_menu


DOC_TO_CONTENT_HTML_PROMPT = load_prompt('md_to_html/content_prompt.md').format(markdown_example=md_example,
                                                                                html_content_example=content_example)


# async def generate_content_html(state: GraphState) -> GraphState:
#     _log()
#     # is_valid = state.get("html_content_is_valid", True)
#     llm = get_llm_content()
#
#     messages = [
#         SystemMessage(content=DOC_TO_CONTENT_HTML_PROMPT.strip()),
#         HumanMessage(content=state["mdFile"])
#     ]
#
#     if state.get("validation_errors"):
#         messages.append(
#             HumanMessage(
#                 content="Fix the following validation errors:\n"
#                         + "\n".join(state["validation_errors"])
#             )
#         )
#
#     response = await llm.ainvoke(messages)
#     _print(response.content)
#
#     return {'html_content': response.content}


def validate_content_html(state: GraphState) -> dict:
    _log()
    errors = []

    html = state.html_content

    # TODO: add validation

    if not errors:
        return {
            "html_content_is_valid": True,
            "validation_errors": []
        }

    return {
        "html_content_is_valid": False,
        "validation_errors": errors,
        "validation_attempts": state.validation_attempts + 1,
    }


DOC_TO_MENU_HTML_PROMPT = load_prompt('md_to_html/menu_prompt.md').format(html_menu_example=menu_example,
                                                                          html_input_example=content_example,
                                                                          )


async def generate_menu_html(state: GraphState) -> dict:
    _log()

    llm = get_llm_menu()
    # чтобы anchor_id были одинковыми - берем сгенерированный html и работаем с ним
    response = await llm.ainvoke(
        [SystemMessage(content=DOC_TO_MENU_HTML_PROMPT.strip()),
         HumanMessage(content=state.html_content),
         ]
    )
    _print(response.content)

    return {
        "html_menu": response.content,
    }


def summarize(state: GraphState) -> dict:
    _log()
    return state.dict(exclude_none=True)


# =======================================================
# Graph builder
# =======================================================


def build_graph() -> StateGraph:
    gen_llm = LLMService().openai()

    gen_content = GenerateContentHtmlNode(llm=gen_llm)
    retry_policy = RetryPolicy(
        max_attempts=5,
        initial_interval=3,
    )

    graph = StateGraph(GraphState)

    # nodes
    graph.add_node("generate_content_html", gen_content, retry_policy=retry_policy)
    graph.add_node("validate_content_html", validate_content_html, retry_policy=retry_policy)
    graph.add_node("generate_menu_html", generate_menu_html, retry_policy=retry_policy)
    graph.add_node("summarize", summarize)

    # edges
    graph.add_edge(START, "generate_content_html")
    graph.add_edge("generate_content_html", "validate_content_html")

    def validation(state: GraphState):
        return (
            "valid"
            if state.html_content_is_valid or state.validation_attempts >= 3
            else "retry"
        )

    graph.add_conditional_edges(
        "validate_content_html",
        validation,
        {
            "retry": "generate_content_html",
            "valid": "generate_menu_html",
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
    fn = inspect.stack()[1].function
    print(f"call: {fn}")


def _print(data):
    pass
    # from textwrap import indent, fill
    #
    # print(indent(
    #     fill(data, width=100),
    #     prefix="│ "
    # ))
