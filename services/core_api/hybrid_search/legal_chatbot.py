import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from search_engine import SearchEngine, SearchMode
from llm_client import LLMClient
from session_manager import SessionManager
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from config import Config

console = Console()

class LegalChatbot:
    def __init__(self):
        # Load .env from parent directory
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        
        self.engine = SearchEngine()
        self.llm = LLMClient()
        self.sessions = SessionManager(sessions_dir=str(Path(__file__).parent.parent / "sessions"))
        self.full_text_dir = Path(Config.FULL_TEXTS_DIR)

    def process_query(self, query: str):
        self.sessions.add_message("user", query)
        
        with console.status("[bold green]Searching precedents..."):
            results = self.engine.search(query, limit=5, mode=SearchMode.HYBRID)
        
        if not results:
            msg = "No relevant legal precedents found in the database."
            console.print(f"[bold red]{msg}[/bold red]")
            self.sessions.add_message("assistant", msg)
            return

        # Prepare context for LLM (Already hydrated by SearchEngine from DB)
        context_docs = [
            {'title': res['title'], 'text': res.get('text_content', '')}
            for res in results
        ]

        # Display Top 5 Important Retrieved Documents
        doc_table = Table(title="📑 Top 5 Relevant Precedents Found", show_header=True, header_style="bold magenta")
        doc_table.add_column("Rank", justify="center")
        doc_table.add_column("Title", style="cyan")
        doc_table.add_column("Year", justify="center")
        doc_table.add_column("Similarity", justify="right")
        
        for i, res in enumerate(results):
            doc_table.add_row(str(i+1), res['title'][:80], str(res['year']), f"{res['score']:.4f}")
        
        console.print(doc_table)

        with console.status("[bold yellow]Synthesizing legal advice..."):
            answer = self.llm.generate_answer(query, context_docs, history=self.sessions.history)
            
        if answer:
            console.print("\n" + "─"* console.width)
            console.print(Panel(
                Markdown(answer), 
                title="⚖️ Legal Assistant Recommendation", 
                subtitle=f"Session: {self.sessions.current_session_id} | Mode: Hybrid",
                border_style="cyan"
            ))
            console.print("─"* console.width + "\n")
            
            # Send message to session history
            self.sessions.add_message(
                "assistant", 
                answer, 
                metadata={"precedents": [r['title'] for r in results]}
            )
        else:
            msg = "Consultation failed. Try reformatting your query."
            console.print(f"[bold red]{msg}[/bold red]")
            self.sessions.add_message("assistant", msg)

    def list_recent_sessions(self):
        history = self.sessions.list_sessions()
        if not history:
            console.print("[dim]No previous sessions found.[/dim]")
            return
            
        table = Table(title="Recent Sessions")
        table.add_column("ID", style="cyan")
        table.add_column("Last Updated", style="magenta")
        table.add_column("Messages", justify="right")
        
        for s in history[:5]:
            table.add_row(s['id'], s['last_updated'][:16], str(s['message_count']))
        
        console.print(table)

    def run(self):
        console.print(Panel.fit(
            "[bold white]Welcome to the AI Legal Research Assistant[/bold white]\n"
            "[dim]Powered by Hybrid Retrieval & Persistent Sessions[/dim]\n"
            "[blue]Commands: 'sessions' to list, 'new' for new chat, 'exit' to quit[/blue]",
            border_style="bold blue"
        ))
        
        while True:
            query = Prompt.ask(f"\n[bold yellow][{self.sessions.current_session_id}][/bold yellow] How can I help?")
            
            if query.lower() in ["exit", "quit", "q"]:
                break
            
            if query.lower() == "sessions":
                self.list_recent_sessions()
                continue
                
            if query.lower() == "new":
                new_id = self.sessions.start_new_session()
                console.print(f"[bold green]Started new session: {new_id}[/bold green]")
                continue
                
            if not query.strip():
                continue
                
            self.process_query(query)

if __name__ == "__main__":
    bot = LegalChatbot()
    
    # Handle direct query from command line if provided
    if len(sys.argv) > 1:
        bot.process_query(" ".join(sys.argv[1:]))
    else:
        bot.run()
