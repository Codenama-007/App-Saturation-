# Project Context — Vibe Code App Saturation

## Overview
An AI-powered market research CLI that analyzes whether a startup/app idea is already saturated. It uses a LangGraph workflow to search Product Hunt and DuckDuckGo, scores market saturation deterministically, and suggests differentiating features. Local Ollama LLMs (Llama3.1:8b) power the analysis.

---

## File Summaries

### `main.py`
Entry point and CLI loop. Uses `rich` for a styled terminal UI.
- Initializes the SQLite memory DB via `init_db()`.
- Prompts the user for an app idea (typing "bye" exits).
- Invokes the LangGraph `graph` with a fresh `AppState`.
- Renders output panels: competitor analysis, market saturation table, build verdict (BUILD / BUILD WITH DIFFERENTIATION / BUILD ONLY IF DIFFERENTIATED / DON'T BUILD), "why this verdict" signals, and suggested differentiating features.
- Shows "(from memory)" suffix when results came from cache.

### `models.py`
Defines `AppState`, a `TypedDict` describing the shared state passed between LangGraph nodes:
- `idea`, `search_query` — user input and LLM-generated query
- `products` (Product Hunt), `web_results` (DuckDuckGo)
- `result` (competitor analysis text), `features` (gap analysis)
- `scoring` (dict of metrics), `from_cache` (bool)

### `tools.py`
External data source tools. Loads `TOKEN` from `.env` via `dotenv`.
- `Search_For_the_product(query)` — queries Product Hunt's GraphQL API (v2) for the top 10 posts by votes. Note: PH API doesn't support free-text search, so the LLM judges relevance downstream. Raises `RuntimeError` on API failure.
- `search_web_for_idea(query)` — uses `DDGS` (DuckDuckGo) to fetch 10 text results, returning title/url/content dicts. Returns `[]` on failure with a warning.

### `graph.py`
Core LangGraph agent workflow. Builds and compiles a `StateGraph` over `AppState`.
- Nodes:
  - `check_cache` — looks up similar past ideas in SQLite memory; short-circuits to END if a match ≥ 85% similarity is found.
  - `route_after_cache` — conditional edge: "cached" → END, "fresh" → generate_query.
  - `generate_query` — LLM turns the idea into a short web search query. Contains a TODO to switch to `langchain_google` / `ChatGoogleGenerativeAI`.
  - `search_products` — calls both DuckDuckGo and Product Hunt tools.
  - `compare_products` — LLM acts as a competition analyst, returns `STATUS: EXISTS / NOT_FOUND` plus matching products.
  - `calculate_scores` — LLM extracts `DIRECT_COMPETITORS` and `HIGH_SIMILARITY` counts, then calls the deterministic scoring engine.
  - `suggest_features` — LLM does competitive gap analysis and suggests 3–5 differentiating features.
  - `save_to_cache` — persists the analysis to SQLite for future reuse.
- `strip_think()` removes `<think>...</think>` thinking blocks from LLM output.
- On compile, exports the workflow diagram to `langgraph_workflow.png` (Mermaid PNG).

### `scoring.py`
Deterministic scoring engine (no LLM involvement in final scores).
- `clamp(value)` — keeps numbers within 0–100.
- `calculate_saturation_score(direct_competitors, high_similarity, total_results, source_count)` computes:
  - competitor density (45%), similarity pressure (30%), relevance density (15%), source coverage (10%) → weighted `saturation_score`
  - `market_gap_score` (100 − saturation)
  - `confidence_score` based on competitor count, sources, and result volume
  - `saturation_level` label: Low / Moderate / High / Very High
- `calculate_opportunity_score(scoring)` blends market gap (45%), inverse competition (20%), inverse similarity (15%), and confidence (20%) into an `opportunity_score`, mapped to a `build_verdict` and `opportunity_level`.

### `memory.py`
SQLite-backed cache at `~/.app_saturation/memory.db` so repeated/similar ideas skip re-research.
- `init_db()` — creates the `idea_cache` table (idea, normalized_idea, search_query, result, features, created_at).
- `_normalize(text)` — lowercases and collapses whitespace.
- `find_similar_idea(idea, threshold=0.85)` — uses `difflib.SequenceMatcher` ratio against all stored ideas; returns the best match above threshold, else `(None, best_score)`.
- `save_idea(...)` — inserts a new cache row with a UTC ISO timestamp.

### `security-analyzer.py`
A separate, standalone project: "SecureScan AI" — an agentic website security scanner built with LangGraph + Ollama (`qwen3:1.7b`).
- Tools (bound to the LLM):
  - `check_website` — reachability, status code, HTTPS check, response time
  - `check_security_headers` — inspects CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
  - `analyze_security` — combines the above into a boolean-header report
  - `report_generator` — pretty-prints a security report with recommendations for missing headers
  - `check_cookies` — inspects cookie Secure/HttpOnly/SameSite attributes (note: has a bug — returns `cookie` instead of `cookies`)
  - `detect_technologies` — sniffs tech stack from headers/HTML (Next.js, React, PHP, WordPress)
- Graph: `chatbot` ↔ `tools` via `tools_condition`, with `MemorySaver` checkpointer for multi-turn chat (thread "Affan").
- Interactive chat loop until "bye"; exports graph image to `langgraph_workflow_security.png`.

### `test.py`
A tiny scratch/test file exercising the `rich` module — pretty-prints a sample `user_profile` dict with syntax highlighting. Not part of the main application.

### `vibe-code-app-detector.py`
Effectively empty/placeholder file (contains a single character `i`). No functionality.

---

## Architecture Flow
```
User idea → check_cache → (hit: END) / (miss: generate_query)
  → search_products (DuckDuckGo + Product Hunt)
  → compare_products (LLM analysis)
  → calculate_scores (deterministic)
  → suggest_features (LLM)
  → save_to_cache → END
```

## Dependencies
- `langgraph`, `langchain_ollama`, `langchain_core` (graph + LLM)
- `rich` (CLI rendering)
- `requests`, `python-dotenv`, `ddgs` (search tools)
- `sqlite3`, `difflib` (memory/cache, stdlib)
- Ollama models: `Llama3.1:8b` (saturation app), `qwen3:1.7b` (security analyzer)
- `.env` must define `TOKEN` (Product Hunt API token)
