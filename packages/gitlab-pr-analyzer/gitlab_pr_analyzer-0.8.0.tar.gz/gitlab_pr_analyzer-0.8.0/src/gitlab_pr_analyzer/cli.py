#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""command-line interface for GitLab merge request analyzer."""

import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .config import config
from .mr_collector import MergeRequestCollector, MergeRequestSummary
from .commit_collector import CommitCollector, CommitSummary
from .matcher import Matcher, MatchResult
from .ai_analyzer import AIAnalyzer
from .diff_provider import DiffProvider
from .utils import (
    check_git,
    check_glab,
    detect_gitlab_project,
    format_datetime,
    get_date_filter_by_days,
    print_glab_installation_guide,
    run_command,
)

console = Console()


def print_banner() -> None:
    """print application banner."""
    banner = f"""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                                                                    ║
    ║      {config.gitlab_instance_name} Merge Request Analyzer          ║
    ║                                                                    ║
    ║     Intelligent MR and Commit Analysis Tool                        ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold magenta")


def check_prerequisites(require_project: bool = True, check_glab_installation: bool = False) -> bool:
    """check CLI prerequisites."""
    errors: List[str] = []
    warnings: List[str] = []

    if not config.gitlab_token:
        errors.append("missing GitLab token. set GITLAB_TOKEN environment variable.")

    if not config.gitlab_host:
        errors.append("missing GitLab host. set GITLAB_HOST to your portal base url.")

    if not check_git():
        errors.append("git is not available in PATH.")

    if require_project and not config.gitlab_host:
        errors.append("cannot detect project without GITLAB_HOST")

    # check glab availability
    if not check_glab():
        if check_glab_installation:
            print_glab_installation_guide()
        warnings.append("glab is not available. some features may be limited.")

    if errors:
        console.print("[red]prerequisite check failed:[/red]")
        for error in errors:
            console.print(f"  [red]- {error}[/red]")
        return False

    if warnings:
        for warning in warnings:
            console.print(f"  [yellow]⚠ {warning}[/yellow]")

    console.print("[green]✓ prerequisites passed[/green]")
    return True


def resolve_project(project: Optional[str]) -> str:
    """resolve project path using CLI option or git remote."""
    if project:
        cleaned = project.strip()

        if cleaned in {"", ".", "./"}:
            raise click.UsageError(
                "invalid project identifier '.'; provide full GitLab path like group/subgroup/project"
            )

        if cleaned.startswith("./") and len(cleaned) > 2:
            cleaned = cleaned[2:]

        return cleaned

    if not config.gitlab_host:
        raise click.UsageError("GITLAB_HOST must be set to auto-detect project path")

    detected = detect_gitlab_project(config.gitlab_host)
    if detected:
        console.print(f"[cyan]detected project: {detected}[/cyan]")
        return detected

    raise click.UsageError(
        "unable to detect project from git remote. please provide --project explicitly."
    )


def summarize_merge_requests(title: str, items: List[MergeRequestSummary]) -> None:
    """render merge request summary table."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("IID", width=8)
    table.add_column("Title", width=40, overflow="fold")
    table.add_column("Author", width=18)
    table.add_column("Updated", width=16)

    for mr in items:
        table.add_row(
            f"!{mr.iid}",
            mr.title,
            mr.author,
            format_datetime(mr.updated_at),
        )

    console.print(table)


def display_match_results(results: List[MatchResult]) -> None:
    """display matcher results in a rich table."""
    if not results:
        console.print("[yellow]no matching merge requests or commits found[/yellow]")
        return

    table = Table(
        title=f"Search Results ({len(results)})",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Rank", width=6)
    table.add_column("Type", width=6)
    table.add_column("Identifier", width=12)
    table.add_column("Title/Message", overflow="fold", width=50)
    table.add_column("Author", width=18)
    table.add_column("Score", width=8)
    table.add_column("Matched Fields", width=20)

    for index, result in enumerate(results, start=1):
        if result.item_type == "MR":
            mr: MergeRequestSummary = result.item  # type: ignore[assignment]
            identifier = f"!{mr.iid}"
            title = mr.title
            author = mr.author
        else:
            commit: CommitSummary = result.item  # type: ignore[assignment]
            identifier = commit.short_sha
            title = commit.message.split("\n")[0]
            author = commit.author

        table.add_row(
            str(index),
            result.item_type,
            identifier,
            title,
            author,
            str(result.score),
            ", ".join(result.matched_fields) or "-",
        )

    console.print(table)


def render_merge_request_panel(mr: MergeRequestSummary) -> None:
    """display merge request details."""
    info_text = f"""
[bold]IID:[/bold] !{mr.iid}
[bold]Title:[/bold] {mr.title}
[bold]Author:[/bold] {mr.author}
[bold]State:[/bold] {mr.state}
[bold]Created:[/bold] {format_datetime(mr.created_at, 'full')}
[bold]Updated:[/bold] {format_datetime(mr.updated_at, 'full')}
{f"[bold]Merged:[/bold] {format_datetime(mr.merged_at, 'full')}" if mr.merged_at else ''}
[bold]Source → Target:[/bold] {mr.source_branch or '-'} → {mr.target_branch or '-'}
[bold]URL:[/bold] {mr.web_url}

[bold]Labels:[/bold] {', '.join(mr.labels) if mr.labels else 'None'}
[bold]Changes Count:[/bold] {mr.changes_count or 'Unknown'}

[bold]Description:[/bold]
{mr.description or 'No description provided.'}
    """

    console.print(Panel(info_text, border_style="magenta"))


def render_commit_panel(commit: CommitSummary) -> None:
    """display commit details."""
    info_text = f"""
[bold]Commit:[/bold] {commit.short_sha}
[bold]Author:[/bold] {commit.author} <{commit.author_email}>
[bold]Authored:[/bold] {format_datetime(commit.authored_date, 'full')}
[bold]Committed:[/bold] {format_datetime(commit.committed_date, 'full')}
[bold]Is Merge:[/bold] {commit.is_merge}
[bold]Parents:[/bold] {', '.join(commit.parents) if commit.parents else 'None'}

[bold]Statistics:[/bold]
  • Files Changed: {commit.files_changed}
  • Insertions: {commit.insertions}
  • Deletions: {commit.deletions}

[bold]Message:[/bold]
{commit.message}
    """

    console.print(Panel(info_text, border_style="magenta"))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """GitLab merge request analyzer CLI.
    
    \b
    Required Environment Variables:
      GITLAB_HOST        Your GitLab instance base URL (e.g., https://gitlab.example.com)
      GITLAB_TOKEN       Personal Access Token with 'read_api' or 'api' scope
    
    \b
    Optional Environment Variables:
      GITLAB_INSTANCE_NAME    Display name for your GitLab instance (default: "GitLab")
      CURSOR_AGENT_PATH       Path to cursor-agent executable for AI analysis features
    
    \b
    Recommended Tools (Install Before Use):
      glab                    GitLab CLI - REQUIRED for optimal diff analysis
                             • macOS: brew install glab
                             • Linux: sudo apt install glab (Ubuntu/Debian)
                             • Windows: choco install glab
                             • After install: glab auth login
                             • Without glab: tool uses API fallback (slower)
    
    \b
    Setup Example:
      # 1. Install glab
      brew install glab
      
      # 2. Authenticate with GitLab
      glab auth login
      
      # 3. Set environment variables
      export GITLAB_HOST="https://gitlab.example.com"
      export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
      
      # 4. Run analysis
      gl-pr-ai traverse -p group/project -d 30
    """


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--project",
    "-p",
    help="GitLab project path (group/subgroup/project). auto-detect if omitted.",
)
@click.option(
    "--months",
    "-m",
    type=int,
    default=3,
    show_default=True,
    help="number of months to look back for merged merge requests",
)
@click.option(
    "--days",
    "-d",
    type=int,
    default=None,
    help="override months with day-based window",
)
def collect(project: Optional[str], months: int, days: Optional[int]) -> None:
    """collect merge requests and commits."""
    print_banner()

    if not check_prerequisites(require_project=False):
        sys.exit(1)

    project_path = resolve_project(project)

    try:
        collector = MergeRequestCollector(project_path)
        time_window_text = f"{days} days" if days else f"{months} months"
        console.print(f"\n[bold]Project:[/bold] {project_path}")
        console.print(f"[bold]Time Window:[/bold] {time_window_text}\n")

        if days:
            data = collector.collect(days=days)
        else:
            data = collector.collect_by_months(months=months)

        console.print(
            f"[bold magenta]Collected {len(data['open'])} open and {len(data['merged'])} merged MRs[/bold magenta]"
        )

        summarize_merge_requests("Open Merge Requests", data["open"][:10])
        summarize_merge_requests("Merged Merge Requests", data["merged"][:10])

        commit_collector = CommitCollector()
        commit_days = days if days else months * 30
        commits = commit_collector.collect_commits(days=commit_days)
        console.print(
            f"\n[bold magenta]Collected {len(commits)} commits[/bold magenta]"
        )

    except Exception as error:
        console.print(f"[red]Error: {error}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("query")
@click.option(
    "--project",
    "-p",
    help="GitLab project path (group/subgroup/project). auto-detect if omitted.",
)
@click.option(
    "--days",
    "-d",
    type=int,
    default=90,
    show_default=True,
    help="number of days to collect data",
)
@click.option(
    "--min-score",
    type=int,
    default=30,
    show_default=True,
    help="minimum match score (0-100)",
)
@click.option(
    "--max-results",
    type=int,
    default=20,
    show_default=True,
    help="maximum number of results",
)
@click.option("--analyze", "-a", is_flag=True, help="analyze top results with AI")
def search(
    query: str,
    project: Optional[str],
    days: int,
    min_score: int,
    max_results: int,
    analyze: bool,
) -> None:
    """search merge requests and commits by query.
    
    Use --analyze flag to enable AI analysis with diff content.
    For best results with --analyze, install: brew install glab && glab auth login
    """
    print_banner()

    if not check_prerequisites(require_project=False, check_glab_installation=analyze):
        sys.exit(1)

    project_path = resolve_project(project)

    try:
        collector = MergeRequestCollector(project_path)
        console.print(f"\n[bold]Project:[/bold] {project_path}\n")

        data = collector.collect(days=days)
        merge_requests = data["open"] + data["merged"]

        commit_collector = CommitCollector()
        commits = commit_collector.collect_commits(days=days)

        matcher = Matcher(minimum_score=min_score)
        results = matcher.search(
            merge_requests, commits, query, max_results=max_results
        )

        console.print()
        display_match_results(results)

        if analyze and results:
            ai_analyzer = AIAnalyzer()
            if not ai_analyzer.is_available:
                console.print(
                    "[yellow]AI analysis not available. configure CURSOR_AGENT_PATH to enable.[/yellow]"
                )
                return

            console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")

            diff_provider = DiffProvider(project_path)

            def provide_diff(item):
                return diff_provider.get_diff(item)

            analyzed = ai_analyzer.batch_analyze(
                [r.item for r in results[:5]],
                include_diff=True,
                diff_provider=provide_diff,
            )

            for item, analysis in analyzed:
                if analysis:
                    ai_analyzer.display_analysis(item, analysis)

            if Confirm.ask("save analysis report to file?", default=False):
                report = ai_analyzer.generate_summary_report(analyzed, query)
                report_file = Path(
                    f"gitlab_mr_analysis_{project_path.replace('/', '_')}.md"
                )
                report.write_text(report)
                console.print(f"[green]✓ report saved to: {report_file}[/green]")

    except Exception as error:
        console.print(f"[red]Error: {error}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("mr_iid", type=int)
@click.option(
    "--project",
    "-p",
    help="GitLab project path (group/subgroup/project). auto-detect if omitted.",
)
@click.option("--analyze", "-a", is_flag=True, help="analyze merge request with AI")
def view_mr(mr_iid: int, project: Optional[str], analyze: bool) -> None:
    """view details of a specific merge request.
    
    Use --analyze flag to enable AI analysis with diff content.
    For best results with --analyze, install: brew install glab && glab auth login
    """
    print_banner()

    if not check_prerequisites(require_project=False, check_glab_installation=analyze):
        sys.exit(1)

    project_path = resolve_project(project)

    try:
        collector = MergeRequestCollector(project_path)
        merge_requests = collector.collect(days=365)
        items = merge_requests["open"] + merge_requests["merged"]
        target = next((mr for mr in items if mr.iid == mr_iid), None)

        if not target:
            console.print(f"[red]merge request !{mr_iid} not found[/red]")
            return

        render_merge_request_panel(target)

        if analyze:
            ai_analyzer = AIAnalyzer()
            if ai_analyzer.is_available:
                diff_provider = DiffProvider(project_path)

                def provide_diff(item: MergeRequestSummary) -> str:
                    return diff_provider.get_diff(item)

                analysis = ai_analyzer.analyze(
                    target, include_diff=True, diff_provider=provide_diff
                )
                if analysis:
                    ai_analyzer.display_analysis(target, analysis)

    except Exception as error:
        console.print(f"[red]Error: {error}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("commit_sha")
@click.option("--analyze", "-a", is_flag=True, help="analyze commit with AI")
def view_commit(commit_sha: str, analyze: bool) -> None:
    """view commit details."""
    print_banner()

    if not check_prerequisites(require_project=False):
        sys.exit(1)

    try:
        commit_collector = CommitCollector()
        commit = commit_collector.get_commit_details(commit_sha)

        if not commit:
            console.print(f"[red]commit {commit_sha} not found[/red]")
            return

        render_commit_panel(commit)

        if analyze:
            ai_analyzer = AIAnalyzer()
            if ai_analyzer.is_available:
                diff_provider = DiffProvider(".")  # use current directory for commits

                def provide_diff(item: CommitSummary) -> str:
                    return diff_provider.get_diff(item)

                analysis = ai_analyzer.analyze(
                    commit, include_diff=True, diff_provider=provide_diff
                )
                if analysis:
                    ai_analyzer.display_analysis(commit, analysis)

    except Exception as error:
        console.print(f"[red]Error: {error}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--project",
    "-p",
    help="GitLab project path (group/subgroup/project). auto-detect if omitted.",
)
@click.option(
    "--days",
    "-d",
    type=int,
    default=60,
    show_default=True,
    help="number of days to traverse merge requests",
)
def traverse(project: Optional[str], days: int) -> None:
    """traverse recent merge requests and analyze them with AI.
    
    This command requires diff analysis for optimal results.
    Install 'glab' CLI tool for best performance: brew install glab && glab auth login
    """
    print_banner()

    if not check_prerequisites(require_project=False, check_glab_installation=True):
        sys.exit(1)

    if days <= 0:
        console.print("[red]days must be a positive integer[/red]")
        sys.exit(1)

    project_path = resolve_project(project)

    ai_analyzer = AIAnalyzer()
    if not ai_analyzer.is_available:
        console.print(
            "[red]AI analysis not available. configure CURSOR_AGENT_PATH to enable.[/red]"
        )
        sys.exit(1)

    try:
        collector = MergeRequestCollector(project_path)
        data = collector.collect(days=days)
        open_merge_requests = data.get("open", [])
        merged_merge_requests = data.get("merged", [])

        console.print("\n[bold]Project:[/bold] {0}".format(project_path))
        console.print("[bold]Traversal Window:[/bold] last {0} days".format(days))
        console.print(
            "[bold magenta]Open MRs:[/bold magenta] {0}".format(
                len(open_merge_requests)
            )
        )
        console.print(
            "[bold magenta]Merged MRs:[/bold magenta] {0}".format(
                len(merged_merge_requests)
            )
        )

        if not open_merge_requests and not merged_merge_requests:
            console.print(
                "[yellow]no merge requests found in the specified range[/yellow]"
            )
            return

        analyzed_items: List[tuple[MergeRequestSummary, Optional[str]]] = []

        diff_provider = DiffProvider(project_path)

        def provide_diff(item: MergeRequestSummary) -> str:
            return diff_provider.get_diff(item)

        def analyze_group(target_items: List[MergeRequestSummary], label: str) -> None:
            if not target_items:
                console.print(
                    "[yellow]no {0} to analyze[/yellow]".format(label.lower())
                )
                return

            console.print("\n[bold cyan]Analyzing {0}...[/bold cyan]".format(label))

            total_items = len(target_items)
            index_value = 1
            for item in target_items:
                console.print(
                    "\n[bold]Analyzing {0} {1}/{2}: MR !{3}[/bold]".format(
                        label[:-1],
                        index_value,
                        total_items,
                        item.iid,
                    )
                )
                analysis = ai_analyzer.analyze(
                    item,
                    include_diff=True,
                    diff_provider=provide_diff,
                )
                analyzed_items.append((item, analysis))
                if analysis:
                    ai_analyzer.display_analysis(item, analysis)
                index_value += 1

        analyze_group(merged_merge_requests, "Merged MRs")
        analyze_group(open_merge_requests, "Open MRs")

        if analyzed_items:
            save_report = Confirm.ask(
                "\nsave traversal analysis report?", default=False
            )
            if save_report:
                summary_query = "Traversal analysis for last {0} days".format(days)
                report = ai_analyzer.generate_summary_report(
                    analyzed_items,
                    query=summary_query,
                )
                safe_name = project_path.replace("/", "_")
                report_file = Path(
                    "gitlab_mr_traversal_{0}_{1}d.md".format(safe_name, days)
                )
                report_file.write_text(report)
                console.print(
                    "[green]✓ report saved to: {0}[/green]".format(report_file)
                )

    except Exception as error:
        console.print(f"[red]Error: {error}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
def interactive() -> None:
    """interactive mode for exploring merge requests and commits."""
    print_banner()

    if not check_prerequisites(require_project=False):
        sys.exit(1)

    try:
        project_input = Prompt.ask(
            "\n[magenta]Project (group/subgroup/project, leave empty to auto-detect)[/magenta]",
            default="",
        )
        project_path = resolve_project(project_input or None)
        days = int(Prompt.ask("[magenta]Days to look back[/magenta]", default="90"))

        collector = MergeRequestCollector(project_path)
        data = collector.collect(days=days)
        merge_requests = data["open"] + data["merged"]

        commit_collector = CommitCollector()
        commits = commit_collector.collect_commits(days=days)

        matcher = Matcher()
        ai_analyzer = AIAnalyzer()

        console.print(f"\n[bold]Project:[/bold] {project_path}")
        console.print(f"[bold]Merge Requests:[/bold] {len(merge_requests)}")
        console.print(f"[bold]Commits:[/bold] {len(commits)}\n")

        while True:
            console.print("\n[bold magenta]Options:[/bold magenta]")
            console.print("  1. Search by query")
            console.print("  2. View merge request by IID")
            console.print("  3. View commit by SHA")
            console.print("  4. Exit")

            choice = Prompt.ask(
                "[magenta]Select an option[/magenta]", choices=["1", "2", "3", "4"]
            )

            if choice == "1":
                query = Prompt.ask("\n[magenta]Enter search query[/magenta]")
                results = matcher.search(merge_requests, commits, query)
                display_match_results(results)

                if (
                    results
                    and ai_analyzer.is_available
                    and Confirm.ask("run AI analysis on top results?")
                ):
                    analyzed = ai_analyzer.batch_analyze(
                        [r.item for r in results[:5]], include_diff=False
                    )
                    for item, analysis in analyzed:
                        if analysis:
                            ai_analyzer.display_analysis(item, analysis)

            elif choice == "2":
                iid = int(Prompt.ask("\n[magenta]Enter merge request IID[/magenta]"))
                target = next((mr for mr in merge_requests if mr.iid == iid), None)
                if target:
                    render_merge_request_panel(target)
                else:
                    console.print(f"[yellow]merge request !{iid} not found[/yellow]")

            elif choice == "3":
                sha = Prompt.ask("\n[magenta]Enter commit SHA[/magenta]")
                commit = commit_collector.get_commit_details(sha)
                if commit:
                    render_commit_panel(commit)
                else:
                    console.print(f"[yellow]commit {sha} not found[/yellow]")

            elif choice == "4":
                console.print("\n[magenta]goodbye![/magenta]")
                break

    except KeyboardInterrupt:
        console.print("\n[magenta]interrupted by user[/magenta]")
        sys.exit(0)
    except Exception as error:
        console.print(f"[red]Error: {error}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
