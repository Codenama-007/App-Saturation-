# generated using claude 
import re
from langgraph.graph import START, END, StateGraph
from langchain_ollama import ChatOllama
from tools import Search_For_the_product, search_web_for_idea
from models import AppState
from memory import find_similar_idea, save_idea



def check_cache(state: AppState):
    match, score = find_similar_idea(state['idea'])
    if match:
        print(f"[memory] Found a similar past idea (similarity: {score:.0%}) — reusing cached result.")
        return {
            "result": match["result"],
            "features": match["features"],
            "search_query": match["search_query"],
            "from_cache": True,
        }
    return {"from_cache": False}


def route_after_cache(state: AppState):
    return "cached" if state["from_cache"] else "fresh"


def save_to_cache(state: AppState):
    save_idea(
        idea=state['idea'],
        search_query=state['search_query'],
        result=state['result'],
        features=state['features'],
    )
    return {}


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

def suggest_features(state: AppState):
    prompt = f"""
You are a senior product strategist doing competitive gap analysis.

User idea:
{state['idea']}

Competitive analysis (already determined):
{state['result']}

Rules:
- Only reference competitors that were explicitly identified as similar
  products in the analysis above. Do NOT treat generic platforms, website
  builders, hosting providers, marketplaces, or design tools (e.g. Shopify,
  Wix, Hostinger, Dribbble, WooCommerce) as competitors unless the analysis
  above specifically named them as a directly competing PRODUCT.
- If the analysis above says STATUS: NOT_FOUND, there are no real
  competitors to critique. In that case, skip "COMPETITOR GAPS" and instead
  suggest features based on common weaknesses in the clothing e-commerce
  space generally (e.g. sizing/fit uncertainty, sustainability transparency,
  return friction) rather than specific products.
- If the analysis above lists real competitors, list what each one lacks
  ONLY if that's stated or clearly implied in the analysis — otherwise say
  "not enough information to tell."

Then suggest 3-5 concrete, differentiating features for the user's idea.
Each must map to a specific gap or, if NOT_FOUND, a specific pain point in
this market. No generic "add AI" or "improve UX" suggestions.

Format:

COMPETITOR GAPS: (or "N/A — no direct competitors found" if STATUS: NOT_FOUND)
- <Product>: <gap>

SUGGESTED DIFFERENTIATORS:
1. <Feature> — addresses: <gap or pain point>
"""
    features = strip_think(llm.invoke(prompt).content)
    return {"features": features}






workflow = StateGraph(AppState)

workflow.add_node("check_cache", check_cache)
workflow.add_node("generate_query", generate_query)
workflow.add_node("search_products", search_products)
workflow.add_node("compare_products", compare_products)
workflow.add_node("suggest_features", suggest_features)
workflow.add_node("save_to_cache", save_to_cache)

workflow.add_edge(START, "check_cache")

workflow.add_conditional_edges(
    "check_cache",
    route_after_cache,
    {
        "cached": END,               # already have result + features, skip everything
        "fresh": "generate_query",   # no match, run the full pipeline
    },
)

workflow.add_edge("generate_query", "search_products")
workflow.add_edge("search_products", "compare_products")
workflow.add_edge("compare_products", "suggest_features")
workflow.add_edge("suggest_features", "save_to_cache")
workflow.add_edge("save_to_cache", END)

graph = workflow.compile()