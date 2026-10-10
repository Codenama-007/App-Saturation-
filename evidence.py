"""
Pure, deterministic helpers (no LLM, no network) so they are easy to unit test.

They answer three questions the old pipeline never asked:
  - Are the search results actually about the idea?   (filter_relevant)
  - Did the LLM's competitors really appear in them?  (ground_competitors)
  - How many independent sites back this up?          (count_domains)
"""
import math
import re
from urllib.parse import urlparse

STOPWORDS = {
    "the", "and", "for", "that", "with", "app", "apps", "best", "top", "tool", "tools",
    "software", "platform", "alternatives", "alternative", "online", "free", "new",
    "build", "make", "want", "wanna", "helps", "help", "people", "project", "like",
    "basically", "their", "your", "into", "from", "using", "based", "ai",
}


def clean_query(raw: str, max_words: int = 8) -> str:
    """Take the first non-empty line, drop quotes/punctuation, cap the length."""
    for line in raw.splitlines():
        line = line.strip().strip("\"'`*-. ")
        if line:
            return " ".join(line.split()[:max_words])
    return ""


def build_queries(base: str) -> list[str]:
    """One idea -> three query shapes. 'alternatives' / 'best X' pull up listicles naming real competitors."""
    core = re.sub(r"\b(apps?|software|tools?)\s*$", "", base.strip(), flags=re.I).strip() or base.strip()
    return [base.strip(), f"best {core} apps", f"{core} app alternatives"]


def core_terms(query: str) -> list[str]:
    """Distinctive word stems (5-char prefixes so 'tracker' matches 'tracking')."""
    words = re.findall(r"[a-z0-9]+", query.lower())
    return sorted({w[:5] for w in words if len(w) > 2 and w not in STOPWORDS})


def _text(result: dict) -> str:
    return f"{result.get('title', '')} {result.get('content', '')}".lower()


def is_relevant(result: dict, terms: list[str]) -> bool:
    if not terms:
        return True  # nothing to judge against
    text = _text(result)
    return sum(t in text for t in terms) >= math.ceil(len(terms) / 2)


def filter_relevant(results: list[dict], query: str) -> list[dict]:
    terms = core_terms(query)
    return [r for r in results if is_relevant(r, terms)]


def domain_of(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def count_domains(results: list[dict]) -> int:
    return len({domain_of(r.get("url", "")) for r in results if r.get("url")})


def parse_extraction(text: str) -> tuple[list[str], int]:
    """Parse 'COMPETITORS: a | b' and 'HIGH_SIMILARITY: n' from LLM output."""
    names: list[str] = []
    m = re.search(r"COMPETITORS:\s*(.*)", text, re.I)
    if m and m.group(1).strip().lower() not in {"", "none", "n/a", "none."}:
        names = [n.strip(" *-.\"'") for n in re.split(r"\||,", m.group(1))]
        names = [n for n in names if n]
    hs = re.search(r"HIGH_SIMILARITY:\s*(\d+)", text, re.I)
    return names[:15], int(hs.group(1)) if hs else 0


def ground_competitors(names: list[str], results: list[dict]) -> list[str]:
    """Keep only names that literally appear in the retrieved text. This is the hallucination guard."""
    haystack = " ".join(_text(r) for r in results)
    kept, seen = [], set()
    for n in names:
        key = n.lower()
        if len(key) >= 3 and key not in seen and key in haystack:
            seen.add(key)
            kept.append(n)
    return kept


def format_results(results: list[dict], limit: int = 20, snippet: int = 220) -> str:
    lines = []
    for i, r in enumerate(results[:limit], 1):
        body = " ".join(r.get("content", "").split())[:snippet]
        lines.append(f"[{i}] {r.get('title', '')} ({domain_of(r.get('url', ''))})\n    {body}")
    return "\n".join(lines) if lines else "(no results)"