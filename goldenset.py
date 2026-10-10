"""
Ideas where we already know the right answer. Add 10-15 over time.
`known` = competitors any decent search should surface.
"""
GOLDEN = [
    {
        "id": "macro_tracker",
        "idea": "app to track macros and monitor fitness activities",
        "kind": "saturated",
        "known": ["myfitnesspal", "cronometer", "macrofactor", "lose it", "fitbit"],
    },
    {
        "id": "todo_app",
        "idea": "a simple to-do list app with reminders",
        "kind": "saturated",
        "known": ["todoist", "ticktick", "microsoft to do", "any.do", "things"],
    },
    {
        "id": "note_taking",
        "idea": "a note taking app with tags and sync across devices",
        "kind": "saturated",
        "known": ["notion", "evernote", "obsidian", "onenote", "bear"],
    },
    {
        "id": "niche_foraging",
        "idea": "app that identifies mushroom species from photos and logs foraging locations",
        "kind": "niche",
        "known": [],
    },
    {
        "id": "nonsense",
        "idea": "asdf qwerty zzzz blorp flarn",
        "kind": "nonsense",
        "known": [],
    },
]

SATURATED = [c for c in GOLDEN if c["kind"] == "saturated"]
NONSENSE = [c for c in GOLDEN if c["kind"] == "nonsense"]