from rich.console import Console
from rich.panel import Panel

from graph import graph
from memory import init_db

init_db()

console = Console()

idea = console.input("[bold cyan]Enter your app idea:[/bold cyan] ")

console.print("\n[bold yellow]Researching...[/bold yellow]\n")

result = graph.invoke(
    {
        "idea": idea,
        "search_query": "",
        "products": [],
        "web_results": [],
        "result": "",
        "features": "",
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

console.print(
    Panel(
        result["features"],
        title=f"Suggested Differentiators{title_suffix}",
        border_style="cyan",
    )
)