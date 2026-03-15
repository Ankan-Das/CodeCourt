"""CodeCourt CLI - Review code from the command line.

Usage:
    codecourt review changes.diff
    codecourt review --stdin < changes.diff
    codecourt review --repo .
    git diff | codecourt review --stdin
"""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from codecourt.agents.coordinator import Coordinator, CoordinatedReviewResult
from codecourt.agents.models import Approval, Severity
from codecourt.providers import list_providers
from codecourt.tools import parse_diff

console = Console()

SEVERITY_STYLES = {
    Severity.CRITICAL: ("bold red", "🔴"),
    Severity.ERROR: ("red", "🟠"),
    Severity.WARNING: ("yellow", "🟡"),
    Severity.INFO: ("blue", "🔵"),
    Severity.PRAISE: ("green", "🟢"),
}

APPROVAL_STYLES = {
    Approval.APPROVE: ("bold green", "✅ APPROVED"),
    Approval.REQUEST_CHANGES: ("bold red", "❌ CHANGES REQUESTED"),
    Approval.COMMENT: ("bold yellow", "💬 COMMENT"),
}


def get_version() -> str:
    """Get the package version."""
    try:
        from importlib.metadata import version
        return version("codecourt")
    except Exception:
        return "0.1.0"


@click.group()
@click.version_option(version=get_version(), prog_name="codecourt")
def cli() -> None:
    """CodeCourt - Where your code faces trial by AI.
    
    Multi-agent code review from the command line.
    """
    pass


@cli.command()
@click.argument("diff_file", type=click.Path(exists=True), required=False)
@click.option(
    "--stdin",
    is_flag=True,
    help="Read diff from standard input",
)
@click.option(
    "--repo",
    type=click.Path(exists=True),
    help="Review uncommitted changes in a git repository",
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic", "ollama"]),
    default="openai",
    help="LLM provider to use",
)
@click.option(
    "--model",
    type=str,
    default=None,
    help="Specific model to use (e.g., gpt-4o, claude-3-5-sonnet-20241022)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["rich", "json", "markdown"]),
    default="rich",
    help="Output format",
)
@click.option(
    "--parallel/--sequential",
    default=True,
    help="Run agents in parallel (faster) or sequentially",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed output",
)
def review(
    diff_file: str | None,
    stdin: bool,
    repo: str | None,
    provider: str,
    model: str | None,
    output_format: str,
    parallel: bool,
    verbose: bool,
) -> None:
    """Review code changes.

    Examples:

        codecourt review changes.diff

        codecourt review --stdin < changes.diff

        git diff | codecourt review --stdin

        codecourt review --repo . --provider ollama
    """
    diff_content = _get_diff_content(diff_file, stdin, repo)
    
    if not diff_content or not diff_content.strip():
        console.print("[yellow]No changes to review.[/yellow]")
        sys.exit(0)

    parsed = parse_diff(diff_content)
    
    if not parsed.files:
        console.print("[yellow]No parseable changes found in diff.[/yellow]")
        sys.exit(0)

    if verbose:
        console.print(f"[dim]Provider: {provider}[/dim]")
        console.print(f"[dim]Model: {model or 'default'}[/dim]")
        console.print(f"[dim]Files: {len(parsed.files)}[/dim]")
        console.print(f"[dim]Additions: {parsed.total_additions}[/dim]")
        console.print(f"[dim]Deletions: {parsed.total_deletions}[/dim]")
        console.print()

    with console.status("[bold blue]Reviewing code...", spinner="dots"):
        result = asyncio.run(_run_review(parsed, provider, model, parallel))

    if output_format == "json":
        _output_json(result)
    elif output_format == "markdown":
        _output_markdown(result)
    else:
        _output_rich(result, verbose)

    sys.exit(_get_exit_code(result))


def _get_diff_content(
    diff_file: str | None,
    stdin: bool,
    repo: str | None,
) -> str:
    """Get diff content from the specified source."""
    if stdin:
        return sys.stdin.read()
    
    if diff_file:
        return Path(diff_file).read_text()
    
    if repo:
        return _get_git_diff(repo)
    
    console.print(
        "[red]Error:[/red] Provide a diff file, --stdin, or --repo\n"
        "\n"
        "Examples:\n"
        "  codecourt review changes.diff\n"
        "  codecourt review --stdin < changes.diff\n"
        "  git diff | codecourt review --stdin\n"
        "  codecourt review --repo ."
    )
    sys.exit(1)


def _get_git_diff(repo_path: str) -> str:
    """Get uncommitted changes from a git repository."""
    import subprocess
    
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        diff = result.stdout
        
        if not diff.strip():
            result = subprocess.run(
                ["git", "diff"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            diff = result.stdout
        
        return diff
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Git error:[/red] {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        console.print("[red]Error:[/red] git command not found")
        sys.exit(1)


async def _run_review(
    parsed,
    provider: str,
    model: str | None,
    parallel: bool,
) -> CoordinatedReviewResult:
    """Run the coordinated review."""
    coordinator = Coordinator.with_default_agents(
        provider_name=provider,
        model=model,
        parallel=parallel,
    )
    return await coordinator.review(parsed)


def _output_rich(result: CoordinatedReviewResult, verbose: bool) -> None:
    """Output results using rich formatting."""
    style, label = APPROVAL_STYLES.get(
        result.approval, 
        ("white", str(result.approval.value))
    )
    
    console.print()
    console.print(Panel(
        Text(label, style=style, justify="center"),
        title="Verdict",
        expand=False,
    ))
    console.print()

    if result.findings:
        table = Table(title="Findings", show_lines=True)
        table.add_column("Severity", style="bold", width=10)
        table.add_column("File", style="cyan", max_width=40)
        table.add_column("Line", justify="right", width=6)
        table.add_column("Message", max_width=60)

        for finding in result.findings:
            style, icon = SEVERITY_STYLES.get(
                finding.severity,
                ("white", "⚪"),
            )
            table.add_row(
                Text(f"{icon} {finding.severity.value}", style=style),
                finding.file or "-",
                str(finding.line) if finding.line else "-",
                finding.message,
            )

        console.print(table)
        console.print()

    console.print(f"[bold]Summary:[/bold] {result.summary.split(chr(10))[0]}")
    
    if verbose and result.agent_results:
        console.print()
        console.print("[bold]Agent Details:[/bold]")
        for name, agent_result in result.agent_results.items():
            console.print(f"  • {name}: {agent_result.approval.value}")

    console.print()
    console.print(
        f"[dim]Stats: {len(result.findings)} findings | "
        f"{result.agents_approving}/{result.total_agents} agents approving | "
        f"confidence: {result.confidence:.0%}[/dim]"
    )


def _output_json(result: CoordinatedReviewResult) -> None:
    """Output results as JSON."""
    import json
    print(json.dumps(result.model_dump(mode="json"), indent=2))


def _output_markdown(result: CoordinatedReviewResult) -> None:
    """Output results as Markdown."""
    style, label = APPROVAL_STYLES.get(
        result.approval,
        ("", result.approval.value)
    )
    
    print(f"# Code Review: {label}")
    print()
    print(f"**Confidence:** {result.confidence:.0%}")
    print()
    
    if result.findings:
        print("## Findings")
        print()
        
        for finding in result.findings:
            _, icon = SEVERITY_STYLES.get(finding.severity, ("", "⚪"))
            location = ""
            if finding.file:
                location = f" in `{finding.file}`"
                if finding.line:
                    location += f" at line {finding.line}"
            
            print(f"### {icon} {finding.severity.value.upper()}{location}")
            print()
            print(finding.message)
            if finding.suggestion:
                print()
                print(f"**Suggestion:** {finding.suggestion}")
            print()
    
    print("## Summary")
    print()
    print(result.summary)


def _get_exit_code(result: CoordinatedReviewResult) -> int:
    """Determine exit code based on review result."""
    if result.approval == Approval.REQUEST_CHANGES:
        return 1
    if result.critical_count > 0:
        return 2
    return 0


@cli.command()
def providers() -> None:
    """List available LLM providers."""
    available = list_providers()
    
    table = Table(title="Available Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    
    for provider in ["openai", "anthropic", "ollama"]:
        status = "✓ Available" if provider in available else "✗ Not configured"
        style = "green" if provider in available else "red"
        table.add_row(provider, Text(status, style=style))
    
    console.print(table)
    console.print()
    console.print("[dim]Configure providers via environment variables or .env file:[/dim]")
    console.print("[dim]  OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_HOST[/dim]")


@cli.command()
@click.argument("diff_file", type=click.Path(exists=True), required=False)
@click.option("--stdin", is_flag=True, help="Read diff from standard input")
def parse(diff_file: str | None, stdin: bool) -> None:
    """Parse and display a diff (for debugging)."""
    if stdin:
        content = sys.stdin.read()
    elif diff_file:
        content = Path(diff_file).read_text()
    else:
        console.print("[red]Provide a diff file or --stdin[/red]")
        sys.exit(1)
    
    parsed = parse_diff(content)
    
    table = Table(title="Parsed Diff")
    table.add_column("File", style="cyan")
    table.add_column("Language", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("+", style="green", justify="right")
    table.add_column("-", style="red", justify="right")
    
    for file in parsed.files:
        status = "modified"
        if file.is_new_file:
            status = "new"
        elif file.is_deleted:
            status = "deleted"
        elif file.is_renamed:
            status = "renamed"
        
        table.add_row(
            file.path,
            file.language or "-",
            status,
            str(len(file.added_lines)),
            str(len(file.removed_lines)),
        )
    
    console.print(table)
    console.print()
    console.print(f"[bold]Total:[/bold] +{parsed.total_additions} -{parsed.total_deletions}")


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
