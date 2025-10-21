#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for collecting commits from Git repositories.

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

import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from git import Repo, Commit as GitCommit
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Commit:
    """represent a Git commit with relevant information."""

    def __init__(self, git_commit: GitCommit, repo_name: Optional[str] = None):
        """
        initialize a Commit object from GitPython commit.

        Args:
            git_commit: GitPython Commit object
            repo_name: repository name for URL generation
        """
        self.sha: str = git_commit.hexsha
        self.short_sha: str = git_commit.hexsha[:7]
        self.message: str = git_commit.message.strip()
        self.author: str = git_commit.author.name
        self.author_email: str = git_commit.author.email
        self.committer: str = git_commit.committer.name
        self.committed_date: datetime = datetime.fromtimestamp(
            git_commit.committed_date
        )
        self.authored_date: datetime = datetime.fromtimestamp(git_commit.authored_date)
        self.parents: List[str] = [p.hexsha for p in git_commit.parents]
        self.is_merge: bool = len(git_commit.parents) > 1
        self.repo_name: Optional[str] = repo_name

        # extract PR number from commit message if present
        self.pr_number: Optional[int] = self._extract_pr_number()

        # parse commit stats
        self.stats: Dict = git_commit.stats.total
        self.files_changed: int = self.stats.get("files", 0)
        self.insertions: int = self.stats.get("insertions", 0)
        self.deletions: int = self.stats.get("deletions", 0)

    def _extract_pr_number(self) -> Optional[int]:
        """
        extract PR number from commit message.

        Returns:
            int: PR number or None if not found
        """
        patterns = [
            r"#(\d+)",
            r"PR[:\s]+(\d+)",
            r"pull request[:\s]+(\d+)",
            r"\(#(\d+)\)",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.message, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def get_url(self) -> Optional[str]:
        """
        get GitHub URL for this commit.

        Returns:
            str: GitHub commit URL or None if repo_name not set
        """
        if self.repo_name:
            return f"https://github.com/{self.repo_name}/commit/{self.sha}"
        return None

    def to_dict(self) -> Dict:
        """
        convert Commit object to dictionary.

        Returns:
            dict: commit data as dictionary
        """
        return {
            "sha": self.sha,
            "short_sha": self.short_sha,
            "message": self.message,
            "author": self.author,
            "author_email": self.author_email,
            "committer": self.committer,
            "committed_date": self.committed_date.isoformat(),
            "authored_date": self.authored_date.isoformat(),
            "parents": self.parents,
            "is_merge": self.is_merge,
            "pr_number": self.pr_number,
            "url": self.get_url(),
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions,
        }

    def __str__(self) -> str:
        """string representation of the commit."""
        emoji = "🔀" if self.is_merge else "📝"
        pr_info = f" (PR #{self.pr_number})" if self.pr_number else ""
        title = self.message.split("\n")[0][:80]
        return f"{emoji} {self.short_sha}: {title}{pr_info} (@{self.author})"


class CommitCollector:
    """collector for fetching commits from Git repositories."""

    def __init__(self, repo_path: str = ".", repo_name: Optional[str] = None):
        """
        initialize commit collector.

        Args:
            repo_path: path to git repository
            repo_name: repository name in format "owner/repo" for URL generation
        """
        try:
            self.repo = Repo(repo_path)
            self.repo_path = repo_path
            self.repo_name = repo_name

            if self.repo.bare:
                raise ValueError("cannot work with bare repositories")

        except Exception as e:
            raise RuntimeError(
                f"failed to initialize repository at {repo_path}: {str(e)}"
            ) from e

    def collect_merge_commits(
        self, branch: str = "HEAD", months: int = 3, author: Optional[str] = None
    ) -> List[Commit]:
        """
        collect merge commits from the repository.

        Args:
            branch: branch to collect from
            months: number of months to look back
            author: filter by author name/email (optional)

        Returns:
            list: list of Commit objects
        """
        console.print(
            f"[cyan]Collecting merge commits from the last {months} months...[/cyan]"
        )

        try:
            since_date = datetime.now() - timedelta(days=months * 30)

            commits = []
            for commit in self.repo.iter_commits(branch, since=since_date):
                if len(commit.parents) > 1:
                    if author:
                        if (
                            author.lower() in commit.author.name.lower()
                            or author.lower() in commit.author.email.lower()
                        ):
                            commits.append(Commit(commit, self.repo_name))
                    else:
                        commits.append(Commit(commit, self.repo_name))

            console.print(f"[green]✓ Found {len(commits)} merge commits[/green]")
            return commits

        except Exception as e:
            console.print(f"[red]Error collecting merge commits: {str(e)}[/red]")
            return []

    def collect_all_commits(
        self,
        branch: str = "HEAD",
        months: int = 3,
        author: Optional[str] = None,
        merge_only: bool = False,
    ) -> List[Commit]:
        """
        collect all commits from the repository.

        Args:
            branch: branch to collect from
            months: number of months to look back
            author: filter by author name/email (optional)
            merge_only: only include merge commits

        Returns:
            list: list of Commit objects
        """
        console.print(
            f"[cyan]Collecting commits from the last {months} months...[/cyan]"
        )

        try:
            since_date = datetime.now() - timedelta(days=months * 30)

            commits = []
            for commit in self.repo.iter_commits(branch, since=since_date):
                if merge_only and len(commit.parents) <= 1:
                    continue

                if author:
                    if (
                        author.lower() in commit.author.name.lower()
                        or author.lower() in commit.author.email.lower()
                    ):
                        commits.append(Commit(commit, self.repo_name))
                else:
                    commits.append(Commit(commit, self.repo_name))

            console.print(f"[green]✓ Found {len(commits)} commits[/green]")
            return commits

        except Exception as e:
            console.print(f"[red]Error collecting commits: {str(e)}[/red]")
            return []

    def get_commit_details(self, sha: str) -> Optional[Commit]:
        """
        get detailed information about a specific commit.

        Args:
            sha: commit SHA (full or short)

        Returns:
            Commit object or None if not found
        """
        try:
            git_commit = self.repo.commit(sha)
            return Commit(git_commit, self.repo_name)

        except Exception as e:
            console.print(f"[red]Error getting commit {sha}: {str(e)}[/red]")
            return None

    def get_commits_by_pr(self, pr_number: int, months: int = 3) -> List[Commit]:
        """
        find commits associated with a specific PR number.

        Args:
            pr_number: PR number to search for
            months: number of months to look back

        Returns:
            list: list of Commit objects
        """
        console.print(f"[cyan]Finding commits for PR #{pr_number}...[/cyan]")

        try:
            since_date = datetime.now() - timedelta(days=months * 30)

            commits = []
            for commit in self.repo.iter_commits("HEAD", since=since_date):
                commit_obj = Commit(commit, self.repo_name)
                if commit_obj.pr_number == pr_number:
                    commits.append(commit_obj)

            console.print(
                f"[green]✓ Found {len(commits)} commits for PR #{pr_number}[/green]"
            )
            return commits

        except Exception as e:
            console.print(f"[red]Error finding commits: {str(e)}[/red]")
            return []
