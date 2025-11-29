from rich.console import Console
from rich.panel import Panel


console = Console()

def warn(message: str):
    console.print(
        Panel.fit(
            f"[bold yellow]⚠ WARNING:[/bold yellow]\n{message}",
            border_style="yellow",
        )
    )



def info(message: str):
    console.print(
        Panel.fit(
            f"[bold cyan]ℹ INFO:[/bold cyan]\n{message}",
            border_style="cyan",
        )
    )

def error(message: str):
    console.print(
        Panel.fit(
            f"[bold red]❌ ERROR:[/bold red]\n{message}",
            border_style="red",
        )
    )

def success(message: str):
    console.print(
        Panel.fit(
            f"[bold green]✔ SUCCESS:[/bold green]\n{message}",
            border_style="green",
        )
    )