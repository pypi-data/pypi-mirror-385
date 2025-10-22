#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration management for GitLab PR Analyzer."""

import os
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Config:
    """application configuration sourced from environment variables."""

    gitlab_token: Optional[str]
    gitlab_host: str
    cursor_agent_path: Optional[str]

    @staticmethod
    def load() -> "Config":
        """load configuration from environment variables."""
        return Config(
            gitlab_token=os.getenv("GITLAB_TOKEN"),
            gitlab_host=os.getenv("GITLAB_HOST", "https://gitlab.com"),
            cursor_agent_path=os.getenv("CURSOR_AGENT_PATH"),
        )

    def validate(self) -> Tuple[bool, list[str]]:
        """validate essential configuration."""
        errors: list[str] = []

        if not self.gitlab_token:
            errors.append("missing GITLAB_TOKEN environment variable")

        if not self.gitlab_host:
            errors.append("missing GITLAB_HOST configuration")

        return len(errors) == 0, errors


config = Config.load()
