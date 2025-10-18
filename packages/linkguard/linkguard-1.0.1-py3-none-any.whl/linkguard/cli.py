import typer
import asyncio
import os
import sys
from typing import Optional, Dict, Any, List, Tuple
from rich.console import Console
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)
from rich.table import Table
from rich.panel import Panel
from rich import box
from pathlib import Path

# Set UTF-8 encoding for Windows console to support Rich Unicode characters
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    # Reconfigure stdout/stderr for current process if available (Python 3.7+)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

from linkguard.scanner.file_scanner import FileScanner
from linkguard.scanner.url_extractor import URLExtractor
from linkguard.scanner.link_checker import LinkChecker
from linkguard.scanner.rules import EnvironmentRules
from linkguard.reporter.exporter import Exporter
from linkguard.utils.config import load_config
from linkguard.utils.logger import get_logger
from linkguard import __version__

app = typer.Typer(
    name="linkguard",
    help="CLI tool for detecting broken links and localhost URLs in " "project files",
)
# Initialize console with safe encoding handling
try:
    console = Console(force_terminal=True, legacy_windows=False)
except Exception:
    # Fallback for environments with limited Unicode support
    console = Console(force_terminal=True, legacy_windows=True, no_color=False)


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(
            f"[bold cyan]LinkGuard[/bold cyan] version " f"[bold green]{__version__}[/bold green]"
        )
        raise typer.Exit()


@app.command()
def scan(
    directory: Optional[str] = typer.Argument(
        None, help="Directory to scan (default: current directory)"
    ),
    mode: str = typer.Option(
        "dev",
        "--mode",
        "-m",
        help="Scanning mode: 'dev' or 'prod' " "(prod flags localhost URLs)",
    ),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Timeout in seconds for HTTP requests"),
    concurrency: int = typer.Option(
        50, "--concurrency", "-c", help="Number of concurrent HTTP requests"
    ),
    max_retries: int = typer.Option(
        2, "--max-retries", "-r", help="Maximum retry attempts for failed requests"
    ),
    export: Optional[str] = typer.Option(
        None, "--export", "-e", help="Export results to a JSON file"
    ),
    ignore: Optional[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help="Comma-separated list of glob patterns to ignore",
    ),
    resolve_relative: bool = typer.Option(
        False, "--resolve-relative", help="Resolve relative file paths to absolute file:// URLs"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version and exit"
    ),
) -> None:
    """Scan directory for broken links and environment violations."""

    # Convert directory to Path, default to current directory
    dir_path = Path(directory) if directory else Path(".")

    # Validate directory exists
    if not dir_path.exists():
        console.print(f"[bold red]Error:[/bold red] Directory does not exist: {dir_path}")
        raise typer.Exit(code=2)

    if not dir_path.is_dir():
        console.print(f"[bold red]Error:[/bold red] Path is not a directory: {dir_path}")
        raise typer.Exit(code=2)

    # Load configuration with CLI overrides
    cli_overrides: Dict[str, Any] = {}
    cli_overrides["mode"] = mode
    cli_overrides["timeout"] = timeout
    cli_overrides["concurrency"] = concurrency
    if ignore is not None:
        # Split comma-separated patterns and strip whitespace
        cli_overrides["ignore_patterns"] = [p.strip() for p in ignore.split(",")]

    try:
        config = load_config(dir_path, cli_overrides)
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        raise typer.Exit(code=2)

    # Get final config values
    final_mode = config.get("mode", "dev")
    final_timeout = config.get("timeout", 10)
    final_concurrency = config.get("concurrency", 10)

    # Initialize logger for verbose mode
    logger = get_logger("linkguard", verbose=verbose)

    # Print header with panel
    header = Panel(
        f"[bold cyan]Directory:[/bold cyan] {dir_path}\n"
        f"[bold cyan]Mode:[/bold cyan] {final_mode} | "
        f"[bold cyan]Timeout:[/bold cyan] {final_timeout}s | "
        f"[bold cyan]Concurrency:[/bold cyan] {final_concurrency} | "
        f"[bold cyan]Max Retries:[/bold cyan] {max_retries}",
        title="[bold blue]LinkGuard Scanner[/bold blue]",
        border_style="blue",
        box=box.ROUNDED,
    )
    console.print(header)
    console.print()

    if verbose:
        if config.get_ignore_patterns():
            patterns = ", ".join(config.get_ignore_patterns())
            logger.info(f"[yellow]Ignoring patterns:[/yellow] {patterns}")
        if resolve_relative:
            logger.info("[yellow]Relative URL resolution:[/yellow] enabled")

    # Scan for files with loading indicator
    with console.status("[bold cyan]Scanning for files...[/bold cyan]", spinner="dots"):
        scanner = FileScanner(dir_path, ignore_patterns=set(config.get_ignore_patterns()))
        files = scanner.scan()

    console.print(
        f"[bold green]✓[/bold green] Found [bold cyan]{len(files)}[/bold cyan] " "files to scan"
    )

    # Extract URLs from files with progress indicator
    extractor = URLExtractor(resolve_relative=resolve_relative)
    all_urls: List[Tuple[Path, Dict[str, Any]]] = []

    with console.status("[bold cyan]Extracting URLs from files...[/bold cyan]", spinner="dots"):
        for file in files:
            urls = extractor.extract_from_file(file)
            if urls:
                all_urls.extend([(file, url) for url in urls])

    console.print(
        f"[bold green]✓[/bold green] Extracted [bold cyan]{len(all_urls)}[/bold cyan] " "URLs"
    )

    if verbose:
        if files:
            file_names = ", ".join(f.name for f in files[:5])
            suffix = "..." if len(files) > 5 else ""
            console.print(f"[dim]  Files: {file_names}{suffix}[/dim]")
        if all_urls:
            # Group URLs by file for cleaner logging
            file_url_counts: Dict[Path, int] = {}
            for file_path, url_info in all_urls:
                file_url_counts[file_path] = file_url_counts.get(file_path, 0) + 1
            url_items = list(file_url_counts.items())[:3]
            url_summary = ", ".join(f"{path.name}({count})" for path, count in url_items)
            if len(file_url_counts) > 3:
                url_summary += "..."
            console.print(f"[dim]  URLs per file: {url_summary}[/dim]")

    console.print()  # Add spacing

    if not all_urls:
        console.print("[bold yellow]No URLs found to check.[/bold yellow]")
        return

    # Check environment rules
    with console.status("[bold cyan]Checking environment rules...[/bold cyan]", spinner="dots"):
        rules = EnvironmentRules(mode=final_mode)
        violations = rules.check_urls(all_urls)

    if violations:
        console.print(f"\n[bold red]⚠ Found {len(violations)} rule violation(s):[/bold red]")
        for i, v in enumerate(violations[:10], 1):  # Show first 10
            console.print(
                f"  {i}. [red]{v.url}[/red]\n"
                f"     [dim]File:[/dim] {v.file_path}:{v.line_number or '?'}\n"
                f"     [dim]Rule:[/dim] {v.rule} ([yellow]{v.severity}[/yellow])"
            )
        if len(violations) > 10:
            console.print(f"  [dim]... and {len(violations) - 10} more violations[/dim]")
        console.print()
    elif verbose:
        console.print("[dim]  ✓ No environment rule violations[/dim]")

    # Check links asynchronously with enhanced progress display
    console.print("[bold blue]» Checking links...[/bold blue]\n")

    checker = LinkChecker(
        timeout=final_timeout, max_concurrent=final_concurrency, max_retries=max_retries
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        TaskProgressColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task(
            "[cyan]Checking links[/cyan]",
            total=len(all_urls),
        )

        def update_progress(completed: int):
            # Update progress bar
            progress.update(task, completed=completed)

            # Log progress milestones in verbose mode
            if verbose and completed <= len(all_urls):
                # Log at 25%, 50%, 75%, 100% or first 2 URLs
                total = len(all_urls)
                milestones = [int(total * 0.25), int(total * 0.5), int(total * 0.75), total]
                if completed <= 2 or completed in milestones:
                    current_file, current_url_data = all_urls[completed - 1]
                    url = current_url_data["url"]
                    # Truncate long URLs
                    display_url = url if len(url) <= 60 else url[:57] + "..."
                    msg = f"[dim]  [{completed}/{len(all_urls)}] {display_url}[/dim]"
                    console.print(msg)

        results = asyncio.run(checker.check_links(all_urls, update_progress))

    # Display Results
    console.print()
    broken_links = [r for r in results if r.is_broken]
    working_links = [r for r in results if not r.is_broken]

    # Calculate average response time for working links
    avg_response_time = (
        sum(r.response_time for r in working_links if r.response_time) / len(working_links)
        if working_links
        else 0
    )

    # Show summary table with enhanced styling
    table = Table(
        title="[bold blue]Scan Summary[/bold blue]",
        box=box.ROUNDED,
        border_style="blue",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="bold")

    table.add_row("Files Scanned", f"[cyan]{len(files)}[/cyan]")
    table.add_row("URLs Found", f"[cyan]{len(all_urls)}[/cyan]")
    table.add_row("Working Links", f"[bold green]{len(working_links)}[/bold green]")
    table.add_row("Broken Links", f"[bold red]{len(broken_links)}[/bold red]")
    table.add_row("Rule Violations", f"[bold yellow]{len(violations)}[/bold yellow]")
    if working_links:
        table.add_row("Avg Response Time", f"[dim]{avg_response_time:.2f}s[/dim]")

    console.print(table)
    console.print()

    # Show broken links details with better formatting
    if broken_links:
        console.print(f"[bold red]✗ Found {len(broken_links)} broken link(s):[/bold red]\n")
        for i, result in enumerate(broken_links[:15], 1):  # Show first 15
            # Determine error display
            error_msg = result.error or f"HTTP {result.status_code}"

            console.print(
                f"  {i}. [red]{result.url}[/red]\n"
                f"     [dim]File:[/dim] {result.file_path}:{result.line_number or '?'}\n"
                f"     [dim]Error:[/dim] [yellow]{error_msg}[/yellow]\n"
                f"     [dim]Response Time:[/dim] {result.response_time:.2f}s"
            )

        if len(broken_links) > 15:
            remaining = len(broken_links) - 15
            console.print(f"\n  [dim]... and {remaining} more broken links[/dim]")

    if working_links and verbose:
        msg = (
            f"\n[bold green]✓ All {len(working_links)} other links are "
            "working correctly![/bold green]"
        )
        console.print(msg)
    elif working_links:
        msg = f"\n[bold green]✓ {len(working_links)} link(s) working correctly" "[/bold green]"
        console.print(msg)

    # Export results if requested
    if export:
        export_path = Path(export)
        extension = export_path.suffix.lower()

        metadata: Dict[str, Any] = {
            "directory": str(dir_path),
            "mode": final_mode,
            "timeout": final_timeout,
            "concurrency": final_concurrency,
            "files_scanned": len(files),
        }

        try:
            if extension == ".json":
                Exporter.export_to_json(results, violations, export_path, metadata)
            elif extension == ".csv":
                Exporter.export_to_csv(results, violations, export_path)
            elif extension in {".md", ".markdown"}:
                Exporter.export_to_markdown(results, violations, export_path, metadata)
            else:
                console.print(
                    f"[yellow]:white_exclamation_mark:[/yellow] "
                    f"Unsupported export format: {extension}"
                )
                msg = "[dim]Supported formats are .json, .csv, .md/.markdown[/dim]"
                console.print(msg)
                return

            console.print(
                f"\n[bold green]✓ Results exported to:[/bold green] " f"[cyan]{export_path}[/cyan]"
            )
            if verbose:
                logger.info(f"[green]Export format:[/green] {extension}")
        except Exception as e:
            console.print(f"\n[bold red]✗ Failed to export results:[/bold red] {e}")

    # Exit with appropriate code
    if violations and final_mode == "prod":
        console.print(
            "\n[bold yellow]⚠ Environment violations detected in " "production mode![/bold yellow]"
        )
        console.print("[dim]These URLs should not be used in production:[/dim]\n")
        for i, v in enumerate(violations[:5], 1):
            console.print(
                f"  {i}. [yellow]{v.url}[/yellow]\n"
                f"     [dim]in {v.file_path}:{v.line_number or '?'} "
                f"({v.rule})[/dim]"
            )
        if len(violations) > 5:
            console.print(f"\n  [dim]... and {len(violations) - 5} more violations[/dim]")
        console.print("\n[bold red]��� Scan failed with exit code 3[/bold red]")
        raise typer.Exit(code=3)

    if broken_links:
        console.print(
            f"\n[bold red]✗ Scan completed with {len(broken_links)} "
            "broken link(s) - exit code 1[/bold red]"
        )
        raise typer.Exit(code=1)

    console.print(
        "\n[bold green]✓ Scan completed successfully - all links are working!" "[/bold green]"
    )
    raise typer.Exit(code=0)


def main():
    app()


if __name__ == "__main__":
    main()
