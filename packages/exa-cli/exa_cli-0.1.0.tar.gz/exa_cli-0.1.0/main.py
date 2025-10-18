import os
import typer
from typing import Optional
from rich.console import Console
from rich.json import JSON
from exa_py import Exa

app = typer.Typer(
    help="CLI tool for Exa search API - neural search engine for the web",
    epilog="Requires EXA_API_KEY environment variable (auto-loaded from .env in project directory)"
)
console = Console()

def get_exa_client() -> Exa:
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        console.print("[red]Error: EXA_API_KEY environment variable not set[/red]")
        raise typer.Exit(1)
    return Exa(api_key=api_key)

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query (e.g., 'best linux window managers')"),
    num_results: Optional[int] = typer.Option(10, "--num", "-n", help="Number of results to return (default: 10)"),
    include_domains: Optional[str] = typer.Option(None, "--include", help="Comma-separated domains to include (e.g., 'github.com,archlinux.org')"),
    exclude_domains: Optional[str] = typer.Option(None, "--exclude", help="Comma-separated domains to exclude"),
    use_autoprompt: bool = typer.Option(True, "--autoprompt/--no-autoprompt", help="Use Exa's autoprompt to optimize query (default: True)"),
):
    """
    Search the web using Exa's neural search.
    
    Returns titles, URLs, and brief snippets. Use 'contents' command to fetch full text.
    
    Example: exa search "rust async programming" --num 5 --include github.com,rust-lang.org
    """
    exa = get_exa_client()
    
    include = include_domains.split(",") if include_domains else None
    exclude = exclude_domains.split(",") if exclude_domains else None
    
    results = exa.search(
        query=query,
        num_results=num_results,
        include_domains=include,
        exclude_domains=exclude,
        use_autoprompt=use_autoprompt,
    )
    
    for result in results.results:
        console.print(f"[bold cyan]{result.title}[/bold cyan]")
        console.print(f"[dim]{result.url}[/dim]")
        if hasattr(result, 'text') and result.text:
            console.print(result.text[:200] + "...")
        console.print()

@app.command()
def similar(
    url: str = typer.Argument(..., help="URL to find similar pages for (e.g., 'https://github.com/linux-surface')"),
    num_results: Optional[int] = typer.Option(10, "--num", "-n", help="Number of similar results to return (default: 10)"),
):
    """
    Find pages similar to a given URL using Exa's semantic similarity.
    
    Useful for discovering related content, alternative implementations, or competitive analysis.
    
    Example: exa similar "https://swaywm.org" --num 5
    """
    exa = get_exa_client()
    
    results = exa.find_similar(url=url, num_results=num_results)
    
    for result in results.results:
        console.print(f"[bold cyan]{result.title}[/bold cyan]")
        console.print(f"[dim]{result.url}[/dim]")
        console.print()

@app.command()
def contents(
    urls: list[str] = typer.Argument(..., help="One or more URLs to fetch content from"),
    text: bool = typer.Option(True, "--text/--no-text", help="Include full text content (default: True, max 5000 chars per page)"),
):
    """
    Fetch clean, readable content from one or more URLs.
    
    Returns markdown-formatted text without ads, navigation, or boilerplate.
    Supports batch fetching - provide multiple URLs to fetch them all in one API call.
    
    Example: exa contents "https://archlinux.org" "https://swaywm.org" --text
    """
    exa = get_exa_client()
    
    result = exa.get_contents(urls=urls, text={"max_characters": 5000} if text else None)
    
    for item in result.results:
        console.print(f"[bold cyan]{item.title}[/bold cyan]")
        console.print(f"[dim]{item.url}[/dim]")
        console.print()
        if hasattr(item, 'text') and item.text:
            console.print(item.text)

@app.command()
def answer(
    query: str = typer.Argument(..., help="Question to answer (e.g., 'what is the linux surface project')"),
    text: bool = typer.Option(False, "--text", help="Include full text from citations (default: False)"),
):
    """
    Get an AI-generated answer to a question with citations.
    
    Combines Exa search with LLM processing to provide factual answers backed by sources.
    Useful for quick research and fact-checking.
    
    Example: exa answer "how do i install arch linux on a surface pro"
    """
    exa = get_exa_client()
    
    result = exa.answer(query=query, text=text)
    
    console.print(f"[bold green]Answer:[/bold green] {result.answer}")
    console.print()
    console.print("[bold]Citations:[/bold]")
    for citation in result.citations:
        console.print(f"  • [cyan]{citation.title}[/cyan]")
        console.print(f"    [dim]{citation.url}[/dim]")

if __name__ == "__main__":
    app()
