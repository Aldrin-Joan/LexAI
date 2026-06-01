import sys
import os
from search_engine import SearchEngine, SearchMode
from llm_client import LLMClient
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def run_rag_demo(query: str):
    """Run a standardized Hybrid RAG (Retrieval-Augmented Generation) demo."""
    engine = SearchEngine()
    llm = LLMClient()
    
    console.print(f"\n[bold blue]>>> Query:[/bold blue] {query}")
    
    # 1. Retrieve relevant cases (Strictly HYBRID)
    # Note: Hybrid mode combines Sparse, Dense (MPNet), and Graph (PageRank)
    with console.status("[bold green]Initializing Hybrid Search (Loading Vector Index)..."):
        results = engine.search(query, limit=5, mode=SearchMode.HYBRID)
    
    if not results:
        console.print("[bold red]No results found.[/bold red]")
        return

    console.print(f"\n[bold green]Found {len(results)} relevant cases via Hybrid Retrieval:[/bold green]")
    for i, res in enumerate(results, 1):
        console.print(f"  {i}. {res['title']} (RRF Score: {res['score']})")

    # 2. Extract context for the top docs
    context_docs = []
    from pathlib import Path
    from config import Config
    full_text_dir = Path(Config.FULL_TEXTS_DIR)

    for res in results:
        doc = {'title': res['title'], 'text': ''}
        file_path = full_text_dir / f"{res['case_id']}.txt"
        if file_path.exists():
            doc['text'] = file_path.read_text(encoding='utf-8', errors='ignore')[:3000]
        context_docs.append(doc)

    # 3. Generate Answer
    with console.status("[bold yellow]Generating legal summary via RAG..."):
        answer = llm.generate_answer(query, context_docs)
    
    if answer:
        console.print("\n" + "="*60)
        console.print(Panel(Markdown(answer), title="AI Legal Assistant Response (Hybrid RAG)", border_style="bold cyan"))
        console.print("="*60 + "\n")
    else:
        console.print("[bold red]Failed to generate answer.[/bold red]")

if __name__ == "__main__":
    # Standardised query for RAG demo
    test_query = "What are the legal precedents for custodial torture compensation in India?"
    if len(sys.argv) > 1:
        test_query = " ".join(sys.argv[1:])
    
    run_rag_demo(test_query)
