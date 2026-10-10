"""Central settings. Override any of them with environment variables."""
import os

LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")      # generates the analysis
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "llama3.1:8b")  # DeepEval judge (use a bigger model than LLM_MODEL)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

RESULTS_PER_QUERY = 8      # DDG results fetched per query variant
MAX_TOTAL_RESULTS = 20     # cap after de-duplicating across variants
MIN_RELEVANT_RESULTS = 3   # fewer than this -> retry with a new query
MAX_RETRIES = 1
MIN_CONFIDENCE = 40        # below this (and few competitors) -> INCONCLUSIVE

SKIP_CACHE = os.getenv("SKIP_CACHE") == "1"  # evals set this so they never read stale results