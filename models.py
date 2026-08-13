from typing import Dict , List , TypedDict

class AppState(TypedDict):
    idea : str 
    search_query : str 
    products: List[Dict]      # from Product Hunt
    web_results: List[Dict]   # from DuckDuckGo
    result : str
    features: str             # NEW: gap analysis + suggestions