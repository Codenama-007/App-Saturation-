from typing import TypedDict


class AppState(TypedDict, total=False):
    idea: str
    search_query: str
    queries: list[str]        # query variants actually sent to DDG
    retries: int
    web_results: list[dict]   # title / url / content
    relevant_results: int     # how many results passed the relevance filter
    competitors: list[str]    # competitor names verified against web_results
    result: str               # competitor analysis text
    features: str             # gap analysis / differentiators
    scoring: dict
    from_cache: bool