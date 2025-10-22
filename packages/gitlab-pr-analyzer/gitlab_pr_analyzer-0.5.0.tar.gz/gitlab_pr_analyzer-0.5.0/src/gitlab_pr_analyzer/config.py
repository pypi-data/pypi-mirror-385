#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""configuration management for GitLab PR Analyzer."""

import os
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Config:
    """application configuration sourced from environment variables."""

    gitlab_token: Optional[str]
    gitlab_host: Optional[str]
    gitlab_instance_name: str
    cursor_agent_path: Optional[str]

    @staticmethod
    def load() -> "Config":
        """load configuration from environment variables."""
        instance_name = os.getenv("GITLAB_INSTANCE_NAME")
        if not instance_name:
            instance_name = "GitLab"

        host_value = os.getenv("GITLAB_HOST")

        return Config(
            gitlab_token=os.getenv("GITLAB_TOKEN"),
            gitlab_host=host_value,
            gitlab_instance_name=instance_name,
            cursor_agent_path=os.getenv("CURSOR_AGENT_PATH"),
        )

    def validate(self) -> Tuple[bool, list[str]]:
        """validate essential configuration."""
        errors: list[str] = []

        if not self.gitlab_token:
            errors.append("missing GITLAB_TOKEN environment variable")

        if not self.gitlab_host:
            errors.append("missing GITLAB_HOST environment variable")

        return len(errors) == 0, errors


config = Config.load()
