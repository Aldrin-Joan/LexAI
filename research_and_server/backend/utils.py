"""
Utility functions for Legal Case Knowledge Graph System.

This module provides helper functions for:
- Text preprocessing
- Date parsing
- Citation standardization
- ID generation
- Rich console formatting
"""

import re
import hashlib
from datetime import datetime
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.table import Table

# Initialize Rich console
console = Console()


def clean_text(text: str) -> str:
    """
    Clean and normalize text.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep legal punctuation
    text = re.sub(r'[^\w\s.,;:()\-\[\]\/&]', '', text)
    return text.strip()


def normalize_case_number(case_number: str) -> str:
    """
    Normalize case number format.

    Args:
        case_number: Raw case number

    Returns:
        Normalized case number
    """
    # Remove extra spaces and convert to uppercase
    case_number = re.sub(r'\s+', ' ', case_number.strip().upper())
    # Standardize common patterns
    case_number = re.sub(r'NO\.?', 'NO', case_number)
    case_number = re.sub(r'OF', 'OF', case_number)
    return case_number


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string to datetime object.

    Args:
        date_str: Date string in various formats

    Returns:
        datetime object or None if parsing fails
    """
    date_formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    return None


def extract_year_from_text(text: str) -> Optional[int]:
    """
    Extract year from text.

    Args:
        text: Text containing year

    Returns:
        Year as integer or None
    """
    # Look for 4-digit year between 1950 and 2030
    match = re.search(r'\b(19[5-9]\d|20[0-2]\d|2030)\b', text)
    if match:
        return int(match.group(1))
    return None


def generate_case_id(
    case_number: str,
    date: datetime,
    court: str
) -> str:
    """
    Generate unique case ID.

    Args:
        case_number: Case number
        date: Case date
        court: Court name

    Returns:
        Unique case ID
    """
    # Create hash from case details
    text = f"{case_number}_{date.isoformat()}_{court}"
    hash_obj = hashlib.md5(text.encode())
    return f"case_{hash_obj.hexdigest()[:12]}"


def generate_entity_id(entity_type: str, text: str) -> str:
    """
    Generate unique entity ID.

    Args:
        entity_type: Type of entity
        text: Entity text

    Returns:
        Unique entity ID
    """
    text_clean = text.lower().strip()
    hash_obj = hashlib.md5(text_clean.encode())
    return f"{entity_type.lower()}_{hash_obj.hexdigest()[:12]}"


def standardize_citation(citation: str) -> str:
    """
    Standardize legal citation format.

    Args:
        citation: Raw citation text

    Returns:
        Standardized citation
    """
    # Remove extra whitespace
    citation = re.sub(r'\s+', ' ', citation.strip())

    # Common patterns for Indian citations
    # AIR format: AIR 2020 SC 1234
    citation = re.sub(
        r'AIR\s+(\d{4})\s+(\w+)\s+(\d+)',
        r'AIR \1 \2 \3',
        citation
    )

    # SCC format: (2020) 5 SCC 123
    citation = re.sub(
        r'\((\d{4})\)\s+(\d+)\s+SCC\s+(\d+)',
        r'(\1) \2 SCC \3',
        citation
    )

    return citation


def calculate_confidence_score(
    scores: List[float],
    method: str = "average"
) -> float:
    """
    Calculate overall confidence score.

    Args:
        scores: List of individual confidence scores
        method: Calculation method (average, min, max)

    Returns:
        Overall confidence score
    """
    if not scores:
        return 0.0

    if method == "average":
        return sum(scores) / len(scores)
    elif method == "min":
        return min(scores)
    elif method == "max":
        return max(scores)
    else:
        return sum(scores) / len(scores)


def print_header(title: str) -> None:
    """Print a styled header."""
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", expand=False))


def print_success(message: str) -> None:
    """Print success message with Rich formatting."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message with Rich formatting."""
    console.print(f"[red]✗[/red] {message}")


def print_info(message: str) -> None:
    """Print info message with Rich formatting."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_warning(message: str) -> None:
    """Print warning message with Rich formatting."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_panel(title: str, content: str, style: str = "blue") -> None:
    """Print content in a Rich panel."""
    console.print(Panel(content, title=title, border_style=style))


def create_progress_bar() -> Progress:
    """Create a Rich progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )


def create_table(
    title: str,
    columns: List[str],
    rows: List[List[str]]
) -> Table:
    """
    Create a Rich table.

    Args:
        title: Table title
        columns: Column headers
        rows: Table rows

    Returns:
        Rich Table object
    """
    table = Table(title=title, show_header=True, header_style="bold")

    for col in columns:
        table.add_column(col)

    for row in rows:
        table.add_row(*row)

    return table


def print_table(
    title: str,
    columns: List[str],
    rows: List[List[str]]
) -> None:
    """Print a Rich table."""
    table = create_table(title, columns, rows)
    console.print(table)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
