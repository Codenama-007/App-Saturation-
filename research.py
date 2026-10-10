from config import MAX_RETRIES, MIN_RELEVANT_RESULTS
from evidence import build_queries, clean_query, filter_relevant, format_results
from llm import ask
from models import AppState
from prompts import COMPARE_PROMPT, QUERY_PROMPT, RETRY_QUERY_PROMPT
from tools import search_many


def generate_query(state: AppState):
    previous = state.get("search_query")  # set only when we are retrying
    if previous:
        prompt = RETRY_QUERY_PROMPT.format(idea=state["idea"], previous=previous)
    else:
        prompt = QUERY_PROMPT.format(idea=state["idea"])

    query = clean_query(ask(prompt)) or clean_query(state["idea"])
    return {
        "search_query": query,
        "retries": state.get("retries", 0) + (1 if previous else 0),
    }


def search_products(state: AppState):
    queries = build_queries(state["search_query"])
    results = search_many(queries)
    relevant = filter_relevant(results, state["search_query"])
    return {"queries": queries, "web_results": results, "relevant_results": len(relevant)}


def route_after_search(state: AppState):
    """Mostly off-topic results? Try one differently worded query before analysing."""
    poor = state.get("relevant_results", 0) < MIN_RELEVANT_RESULTS
    if poor and state.get("retries", 0) < MAX_RETRIES:
        return "retry"
    return "analyze"


def compare_products(state: AppState):
    results = state.get("web_results", [])
    relevant = filter_relevant(results, state["search_query"])
    shown = relevant or results  # prefer on-topic results; fall back so the LLM isn't blind

    prompt = COMPARE_PROMPT.format(idea=state["idea"], results=format_results(shown))
    return {"result": ask(prompt)}