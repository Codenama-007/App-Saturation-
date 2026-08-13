from rich.console import Console
from rich.panel import Panel

from graph import graph

console = Console()
    

while True:
    idea = console.input("[bold cyan]Enter your app idea:[/bold cyan] ")
    
    if "bye" in idea.lower():
        print(" Thank you for using for our LLM ")
        break
        
    console.print("\n[bold yellow]Researching Product Hunt...[/bold yellow]\n")
    result = graph.invoke(
        {
            "idea": idea,
            "search_query": "",
            "products": [],
            "web_results": [],
            "result": "",
        }
    )

    console.print(
        Panel(
            result["result"],
            title="App Saturation - Stage 1",
            border_style="green",
        )
    )