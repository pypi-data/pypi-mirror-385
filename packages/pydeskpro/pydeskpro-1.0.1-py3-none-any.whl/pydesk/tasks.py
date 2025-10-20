import json, os
from rich.console import Console
from rich.table import Table

console = Console()
DATA_FILE = os.path.expanduser("~/.pydesk/tasks.json")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
if not os.path.exists(DATA_FILE):
    json.dump([], open(DATA_FILE, "w"))

def load_tasks():
    return json.load(open(DATA_FILE))

def save_tasks(tasks):
    json.dump(tasks, open(DATA_FILE, "w"), indent=2)

def menu():
    while True:
        console.print("\n[bold cyan]-- Tasks Menu --[/bold cyan]")
        console.print("1. Add Task\n2. View Tasks\n3. Delete Task\n4. Back")
        choice = console.input("[yellow]Select:[/yellow] ").strip()
        if choice == "1":
            task = console.input("Enter task: ")
            tasks = load_tasks()
            tasks.append(task)
            save_tasks(tasks)
            console.print("[green]Task added![/green]")
        elif choice == "2":
            tasks = load_tasks()
            table = Table(title="Tasks")
            table.add_column("No")
            table.add_column("Task")
            for i, t in enumerate(tasks, 1):
                table.add_row(str(i), t)
            console.print(table)
        elif choice == "3":
            tasks = load_tasks()
            for i, t in enumerate(tasks, 1):
                console.print(f"{i}. {t}")
            idx = console.input("Delete task number: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(tasks):
                del tasks[int(idx)-1]
                save_tasks(tasks)
                console.print("[red]Task deleted![/red]")
            else:
                console.print("[red]Invalid choice![/red]")
        elif choice == "4":
            break
        else:
            console.print("[red]Invalid option![/red]")