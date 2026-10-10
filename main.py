from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from graph import graph
from memory import init_db


init_db()

console = Console()


while True:

    idea = console.input(
        "\n[bold cyan]Enter your app idea:[/bold cyan] "
    )

    if "bye" in idea.lower():

        console.print(
            "\n[bold green]Thank you for using App Saturation Radar![/bold green]\n"
        )

        break


    console.print(
        "\n[bold yellow]🔎 Researching your idea...[/bold yellow]\n"
    )


    result = graph.invoke(
        {
            "idea": idea,
            "search_query": "",
            "products": [],
            "web_results": [],
            "result": "",
            "features": "",
            "scoring": {},
            "from_cache": False,
        }
    )


    title_suffix = (
        " (from memory)"
        if result.get("from_cache")
        else ""
    )


    console.print(
        Panel(
            result.get(
                "result",
                "No competitor analysis available."
            ),
            title=f"🔎 Existing Products{title_suffix}",
            border_style="green",
        )
    )


    scoring = result.get(
        "scoring",
        {}
    )


    saturation_score = scoring.get(
        "saturation_score",
        0
    )

    saturation_level = scoring.get(
        "saturation_level",
        "Unknown"
    )

    competition_density = scoring.get(
        "competition_density",
        0
    )

    similarity_score = scoring.get(
        "similarity_score",
        0
    )

    market_gap_score = scoring.get(
        "market_gap_score",
        0
    )

    confidence_score = scoring.get(
        "confidence_score",
        0
    )

    direct_competitors = scoring.get(
        "relevant_competitors",
        0
    )

    high_similarity = scoring.get(
        "high_similarity_competitors",
        0
    )

    opportunity_score = scoring.get(
        "opportunity_score",
        0
    )

    opportunity_level = scoring.get(
        "opportunity_level",
        "Unknown"
    )

    build_verdict = scoring.get(
        "build_verdict",
        "UNKNOWN"
    )


    saturation_table = Table(
        show_header=False,
        box=None,
        expand=True,
    )

    saturation_table.add_row(
        "Saturation Score",
        f"[bold]{saturation_score}/100[/bold]"
    )

    saturation_table.add_row(
        "Saturation Level",
        f"[bold]{saturation_level}[/bold]"
    )

    saturation_table.add_row(
        "Competition Density",
        f"{competition_density}/100"
    )

    saturation_table.add_row(
        "Similarity Score",
        f"{similarity_score}/100"
    )

    saturation_table.add_row(
        "Market Gap",
        f"{market_gap_score}/100"
    )

    saturation_table.add_row(
        "Research Confidence",
        f"{confidence_score}/100"
    )

    saturation_table.add_row(
        "Direct Competitors",
        str(direct_competitors)
    )

    saturation_table.add_row(
        "High-Similarity Competitors",
        str(high_similarity)
    )


    console.print(
        Panel(
            saturation_table,
            title="📊 MARKET SATURATION ANALYSIS",
            border_style="magenta",
        )
    )


    if build_verdict == "BUILD":

        verdict_icon = "🟢"
        verdict_style = "bold green"

    elif build_verdict == "BUILD WITH DIFFERENTIATION":

        verdict_icon = "🟡"
        verdict_style = "bold yellow"

    elif build_verdict == "BUILD ONLY IF DIFFERENTIATED":

        verdict_icon = "🟠"
        verdict_style = "bold dark_orange"

    elif build_verdict == "DON'T BUILD":

        verdict_icon = "🔴"
        verdict_style = "bold red"

    else:

        verdict_icon = "⚪"
        verdict_style = "bold white"


    verdict_text = f"""
[{verdict_style}]
{verdict_icon} {build_verdict}
[/{verdict_style}]

[bold cyan]OPPORTUNITY SCORE[/bold cyan]

[bold]{opportunity_score}/100[/bold]

[bold]OPPORTUNITY LEVEL[/bold]

{opportunity_level}

[dim]
This score estimates the opportunity based on the
competitive evidence available in this analysis.

It is NOT a prediction of revenue, profitability,
or startup success.
[/dim]
"""


    console.print(
        Panel(
            verdict_text,
            title="🧠 BUILD VERDICT",
            border_style="cyan",
        )
    )


    why_table = Table(
        show_header=True,
        expand=True,
    )

    why_table.add_column(
        "Signal"
    )

    why_table.add_column(
        "Score",
        justify="right"
    )

    why_table.add_row(
        "Market Gap",
        f"{market_gap_score}/100"
    )

    why_table.add_row(
        "Competition Density",
        f"{competition_density}/100"
    )

    why_table.add_row(
        "Similarity",
        f"{similarity_score}/100"
    )

    why_table.add_row(
        "Research Confidence",
        f"{confidence_score}/100"
    )

    console.print(
        Panel(
            why_table,
            title="📈 WHY THIS VERDICT?",
            border_style="blue",
        )
    )


    console.print(
        Panel(
            result.get(
                "features",
                "No differentiating features generated."
            ),
            title="💡 SUGGESTED DIFFERENTIATING FEATURES",
            border_style="green",
        )
    )


    console.print(
        "\n[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]"
    )

    console.print(
        "[bold green]Market validation complete.[/bold green]"
    )

    console.print(
        "[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]\n"
    )
