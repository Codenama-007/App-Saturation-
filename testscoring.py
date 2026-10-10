"""Pure unit tests for scoring.py: no LLM, no network, run in milliseconds."""
import pytest

from scoring import (
    INCONCLUSIVE,
    calculate_opportunity_score,
    calculate_saturation_score,
)


def score(direct=0, sim=0, total=20, sources=0, relevant=0):
    s = calculate_saturation_score(direct, sim, total, sources, relevant)
    return calculate_opportunity_score(s)


def test_more_competitors_never_lowers_saturation():
    values = [score(direct=n, sources=6, relevant=15)["saturation_score"] for n in range(0, 15)]
    assert values == sorted(values)


@pytest.mark.parametrize("direct", [0, 1, 5, 10, 50])
@pytest.mark.parametrize("relevant", [0, 5, 20])
def test_all_scores_stay_in_range(direct, relevant):
    s = score(direct=direct, sim=direct, total=20, sources=relevant, relevant=relevant)
    for key in ("saturation_score", "market_gap_score", "confidence_score", "opportunity_score"):
        assert 0 <= s[key] <= 100, key


def test_bad_search_is_inconclusive_not_build():
    """The original bug: 0 competitors from irrelevant results gave BUILD 85/100."""
    assert score(direct=0, relevant=0, sources=0)["build_verdict"] == INCONCLUSIVE
    assert score(direct=0, relevant=2, sources=2)["build_verdict"] == INCONCLUSIVE


def test_empty_market_with_strong_evidence_can_build():
    s = score(direct=0, relevant=12, sources=8)
    assert s["build_verdict"] == "BUILD"


def test_verified_competitors_are_never_inconclusive():
    assert score(direct=4, sim=2, relevant=1, sources=1)["build_verdict"] != INCONCLUSIVE


def test_crowded_market_is_not_build():
    assert score(direct=10, sim=8, relevant=15, sources=8)["build_verdict"] != "BUILD"