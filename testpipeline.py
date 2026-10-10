"""
End-to-end evals: real LLM, real DuckDuckGo, DeepEval judge. Slow.

    pytest evals/test_pipeline.py                      # plain pytest
    deepeval test run evals/test_pipeline.py           # with DeepEval's reporting

Thresholds are starting points. Run once, look at the scores, then calibrate.
"""
import functools

import pytest
from deepeval import assert_test
from deepeval.metrics import ContextualRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.models import OllamaModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from config import JUDGE_MODEL, OLLAMA_URL
from goldenset import GOLDEN, NONSENSE, SATURATED
from scoring import INCONCLUSIVE

pytestmark = pytest.mark.llm
ids = lambda c: c["id"]


@functools.lru_cache(maxsize=None)
def run_idea(idea: str) -> dict:
    from graph import graph  # imported lazily so collection stays cheap

    return graph.invoke({"idea": idea})


def context(state: dict) -> list[str]:
    return [f"{r['title']}: {r['content']}" for r in state.get("web_results", [])]


@pytest.fixture(scope="module")
def judge():
    return OllamaModel(model=JUDGE_MODEL, base_url=OLLAMA_URL)


# ---- plain assertions (fast and reliable: no judge needed) -----------------

@pytest.mark.parametrize("case", GOLDEN, ids=ids)
def test_scores_in_range(case):
    s = run_idea(case["idea"])["scoring"]
    for key in ("saturation_score", "market_gap_score", "confidence_score", "opportunity_score"):
        assert 0 <= s[key] <= 100


@pytest.mark.parametrize("case", SATURATED, ids=ids)
def test_saturated_market_is_not_build(case):
    s = run_idea(case["idea"])["scoring"]
    assert s["build_verdict"] != "BUILD", s


@pytest.mark.parametrize("case", SATURATED, ids=ids)
def test_finds_known_competitors(case):
    found = " ".join(run_idea(case["idea"])["competitors"]).lower()
    hits = [k for k in case["known"] if k in found]
    assert len(hits) >= 2, f"only found {hits}"


@pytest.mark.parametrize("case", NONSENSE, ids=ids)
def test_nonsense_idea_is_inconclusive(case):
    assert run_idea(case["idea"])["scoring"]["build_verdict"] == INCONCLUSIVE


# ---- DeepEval metrics (LLM judge) ------------------------------------------

@pytest.mark.parametrize("case", SATURATED, ids=ids)
def test_retrieval_is_relevant(case, judge):
    state = run_idea(case["idea"])
    tc = LLMTestCase(input=case["idea"], actual_output=state["result"], retrieval_context=context(state))
    assert_test(tc, [ContextualRelevancyMetric(threshold=0.5, model=judge)])


@pytest.mark.parametrize("case", SATURATED, ids=ids)
def test_analysis_is_faithful_to_results(case, judge):
    state = run_idea(case["idea"])
    tc = LLMTestCase(input=case["idea"], actual_output=state["result"], retrieval_context=context(state))
    assert_test(tc, [FaithfulnessMetric(threshold=0.7, model=judge)])


@pytest.mark.parametrize("case", [c for c in GOLDEN if c["kind"] != "nonsense"], ids=ids)
def test_features_are_specific(case, judge):
    state = run_idea(case["idea"])
    metric = GEval(
        name="Feature specificity",
        criteria=(
            "The output suggests concrete, specific product features tied to a stated gap or "
            "pain point. Penalize generic suggestions ('add AI', 'better UX') and claims that "
            "something is missing from the market without supporting evidence."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=judge,
        threshold=0.6,
    )
    assert_test(LLMTestCase(input=case["idea"], actual_output=state["features"]), [metric])