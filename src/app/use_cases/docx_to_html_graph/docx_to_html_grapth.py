



from typing import Any, TypedDict
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
    
# =======================================================
# Graph builder
# =======================================================




def build_docx_to_html_graph(
        llm: Any
) -> StateGraph:
    graph = StateGraph(GraphState)
    
    graph.add_node("menu", generate_html_menu)
    graph.add_node("content", generate_html_content)
    graph.add_node("validate_html", validate_html_content)
    
    graph.add_edge(START, "menu")
    graph.add_edge("menu", "content")
    graph.add_edge("content", "validate_html")
    graph.add_edge("validate_html", END)
    
    return graph



docx_to_html_graph = build_docx_to_html_graph(
    llm=LLMService().openai(),
)

comparison_app = docx_to_html_graph.compile()
