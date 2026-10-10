"""All LLM prompts in one place."""

QUERY_PROMPT = """You are researching whether a startup idea already exists.

Idea:
{idea}

Return ONLY a short web search query (3-6 words) naming the product category,
for example: "macro tracking app". No explanation, no quotes."""

RETRY_QUERY_PROMPT = """You are researching whether a startup idea already exists.

Idea:
{idea}

The query "{previous}" returned mostly off-topic results.
Return ONLY a different short search query (3-6 words) using other wording
for the same product category. No explanation, no quotes."""

COMPARE_PROMPT = """You are a startup competition analyst.

User idea:
{idea}

Web search results:
{results}

List ONLY real products named in the results above that solve the same core
problem as the idea. For each give: name - one-line reason it is similar.
Do not invent products and do not list products that are not in the results.
Do not list generic platforms, marketplaces, hosting providers or design tools.
If nothing matches, write exactly: None found in the results."""

EXTRACT_PROMPT = """Extract structured data from this competitive analysis.

User idea:
{idea}

Analysis:
{analysis}

Return ONLY these two lines:
COMPETITORS: <product names separated by | , or NONE>
HIGH_SIMILARITY: <integer: how many of those are nearly identical to the idea>

Only include products that directly solve the same core problem."""

FEATURES_PROMPT = """You are a senior product strategist doing competitive gap analysis.

User idea:
{idea}

Verified competitors: {competitors}

Evidence (search results):
{evidence}

Rules:
- Only critique competitors from the verified list.
- State a competitor's gap only if the evidence shows or clearly implies it;
  otherwise write "not enough information to tell".
- Never claim something is "missing from the market" unless the evidence
  supports it. Features that the evidence shows existing products already
  have are not differentiators.
- Suggest 3-5 concrete, specific features. No generic "add AI" or "improve UX".

Format:

COMPETITOR GAPS:
- <Product>: <gap>

SUGGESTED DIFFERENTIATORS:
1. <Feature> - addresses: <specific gap or pain point>"""