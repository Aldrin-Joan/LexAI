import sys
import os
from search_engine import SearchEngine, SearchMode
from llm_client import LLMClient
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from pathlib import Path
from config import Config

console = Console()

def run_case_brief(query: str):
    """Retrieve a specific case and generate a structured Case Brief."""
    engine = SearchEngine()
    llm = LLMClient()
    
    console.print(f"\n[bold blue]>>> Analyzing Case:[/bold blue] {query}")
    
    # 1. Retrieve the specific case
    # We use HYBRID mode to find the best match for the query/title
    with console.status("[bold green]Locating judgment in database..."):
        results = engine.search(query, limit=1, mode=SearchMode.HYBRID)
    
    if not results:
        console.print("[bold red]Case not found.[/bold red]")
        return

    case = results[0]
    case_id = case['case_id']
    case_title = case['title']
    
    console.print(f"[bold green]Verified Match:[/bold green] {case_title} ({case_id})")

    # 2. Extract full text context
    with console.status("[bold blue]Extracting judgment text..."):
        file_path = Path(Config.FULL_TEXTS_DIR) / f"{case_id}.txt"
        if file_path.exists():
            full_text = file_path.read_text(encoding='utf-8', errors='ignore')
        else:
            console.print("[bold red]Full text not found on disk.[/bold red]")
            return

    # 3. Generate Case Brief
    with console.status(f"[bold yellow]Generating structured Brief for '{case_title}'..."):
        # We pass the metadata dictionary as well
        brief = llm.generate_case_brief(case_title, full_text, metadata=case)
    
    if brief:
        console.print("\n" + "="*70)
        console.print(Panel(Markdown(brief), title=f"LEGAL BRIEF: {case_title}", border_style="bold green"))
        console.print("="*70 + "\n")
        
        # Save to file
        output_file = f"case_brief_{case_id}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Case Brief: {case_title}\n\n")
            f.write(brief)
        console.print(f"[italic]Brief saved to {output_file}[/italic]")
    else:
        console.print("[bold red]Failed to generate brief.[/bold red]")

if __name__ == "__main__":
    # Landmark default case (or pass via CLI)
    target_case = "Kesavananda Bharati v. State of Kerala"
    if len(sys.argv) > 1:
        target_case = " ".join(sys.argv[1:])
    
    run_case_brief(target_case)
