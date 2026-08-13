from typing import Dict , List , TypedDict

class AppState(TypedDict):
    idea : str 
    search_query : str        # User's Query 
    products: List[Dict]      # from Product Hunt
    web_results: List[Dict]   # from DuckDuckGo
    result : str              # total results from product hunt and DuckDuckGo
    features: str             # NEW: gap analysis + suggestions
    from_cache: bool   # NEW