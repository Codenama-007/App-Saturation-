# Importing the required Dependencies
import os
import requests
from dotenv import load_dotenv
from ddgs import DDGS

# This is for getting the API keys that are stored in the .env file
load_dotenv()

TOKEN = os.getenv("TOKEN")


# This is the tool that will search for the Product 
# Product Hunt uses graphql 
# while the post request it needs to be converted into json
def Search_For_the_product(query: str):
    """
    NOTE: Product Hunt's API does not support free-text search on posts.
    This fetches top posts (by votes) — the LLM downstream decides relevance.
    """
    url = "https://api.producthunt.com/v2/api/graphql"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    graphql_query = """
    query RecentPosts {
      posts(first: 10, order: VOTES) {
        edges {
          node {
            name
            tagline
            url
          }
        }
      }
    }
    """

    try:
        response = requests.post(
            url=url,
            headers=headers,
            json={"query": graphql_query},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Product Hunt request failed: {e}") from e
    except ValueError:
        raise RuntimeError(f"Product Hunt returned non-JSON response: {response.text[:500]}")

    if "errors" in data:
        raise RuntimeError(f"Product Hunt GraphQL error:\n{data['errors']}")

    edges = data["data"]["posts"]["edges"]
    # print(edges)

    return [
        {
            "name": edge["node"]["name"],
            "tagline": edge["node"]["tagline"],
            "url": edge["node"]["url"],
        }
        for edge in edges
    ]
    
# this is for searching the idea accross the web 
def search_web_for_idea(query: str):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10))
    except Exception as e:
        print(f"[warning] DuckDuckGo search failed: {e}")
        return []

    return [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "content": r.get("body", ""),
        }
        for r in results
    ]