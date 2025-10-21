#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-line interface for GitHub PR Analyzer.

MIT License

Copyright (c) 2025 GitHub PR Analyzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
from typing import Optional
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from .config import config
from .utils import check_gh_cli, check_git
from .pr_collector import PRCollector
from .commit_collector import CommitCollector
from .diff_viewer import DiffViewer
from .matcher import Matcher, MatchResult
from .ai_analyzer import AIAnalyzer

console = Console()


def print_banner():
    """print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        GitHub PR & Commit Analyzer v1.0.0            ║
    ║                                                       ║
    ║     Intelligent PR and Commit Analysis Tool          ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def check_prerequisites() -> bool:
    """
    check if all prerequisites are installed.

    Returns:
        bool: True if all prerequisites are met
    """
    console.print("\n[cyan]Checking prerequisites...[/cyan]")

    errors = []

    if not check_git():
        errors.append("Git is not installed or not in PATH")
    else:
        console.print("[green]✓ Git found[/green]")

    if not check_gh_cli():
        errors.append("GitHub CLI (gh) is not installed or not authenticated")
        console.print("[red]✗ GitHub CLI not ready[/red]")
    else:
        console.print("[green]✓ GitHub CLI found and authenticated[/green]")

    is_valid, config_errors = config.validate()
    if not is_valid:
        console.print("[yellow]⚠ Configuration warnings:[/yellow]")
        for error in config_errors:
            console.print(f"  [yellow]- {error}[/yellow]")

    if errors:
        console.print("\n[red]Prerequisites not met:[/red]")
        for error in errors:
            console.print(f"  [red]✗ {error}[/red]")
        return False

    console.print("[green]✓ All prerequisites met[/green]\n")
    return True


def display_results_table(results: list[MatchResult]):
    """
    display search results in a table.

    Args:
        results: list of match results
    """
    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    table = Table(
        title=f"Search Results ({len(results)} matches)",
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("#", style="dim", width=4)
    table.add_column("Type", width=8)
    table.add_column("ID", width=10)
    table.add_column("Title/Message", style="green", no_wrap=False)
    table.add_column("Author", width=15)
    table.add_column("Score", justify="right", width=8)

    for idx, result in enumerate(results, 1):
        if result.item_type == "PR":
            item = result.item
            item_id = f"#{item.number}"
            title = item.title[:80]
            author = item.author
        else:
            item = result.item
            item_id = item.short_sha
            title = item.message.split("\n")[0][:80]
            author = item.author

        score_style = (
            "green" if result.score >= 70 else "yellow" if result.score >= 50 else "red"
        )

        table.add_row(
            str(idx),
            result.item_type,
            item_id,
            title,
            author,
            f"[{score_style}]{result.score}[/{score_style}]",
        )

    console.print(table)


@click.group()
def cli():
    """GitHub PR and Commit Analyzer - Find and analyze relevant changes."""
    pass


@cli.command()
@click.option(
    "--repo",
    "-r",
    help="Repository in format owner/repo (auto-detect if not specified)",
)
@click.option(
    "--months",
    "-m",
    type=int,
    default=3,
    help="Number of months to look back for merged items",
)
def collect(repo: Optional[str], months: int):
    """Collect all PRs and commits from the repository."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    try:
        pr_collector = PRCollector(repo)
        console.print(f"\n[bold]Repository:[/bold] {pr_collector.repo}\n")

        all_prs = pr_collector.collect_all_prs(months)

        console.print(f"\n[bold cyan]Summary:[/bold cyan]")
        console.print(f"  • Open PRs: {len(all_prs['open'])}")
        console.print(
            f"  • Merged PRs (last {months} months): {len(all_prs['merged'])}"
        )

        commit_collector = CommitCollector(repo_name=pr_collector.repo)
        merge_commits = commit_collector.collect_merge_commits(months=months)

        console.print(f"  • Merge Commits (last {months} months): {len(merge_commits)}")
        console.print()

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--repo", "-r", help="Repository in format owner/repo")
@click.option("--months", "-m", type=int, default=3, help="Months to look back")
@click.option("--min-score", type=int, default=30, help="Minimum match score (0-100)")
@click.option("--max-results", type=int, default=20, help="Maximum number of results")
@click.option("--analyze", "-a", is_flag=True, help="Analyze results with AI")
@click.option("--show-diff", "-d", is_flag=True, help="Show diff for each result")
def search(
    query: str,
    repo: Optional[str],
    months: int,
    min_score: int,
    max_results: int,
    analyze: bool,
    show_diff: bool,
):
    """Search for PRs and commits matching a query."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    try:
        pr_collector = PRCollector(repo)
        console.print(f"\n[bold]Repository:[/bold] {pr_collector.repo}\n")

        all_prs = pr_collector.collect_all_prs(months)
        all_pr_list = all_prs["open"] + all_prs["merged"]

        commit_collector = CommitCollector(repo_name=pr_collector.repo)
        commits = commit_collector.collect_all_commits(months=months)

        console.print()

        matcher = Matcher()
        results = matcher.search(
            all_pr_list, commits, query, min_score=min_score, max_results=max_results
        )

        console.print()
        display_results_table(results)

        if not results:
            return

        if show_diff or analyze:
            diff_viewer = DiffViewer(repo_name=pr_collector.repo)

            if show_diff:
                console.print("\n[bold cyan]Displaying diffs...[/bold cyan]\n")
                for result in results[:5]:
                    if result.item_type == "PR":
                        diff_viewer.display_pr_diff(result.item.number, max_lines=100)
                    else:
                        diff_viewer.display_commit_diff(result.item.sha, max_lines=100)
                    console.print()

            if analyze:
                ai_analyzer = AIAnalyzer()
                if not ai_analyzer.is_available:
                    console.print(
                        "\n[yellow]AI analysis not available. Please configure cursor-agent in .env[/yellow]"
                    )
                    return

                console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")

                items_to_analyze = [r.item for r in results[:5]]
                analyzed = ai_analyzer.batch_analyze(
                    items_to_analyze, include_diff=True, diff_viewer=diff_viewer
                )

                for item, analysis in analyzed:
                    if analysis:
                        ai_analyzer.display_analysis(item, analysis)

                save_report = Confirm.ask("\nSave analysis report to file?")
                if save_report:
                    report = ai_analyzer.generate_summary_report(analyzed, query)
                    report_file = (
                        f"pr_analysis_report_{pr_collector.repo.replace('/', '_')}.md"
                    )
                    Path(report_file).write_text(report)
                    console.print(f"[green]✓ Report saved to: {report_file}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("pr_number", type=int)
@click.option("--repo", "-r", help="Repository in format owner/repo")
@click.option("--analyze", "-a", is_flag=True, help="Analyze with AI")
def view_pr(pr_number: int, repo: Optional[str], analyze: bool):
    """View details of a specific PR."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    try:
        pr_collector = PRCollector(repo)
        console.print(f"\n[bold]Repository:[/bold] {pr_collector.repo}\n")

        pr = pr_collector.get_pr_details(pr_number)
        if not pr:
            console.print(f"[red]PR #{pr_number} not found[/red]")
            return

        info_text = f"""
[bold cyan]PR #{pr.number}[/bold cyan]: {pr.title}

[bold]Author:[/bold] {pr.author}
[bold]State:[/bold] {pr.state}
[bold]Created:[/bold] {pr.created_at}
[bold]Updated:[/bold] {pr.updated_at}
[bold]URL:[/bold] {pr.url}

[bold]Statistics:[/bold]
  • Files Changed: {pr.changed_files}
  • Additions: {pr.additions}
  • Deletions: {pr.deletions}
  • Labels: {', '.join(pr.labels) if pr.labels else 'None'}

[bold]Description:[/bold]
{pr.body or 'No description provided.'}
        """

        console.print(Panel(info_text, border_style="cyan"))

        diff_viewer = DiffViewer(repo_name=pr_collector.repo)

        show_diff = Confirm.ask("\nShow diff?", default=True)
        if show_diff:
            diff_viewer.display_pr_diff(pr_number)

        if analyze:
            ai_analyzer = AIAnalyzer()
            if ai_analyzer.is_available:
                console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")
                analysis = ai_analyzer.analyze(
                    pr, include_diff=True, diff_viewer=diff_viewer
                )
                if analysis:
                    ai_analyzer.display_analysis(pr, analysis)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("commit_sha")
@click.option("--analyze", "-a", is_flag=True, help="Analyze with AI")
def view_commit(commit_sha: str, analyze: bool):
    """View details of a specific commit."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    try:
        commit_collector = CommitCollector()

        commit = commit_collector.get_commit_details(commit_sha)
        if not commit:
            console.print(f"[red]Commit {commit_sha} not found[/red]")
            return

        info_text = f"""
[bold cyan]Commit {commit.short_sha}[/bold cyan]

[bold]Author:[/bold] {commit.author} <{commit.author_email}>
[bold]Date:[/bold] {commit.committed_date}
[bold]Is Merge:[/bold] {commit.is_merge}
{f'[bold]PR Number:[/bold] #{commit.pr_number}' if commit.pr_number else ''}

[bold]Statistics:[/bold]
  • Files Changed: {commit.files_changed}
  • Insertions: {commit.insertions}
  • Deletions: {commit.deletions}

[bold]Message:[/bold]
{commit.message}
        """

        console.print(Panel(info_text, border_style="cyan"))

        diff_viewer = DiffViewer()

        show_diff = Confirm.ask("\nShow diff?", default=True)
        if show_diff:
            diff_viewer.display_commit_diff(commit.sha)

        if analyze:
            ai_analyzer = AIAnalyzer()
            if ai_analyzer.is_available:
                console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")
                analysis = ai_analyzer.analyze(
                    commit, include_diff=True, diff_viewer=diff_viewer
                )
                if analysis:
                    ai_analyzer.display_analysis(commit, analysis)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def interactive():
    """Interactive mode for exploring PRs and commits."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    try:
        repo = Prompt.ask(
            "\n[cyan]Repository (owner/repo, or press Enter to auto-detect)[/cyan]",
            default="",
        )
        months = int(Prompt.ask("[cyan]Months to look back[/cyan]", default="3"))

        pr_collector = PRCollector(repo if repo else None)
        console.print(f"\n[bold]Repository:[/bold] {pr_collector.repo}\n")

        console.print("[cyan]Collecting data...[/cyan]\n")
        all_prs = pr_collector.collect_all_prs(months)
        all_pr_list = all_prs["open"] + all_prs["merged"]

        commit_collector = CommitCollector(repo_name=pr_collector.repo)
        commits = commit_collector.collect_all_commits(months=months)

        diff_viewer = DiffViewer(repo_name=pr_collector.repo)
        matcher = Matcher()
        ai_analyzer = AIAnalyzer()

        console.print(f"\n[bold cyan]Data collected:[/bold cyan]")
        console.print(f"  • Total PRs: {len(all_pr_list)}")
        console.print(f"  • Total Commits: {len(commits)}")
        console.print()

        while True:
            console.print("\n[bold cyan]Options:[/bold cyan]")
            console.print("  1. Search by query")
            console.print("  2. View specific PR")
            console.print("  3. View specific commit")
            console.print("  4. Exit")

            choice = Prompt.ask(
                "\n[cyan]Choose an option[/cyan]", choices=["1", "2", "3", "4"]
            )

            if choice == "1":
                query = Prompt.ask("\n[cyan]Enter search query[/cyan]")

                results = matcher.search(
                    all_pr_list, commits, query, min_score=30, max_results=20
                )
                display_results_table(results)

                if results:
                    if Confirm.ask("\nAnalyze results with AI?"):
                        if ai_analyzer.is_available:
                            items = [r.item for r in results[:5]]
                            analyzed = ai_analyzer.batch_analyze(
                                items, include_diff=True, diff_viewer=diff_viewer
                            )

                            for item, analysis in analyzed:
                                if analysis:
                                    ai_analyzer.display_analysis(item, analysis)
                        else:
                            console.print("[yellow]AI analysis not available[/yellow]")

            elif choice == "2":
                pr_number = int(Prompt.ask("\n[cyan]Enter PR number[/cyan]"))
                pr = pr_collector.get_pr_details(pr_number)

                if pr:
                    console.print(f"\n{pr}")
                    if Confirm.ask("Show diff?"):
                        diff_viewer.display_pr_diff(pr_number)
                    if Confirm.ask("Analyze with AI?"):
                        if ai_analyzer.is_available:
                            analysis = ai_analyzer.analyze(
                                pr, include_diff=True, diff_viewer=diff_viewer
                            )
                            if analysis:
                                ai_analyzer.display_analysis(pr, analysis)

            elif choice == "3":
                sha = Prompt.ask("\n[cyan]Enter commit SHA[/cyan]")
                commit = commit_collector.get_commit_details(sha)

                if commit:
                    console.print(f"\n{commit}")
                    if Confirm.ask("Show diff?"):
                        diff_viewer.display_commit_diff(sha)
                    if Confirm.ask("Analyze with AI?"):
                        if ai_analyzer.is_available:
                            analysis = ai_analyzer.analyze(
                                commit, include_diff=True, diff_viewer=diff_viewer
                            )
                            if analysis:
                                ai_analyzer.display_analysis(commit, analysis)

            elif choice == "4":
                console.print("\n[cyan]Goodbye![/cyan]")
                break

    except KeyboardInterrupt:
        console.print("\n\n[cyan]Interrupted by user[/cyan]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
