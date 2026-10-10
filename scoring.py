"""
Deterministic scoring engine. The LLM never produces the final numbers.

Key change: CONFIDENCE now measures how much *relevant* evidence we retrieved,
not how many competitors we found. Before, "found 0 competitors" capped
confidence at 50 and the verdict still said BUILD. Finding nothing because the
search was bad is not the same as the market being empty.
"""
from config import MIN_CONFIDENCE

INCONCLUSIVE = "INCONCLUSIVE"


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(value, maximum))


def calculate_saturation_score(
    direct_competitors: int,
    high_similarity: int,
    total_results: int,
    source_count: int,
    relevant_results: int = 0,
) -> dict:
    """
    direct_competitors: competitors verified against the search results
    high_similarity:    how many of those are near-identical to the idea
    total_results:      results examined
    source_count:       distinct domains among the RELEVANT results
    relevant_results:   results that passed the relevance filter
    """
    competitor_density = clamp((direct_competitors / 10) * 100)
    similarity_pressure = clamp((high_similarity / max(direct_competitors, 1)) * 100)
    relevance_density = clamp((direct_competitors / total_results) * 100) if total_results > 0 else 0
    source_coverage = clamp((source_count / 6) * 100)

    saturation_score = round(
        clamp(
            competitor_density * 0.45
            + similarity_pressure * 0.30
            + relevance_density * 0.15
            + source_coverage * 0.10
        ),
        1,
    )
    market_gap_score = round(100 - saturation_score, 1)

    # Evidence quality: enough on-topic results, from enough independent sites.
    confidence_score = round(
        clamp(min(relevant_results / 10, 1) * 60 + min(source_count / 6, 1) * 40), 1
    )

    if saturation_score < 25:
        level = "Low"
    elif saturation_score < 50:
        level = "Moderate"
    elif saturation_score < 75:
        level = "High"
    else:
        level = "Very High"

    return {
        "saturation_score": saturation_score,
        "saturation_level": level,
        "competition_density": round(competitor_density, 1),
        "similarity_score": round(similarity_pressure, 1),
        "market_gap_score": market_gap_score,
        "confidence_score": confidence_score,
        "relevant_competitors": direct_competitors,
        "high_similarity_competitors": high_similarity,
        "relevant_results": relevant_results,
    }


def calculate_opportunity_score(scoring: dict) -> dict:
    market_gap = float(scoring.get("market_gap_score", 0))
    competition = float(scoring.get("competition_density", 0))
    similarity = float(scoring.get("similarity_score", 0))
    confidence = float(scoring.get("confidence_score", 0))

    opportunity_score = round(
        clamp(
            market_gap * 0.45
            + (100 - competition) * 0.20
            + (100 - similarity) * 0.15
            + confidence * 0.20
        ),
        1,
    )

    if opportunity_score >= 71:
        verdict, level = "BUILD", "Strong Opportunity"
    elif opportunity_score >= 51:
        verdict, level = "BUILD WITH DIFFERENTIATION", "Promising, but differentiation matters"
    elif opportunity_score >= 31:
        verdict, level = "BUILD ONLY IF DIFFERENTIATED", "Difficult market"
    else:
        verdict, level = "DON'T BUILD", "Weak Opportunity"

    # Evidence guard. Low confidence only blocks the verdict when we also found
    # few competitors: seeing 3+ verified competitors is positive evidence of
    # saturation, while seeing none through a bad search proves nothing.
    if confidence < MIN_CONFIDENCE and scoring.get("relevant_competitors", 0) < 3:
        verdict, level = INCONCLUSIVE, "Not enough evidence to judge"

    scoring["opportunity_score"] = opportunity_score
    scoring["opportunity_level"] = level
    scoring["build_verdict"] = verdict
    return scoring