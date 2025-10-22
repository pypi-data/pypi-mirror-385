#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge request collector for GitLab projects."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .gitlab_client import GitLabClient
from .utils import get_date_filter, get_date_filter_by_days

console = Console()


@dataclass
class MergeRequestSummary:
    """summary of merge request details used by analyzer."""

    iid: int
    title: str
    author: str
    state: str
    created_at: str
    updated_at: str
    merged_at: Optional[str]
    web_url: str
    description: Optional[str]
    labels: List[str]
    changes_count: Optional[str]
    source_branch: Optional[str]
    target_branch: Optional[str]


class MergeRequestCollector:
    """collect merge requests using GitLab API."""

    def __init__(self, project: str, client: Optional[GitLabClient] = None):
        self.project_identifier = project
        self.client = client or GitLabClient()
        self.project = self.client.get_project(project)

    def _convert(self, mr) -> MergeRequestSummary:
        return MergeRequestSummary(
            iid=mr.iid,
            title=mr.title or "",
            author=mr.author.get("name", "unknown") if mr.author else "unknown",
            state=mr.state,
            created_at=mr.created_at,
            updated_at=mr.updated_at,
            merged_at=getattr(mr, "merged_at", None),
            web_url=mr.web_url,
            description=mr.description,
            labels=mr.labels or [],
            changes_count=getattr(mr, "changes_count", None),
            source_branch=getattr(mr, "source_branch", None),
            target_branch=getattr(mr, "target_branch", None),
        )

    def collect(self, days: int = 60) -> Dict[str, List[MergeRequestSummary]]:
        """collect open and merged merge requests within given days."""
        date_filter = get_date_filter_by_days(days)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Collecting merge requests...", total=None)

            open_mrs = self.client.list_merge_requests(
                self.project, state="opened", updated_after=date_filter
            )
            merged_mrs = self.client.list_merge_requests(
                self.project, state="merged", updated_after=date_filter
            )

            open_converted = [self._convert(mr) for mr in open_mrs]
            merged_converted = [self._convert(mr) for mr in merged_mrs]

            progress.update(task, completed=True)

        return {"open": open_converted, "merged": merged_converted}

    def collect_by_months(self, months: int = 3) -> Dict[str, List[MergeRequestSummary]]:
        """collect open and merged merge requests within given months."""
        if months <= 0:
            raise ValueError("months must be positive")

        date_filter = get_date_filter(months)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Collecting merge requests...", total=None)

            open_mrs = self.client.list_merge_requests(
                self.project, state="opened", updated_after=date_filter
            )
            merged_mrs = self.client.list_merge_requests(
                self.project, state="merged", updated_after=date_filter
            )

            open_converted = [self._convert(mr) for mr in open_mrs]
            merged_converted = [self._convert(mr) for mr in merged_mrs]

            progress.update(task, completed=True)

        return {"open": open_converted, "merged": merged_converted}
