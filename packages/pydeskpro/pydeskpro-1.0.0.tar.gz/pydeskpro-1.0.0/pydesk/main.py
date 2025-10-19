import click
import os, json
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from pydesk import tasks, notes, expenses, backup

console = Console()

CONFIG_DIR = os.path.expanduser("~/.pydesk")   # ~/.pydesk in Android filesystem
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Ensure the directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Ensure the file exists
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump({}, f)

def get_config():
    cfg = json.load(open(CONFIG_FILE))
    if "backup_interval_days" not in cfg:
        cfg["backup_interval_days"] = 7
    if "last_backup" not in cfg:
        cfg["last_backup"] = None
    if "name" not in cfg:
        cfg["name"] = ""
    return cfg

def save_config(cfg):
    json.dump(cfg, open(CONFIG_FILE, "w"), indent=2)

def get_user_name():
    cfg = get_config()
    if not cfg["name"].strip():
        console.print("[bold yellow]Welcome to PyDesk![/bold yellow]")
        name = console.input("What's your name? ").strip()
        cfg["name"] = name or "User"
        save_config(cfg)
    return cfg["name"]

def scheduled_backup():
    cfg = get_config()
    interval_days = cfg.get("backup_interval_days", 7)
    last_backup = cfg.get("last_backup")
    now = datetime.now()
    do_backup = False
    if last_backup:
        last = datetime.fromisoformat(last_backup)
        if now - last >= timedelta(days=interval_days):
            do_backup = True
    else:
        do_backup = True
    if do_backup:
        console.print("[cyan]Performing scheduled backup...[/cyan]")
        backup.backup()
        cfg["last_backup"] = now.isoformat()
        save_config(cfg)

def dashboard(name):
    num_tasks = len(tasks.load_tasks())
    num_notes = len(notes.load_notes())
    total_exp = sum(e["amount"] for e in expenses.load_expenses())
    console.print("\n[bold cyan]==============================[/bold cyan]")
    console.print(f"[bold green]  Welcome back, {name}! 👋[/bold green]")
    console.print("[bold cyan]==============================[/bold cyan]")
    console.print(f"[yellow]Tasks:[/yellow] {num_tasks} | [yellow]Notes:[/yellow] {num_notes} | [yellow]Total Spent:[/yellow] {total_exp:.2f}")
    console.print("[dim]Select an option below:[/dim]\n")

def set_backup_interval():
    cfg = get_config()
    console.print("\n[bold cyan]-- Backup Interval Settings --[/bold cyan]")
    console.print("1. Daily\n2. Weekly")
    choice = console.input("Select backup frequency: ").strip()
    if choice == "1":
        cfg["backup_interval_days"] = 1
    elif choice == "2":
        cfg["backup_interval_days"] = 7
    else:
        console.print("[red]Invalid choice![/red]")
        return
    save_config(cfg)
    console.print(f"[green]Backup interval set to {cfg['backup_interval_days']} day(s).[/green]")

def show_backup_menu():
    while True:
        console.print("\n[bold cyan]-- Backup & Restore --[/bold cyan]")
        console.print("1. Create Backup\n2. Restore Backup\n3. Back")
        choice = console.input("[yellow]Select:[/yellow] ").strip()
        if choice == "1":
            backup.backup()
        elif choice == "2":
            path = console.input("Enter backup file path (e.g., pydesk_backup.zip): ").strip()
            if path:
                backup.restore(path)
        elif choice == "3":
            break
        else:
            console.print("[red]Invalid option![/red]")

def show_menu(name):
    while True:
        menu = Table(show_header=False)
        menu.add_row("1.", "Tasks")
        menu.add_row("2.", "Notes")
        menu.add_row("3.", "Expenses")
        menu.add_row("4.", "Backup & Restore")
        menu.add_row("5.", "Change Name")
        menu.add_row("6.", "Backup Interval Settings")
        menu.add_row("7.", "Exit")
        console.print(menu)
        choice = console.input("\n[bold yellow]Select an option:[/bold yellow] ").strip()
        if choice == "1":
            tasks.menu()
        elif choice == "2":
            notes.menu()
        elif choice == "3":
            expenses.menu()
        elif choice == "4":
            show_backup_menu()
        elif choice == "5":
            cfg = get_config()
            new_name = console.input("Enter new name: ").strip()
            cfg["name"] = new_name or cfg.get("name", "User")
            save_config(cfg)
            console.print(f"[green]Name updated to {cfg['name']}![/green]")
            name = cfg["name"]
        elif choice == "6":
            set_backup_interval()
        elif choice == "7":
            console.print("[bold red]Goodbye![/bold red]")
            backup.backup()  # auto backup on exit
            break
        else:
            console.print("[red]Invalid choice, try again![/red]")

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """PyDesk - Personal CLI Assistant"""
    if ctx.invoked_subcommand is None:
        name = get_user_name()
        scheduled_backup()
        dashboard(name)
        show_menu(name)