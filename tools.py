"""External data source: DuckDuckGo only."""
import time

from ddgs import DDGS

from config import MAX_TOTAL_RESULTS, RESULTS_PER_QUERY


def search_web(query: str, max_results: int = RESULTS_PER_QUERY) -> list[dict]:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        print(f"[warning] DuckDuckGo search failed for {query!r}: {e}")
        return []

    return [
        {"title": r.get("title", ""), "url": r.get("href", ""), "content": r.get("body", "")}
        for r in results
    ]


def search_many(queries: list[str]) -> list[dict]:
    """Run several query variants, de-duplicate by URL, cap the total."""
    seen, merged = set(), []
    for i, q in enumerate(queries):
        if i:
            time.sleep(1)  # be polite; DDG rate-limits bursts
        for r in search_web(q):
            if r["url"] and r["url"] not in seen:
                seen.add(r["url"])
                merged.append(r)
    return merged[:MAX_TOTAL_RESULTS]