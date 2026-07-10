from typing import TypedDict, List
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from app.policies.policies_loader import load_prompt
from app.policies.prompts.md_to_html.examples import menu_example, md_example, content_example
from common import ApiMode, env
from infrastructure.llm.llm import LLMService

mode: ApiMode = env.api_mode()


# =======================================================
# Graph state
# =======================================================

class GraphState(TypedDict, total=False):
    mdFile: str
    validation_attempts: int
    validation_errors: List[str]
    html_content_is_valid: bool

    # content
    html_menu: str
    html_content: str


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

    def __call__(self, state: GraphState) -> GraphState:
        raise NotImplementedError


# =======================================================
# Nodes
# =======================================================

class GenerateContentHtmlNode(BaseNode):
    """Генерация HTML структуры из Markdown"""

    def __init__(self, llm):
        super().__init__(
            step="generate_content_html", title="Генерация HTML структуры"
        )
        self._llm = llm

    async def __call__(self, state: GraphState) -> GraphState:
        _log(self.step)

        content_prompt = load_prompt('md_to_html/content_prompt.md').format(markdown_example=md_example,
                                                                            html_content_example=content_example)
        messages = [
            SystemMessage(content=content_prompt.strip()),
            HumanMessage(content=state.get('mdFile', '')),
        ]

        errors = state.get("validation_errors", [])

        if not isinstance(errors, list):
            errors = []

        if errors:
            messages.append(
                HumanMessage(
                    content="Fix the following validation errors:\n"
                            + "\n".join(errors)
                )
            )

        response = await self._llm.ainvoke(messages)

        return {'html_content': response.content.strip()}


def validate_content_html(state: GraphState) -> GraphState:
    _log('validate_content_html')

    errors = []

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


class GenerateMenuHtmlNode(BaseNode):
    """Генерация HTML меню из content"""

    def __init__(self, llm):
        super().__init__(
            step="generate_menu_html", title="Генерация HTML menu"
        )
        self._llm = llm

    menu_prompt = load_prompt('md_to_html/menu_prompt.md').format(html_menu_example=menu_example,
                                                                  html_input_example=content_example,
                                                                  )

    async def __call__(self, state: GraphState) -> GraphState:
        _log(self.step)

        # чтобы anchor_id были одинковыми - берем сгенерированный html и работаем с ним
        response = await self._llm.ainvoke(
            [SystemMessage(content=self.menu_prompt.strip()),
             HumanMessage(content=state.get('html_content')),
             ]
        )

        return {
            "html_menu": response.content,
        }


# =======================================================
# Graph builder
# =======================================================

def build_md_to_html_graph(llm_content, llm_menu) -> StateGraph:
    retry_policy = RetryPolicy(
        max_attempts=5,
        initial_interval=3,
    )

    graph = StateGraph(GraphState)
    # ___ Nodes ___
    content = GenerateContentHtmlNode(llm=llm_content)
    graph.add_node("generate_content_html", content, retry_policy=retry_policy)

    graph.add_node("validate_content_html", validate_content_html, retry_policy=retry_policy)

    menu = GenerateMenuHtmlNode(llm_menu)
    graph.add_node("generate_menu_html", menu, retry_policy=retry_policy)

    # ___ Edges ___
    graph.add_edge(START, "generate_content_html")

    graph.add_edge("generate_content_html", "validate_content_html")

    def validation(state: GraphState):
        return (
            "valid"
            if state.get('html_content_is_valid') or state.get('validation_attempts', 0) >= 3
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

    graph.add_edge("generate_menu_html", END)

    return graph


def compile_md_to_html_graph():
    return build_md_to_html_graph(
        llm_content=LLMService().openai(),
        llm_menu=LLMService().openai(),
    ).compile()


def _log(step: str):
    if mode == ApiMode.PROD:
        return

    print(f"node: {step}")
