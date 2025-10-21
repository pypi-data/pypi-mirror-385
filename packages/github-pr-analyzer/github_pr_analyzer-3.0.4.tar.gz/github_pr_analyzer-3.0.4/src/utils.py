#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for the PR analyzer.

MIT License

Copyright (c) 2025 GitHub PR Analyzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
    """
    run a shell command safely.

    Args:
        command: command as list of strings
        cwd: working directory
        capture_output: whether to capture stdout/stderr
        check: whether to raise exception on error

    Returns:
        tuple: (return_code, stdout, stderr)
    """
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
            error_msg = f"command failed: {' '.join(command)}"
            if result.stderr:
                error_msg += f"\nError: {result.stderr}"
            raise RuntimeError(error_msg)

        return result.returncode, result.stdout, result.stderr

    except FileNotFoundError as e:
        raise RuntimeError(
            f"command not found: {command[0]}. Please ensure it is installed."
        ) from e
    except Exception as e:
        raise RuntimeError(f"failed to execute command: {str(e)}") from e


def check_gh_cli() -> bool:
    """
    check if gh CLI is installed and authenticated.

    Returns:
        bool: True if gh CLI is ready to use
    """
    try:
        returncode, stdout, stderr = run_command(["gh", "--version"], check=False)
        if returncode != 0:
            return False

        returncode, stdout, stderr = run_command(["gh", "auth", "status"], check=False)
        if returncode != 0:
            console.print("[yellow]Warning: gh CLI is not authenticated[/yellow]")
            console.print("Please run: gh auth login")
            return False

        return True

    except Exception:
        return False


def check_git() -> bool:
    """
    check if git is installed.

    Returns:
        bool: True if git is installed
    """
    try:
        returncode, _, _ = run_command(["git", "--version"], check=False)
        return returncode == 0
    except Exception:
        return False


def get_date_filter(months: int) -> str:
    """
    get date string for filtering PRs.

    Args:
        months: number of months to look back

    Returns:
        str: date string in ISO format
    """
    date = datetime.now() - timedelta(days=months * 30)
    return date.strftime("%Y-%m-%d")


def get_date_filter_by_days(days: int) -> str:
    """
    get date string for filtering PRs using days.

    Args:
        days: number of days to look back

    Returns:
        str: date string in ISO format
    """
    if days <= 0:
        raise ValueError("days must be a positive integer")

    date = datetime.now() - timedelta(days=days)
    return date.strftime("%Y-%m-%d")


def normalize_text(text: str) -> str:
    """
    normalize text by lowercasing and trimming whitespace.

    Args:
        text: text to normalize

    Returns:
        str: normalized text
    """
    if text is None:
        return ""

    normalized = text.lower()
    normalized = normalized.strip()
    return normalized


def normalize_keywords(keywords: Iterable[str]) -> List[str]:
    """
    normalize keywords by lowercasing and removing duplicates.

    Args:
        keywords: iterable of keywords

    Returns:
        list: normalized unique keywords preserving order
    """
    seen = set()
    normalized_keywords: List[str] = []

    for keyword in keywords:
        if keyword is None:
            continue

        normalized = normalize_text(keyword)
        if not normalized:
            continue

        if normalized not in seen:
            seen.add(normalized)
            normalized_keywords.append(normalized)

    return normalized_keywords


def format_pr_url(repo: str, pr_number: int) -> str:
    """
    format a GitHub PR URL.

    Args:
        repo: repository in format "owner/repo"
        pr_number: PR number

    Returns:
        str: full GitHub PR URL
    """
    return f"https://github.com/{repo}/pull/{pr_number}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    truncate text to specified length.

    Args:
        text: text to truncate
        max_length: maximum length

    Returns:
        str: truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def validate_repo_format(repo: str) -> bool:
    """
    validate repository format (owner/repo).

    Args:
        repo: repository string

    Returns:
        bool: True if format is valid
    """
    if not repo:
        return False
    parts = repo.split("/")
    if len(parts) != 2:
        return False
    if not parts[0] or not parts[1]:
        return False
    return True


def format_datetime(dt, format_type: str = "short") -> str:
    """
    format datetime for display.

    Args:
        dt: datetime object or ISO string
        format_type: "short" for MM-DD HH:MM, "full" for full datetime

    Returns:
        str: formatted datetime string
    """
    from datetime import datetime

    if not dt:
        return "Unknown"

    try:
        # handle different input types
        if isinstance(dt, str):
            # handle ISO format with Z timezone
            if dt.endswith("Z"):
                dt = dt.replace("Z", "+00:00")
            parsed_dt = datetime.fromisoformat(dt)
        elif hasattr(dt, "strftime"):
            parsed_dt = dt
        else:
            return "Unknown"

        if format_type == "short":
            return parsed_dt.strftime("%m-%d %H:%M")
        elif format_type == "full":
            return parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return parsed_dt.strftime("%m-%d %H:%M")

    except Exception:
        return "Unknown"
