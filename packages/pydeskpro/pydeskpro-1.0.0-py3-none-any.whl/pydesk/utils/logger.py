from rich.console import Console

console = Console()

def log_info(message: str):
    console.print(f"[cyan]ℹ️ {message}[/cyan]")

def log_success(message: str):
    console.print(f"[green]✅ {message}[/green]")

def log_error(message: str):
    console.print(f"[red]❌ {message}[/red]")