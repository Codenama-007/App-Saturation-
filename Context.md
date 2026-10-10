# Project Context — Vibe Code App Saturation

## Overview
An AI-powered market research CLI that analyzes whether a startup/app idea is already saturated. It uses a LangGraph workflow to search the web with DuckDuckGo, verifies the competitors the LLM names against the retrieved results, scores market saturation deterministically, and suggests differentiating features. Local Ollama LLMs power the analysis. LLM output quality is measured with DeepEval.

Product Hunt has been removed. DuckDuckGo is the only data source.

---

## Project Layout (flat, all files in the repo root)

```
main.py            CLI entry point
memory.py          SQLite cache
test.py            scratch file for `rich` (not part of the app)

config.py          settings: model names, thresholds, SKIP_CACHE
llm.py             ChatOllama instance, strip_think(), ask()
prompts.py         every LLM prompt
models.py          AppState TypedDict
tools.py           DuckDuckGo search
evidence.py        relevance filter, competitor verification, parsing (pure, no LLM)
scoring.py         deterministic scoring + evidence guard
cache.py           cache nodes
research.py        query / search / compare nodes
analysis.py        scoring / feature nodes
graph.py           LangGraph wiring only

conftest.py        sets SKIP_CACHE=1 for all tests
golden_set.py      ideas with known answers for evals
test_scoring.py    unit tests for scoring.py (no LLM)
test_evidence.py   unit tests for evidence.py (no LLM)
test_pipeline.py   end-to-end evals with DeepEval (slow)
pytest.ini         pytest config and the `llm` marker
requirements-dev.txt   pytest, deepeval
```

---

## File Summaries

### `main.py`
Entry point and CLI loop. Uses `rich` for a styled terminal UI.
- Initializes the SQLite memory DB via `init_db()`.
- Prompts the user for an app idea (typing "bye" exits).
- Invokes the LangGraph `graph` with a fresh `AppState`.
- Renders output panels: competitor analysis, market saturation table, build verdict, "why this verdict" signals, and suggested differentiating features.
- Shows "(from memory)" suffix when results came from cache.
- **TODO:** handle the new `INCONCLUSIVE` verdict (add it to any verdict→color/emoji mapping) and stop reading `state["products"]`, which no longer exists.

### `config.py`
Single place for settings. Everything can be overridden with environment variables.
- `LLM_MODEL` (default `llama3.2:3b`), `JUDGE_MODEL` (default `llama3.1:8b`), `OLLAMA_URL`
- `RESULTS_PER_QUERY` (8), `MAX_TOTAL_RESULTS` (20)
- `MIN_RELEVANT_RESULTS` (3), `MAX_RETRIES` (1), `MIN_CONFIDENCE` (40)
- `SKIP_CACHE` — true when `SKIP_CACHE=1`; evals set this so they never read or write the cache.

### `llm.py`
- `llm` — the shared `ChatOllama` instance (temperature 0).
- `strip_think(text)` — removes `<think>...</think>` blocks.
- `ask(prompt)` — invokes the LLM and strips thinking blocks.

### `prompts.py`
All prompt templates: `QUERY_PROMPT`, `RETRY_QUERY_PROMPT`, `COMPARE_PROMPT`, `EXTRACT_PROMPT`, `FEATURES_PROMPT`. The features prompt is domain-neutral and tells the LLM not to claim a market gap unless the evidence supports it.

### `models.py`
Defines `AppState`, a `TypedDict` (`total=False`) shared between LangGraph nodes:
- `idea`, `search_query`, `queries` (the query variants sent to DDG), `retries`
- `web_results` (DuckDuckGo), `relevant_results` (count that passed the relevance filter)
- `competitors` (names verified against the results)
- `result` (competitor analysis text), `features` (gap analysis)
- `scoring` (dict of metrics), `from_cache` (bool)

### `tools.py`
DuckDuckGo search only. No API keys or `.env` needed.
- `search_web(query, max_results)` — fetches results via `DDGS`, returns title/url/content dicts. Returns `[]` on failure with a warning.
- `search_many(queries)` — runs several query variants, de-duplicates by URL, caps the total.

### `evidence.py`
Pure, deterministic helpers (no LLM, no network), which makes them easy to unit test.
- `clean_query(raw)` — first line, strips quotes/punctuation, caps length.
- `build_queries(base)` — one idea becomes three query shapes: the base query, `best X apps`, `X app alternatives`.
- `core_terms(query)` / `filter_relevant(results, query)` — keeps results that mention at least half the distinctive query terms (5-char stems, so "tracker" matches "tracking").
- `ground_competitors(names, results)` — keeps only competitor names that literally appear in the retrieved text. This is the hallucination guard.
- `parse_extraction(text)` — parses `COMPETITORS:` and `HIGH_SIMILARITY:` lines from LLM output.
- `count_domains(results)` — distinct domains (ignoring `www.`).
- `format_results(results)` — compact numbered text for prompts.

### `scoring.py`
Deterministic scoring engine (no LLM involvement in final scores).
- `calculate_saturation_score(direct_competitors, high_similarity, total_results, source_count, relevant_results)`:
  - competitor density (45%), similarity pressure (30%), relevance density (15%), source coverage (10%) → `saturation_score`
  - `market_gap_score` = 100 − saturation
  - `confidence_score` = evidence quality: on-topic results (60%) + distinct domains among them (40%). It no longer depends on how many competitors were found.
  - `saturation_level`: Low / Moderate / High / Very High
- `calculate_opportunity_score(scoring)` blends market gap (45%), inverse competition (20%), inverse similarity (15%) and confidence (20%) into `opportunity_score`, mapped to `build_verdict` and `opportunity_level`: BUILD / BUILD WITH DIFFERENTIATION / BUILD ONLY IF DIFFERENTIATED / DON'T BUILD.
- **Evidence guard:** if confidence is below `MIN_CONFIDENCE` and fewer than 3 competitors were verified, the verdict becomes `INCONCLUSIVE` ("Not enough evidence to judge"). A bad search is no longer mistaken for an empty market. Three or more verified competitors always count as evidence of saturation.

### `cache.py`
- `check_cache` — looks up similar past ideas in SQLite memory; short-circuits to END on a match ≥ 85%. Skipped when `SKIP_CACHE` is set.
- `route_after_cache` — "cached" → END, "fresh" → `generate_query`.
- `save_to_cache` — persists the analysis. Skips `INCONCLUSIVE` results and is skipped when `SKIP_CACHE` is set.

### `research.py`
- `generate_query` — LLM turns the idea into a short category query. On a retry it is told the previous query returned off-topic results and asks for different wording.
- `search_products` — builds the three query variants, searches DuckDuckGo, counts how many results are relevant.
- `route_after_search` — if fewer than `MIN_RELEVANT_RESULTS` results are relevant and retries remain → "retry", otherwise "analyze".
- `compare_products` — LLM lists real products named in the (relevant) results that solve the same problem.

### `analysis.py`
- `calculate_scores` — LLM extracts competitor names and a high-similarity count; names are verified against the results; the deterministic scoring engine runs; the `STATUS:` line (EXISTS / NOT_FOUND / INCONCLUSIVE) is written in code so it cannot contradict the analysis. Unverified names are listed as ignored.
- `suggest_features` — LLM does gap analysis using only verified competitors and the retrieved evidence. For `INCONCLUSIVE` results it skips the LLM and says there isn't enough evidence, instead of inventing market gaps.

### `graph.py`
Wiring only. Builds and compiles the `StateGraph` over `AppState`. Run `python graph.py` to export the Mermaid diagram to `langgraph_workflow.png` (needs internet). It no longer draws the diagram at import time.

### `memory.py`
SQLite-backed cache at `~/.app_saturation/memory.db` so repeated/similar ideas skip re-research. (Unchanged.)
- `init_db()` — creates the `idea_cache` table.
- `_normalize(text)` — lowercases and collapses whitespace.
- `find_similar_idea(idea, threshold=0.85)` — `difflib.SequenceMatcher` against stored ideas; returns the best match above threshold, else `(None, best_score)`.
- `save_idea(...)` — inserts a cache row with a UTC ISO timestamp.

### `test.py`
Scratch file exercising `rich`. Not part of the main application.

---

## Architecture Flow
```
User idea → check_cache → (hit: END) / (miss: generate_query)
  → search_products (DuckDuckGo, 3 query variants)
  → route_after_search → (few relevant results & retries left: back to generate_query)
                       → (otherwise: compare_products)
  → compare_products (LLM lists matching products)
  → calculate_scores (LLM names competitors → verified against results → deterministic scores)
  → suggest_features (LLM, or a fixed "insufficient evidence" message if INCONCLUSIVE)
  → save_to_cache (skips INCONCLUSIVE) → END
```

---

## Evaluation (DeepEval + pytest)

The pipeline is treated as a RAG flow: the DuckDuckGo results are the retrieval context, and the analysis and features are the generated output.

**Fast tests, no LLM (run in milliseconds):**
- `test_scoring.py` — scores stay in 0–100; more competitors never lower saturation; a bad search gives `INCONCLUSIVE` and never `BUILD`; verified competitors are never inconclusive.
- `test_evidence.py` — query building, relevance filtering, competitor grounding, parsing, domain counting.

**End-to-end tests (`test_pipeline.py`, marked `llm`, slow):**
- Plain assertions: scores in range; saturated ideas are not `BUILD`; at least two known competitors are found; a nonsense idea is `INCONCLUSIVE`.
- DeepEval metrics, judged by `JUDGE_MODEL`: `ContextualRelevancyMetric` (is the retrieval on-topic), `FaithfulnessMetric` (does the analysis stick to the results), `GEval` "Feature specificity" (are suggested features concrete and not generic).

**Golden set (`golden_set.py`):** macro tracker, to-do app, note-taking app (saturated), mushroom foraging app (niche), and a nonsense string. Grow this to 10–15 ideas over time.

**Commands:**
```bash
pip install -r requirements-dev.txt
pytest -m "not llm"                        # fast tests only
pytest test_scoring.py test_evidence.py    # same, without needing deepeval installed
deepeval test run test_pipeline.py         # full evals with DeepEval reporting
```

Metric thresholds are starting points. Run once, look at the actual scores, then calibrate. Use a larger model as the judge than the one generating the answers.

---

## Dependencies
- `langgraph`, `langchain_ollama`, `langchain_core` (graph + LLM)
- `rich` (CLI rendering)
- `ddgs` (DuckDuckGo search)
- `sqlite3`, `difflib` (memory/cache, stdlib)
- Dev/eval: `pytest`, `deepeval` (see `requirements-dev.txt`)
- Ollama models: `llama3.2:3b` by default for the app (set `LLM_MODEL=llama3.1:8b` for better extraction), `llama3.1:8b` as the DeepEval judge
- No `.env` is required any more. `requests` and `python-dotenv` are no longer used by the app.

---

## Not part of this project
`security-analyzer.py` ("SecureScan AI", a separate LangGraph + Ollama security scanner) and `vibe-code-app-detector.py` (an empty placeholder) are separate and not part of this app. Keep them out of the repo root or in their own folders.