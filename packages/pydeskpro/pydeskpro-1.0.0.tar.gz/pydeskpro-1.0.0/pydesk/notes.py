import json, os
from rich.console import Console
from rich.table import Table

console = Console()
DATA_FILE = os.path.expanduser("~/.pydesk/notes.json")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
if not os.path.exists(DATA_FILE):
    json.dump([], open(DATA_FILE, "w"))

def load_notes():
    return json.load(open(DATA_FILE))

def save_notes(notes):
    json.dump(notes, open(DATA_FILE, "w"), indent=2)

def menu():
    while True:
        console.print("\n[bold cyan]-- Notes Menu --[/bold cyan]")
        console.print("1. Add Note\n2. View Notes\n3. Delete Note\n4. Back")
        choice = console.input("[yellow]Select:[/yellow] ").strip()
        if choice == "1":
            title = console.input("Title: ")
            body = console.input("Body: ")
            notes = load_notes()
            notes.append({"title": title, "body": body})
            save_notes(notes)
            console.print("[green]Note added![/green]")
        elif choice == "2":
            notes = load_notes()
            table = Table(title="Notes")
            table.add_column("No")
            table.add_column("Title")
            table.add_column("Body")
            for i, n in enumerate(notes, 1):
                table.add_row(str(i), n["title"], n["body"])
            console.print(table)
        elif choice == "3":
            notes = load_notes()
            for i, n in enumerate(notes, 1):
                console.print(f"{i}. {n['title']}")
            idx = console.input("Delete note number: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(notes):
                del notes[int(idx)-1]
                save_notes(notes)
                console.print("[red]Note deleted![/red]")
            else:
                console.print("[red]Invalid choice![/red]")
        elif choice == "4":
            break
        else:
            console.print("[red]Invalid option![/red]")