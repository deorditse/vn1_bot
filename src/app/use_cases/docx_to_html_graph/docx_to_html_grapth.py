from typing import Any, TypedDict, Dict
from langgraph.graph import StateGraph, START, END

from infrastructure.llm.llm import LLMService


# =======================================================
# Graph state
# =======================================================


class GraphState(TypedDict, total=False):
    file: bytes
    html_menu: str
    html_content: str

    # validation
    html_is_valid: bool
    html_validation_errors: list[str]


def generate_doc_to_md(state: GraphState) -> GraphState:
    print(state)
    return state


def generate_html_menu(state: GraphState) -> GraphState:
    print(state)
    return state


def generate_html_content(state: GraphState) -> GraphState:
    print(state)
    return state


def validate_html(state: GraphState) -> GraphState:
    is_valid = True  # ← здесь реальная проверка
    return {
        **state,
        "html_is_valid": is_valid,
        "html_validation_errors": [] if is_valid else ["error"]
    }


def summarize(state: GraphState) -> GraphState:
    print(state)
    return state


def validation_router(state: GraphState) -> str:
    return "summarize" if state.get("html_is_valid") else "content"


# =======================================================
# Graph builder
# =======================================================

async def build_docx_to_html_graph(file: bytes) -> Dict:
    # llm = LLMService().openai()

    initState = GraphState(file=file)
    graph = StateGraph(GraphState)

    graph.add_node("doc_to_md", generate_doc_to_md)
    graph.add_node("menu", generate_html_menu)
    graph.add_node("content", generate_html_content)
    graph.add_node("validate_html", validate_html)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "doc_to_md")
    graph.add_edge("doc_to_md", "menu")
    graph.add_edge("menu", 'summarize')
    graph.add_edge("doc_to_md", "content")
    graph.add_edge("content", "validate_html")

    graph.add_conditional_edges(
        "validate_html",
        validation_router,
        {
            "content": "content",
            "summarize": "summarize",
        },
    )
    graph.add_edge("summarize", END)

    app = graph.compile()

    png_bytes = app.get_graph().draw_mermaid_png()
    # Сохранить граф
    with open("graph.png", "wb") as f:
        f.write(png_bytes)

    result_generated = await app.ainvoke(initState)

    return {}
