import os
import sqlite3
import difflib
from datetime import datetime, timezone

DB_DIR = os.path.expanduser("~/.app_saturation")
DB_PATH = os.path.join(DB_DIR, "memory.db")


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS idea_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea TEXT NOT NULL,
            normalized_idea TEXT NOT NULL,
            search_query TEXT,
            result TEXT,
            features TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def find_similar_idea(idea: str, threshold: float = 0.85):
    """Return (row_dict, score) for the closest past idea if it's above threshold, else (None, best_score)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM idea_cache").fetchall()
    conn.close()

    normalized_input = _normalize(idea)
    best_match, best_score = None, 0.0

    for row in rows:
        score = difflib.SequenceMatcher(None, normalized_input, row["normalized_idea"]).ratio()
        if score > best_score:
            best_score = score
            best_match = row

    if best_match and best_score >= threshold:
        return dict(best_match), best_score
    return None, best_score


def save_idea(idea: str, search_query: str, result: str, features: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO idea_cache
           (idea, normalized_idea, search_query, result, features, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (idea, _normalize(idea), search_query, result, features,
         datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()