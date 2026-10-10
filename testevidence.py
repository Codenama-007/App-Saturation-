"""Pure unit tests for evidence.py."""
from evidence import (
    build_queries,
    clean_query,
    core_terms,
    count_domains,
    filter_relevant,
    ground_competitors,
    parse_extraction,
)

R = lambda title, body="", url="https://a.com/x": {"title": title, "content": body, "url": url}


def test_build_queries_makes_three_distinct_shapes():
    qs = build_queries("macro tracking app")
    assert qs[0] == "macro tracking app"
    assert qs[1] == "best macro tracking apps"
    assert qs[2] == "macro tracking app alternatives"


def test_core_terms_ignore_generic_words_and_stem():
    terms = core_terms("best macro tracker apps")
    assert "macro" in terms and "track" in terms
    assert "best" not in terms and "apps"[:5] not in terms


def test_relevance_filter_drops_off_topic_results():
    results = [
        R("Best macro tracking apps of 2026"),
        R("CREEM 2.0 - sales platform", "grow your SaaS revenue"),
        R("Macro tracker review", "tracking calories and macros"),
    ]
    kept = filter_relevant(results, "macro tracking app")
    assert [r["title"] for r in kept] == ["Best macro tracking apps of 2026", "Macro tracker review"]


def test_grounding_removes_invented_competitors():
    results = [R("MyFitnessPal vs Cronometer", "popular calorie counters")]
    kept = ground_competitors(["MyFitnessPal", "Cronometer", "MacroGenius"], results)
    assert kept == ["MyFitnessPal", "Cronometer"]


def test_grounding_dedupes_and_is_case_insensitive():
    results = [R("myfitnesspal review")]
    assert ground_competitors(["MyFitnessPal", "myfitnesspal"], results) == ["MyFitnessPal"]


def test_parse_extraction():
    names, hs = parse_extraction("COMPETITORS: MyFitnessPal | Cronometer\nHIGH_SIMILARITY: 2")
    assert names == ["MyFitnessPal", "Cronometer"] and hs == 2


def test_parse_extraction_none_and_garbage():
    assert parse_extraction("COMPETITORS: NONE\nHIGH_SIMILARITY: 0") == ([], 0)
    assert parse_extraction("the model rambled instead") == ([], 0)


def test_count_domains_ignores_www_and_duplicates():
    results = [
        R("a", url="https://www.x.com/1"),
        R("b", url="https://x.com/2"),
        R("c", url="https://y.org/3"),
    ]
    assert count_domains(results) == 2


def test_clean_query():
    assert clean_query('\n  "macro tracking app".\n') == "macro tracking app"
    assert clean_query("") == ""