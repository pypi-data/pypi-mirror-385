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
from typing import List, Dict, Union, Tuple
from fuzzywuzzy import fuzz
from rich.console import Console

from .pr_collector import PullRequest
from .commit_collector import Commit
from .smart_search_analyzer import SmartSearchAnalyzer

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

    def _normalize_text(self, text: str) -> str:
        """
        normalize text for matching.

        Args:
            text: text to normalize

        Returns:
            str: normalized text
        """
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _calculate_score(
        self, query: str, text: str, field_weight: float = 1.0
    ) -> Tuple[int, bool]:
        """
        calculate match score between query and text.

        Args:
            query: search query
            text: text to search in
            field_weight: weight for this field (0.0-1.0)

        Returns:
            tuple: (score, is_match)
        """
        query_norm = self._normalize_text(query)
        text_norm = self._normalize_text(text)

        if query_norm in text_norm:
            score = 100
            is_match = True
        else:
            score = fuzz.partial_ratio(query_norm, text_norm)
            is_match = score >= self.fuzzy_threshold

        weighted_score = int(score * field_weight)

        return weighted_score, is_match

    def match_pr(self, pr: PullRequest, query: str) -> MatchResult:
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

        title_score, title_match = self._calculate_score(
            query, pr.title, field_weights["title"]
        )
        if title_match:
            total_score += title_score
            matched_fields.append("title")

        body_score, body_match = self._calculate_score(
            query, pr.body, field_weights["body"]
        )
        if body_match:
            total_score += body_score
            matched_fields.append("body")

        author_score, author_match = self._calculate_score(
            query, pr.author, field_weights["author"]
        )
        if author_match:
            total_score += author_score
            matched_fields.append("author")

        if pr.labels:
            labels_text = " ".join(pr.labels)
            labels_score, labels_match = self._calculate_score(
                query, labels_text, field_weights["labels"]
            )
            if labels_match:
                total_score += labels_score
                matched_fields.append("labels")

        max_possible_score = sum(field_weights.values()) * 100
        normalized_score = min(100, int((total_score / max_possible_score) * 100))

        return MatchResult(pr, normalized_score, matched_fields)

    def match_commit(self, commit: Commit, query: str) -> MatchResult:
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
            "author": 0.5,
        }

        message_score, message_match = self._calculate_score(
            query, commit.message, field_weights["message"]
        )
        if message_match:
            total_score += message_score
            matched_fields.append("message")

        author_score, author_match = self._calculate_score(
            query, commit.author, field_weights["author"]
        )
        if author_match:
            total_score += author_score
            matched_fields.append("author")

        max_possible_score = sum(field_weights.values()) * 100
        normalized_score = min(100, int((total_score / max_possible_score) * 100))

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

        for i, keyword in enumerate(keywords):
            # weight keywords by position (first keywords are more important)
            keyword_weight = 1.0 - (i * 0.1)  # decrease weight by 10% for each position
            keyword_weight = max(keyword_weight, 0.3)  # minimum weight of 30%

            # search PRs
            for pr in prs:
                item_id = f"pr_{pr.number}"
                match = self.match_pr(pr, keyword)

                if match.score >= min_score:
                    weighted_score = int(match.score * keyword_weight)

                    if item_id in all_results:
                        # combine scores (take maximum but add bonus for multiple matches)
                        existing_score = all_results[item_id].score
                        combined_score = max(existing_score, weighted_score) + min(
                            10, weighted_score // 10
                        )
                        all_results[item_id].score = min(100, combined_score)
                        all_results[item_id].matched_fields.extend(match.matched_fields)
                    else:
                        match.score = weighted_score
                        all_results[item_id] = match

            # search commits
            for commit in commits:
                item_id = f"commit_{commit.sha}"
                match = self.match_commit(commit, keyword)

                if match.score >= min_score:
                    weighted_score = int(match.score * keyword_weight)

                    if item_id in all_results:
                        # combine scores
                        existing_score = all_results[item_id].score
                        combined_score = max(existing_score, weighted_score) + min(
                            10, weighted_score // 10
                        )
                        all_results[item_id].score = min(100, combined_score)
                        all_results[item_id].matched_fields.extend(match.matched_fields)
                    else:
                        match.score = weighted_score
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

        for pr in prs:
            match = self.match_pr(pr, query)
            if match.score >= min_score:
                results.append(match)

        for commit in commits:
            match = self.match_commit(commit, query)
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

        for keyword in keywords:
            for pr in prs:
                match = self.match_pr(pr, keyword)

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
                    results_by_item[item_key]["matched_fields"].update(
                        match.matched_fields
                    )
                    results_by_item[item_key]["keyword_matches"] += 1

            for commit in commits:
                match = self.match_commit(commit, keyword)

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
                    results_by_item[item_key]["matched_fields"].update(
                        match.matched_fields
                    )
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
