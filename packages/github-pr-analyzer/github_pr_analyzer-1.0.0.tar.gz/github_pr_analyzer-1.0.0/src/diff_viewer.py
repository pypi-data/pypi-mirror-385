#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for viewing diffs of PRs and commits.

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
from typing import Optional, List, Dict
from git import Repo, Diff
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table

from .utils import run_command

console = Console()


class DiffViewer:
    """viewer for displaying diffs from PRs and commits."""

    def __init__(self, repo_path: str = ".", repo_name: Optional[str] = None):
        """
        initialize diff viewer.

        Args:
            repo_path: path to git repository
            repo_name: repository name in format "owner/repo"
        """
        try:
            self.repo = Repo(repo_path)
            self.repo_path = repo_path
            self.repo_name = repo_name
        except Exception as e:
            raise RuntimeError(f"failed to initialize repository: {str(e)}") from e

    def get_commit_diff(self, sha: str, context_lines: int = 3) -> Optional[str]:
        """
        get diff for a specific commit.

        Args:
            sha: commit SHA
            context_lines: number of context lines

        Returns:
            str: diff content or None if error
        """
        try:
            commit = self.repo.commit(sha)

            if len(commit.parents) == 0:
                diff_text = commit.diff(None, create_patch=True)
            else:
                parent = commit.parents[0]
                diff_text = parent.diff(commit, create_patch=True)

            diff_output = []
            for diff_item in diff_text:
                if diff_item.diff:
                    diff_output.append(diff_item.diff.decode("utf-8", errors="replace"))

            return "\n".join(diff_output)

        except Exception as e:
            console.print(f"[red]Error getting commit diff: {str(e)}[/red]")
            return None

    def get_pr_diff(self, pr_number: int) -> Optional[str]:
        """
        get diff for a specific PR using gh CLI.

        Args:
            pr_number: PR number

        Returns:
            str: diff content or None if error
        """
        try:
            if not self.repo_name:
                console.print(
                    "[yellow]Warning: repo_name not set, cannot fetch PR diff[/yellow]"
                )
                return None

            command = ["gh", "pr", "diff", str(pr_number), "--repo", self.repo_name]

            _, stdout, _ = run_command(command)
            return stdout

        except Exception as e:
            console.print(f"[red]Error getting PR diff: {str(e)}[/red]")
            return None

    def get_pr_files(self, pr_number: int) -> List[Dict[str, any]]:
        """
        get list of files changed in a PR.

        Args:
            pr_number: PR number

        Returns:
            list: list of file information dictionaries
        """
        try:
            if not self.repo_name:
                console.print(
                    "[yellow]Warning: repo_name not set, cannot fetch PR files[/yellow]"
                )
                return []

            command = [
                "gh",
                "pr",
                "view",
                str(pr_number),
                "--repo",
                self.repo_name,
                "--json",
                "files",
            ]

            _, stdout, _ = run_command(command)
            data = json.loads(stdout)

            return data.get("files", [])

        except Exception as e:
            console.print(f"[red]Error getting PR files: {str(e)}[/red]")
            return []

    def get_commit_files(self, sha: str) -> List[str]:
        """
        get list of files changed in a commit.

        Args:
            sha: commit SHA

        Returns:
            list: list of file paths
        """
        try:
            commit = self.repo.commit(sha)

            if len(commit.parents) == 0:
                return []

            parent = commit.parents[0]
            diff_index = parent.diff(commit)

            files = []
            for diff_item in diff_index:
                if diff_item.a_path:
                    files.append(diff_item.a_path)
                if diff_item.b_path and diff_item.b_path != diff_item.a_path:
                    files.append(diff_item.b_path)

            return list(set(files))

        except Exception as e:
            console.print(f"[red]Error getting commit files: {str(e)}[/red]")
            return []

    def display_commit_diff(self, sha: str, max_lines: int = 500):
        """
        display commit diff in a formatted way.

        Args:
            sha: commit SHA
            max_lines: maximum number of lines to display
        """
        diff = self.get_commit_diff(sha)

        if not diff:
            console.print("[yellow]No diff available[/yellow]")
            return

        lines = diff.split("\n")
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            truncated = True
        else:
            truncated = False

        diff_text = "\n".join(lines)

        try:
            syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Commit {sha[:7]}", border_style="cyan"))

            if truncated:
                console.print(
                    f"[yellow]⚠ Output truncated to {max_lines} lines[/yellow]"
                )
        except Exception:
            console.print(diff_text)

    def display_pr_diff(self, pr_number: int, max_lines: int = 500):
        """
        display PR diff in a formatted way.

        Args:
            pr_number: PR number
            max_lines: maximum number of lines to display
        """
        diff = self.get_pr_diff(pr_number)

        if not diff:
            console.print("[yellow]No diff available[/yellow]")
            return

        lines = diff.split("\n")
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            truncated = True
        else:
            truncated = False

        diff_text = "\n".join(lines)

        try:
            syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"PR #{pr_number}", border_style="cyan"))

            if truncated:
                console.print(
                    f"[yellow]⚠ Output truncated to {max_lines} lines[/yellow]"
                )
        except Exception:
            console.print(diff_text)

    def display_file_list(self, files: List[str], title: str = "Changed Files"):
        """
        display a list of changed files in a table.

        Args:
            files: list of file paths
            title: table title
        """
        if not files:
            console.print("[yellow]No files changed[/yellow]")
            return

        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("File Path", style="green")

        for file_path in files:
            table.add_row(file_path)

        console.print(table)

    def get_file_content_at_commit(self, sha: str, file_path: str) -> Optional[str]:
        """
        get content of a file at a specific commit.

        Args:
            sha: commit SHA
            file_path: path to file

        Returns:
            str: file content or None if not found
        """
        try:
            commit = self.repo.commit(sha)
            blob = commit.tree / file_path
            return blob.data_stream.read().decode("utf-8", errors="replace")

        except Exception as e:
            console.print(f"[red]Error reading file: {str(e)}[/red]")
            return None

    def compare_file_between_commits(
        self, sha1: str, sha2: str, file_path: str
    ) -> Optional[str]:
        """
        compare a specific file between two commits.

        Args:
            sha1: first commit SHA
            sha2: second commit SHA
            file_path: path to file

        Returns:
            str: diff content or None if error
        """
        try:
            commit1 = self.repo.commit(sha1)
            commit2 = self.repo.commit(sha2)

            diff = commit1.diff(commit2, paths=file_path, create_patch=True)

            diff_output = []
            for diff_item in diff:
                if diff_item.diff:
                    diff_output.append(diff_item.diff.decode("utf-8", errors="replace"))

            return "\n".join(diff_output)

        except Exception as e:
            console.print(f"[red]Error comparing file: {str(e)}[/red]")
            return None
