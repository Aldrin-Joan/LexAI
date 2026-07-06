import os
import sqlite3
from pathlib import Path
from rich.console import Console
from rich.progress import track
from config import Config

console = Console()

def migrate_texts_to_db():
    db_path = Config.INDEX_DB_PATH
    full_text_dir = Path("data/full_texts")
    
    if not full_text_dir.exists():
        console.print(f"[bold red]Source directory {full_text_dir} not found![/bold red]")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure the full_text column exists in the cases table
    try:
        cursor.execute("ALTER TABLE cases ADD COLUMN full_text TEXT")
        console.print("[green]Added 'full_text' column to 'cases' table.[/green]")
    except sqlite3.OperationalError:
        console.print("[yellow]'full_text' column already exists.[/yellow]")

    # Also update the FTS table to include content if needed
    # (Actually we'll just store the full text in the cases table for RAG)

    txt_files = list(full_text_dir.glob("*.txt"))
    console.print(f"Found {len(txt_files)} text files to migrate.")

    updated_count = 0
    for file_path in track(txt_files, description="Migrating texts..."):
        case_id = file_path.stem
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # 1. Update the main cases table
            cursor.execute(
                "UPDATE cases SET full_text = ? WHERE case_id = ?",
                (content, case_id)
            )

            # 2. Update the FTS table for keyword search
            # (We only index the first 50,000 chars to avoid FTS limits)
            cursor.execute(
                "UPDATE cases_fts SET content = ? WHERE case_id = ?",
                (content[:50000], case_id)
            )
            
            if cursor.rowcount > 0:
                updated_count += 1
            
            # Periodic commit to prevent rollback on interrupt
            if updated_count % 10 == 0:
                conn.commit()
                
        except Exception as e:
            console.print(f"[dim red]Error processing {case_id}: {e}[/dim red]")

    conn.commit()
    
    # Verify migration
    cursor.execute("SELECT COUNT(*) FROM cases WHERE full_text IS NOT NULL")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    console.print(f"\n[bold green]Migration Complete![/bold green]")
    console.print(f"Successfully updated [blue]{updated_count}[/blue] case records.")
    console.print(f"Total cases with embedded text: [blue]{count}[/blue]")

if __name__ == "__main__":
    migrate_texts_to_db()
