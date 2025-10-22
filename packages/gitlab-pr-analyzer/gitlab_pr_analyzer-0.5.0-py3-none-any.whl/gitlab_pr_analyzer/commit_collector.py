#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Commit collector for GitLab projects."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from git import Repo, Commit as GitCommit
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class CommitSummary:
    """minimal commit information."""

    def __init__(self, commit: GitCommit):
        self.sha = commit.hexsha
        self.short_sha = commit.hexsha[:7]
        self.message = commit.message.strip()
        self.author = commit.author.name
        self.author_email = commit.author.email
        self.committed_date = datetime.fromtimestamp(commit.committed_date)
        self.authored_date = datetime.fromtimestamp(commit.authored_date)
        self.parents = [parent.hexsha for parent in commit.parents]
        self.is_merge = len(commit.parents) > 1
        stats = commit.stats.total
        self.files_changed = stats.get("files", 0)
        self.insertions = stats.get("insertions", 0)
        self.deletions = stats.get("deletions", 0)

    def to_dict(self) -> Dict[str, object]:
        return {
            "sha": self.sha,
            "short_sha": self.short_sha,
            "message": self.message,
            "author": self.author,
            "author_email": self.author_email,
            "committed_date": self.committed_date.isoformat(),
            "authored_date": self.authored_date.isoformat(),
            "parent_count": len(self.parents),
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions,
        }


class CommitCollector:
    """collect commits using local Git repository."""

    def __init__(self, repo_path: str = "."):
        path = Path(repo_path)
        if not path.exists():
            raise RuntimeError(f"repository path not found: {repo_path}")

        self.repo = Repo(path)
        if self.repo.bare:
            raise RuntimeError("bare repository not supported")

    def collect_commits(
        self,
        branch: str = "HEAD",
        days: int = 60,
        include_merge_only: bool = False,
    ) -> List[CommitSummary]:
        """collect commits within the given days."""
        if days <= 0:
            raise ValueError("days must be positive")

        since = datetime.now() - timedelta(days=days)

        results: List[CommitSummary] = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Collecting commits...", total=None)
            for commit in self.repo.iter_commits(branch, since=since):
                summary = CommitSummary(commit)
                if include_merge_only and not summary.is_merge:
                    continue
                results.append(summary)
            progress.update(task, completed=True)

        console.print(f"[green]✓ Collected {len(results)} commits[/green]")
        return results

    def get_commit_details(self, sha: str) -> Optional[CommitSummary]:
        """get details for a specific commit."""
        try:
            commit = self.repo.commit(sha)
            return CommitSummary(commit)
        except Exception as error:
            console.print(f"[red]Error getting commit {sha}: {error}[/red]")
            return None
