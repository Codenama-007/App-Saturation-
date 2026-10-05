from rich.console import Console
from rich.panel import Panel

from graph import graph
from memory import init_db

init_db()

console = Console()
while True:
    

    idea = console.input("[bold cyan]Enter your app idea:[/bold cyan] ")
    
    if "bye" in idea.lower():
        print(" thank you for using our llm ")
        break
    

    console.print("\n[bold yellow]Researching...[/bold yellow]\n")

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

    title_suffix = " (from memory)" if result.get("from_cache") else ""

    console.print(
        Panel(
            result["result"],
            title=f"App Saturation - Existing Products{title_suffix}",
            border_style="green",
        )
    )

    scoring = result.get("scoring", {})

    score_text = f"""
    [bold]SATURATION SCORE[/bold]
    {scoring.get("saturation_score", 0)}/100

    [bold]SATURATION LEVEL[/bold]
    {scoring.get("saturation_level", "Unknown")}

    [bold]COMPETITION DENSITY[/bold]
    {scoring.get("competition_density", 0)}/100

    [bold]SIMILARITY SCORE[/bold]
    {scoring.get("similarity_score", 0)}/100

    [bold]MARKET GAP SCORE[/bold]
    {scoring.get("market_gap_score", 0)}/100

    [bold]CONFIDENCE[/bold]
    {scoring.get("confidence_score", 0)}/100

    [bold]DIRECT COMPETITORS[/bold]
    {scoring.get("relevant_competitors", 0)}

    [bold]HIGH-SIMILARITY COMPETITORS[/bold]
    {scoring.get("high_similarity_competitors", 0)}
    """
    
    console.print(
        Panel(
            result.get("features", "No differentiating features generated."),
            title="Suggested Differentiating Features",
            border_style="cyan",
        )
    )
    console.print(
        Panel(
            score_text,
            title="Market Saturation Score",
            border_style="magenta",
        )
    )