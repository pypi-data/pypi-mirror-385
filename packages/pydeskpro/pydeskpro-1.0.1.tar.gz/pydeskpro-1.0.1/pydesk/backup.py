import os
import zipfile
from rich.console import Console

console = Console()
DATA_DIR = os.path.expanduser("~/.pydesk")
BACKUP_NAME = "pydesk_backup.zip"

def backup():
    """Create a zip backup of all PyDesk data"""
    if not os.path.exists(DATA_DIR):
        console.print("[red]No data to backup![/red]")
        return
    with zipfile.ZipFile(BACKUP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DATA_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DATA_DIR)
                zipf.write(full_path, rel_path)
    console.print(f"[green]Backup created successfully:[/green] {BACKUP_NAME}")


def restore(zip_path):
    """Restore all data from a zip backup"""
    if not os.path.exists(zip_path):
        console.print(f"[red]Backup file not found: {zip_path}[/red]")
        return
    with zipfile.ZipFile(zip_path, "r") as zipf:
        zipf.extractall(DATA_DIR)
    console.print(f"[green]Data restored successfully from {zip_path}![/green]")