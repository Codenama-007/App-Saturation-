from config import SKIP_CACHE
from memory import find_similar_idea, save_idea
from models import AppState
from scoring import INCONCLUSIVE


def check_cache(state: AppState):
    if SKIP_CACHE:  # evals must always run the real pipeline
        return {"from_cache": False}

    match, score = find_similar_idea(state["idea"])
    if match:
        print(f"[memory] Found a similar past idea (similarity: {score:.0%}) - reusing cached result.")
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
    # Never cache a non-answer, or the user would keep getting it back.
    if SKIP_CACHE or state.get("scoring", {}).get("build_verdict") == INCONCLUSIVE:
        return {}
    save_idea(
        idea=state["idea"],
        search_query=state["search_query"],
        result=state["result"],
        features=state["features"],
    )
    return {}
