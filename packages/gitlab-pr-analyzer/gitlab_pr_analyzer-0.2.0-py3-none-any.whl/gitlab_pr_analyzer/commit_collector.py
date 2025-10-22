#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Commit collector for GitLab projects."""

from typing import List, Optional
from datetime import datetime, timedelta
from git import Repo, Commit as GitCommit
from rich.console import Console

from .utils import normalize_text

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

    def to_dict(self):
        return {
            "sha": self.sha,
            "short_sha": self.short_sha,
            "message": self.message,
            "author": self.author,
            "author_email": self.author_email,
            "committed_date": self.committed_date.isoformat(),
            "authored_date": self.authored_date.isoformat(),
            "parent_count": len(self.parents),
        }


class CommitCollector:
    """collect commits using local Git repository."""

    def __init__(self, repo_path: str = "."):
        self.repo = Repo(repo_path)
        if self.repo.bare:
            raise RuntimeError("bare repository not supported")

    def collect_commits(
        self, branch: str = "HEAD", days: int = 60
    ) -> List[CommitSummary]:
        """collect commits within the given days."""
        since = datetime.now() - timedelta(days=days)

        results: List[CommitSummary] = []
        for commit in self.repo.iter_commits(branch, since=since):
            results.append(CommitSummary(commit))

        console.print(f"[green]✓ Collected {len(results)} commits[/green]")
        return results
