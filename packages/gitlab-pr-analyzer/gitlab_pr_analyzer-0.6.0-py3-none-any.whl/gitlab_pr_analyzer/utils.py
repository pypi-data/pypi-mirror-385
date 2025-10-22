#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""utility helpers for GitLab MR analyzer."""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from rich.console import Console

console = Console()


def run_command(
    command: List[str],
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
            error_message = f"command failed: {' '.join(command)}"
            if result.stderr:
                error_message = f"{error_message}\nError: {result.stderr}"
            raise RuntimeError(error_message)

        return result.returncode, result.stdout, result.stderr

    except FileNotFoundError as error:
        raise RuntimeError(
            f"command not found: {command[0]}. please ensure it is installed."
        ) from error
    except Exception as error:
        raise RuntimeError(f"failed to execute command: {error}") from error


def check_git() -> bool:
    """check if git is installed."""
    try:
        returncode, _, _ = run_command(["git", "--version"], check=False)
        return returncode == 0
    except Exception:
        return False


def get_date_filter(months: int) -> str:
    """get iso date string months ago."""
    if months <= 0:
        raise ValueError("months must be a positive integer")

    target = datetime.now() - timedelta(days=months * 30)
    return target.strftime("%Y-%m-%d")


def get_date_filter_by_days(days: int) -> str:
    """get iso date string days ago."""
    if days <= 0:
        raise ValueError("days must be a positive integer")

    target = datetime.now() - timedelta(days=days)
    return target.strftime("%Y-%m-%d")


def normalize_text(text: Optional[str]) -> str:
    """normalize text by lowercasing and stripping."""
    if text is None:
        return ""

    normalized = text.lower()
    return normalized.strip()


def normalize_keywords(keywords: Iterable[str]) -> List[str]:
    """normalize keywords by removing duplicates while preserving order."""
    seen = set()
    result: List[str] = []

    for keyword in keywords:
        if keyword is None:
            continue

        normalized = normalize_text(keyword)
        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        result.append(normalized)

    return result


def format_datetime(value, format_type: str = "short") -> str:
    """format datetime or iso string for display."""
    if not value:
        return "unknown"

    try:
        if isinstance(value, str):
            cleaned = value
            if cleaned.endswith("Z"):
                cleaned = cleaned.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(cleaned)
        elif hasattr(value, "strftime"):
            parsed = value
        else:
            return "unknown"

        if format_type == "full":
            return parsed.strftime("%Y-%m-%d %H:%M:%S")

        if format_type == "date":
            return parsed.strftime("%Y-%m-%d")

        return parsed.strftime("%m-%d %H:%M")

    except Exception:
        return "unknown"


def truncate_text(text: str, max_length: int = 100) -> str:
    """truncate text to a maximum length."""
    if len(text) <= max_length:
        return text

    truncated = text[: max_length - 3]
    return f"{truncated}..."


def validate_project_path(project_path: str) -> bool:
    """validate GitLab project path (supports nested groups)."""
    if not project_path:
        return False

    parts = [segment for segment in project_path.split("/") if segment]
    if len(parts) < 2:
        return False

    return True


def detect_gitlab_project(host: str) -> Optional[str]:
    """detect GitLab project path from git remotes."""
    try:
        returncode, stdout, _ = run_command(
            ["git", "remote", "get-url", "origin"], check=False
        )
        if returncode != 0:
            return None

        remote_url = stdout.strip()
        if not remote_url:
            return None

        normalized_host = host
        if normalized_host.endswith("/"):
            normalized_host = normalized_host[:-1]

        if normalized_host not in remote_url:
            return None

        project_path = None

        if remote_url.startswith("git@"):  # ssh format
            # example: git@host:group/project.git
            parts = remote_url.split(":", 1)
            if len(parts) == 2:
                project_path = parts[1]
        else:
            # http(s) format
            host_index = remote_url.find(normalized_host)
            if host_index != -1:
                suffix = remote_url[host_index + len(normalized_host) :]
                if suffix.startswith("/"):
                    suffix = suffix[1:]
                project_path = suffix

        if project_path is None:
            return None

        if project_path.endswith(".git"):
            project_path = project_path[:-4]

        project_path = project_path.strip("/")
        if not validate_project_path(project_path):
            return None

        return project_path

    except Exception:
        return None


def ensure_output_directory(path: Path) -> None:
    """ensure output directory exists."""
    try:
        if path.exists():
            return
        path.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        raise RuntimeError(f"failed to prepare output directory: {error}") from error
