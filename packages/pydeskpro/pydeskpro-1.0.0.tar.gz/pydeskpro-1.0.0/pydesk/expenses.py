import json, os
from rich.console import Console
from rich.table import Table

console = Console()
DATA_FILE = os.path.expanduser("~/.pydesk/expenses.json")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
if not os.path.exists(DATA_FILE):
    json.dump([], open(DATA_FILE, "w"))

def load_expenses():
    return json.load(open(DATA_FILE))

def save_expenses(expenses):
    json.dump(expenses, open(DATA_FILE, "w"), indent=2)

def menu():
    while True:
        console.print("\n[bold cyan]-- Expenses Menu --[/bold cyan]")
        console.print("1. Add Expense\n2. View Expenses\n3. Delete Expense\n4. Total\n5. Back")
        choice = console.input("[yellow]Select:[/yellow] ").strip()
        if choice == "1":
            desc = console.input("Description: ")
            amount = console.input("Amount: ").strip()
            try:
                amount = float(amount)
                expenses = load_expenses()
                expenses.append({"desc": desc, "amount": amount})
                save_expenses(expenses)
                console.print("[green]Expense added![/green]")
            except ValueError:
                console.print("[red]Invalid amount![/red]")
        elif choice == "2":
            expenses = load_expenses()
            table = Table(title="Expenses")
            table.add_column("No")
            table.add_column("Description")
            table.add_column("Amount")
            total = 0
            for i, e in enumerate(expenses, 1):
                table.add_row(str(i), e["desc"], f"{e['amount']:.2f}")
                total += e["amount"]
            console.print(table)
            console.print(f"[bold green]Total: {total:.2f}[/bold green]")
        elif choice == "3":
            expenses = load_expenses()
            for i, e in enumerate(expenses, 1):
                console.print(f"{i}. {e['desc']} ({e['amount']})")
            idx = console.input("Delete expense number: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(expenses):
                del expenses[int(idx)-1]
                save_expenses(expenses)
                console.print("[red]Expense deleted![/red]")
            else:
                console.print("[red]Invalid choice![/red]")
        elif choice == "4":
            total = sum(e["amount"] for e in load_expenses())
            console.print(f"[bold green]Total Expenses: {total:.2f}[/bold green]")
        elif choice == "5":
            break
        else:
            console.print("[red]Invalid option![/red]")