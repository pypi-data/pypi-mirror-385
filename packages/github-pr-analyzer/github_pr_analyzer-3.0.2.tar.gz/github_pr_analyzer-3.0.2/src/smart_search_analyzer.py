#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smart search analyzer for extracting optimal search keywords using AI.

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
import tempfile
from typing import Optional, List, Dict
from pathlib import Path
from rich.console import Console

from .config import config
from .utils import run_command

console = Console()


class SmartSearchAnalyzer:
    """analyzer for extracting optimal search keywords using AI."""

    def __init__(self, cursor_agent_path: Optional[str] = None):
        """
        initialize smart search analyzer.

        Args:
            cursor_agent_path: path to cursor-agent executable
        """
        self.cursor_agent_path = cursor_agent_path or config.cursor_agent_path
        self.is_available = self._check_availability()

    def _check_availability(self) -> bool:
        """
        check if cursor-agent is available.

        Returns:
            bool: True if cursor-agent is available
        """
        if not self.cursor_agent_path:
            return False

        cursor_path = Path(self.cursor_agent_path)
        if not cursor_path.exists():
            return False

        return True

    def _create_keyword_extraction_prompt(self, user_query: str) -> str:
        """
        create prompt for extracting search keywords from user query.

        Args:
            user_query: user's search query

        Returns:
            str: formatted prompt for keyword extraction
        """
        prompt = f"""
# Search Query Analysis Task

## User Query
"{user_query}"

## Task
Analyze the user's search query and extract the most effective search keywords for finding relevant GitHub Pull Requests and commits. 

## Requirements
1. Extract 5-10 high-quality search keywords/phrases
2. Prioritize keywords by relevance and discriminative power
3. Include different types of keywords:
   - Technical terms (functions, APIs, technologies)
   - Action words (fix, add, update, refactor, etc.)
   - Domain-specific terms
   - Author names (if mentioned)
   - File types or paths (if relevant)

## Output Format
Provide ONLY a JSON array of keywords, ordered by priority (most important first):

```json
[
  "keyword1",
  "keyword2", 
  "keyword3",
  ...
]
```

## Examples
- Query: "fix authentication bug in user login"
  Output: ["authentication", "login", "fix", "bug", "user", "auth", "security"]

- Query: "add new API endpoint for payment processing"
  Output: ["API", "endpoint", "payment", "add", "new", "processing", "REST", "service"]

- Query: "refactor database connection by john smith"
  Output: ["database", "connection", "refactor", "john smith", "db", "sql", "optimization"]

Now analyze the user query and provide the keyword array:
"""
        return prompt

    def extract_search_keywords(self, user_query: str) -> List[str]:
        """
        extract optimal search keywords from user query using AI.

        Args:
            user_query: user's search query

        Returns:
            list: list of extracted keywords ordered by priority
        """
        if not self.is_available:
            # fallback to simple keyword extraction
            return self._fallback_keyword_extraction(user_query)

        console.print(f"[cyan]Analyzing search query with AI...[/cyan]")

        prompt = self._create_keyword_extraction_prompt(user_query)

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as f:
                f.write(prompt)
                prompt_file = f.name

            command = [self.cursor_agent_path, "--file", prompt_file]

            _, stdout, stderr = run_command(command, check=False)

            Path(prompt_file).unlink()

            if stderr:
                console.print(f"[yellow]Warning: {stderr}[/yellow]")

            if stdout:
                # extract JSON array from response
                keywords = self._parse_keywords_response(stdout.strip())
                if keywords:
                    console.print(
                        f"[green]✓ Extracted {len(keywords)} keywords[/green]"
                    )
                    return keywords

            console.print(
                "[yellow]AI keyword extraction failed, using fallback[/yellow]"
            )
            return self._fallback_keyword_extraction(user_query)

        except Exception as e:
            console.print(f"[red]Error during AI keyword extraction: {str(e)}[/red]")
            return self._fallback_keyword_extraction(user_query)

    def _parse_keywords_response(self, response: str) -> List[str]:
        """
        parse keywords from AI response.

        Args:
            response: AI response text

        Returns:
            list: extracted keywords or empty list if parsing fails
        """
        try:
            # try to find JSON array in response
            import re

            # look for JSON array pattern
            json_pattern = r"\[[\s\S]*?\]"
            matches = re.findall(json_pattern, response)

            for match in matches:
                try:
                    keywords = json.loads(match)
                    if isinstance(keywords, list) and all(
                        isinstance(k, str) for k in keywords
                    ):
                        # filter out empty strings and limit to 10 keywords
                        return [k.strip() for k in keywords if k.strip()][:10]
                except json.JSONDecodeError:
                    continue

            # if no valid JSON found, try to extract keywords from text
            lines = response.split("\n")
            keywords = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("```"):
                    # remove quotes and extract potential keywords
                    cleaned = re.sub(r'["\'\[\],]', "", line).strip()
                    if cleaned and len(cleaned) > 1:
                        keywords.append(cleaned)

            return keywords[:10] if keywords else []

        except Exception:
            return []

    def _fallback_keyword_extraction(self, user_query: str) -> List[str]:
        """
        fallback keyword extraction when AI is not available.

        Args:
            user_query: user's search query

        Returns:
            list: extracted keywords using simple rules
        """
        import re

        # normalize query
        query = user_query.lower().strip()

        # remove common stop words but keep technical terms
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
        }

        # split into words and phrases
        words = re.findall(r"\b\w+\b", query)

        # extract meaningful keywords
        keywords = []

        # add individual words (filtered)
        for word in words:
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)

        # add potential phrases (2-3 words)
        for i in range(len(words) - 1):
            phrase = " ".join(words[i : i + 2])
            if len(phrase) > 4:
                keywords.append(phrase)

        # prioritize technical terms and action words
        priority_patterns = [
            r"\b(fix|bug|error|issue)\b",
            r"\b(add|new|create|implement)\b",
            r"\b(update|modify|change|edit)\b",
            r"\b(refactor|cleanup|optimize)\b",
            r"\b(api|endpoint|service|function)\b",
            r"\b(database|db|sql|query)\b",
            r"\b(auth|authentication|login|security)\b",
            r"\b(test|testing|unit|integration)\b",
        ]

        priority_keywords = []
        for pattern in priority_patterns:
            matches = re.findall(pattern, query)
            priority_keywords.extend(matches)

        # combine and deduplicate
        all_keywords = priority_keywords + keywords
        seen = set()
        result = []

        for keyword in all_keywords:
            if keyword not in seen and len(keyword) > 1:
                seen.add(keyword)
                result.append(keyword)

        return result[:10]  # limit to 10 keywords

    def analyze_search_effectiveness(
        self, keywords: List[str], total_items: int, matched_items: int
    ) -> Dict[str, any]:
        """
        analyze search effectiveness and suggest improvements.

        Args:
            keywords: used keywords
            total_items: total number of items searched
            matched_items: number of matched items

        Returns:
            dict: analysis results and suggestions
        """
        effectiveness_ratio = matched_items / total_items if total_items > 0 else 0

        analysis = {
            "effectiveness_ratio": effectiveness_ratio,
            "keywords_used": keywords,
            "total_items": total_items,
            "matched_items": matched_items,
            "suggestions": [],
        }

        # provide suggestions based on results
        if effectiveness_ratio < 0.01:  # less than 1% match
            analysis["suggestions"].append("Try broader or more general keywords")
            analysis["suggestions"].append("Consider using synonyms or related terms")
        elif effectiveness_ratio > 0.5:  # more than 50% match
            analysis["suggestions"].append(
                "Results may be too broad, try more specific keywords"
            )
            analysis["suggestions"].append(
                "Consider adding technical details or constraints"
            )
        else:
            analysis["suggestions"].append("Good keyword balance - results are focused")

        return analysis
