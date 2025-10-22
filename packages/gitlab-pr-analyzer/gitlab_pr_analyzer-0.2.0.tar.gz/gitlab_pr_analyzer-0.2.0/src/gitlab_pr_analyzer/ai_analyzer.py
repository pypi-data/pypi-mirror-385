#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI analysis integration using cursor-agent for GitLab analyzer."""

from typing import List, Optional
from rich.console import Console
from rich.markdown import Markdown

from .config import config
from .utils import run_command

console = Console()


class AIAnalyzer:
    """delegate analysis to cursor-agent if available."""

    def __init__(self, cursor_agent_path: Optional[str] = None):
        self.cursor_agent_path = cursor_agent_path or config.cursor_agent_path
        self.is_available = self._check_availability()

    def _check_availability(self) -> bool:
        if not self.cursor_agent_path:
            console.print(
                "[yellow]AI analysis disabled: CURSOR_AGENT_PATH not configured[/yellow]"
            )
            return False
        return True

    def analyze(self, title: str, body: str) -> Optional[str]:
        if not self.is_available:
            return None

        prompt = f"""# Merge Request Analysis

Title: {title}

Description:
{body}

Provide a concise summary including scope, risks, and validation hints.
"""

        command = [
            self.cursor_agent_path,
            "--print",
            "--output-format",
            "text",
            "agent",
            prompt,
        ]

        _, stdout, stderr = run_command(command, check=False)

        if stderr:
            console.print(f"[yellow]{stderr}[/yellow]")

        if stdout:
            return stdout.strip()

        return None

    def display(self, title: str, analysis: str) -> None:
        console.print(f"\n[bold cyan]AI Analysis: {title}[/bold cyan]\n")
        try:
            console.print(Markdown(analysis))
        except Exception:
            console.print(analysis)
