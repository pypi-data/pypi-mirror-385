#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility helpers for GitLab PR Analyzer."""

import subprocess
from typing import Iterable, List, Optional, Tuple
from datetime import datetime, timedelta
from rich.console import Console


console = Console()


def run_command(
    command: list[str],
    cwd: Optional[str] = None,
    capture_output: bool = True,
    check: bool = True,
    input_data: Optional[str] = None,
) -> Tuple[int, str, str]:
    """run shell command safely."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False,
            input=input_data,
        )

        if check and result.returncode != 0:
            raise RuntimeError(result.stderr or "command failed")

        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"command not found: {command[0]}. please ensure it is installed."
        ) from exc


def format_datetime(dt, fmt: str = "short") -> str:
    """format datetime for display."""
    if not dt:
        return "unknown"

    if isinstance(dt, str):
        if dt.endswith("Z"):
            dt = dt.replace("Z", "+00:00")
        dt_obj = datetime.fromisoformat(dt)
    else:
        dt_obj = dt

    if fmt == "short":
        return dt_obj.strftime("%m-%d %H:%M")
    return dt_obj.strftime("%Y-%m-%d %H:%M:%S")


def get_date_filter_by_days(days: int) -> str:
    """calculate iso date string days ago."""
    if days <= 0:
        raise ValueError("days must be positive")

    date = datetime.now() - timedelta(days=days)
    return date.strftime("%Y-%m-%d")


def normalize_text(text: Optional[str]) -> str:
    """lowercase and strip text."""
    if not text:
        return ""
    return text.lower().strip()


def normalize_keywords(keywords: Iterable[str]) -> List[str]:
    """normalize keywords while preserving order."""
    unique = []
    seen = set()

    for keyword in keywords:
        normalized = normalize_text(keyword)
        if not normalized or normalized in seen:
            continue
        unique.append(normalized)
        seen.add(normalized)

    return unique


def check_git() -> bool:
    """check if git is available."""
    try:
        returncode, _, _ = run_command(["git", "--version"], check=False)
        return returncode == 0
    except Exception:
        return False
