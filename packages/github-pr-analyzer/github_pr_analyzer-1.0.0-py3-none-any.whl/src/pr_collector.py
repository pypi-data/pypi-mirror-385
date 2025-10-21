#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for collecting Pull Requests from GitHub repositories.

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

import json
from typing import List, Dict, Optional
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .utils import run_command, get_date_filter, validate_repo_format

console = Console()


class PullRequest:
    """represent a GitHub Pull Request with relevant information."""

    def __init__(self, data: Dict):
        """
        initialize a PR object from GitHub API data.

        Args:
            data: dictionary containing PR information from gh CLI
        """
        self.number: int = data.get("number", 0)
        self.title: str = data.get("title", "")
        self.author: str = (
            data.get("author", {}).get("login", "unknown")
            if isinstance(data.get("author"), dict)
            else data.get("author", "unknown")
        )
        self.state: str = data.get("state", "")
        self.created_at: str = data.get("createdAt", "")
        self.updated_at: str = data.get("updatedAt", "")
        self.merged_at: Optional[str] = data.get("mergedAt")
        self.url: str = data.get("url", "")
        self.body: str = data.get("body", "")
        self.labels: List[str] = [
            label.get("name", "") for label in data.get("labels", [])
        ]
        self.base_ref: str = data.get("baseRefName", "")
        self.head_ref: str = data.get("headRefName", "")
        self.additions: int = data.get("additions", 0)
        self.deletions: int = data.get("deletions", 0)
        self.changed_files: int = data.get("changedFiles", 0)

    def to_dict(self) -> Dict:
        """
        convert PR object to dictionary.

        Returns:
            dict: PR data as dictionary
        """
        return {
            "number": self.number,
            "title": self.title,
            "author": self.author,
            "state": self.state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "merged_at": self.merged_at,
            "url": self.url,
            "body": self.body,
            "labels": self.labels,
            "base_ref": self.base_ref,
            "head_ref": self.head_ref,
            "additions": self.additions,
            "deletions": self.deletions,
            "changed_files": self.changed_files,
        }

    def __str__(self) -> str:
        """string representation of the PR."""
        status_emoji = (
            "✅" if self.state == "MERGED" else "🔄" if self.state == "OPEN" else "❌"
        )
        return f"{status_emoji} #{self.number}: {self.title} (@{self.author})"


class PRCollector:
    """collector for fetching Pull Requests from GitHub."""

    def __init__(self, repo: Optional[str] = None):
        """
        initialize PR collector.

        Args:
            repo: repository in format "owner/repo" (optional, will auto-detect from git)
        """
        self.repo = repo
        if not self.repo:
            self.repo = self._detect_repo()

        if not validate_repo_format(self.repo):
            raise ValueError(
                f"invalid repository format: {self.repo}. Expected format: owner/repo"
            )

    def _detect_repo(self) -> str:
        """
        detect repository from git remote.

        Returns:
            str: repository in format "owner/repo"
        """
        try:
            _, stdout, _ = run_command(["git", "remote", "get-url", "origin"])
            remote_url = stdout.strip()

            if "github.com" not in remote_url:
                raise ValueError("not a GitHub repository")

            if remote_url.startswith("git@github.com:"):
                repo = remote_url.replace("git@github.com:", "").replace(".git", "")
            elif "github.com/" in remote_url:
                repo = remote_url.split("github.com/")[1].replace(".git", "")
            else:
                raise ValueError("cannot parse GitHub repository URL")

            return repo.strip("/")

        except Exception as e:
            raise RuntimeError(f"failed to detect repository: {str(e)}") from e

    def collect_open_prs(self) -> List[PullRequest]:
        """
        collect all open Pull Requests.

        Returns:
            list: list of PullRequest objects
        """
        console.print(f"[cyan]Collecting open PRs from {self.repo}...[/cyan]")

        try:
            command = [
                "gh",
                "pr",
                "list",
                "--repo",
                self.repo,
                "--state",
                "open",
                "--json",
                "number,title,author,state,createdAt,updatedAt,mergedAt,url,body,labels,baseRefName,headRefName,additions,deletions,changedFiles",
                "--limit",
                "1000",
            ]

            _, stdout, _ = run_command(command)

            pr_data = json.loads(stdout)
            prs = [PullRequest(pr) for pr in pr_data]

            console.print(f"[green]✓ Found {len(prs)} open PRs[/green]")
            return prs

        except Exception as e:
            console.print(f"[red]Error collecting open PRs: {str(e)}[/red]")
            return []

    def collect_merged_prs(self, months: int = 3) -> List[PullRequest]:
        """
        collect merged Pull Requests from the last N months.

        Args:
            months: number of months to look back

        Returns:
            list: list of PullRequest objects
        """
        console.print(
            f"[cyan]Collecting merged PRs from the last {months} months...[/cyan]"
        )

        try:
            date_filter = get_date_filter(months)

            command = [
                "gh",
                "pr",
                "list",
                "--repo",
                self.repo,
                "--state",
                "merged",
                "--search",
                f"merged:>={date_filter}",
                "--json",
                "number,title,author,state,createdAt,updatedAt,mergedAt,url,body,labels,baseRefName,headRefName,additions,deletions,changedFiles",
                "--limit",
                "1000",
            ]

            _, stdout, _ = run_command(command)

            pr_data = json.loads(stdout)
            prs = [PullRequest(pr) for pr in pr_data]

            console.print(f"[green]✓ Found {len(prs)} merged PRs[/green]")
            return prs

        except Exception as e:
            console.print(f"[red]Error collecting merged PRs: {str(e)}[/red]")
            return []

    def collect_all_prs(self, months: int = 3) -> Dict[str, List[PullRequest]]:
        """
        collect all PRs (open and merged).

        Args:
            months: number of months to look back for merged PRs

        Returns:
            dict: dictionary with 'open' and 'merged' lists
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Collecting PRs...", total=None)

            open_prs = self.collect_open_prs()
            merged_prs = self.collect_merged_prs(months)

            progress.update(task, completed=True)

        return {"open": open_prs, "merged": merged_prs}

    def get_pr_details(self, pr_number: int) -> Optional[PullRequest]:
        """
        get detailed information about a specific PR.

        Args:
            pr_number: PR number

        Returns:
            PullRequest object or None if not found
        """
        try:
            command = [
                "gh",
                "pr",
                "view",
                str(pr_number),
                "--repo",
                self.repo,
                "--json",
                "number,title,author,state,createdAt,updatedAt,mergedAt,url,body,labels,baseRefName,headRefName,additions,deletions,changedFiles",
            ]

            _, stdout, _ = run_command(command)
            pr_data = json.loads(stdout)

            return PullRequest(pr_data)

        except Exception as e:
            console.print(f"[red]Error getting PR #{pr_number}: {str(e)}[/red]")
            return None
