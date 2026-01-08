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

    # validation
    html_content_is_valid: bool


def generate_menu_html(state: GraphState) -> GraphState:
    md = state["mdFile"]
    print(f"generate_content_html: {state}")

    return {
        "mdFile": state["mdFile"],
        "html_menu": "html_menu",
    }


def generate_content_html(state: GraphState) -> GraphState:
    md = state["mdFile"]
    print(f"generate_content_html: {state}")

    return {'html_content': "html_content"}


def validate_content_html(state: GraphState) -> GraphState:
    is_valid = True  # ← здесь реальная проверка

    return {
        "html_content_is_valid": is_valid
    }


def summarize(state: GraphState) -> GraphState:
    print(state)
    return {}

    # =======================================================
    # Graph builder
    # =======================================================


llm = LLMService().openai()


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
    graph.add_edge("generate_menu_html", 'generate_content_html')
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

    graph.set_entry_point("generate_menu_html")
    graph.set_finish_point("summarize")

    app = graph.compile()

    png_bytes = app.get_graph().draw_mermaid_png()
    # Сохранить граф
    with open("graph.png", "wb") as f:
        f.write(png_bytes)

    result_generated = await app.ainvoke(initState)

    return result_generated
