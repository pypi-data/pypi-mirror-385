#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for matching PRs and commits based on user queries.

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
from typing import Dict, List, Optional, Tuple, Union
from rich.console import Console

from .pr_collector import PullRequest
from .commit_collector import Commit
from .smart_search_analyzer import SmartSearchAnalyzer
from .utils import normalize_keywords, normalize_text

console = Console()


class MatchResult:
    """represent a match result with score and reason."""

    def __init__(
        self, item: Union[PullRequest, Commit], score: int, matched_fields: List[str]
    ):
        """
        initialize match result.

        Args:
            item: matched PR or Commit
            score: match score (0-100)
            matched_fields: list of fields that matched
        """
        self.item = item
        self.score = score
        self.matched_fields = matched_fields
        self.item_type = "PR" if isinstance(item, PullRequest) else "Commit"

    def __str__(self) -> str:
        """string representation of match result."""
        return f"[{self.item_type}] {str(self.item)} (Score: {self.score})"


class Matcher:
    """matcher for finding relevant PRs and commits based on queries."""

    def __init__(self, fuzzy_threshold: int = 60, use_smart_search: bool = True):
        """
        initialize matcher.

        Args:
            fuzzy_threshold: minimum fuzzy match score (0-100)
            use_smart_search: whether to use AI-powered smart search
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.use_smart_search = use_smart_search
        self.smart_analyzer = SmartSearchAnalyzer() if use_smart_search else None

    def _calculate_keyword_weight(
        self,
        keyword_hits: Dict[str, int],
        base_weight: float,
    ) -> int:
        """
        calculate keyword-based score contribution.

        Args:
            keyword_hits: mapping of keyword to hit count
            base_weight: weight assigned for the field

        Returns:
            int: weighted score based on keyword matches
        """
        total_hits = sum(keyword_hits.values())
        if total_hits == 0:
            return 0

        return int(min(100, total_hits * 20 * base_weight))

    def match_pr(self, pr: PullRequest, keywords: List[str]) -> MatchResult:
        """
        match a PR against a query.

        Args:
            pr: PullRequest object
            query: search query

        Returns:
            MatchResult: match result with score
        """
        total_score = 0
        matched_fields = []

        field_weights = {
            "title": 1.0,
            "body": 0.8,
            "author": 0.5,
            "labels": 0.6,
        }

        normalized_keywords = normalize_keywords(keywords)

        # analyze title
        title_hits: Dict[str, int] = {}
        title_lower = normalize_text(pr.title)
        for keyword in normalized_keywords:
            if keyword and keyword in title_lower:
                title_hits[keyword] = title_hits.get(keyword, 0) + 1

        if title_hits:
            title_score = self._calculate_keyword_weight(
                title_hits, field_weights["title"]
            )
            total_score += title_score
            matched_fields.append("title")

        # analyze body
        if pr.body:
            body_hits: Dict[str, int] = {}
            body_lower = normalize_text(pr.body)
            for keyword in normalized_keywords:
                if keyword and keyword in body_lower:
                    body_hits[keyword] = body_hits.get(keyword, 0) + 1

            if body_hits:
                body_score = self._calculate_keyword_weight(
                    body_hits, field_weights["body"]
                )
                total_score += body_score
                matched_fields.append("body")

        # analyze author
        author_hits: Dict[str, int] = {}
        author_lower = normalize_text(pr.author)
        for keyword in normalized_keywords:
            if keyword and keyword in author_lower:
                author_hits[keyword] = author_hits.get(keyword, 0) + 1

        if author_hits:
            author_score = self._calculate_keyword_weight(
                author_hits, field_weights["author"]
            )
            total_score += author_score
            matched_fields.append("author")

        # analyze labels
        if pr.labels:
            labels_hits: Dict[str, int] = {}
            labels_lower = normalize_text(" ".join(pr.labels))
            for keyword in normalized_keywords:
                if keyword and keyword in labels_lower:
                    labels_hits[keyword] = labels_hits.get(keyword, 0) + 1

            if labels_hits:
                labels_score = self._calculate_keyword_weight(
                    labels_hits, field_weights["labels"]
                )
                total_score += labels_score
                matched_fields.append("labels")

        normalized_score = min(100, total_score)

        return MatchResult(pr, normalized_score, matched_fields)

    def match_commit(
        self,
        commit: Commit,
        keywords: List[str],
    ) -> MatchResult:
        """
        match a commit against a query.

        Args:
            commit: Commit object
            query: search query

        Returns:
            MatchResult: match result with score
        """
        total_score = 0
        matched_fields = []

        field_weights = {
            "message": 1.0,
            "author": 0.4,
        }

        normalized_keywords = normalize_keywords(keywords)

        # commit message
        message_hits: Dict[str, int] = {}
        message_lower = normalize_text(commit.message)
        for keyword in normalized_keywords:
            if keyword and keyword in message_lower:
                message_hits[keyword] = message_hits.get(keyword, 0) + 1

        if message_hits:
            message_score = self._calculate_keyword_weight(
                message_hits, field_weights["message"]
            )
            total_score += message_score
            matched_fields.append("message")

        # commit author
        author_hits: Dict[str, int] = {}
        author_lower = normalize_text(commit.author)
        for keyword in normalized_keywords:
            if keyword and keyword in author_lower:
                author_hits[keyword] = author_hits.get(keyword, 0) + 1

        if author_hits:
            author_score = self._calculate_keyword_weight(
                author_hits, field_weights["author"]
            )
            total_score += author_score
            matched_fields.append("author")

        normalized_score = min(100, total_score)

        return MatchResult(commit, normalized_score, matched_fields)

    def smart_search(
        self,
        prs: List[PullRequest],
        commits: List[Commit],
        query: str,
        min_score: int = 30,
        max_results: int = 20,
    ) -> List[MatchResult]:
        """
        smart search using AI-extracted keywords.

        Args:
            prs: list of PRs to search
            commits: list of commits to search
            query: search query
            min_score: minimum score to include in results
            max_results: maximum number of results to return

        Returns:
            list: sorted list of MatchResults
        """
        if (
            not self.use_smart_search
            or not self.smart_analyzer
            or not self.smart_analyzer.is_available
        ):
            console.print(
                "[yellow]Smart search not available, using standard search[/yellow]"
            )
            return self.search(prs, commits, query, min_score, max_results)

        console.print(f"[cyan]Smart searching for: '{query}'...[/cyan]")

        # extract keywords using AI
        keywords = self.smart_analyzer.extract_search_keywords(query)

        if not keywords:
            console.print(
                "[yellow]No keywords extracted, using original query[/yellow]"
            )
            return self.search(prs, commits, query, min_score, max_results)

        console.print(
            f"[cyan]Using keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}[/cyan]"
        )

        # search with each keyword and combine results
        all_results = {}  # item_id -> MatchResult

        normalized_keywords = normalize_keywords(keywords)

        # search PRs
        for pr in prs:
            item_id = f"pr_{pr.number}"
            match = self.match_pr(pr, normalized_keywords)

            if match.score >= min_score:
                all_results[item_id] = match

        # search commits
        for commit in commits:
            item_id = f"commit_{commit.sha}"
            match = self.match_commit(commit, normalized_keywords)

            if match.score >= min_score:
                all_results[item_id] = match

        # convert to list and sort
        results = list(all_results.values())
        results.sort(key=lambda x: x.score, reverse=True)

        if len(results) > max_results:
            results = results[:max_results]

        # analyze search effectiveness
        total_items = len(prs) + len(commits)
        if self.smart_analyzer:
            effectiveness = self.smart_analyzer.analyze_search_effectiveness(
                keywords, total_items, len(results)
            )

            if effectiveness["suggestions"]:
                console.print(
                    f"[dim]💡 Suggestions: {effectiveness['suggestions'][0]}[/dim]"
                )

        console.print(
            f"[green]✓ Found {len(results)} matches using smart search[/green]"
        )

        return results

    def search(
        self,
        prs: List[PullRequest],
        commits: List[Commit],
        query: str,
        min_score: int = 30,
        max_results: int = 20,
    ) -> List[MatchResult]:
        """
        search for matching PRs and commits.

        Args:
            prs: list of PRs to search
            commits: list of commits to search
            query: search query
            min_score: minimum score to include in results
            max_results: maximum number of results to return

        Returns:
            list: sorted list of MatchResults
        """
        # use smart search if available, otherwise fall back to standard search
        if (
            self.use_smart_search
            and self.smart_analyzer
            and self.smart_analyzer.is_available
        ):
            return self.smart_search(prs, commits, query, min_score, max_results)

        console.print(f"[cyan]Searching for: '{query}'...[/cyan]")

        results = []

        normalized_keywords = normalize_keywords([query])

        for pr in prs:
            match = self.match_pr(pr, normalized_keywords)
            if match.score >= min_score:
                results.append(match)

        for commit in commits:
            match = self.match_commit(commit, normalized_keywords)
            if match.score >= min_score:
                results.append(match)

        results.sort(key=lambda x: x.score, reverse=True)

        if len(results) > max_results:
            results = results[:max_results]

        console.print(f"[green]✓ Found {len(results)} matches[/green]")

        return results

    def search_by_keywords(
        self,
        prs: List[PullRequest],
        commits: List[Commit],
        keywords: List[str],
        match_all: bool = False,
        min_score: int = 30,
    ) -> List[MatchResult]:
        """
        search using multiple keywords.

        Args:
            prs: list of PRs to search
            commits: list of commits to search
            keywords: list of keywords to search for
            match_all: if True, require all keywords to match
            min_score: minimum score per keyword

        Returns:
            list: sorted list of MatchResults
        """
        console.print(f"[cyan]Searching with keywords: {', '.join(keywords)}...[/cyan]")

        results_by_item = {}

        normalized_keywords = normalize_keywords(keywords)

        for pr in prs:
            match = self.match_pr(pr, normalized_keywords)

            item_key = f"pr_{pr.number}"
            if item_key not in results_by_item:
                results_by_item[item_key] = {
                    "item": pr,
                    "scores": [],
                    "matched_fields": set(),
                    "keyword_matches": 0,
                }

            if match.score >= min_score:
                results_by_item[item_key]["scores"].append(match.score)
                results_by_item[item_key]["matched_fields"].update(match.matched_fields)
                results_by_item[item_key]["keyword_matches"] += 1

        for commit in commits:
            match = self.match_commit(commit, normalized_keywords)

            item_key = f"commit_{commit.sha}"
            if item_key not in results_by_item:
                results_by_item[item_key] = {
                    "item": commit,
                    "scores": [],
                    "matched_fields": set(),
                    "keyword_matches": 0,
                }

            if match.score >= min_score:
                results_by_item[item_key]["scores"].append(match.score)
                results_by_item[item_key]["matched_fields"].update(match.matched_fields)
                results_by_item[item_key]["keyword_matches"] += 1

        results = []
        for item_data in results_by_item.values():
            if match_all:
                if item_data["keyword_matches"] < len(keywords):
                    continue
            else:
                if item_data["keyword_matches"] == 0:
                    continue

            avg_score = (
                sum(item_data["scores"]) // len(item_data["scores"])
                if item_data["scores"]
                else 0
            )

            results.append(
                MatchResult(
                    item_data["item"], avg_score, list(item_data["matched_fields"])
                )
            )

        results.sort(key=lambda x: x.score, reverse=True)

        console.print(f"[green]✓ Found {len(results)} matches[/green]")

        return results
