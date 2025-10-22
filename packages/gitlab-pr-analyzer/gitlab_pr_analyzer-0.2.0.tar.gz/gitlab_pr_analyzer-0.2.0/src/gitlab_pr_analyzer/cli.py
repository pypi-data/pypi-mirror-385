#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-line interface for GitLab PR Analyzer."""

import sys
from typing import List, Optional
import click
from rich.console import Console
from rich.table import Table

from .config import config
from .mr_collector import MergeRequestCollector
from .commit_collector import CommitCollector
from .matcher import Matcher
from .utils import check_git, format_datetime

console = Console()


def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║         GitLab Merge Request Analyzer v0.1.0          ║
    ║                                                       ║
    ║     Intelligent MR and Commit Analysis Tool           ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold magenta")


def check_prerequisites() -> bool:
    errors: List[str] = []

    if not config.gitlab_token:
        errors.append("Missing GitLab token. Set GITLAB_TOKEN environment variable.")

    if not check_git():
        errors.append("Git is not available in PATH.")

    if errors:
        console.print("[red]Prerequisite check failed:[/red]")
        for error in errors:
            console.print(f"  [red]- {error}[/red]")
        return False

    console.print("[green]✓ Prerequisites passed[/green]")
    return True


def summarize_mrs(title: str, mrs) -> None:
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("IID", width=8)
    table.add_column("Title", width=40, overflow="fold")
    table.add_column("Author", width=18)
    table.add_column("Updated", width=16)

    for mr in mrs:
        table.add_row(
            f"!{mr.iid}",
            mr.title,
            mr.author,
            format_datetime(mr.updated_at),
        )

    console.print(table)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """GitLab Merge Request Analyzer."""


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--project", "-p", required=True, help="GitLab project id or path")
@click.option("--days", "-d", default=60, show_default=True, help="Days to look back")
def collect(project: str, days: int):
    """Collect merge requests and commits."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    collector = MergeRequestCollector(project)
    data = collector.collect(days=days)

    console.print(
        f"\n[bold magenta]Collected {len(data['open'])} open and {len(data['merged'])} merged MRs[/bold magenta]"
    )

    summarize_mrs("Open Merge Requests", data["open"][:10])
    summarize_mrs("Merged Merge Requests", data["merged"][:10])

    commit_collector = CommitCollector()
    commits = commit_collector.collect_commits(days=days)
    console.print(f"\n[bold magenta]Collected {len(commits)} commits[/bold magenta]")


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("query")
@click.option("--project", "-p", required=True, help="GitLab project id or path")
@click.option("--days", "-d", default=60, show_default=True, help="Days to look back")
@click.option(
    "--max-results",
    type=int,
    default=20,
    show_default=True,
    help="Maximum number of results to display",
)
def search(query: str, project: str, days: int, max_results: int):
    """Search merge requests by keyword list derived from query."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    collector = MergeRequestCollector(project)
    data = collector.collect(days=days)

    keywords = query.split()
    matcher = Matcher()

    results = []
    for mr in data["open"] + data["merged"]:
        match = matcher.match_merge_request(mr, keywords)
        if match.score > 0:
            results.append(match)

    results.sort(key=lambda result: result.score, reverse=True)
    results = results[:max_results]

    if not results:
        console.print("[yellow]No matching merge requests found[/yellow]")
        return

    table = Table(
        title=f"Search Results ({len(results)})",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Rank", width=6)
    table.add_column("IID", width=8)
    table.add_column("Title", width=40, overflow="fold")
    table.add_column("Score", width=8)
    table.add_column("Matched Fields", width=20)

    for index, result in enumerate(results, start=1):
        mr = result.item
        table.add_row(
            str(index),
            f"!{mr.iid}",
            mr.title,
            str(result.score),
            ", ".join(result.matched_fields) or "-",
        )

    console.print(table)


if __name__ == "__main__":
    cli()
