import re

from evidence import (
    count_domains,
    filter_relevant,
    format_results,
    ground_competitors,
    parse_extraction,
)
from llm import ask
from models import AppState
from prompts import EXTRACT_PROMPT, FEATURES_PROMPT
from scoring import INCONCLUSIVE, calculate_opportunity_score, calculate_saturation_score


def calculate_scores(state: AppState):
    """LLM names competitors -> we verify them against the results -> deterministic scoring."""
    results = state.get("web_results", [])
    relevant = filter_relevant(results, state["search_query"])

    raw = ask(EXTRACT_PROMPT.format(idea=state["idea"], analysis=state["result"]))
    names, high_similarity = parse_extraction(raw)
    grounded = ground_competitors(names, results)
    unverified = [n for n in names if n not in grounded]

    scoring = calculate_saturation_score(
        direct_competitors=len(grounded),
        high_similarity=min(high_similarity, len(grounded)),
        total_results=len(results),
        source_count=count_domains(relevant),
        relevant_results=len(relevant),
    )
    scoring = calculate_opportunity_score(scoring)

    # Build the STATUS line ourselves so it can't contradict the analysis text.
    if scoring["build_verdict"] == INCONCLUSIVE:
        status = "INCONCLUSIVE"
    else:
        status = "EXISTS" if grounded else "NOT_FOUND"

    body = re.sub(r"^\s*STATUS:.*$", "", state["result"], flags=re.I | re.M).strip()
    text = f"STATUS: {status}\n\n{body}"
    if unverified:
        text += "\n\nNot found in the search results (ignored): " + ", ".join(unverified)

    return {"competitors": grounded, "result": text, "scoring": scoring}


def suggest_features(state: AppState):
    if state["scoring"]["build_verdict"] == INCONCLUSIVE:
        return {
            "features": (
                "COMPETITOR GAPS: N/A\n\n"
                "SUGGESTED DIFFERENTIATORS:\n"
                "Not enough reliable evidence was found to suggest differentiators "
                "without inventing market gaps. Try rephrasing the idea with the "
                "product category and the target user."
            )
        }

    relevant = filter_relevant(state.get("web_results", []), state["search_query"])
    prompt = FEATURES_PROMPT.format(
        idea=state["idea"],
        competitors=", ".join(state.get("competitors", [])) or "none verified",
        evidence=format_results(relevant, limit=10),
    )
    return {"features": ask(prompt)}