from typing import Any, TypedDict, Dict
from langgraph.graph import StateGraph, START, END

from infrastructure.llm.llm import LLMService


# =======================================================
# Graph state
# =======================================================


class GraphState(TypedDict, total=False):
    mdFile: str
    html_menu: str
    html_content: str

    # validation
    html_content_is_valid: bool
    html_validation_errors: list[str]


def generate_menu_html(state: GraphState) -> GraphState:
    md = state["mdFile"]
    state['html_menu'] = "html_menu"
    print(state)

    return state


def generate_content_html(state: GraphState) -> GraphState:
    md = state["mdFile"]
    state['html_content'] = "html_content"
    print(state)

    return state


def validate_content_html(state: GraphState) -> GraphState:
    is_valid = True  # ← здесь реальная проверка
    return {
        **state,
        "html_content_is_valid": is_valid,
        "html_validation_errors": [] if is_valid else ["error"]
    }


def summarize(state: GraphState) -> GraphState:
    print(state)
    return state


# =======================================================
# Graph builder
# =======================================================

async def build_docx_to_html_graph(file: bytes) -> Dict:
    llm = LLMService().openai()

    # convert file to MD
    md = ''''''

    initState = GraphState(mdFile=md)
    graph = StateGraph(GraphState)

    graph.add_node("generate_menu_html", generate_menu_html)
    graph.add_node("generate_content_html", generate_content_html)
    graph.add_node("validate_content_html", validate_content_html)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "generate_menu_html")
    graph.add_edge("generate_menu_html", 'summarize')

    graph.add_edge(START, "generate_content_html")
    graph.add_edge("generate_content_html", "validate_content_html")

    def validation_router(state: GraphState) -> str:
        return "summarize" if state.get(
            "html_content_is_valid") else "generate_content_html"

    # продумать как не уйти в рекурсию
    graph.add_conditional_edges(
        "validate_content_html",
        validation_router,
        {
            "generate_content_html": "generate_content_html",
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
