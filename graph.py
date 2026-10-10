"""Graph wiring only. Logic lives in nodes/, helpers in evidence.py and scoring.py."""
from langgraph.graph import END, START, StateGraph
 
from models import AppState
from analysis import calculate_scores, suggest_features
from cache import check_cache, route_after_cache, save_to_cache
from research import compare_products, generate_query, route_after_search, search_products
workflow = StateGraph(AppState)
 
workflow.add_node("check_cache", check_cache)
workflow.add_node("generate_query", generate_query)
workflow.add_node("search_products", search_products)
workflow.add_node("compare_products", compare_products)
workflow.add_node("calculate_scores", calculate_scores)
workflow.add_node("suggest_features", suggest_features)
workflow.add_node("save_to_cache", save_to_cache)
 
workflow.add_edge(START, "check_cache")
workflow.add_conditional_edges(
    "check_cache", route_after_cache, {"cached": END, "fresh": "generate_query"}
)
workflow.add_edge("generate_query", "search_products")
workflow.add_conditional_edges(
    "search_products",
    route_after_search,
    {"retry": "generate_query", "analyze": "compare_products"},
)
workflow.add_edge("compare_products", "calculate_scores")
workflow.add_edge("calculate_scores", "suggest_features")
workflow.add_edge("suggest_features", "save_to_cache")
workflow.add_edge("save_to_cache", END)
 
graph = workflow.compile()
 
 
def export_diagram(path: str = "langgraph_workflow.png") -> None:
    """Run `python graph.py` to regenerate the diagram (needs internet for mermaid.ink)."""
    with open(path, "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
    print(f"Graph image saved as {path}")
 
 
if __name__ == "__main__":
    export_diagram()