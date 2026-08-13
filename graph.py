# generated using claude 
import re
from langgraph.graph import START, END, StateGraph
from langchain_ollama import ChatOllama
from tools import Search_For_the_product, search_web_for_idea
from models import AppState

llm = ChatOllama(model='qwen3:1.7b', temperature=0)

def strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def generate_query(state: AppState):
    prompt = f"""
        You are researching whether a startup idea already exists.

        Idea:
        {state['idea']}

        Return only a short web search query (no explanation).
    """
    query = strip_think(llm.invoke(prompt).content)
    return {"search_query": query}


def search_products(state: AppState):
    web_results = search_web_for_idea(state['search_query'])

    try:
        products = Search_For_the_product(state['search_query'])
    except RuntimeError as e:
        print(f"[warning] Product Hunt search failed: {e}")
        products = []

    return {"web_results": web_results, "products": products}


def compare_products(state: AppState):
    prompt = f"""
You are a startup competition analyst.

User idea:
{state['idea']}

Web search results (primary source — most relevant):
{state['web_results']}

Product Hunt top posts (secondary, may be unrelated — use only if genuinely relevant):
{state['products']}

Determine whether a substantially similar product already exists.

Respond with:
STATUS: EXISTS / NOT_FOUND

Then list the top matching products and explain why they are similar.
"""
    result = strip_think(llm.invoke(prompt).content)
    return {"result": result}


workflow = StateGraph(AppState)

workflow.add_node("generate_query", generate_query)
workflow.add_node("search_products", search_products)
workflow.add_node("compare_products", compare_products)

workflow.add_edge(START, "generate_query")
workflow.add_edge("generate_query", "search_products")
workflow.add_edge("search_products", "compare_products")
workflow.add_edge("compare_products", END)

graph = workflow.compile()