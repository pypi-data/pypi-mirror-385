#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitLab API client helpers."""

from typing import Iterable, Optional
import gitlab
from gitlab.v4.objects import MergeRequest

from .config import config
from .utils import validate_project_path


class GitLabClient:
    """wrapper around python-gitlab for simplified operations."""

    def __init__(self, host: Optional[str] = None, token: Optional[str] = None):
        host_url = host or config.gitlab_host
        token_value = token or config.gitlab_token

        if not host_url:
            raise RuntimeError(
                "gitlab host not configured; set GITLAB_HOST to the portal base url"
            )

        if not token_value:
            raise RuntimeError("gitlab token not configured; set GITLAB_TOKEN")

        self.client = gitlab.Gitlab(url=host_url, private_token=token_value)

    def get_project(self, identifier: str):
        """Get project by id or path."""
        if identifier is None:
            raise RuntimeError("project identifier is required")

        cleaned = str(identifier).strip()

        if cleaned in {"", ".", "./"}:
            raise RuntimeError(
                "invalid project identifier '.'; provide full GitLab path like group/subgroup/project"
            )

        if cleaned.startswith("./") and len(cleaned) > 2:
            cleaned = cleaned[2:]

        if not cleaned.isdigit() and not validate_project_path(cleaned):
            raise RuntimeError(
                "invalid project identifier '{0}'. expected group/subgroup/project or numeric id".format(
                    cleaned
                )
            )

        return self.client.projects.get(cleaned)

    def list_merge_requests(
        self,
        project,
        state: str,
        updated_after: Optional[str] = None,
    ) -> Iterable[MergeRequest]:
        """list merge requests filtered by state and date."""
        params = {"state": state, "order_by": "updated_at", "sort": "desc"}

        if updated_after:
            params["updated_after"] = updated_after

        return project.mergerequests.list(all=True, **params)
