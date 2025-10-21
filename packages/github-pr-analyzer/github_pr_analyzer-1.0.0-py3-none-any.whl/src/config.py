#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration management for the PR analyzer.

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

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """configuration class for managing application settings."""

    def __init__(self):
        """initialize configuration with environment variables."""
        load_dotenv()

        self.cursor_agent_path: Optional[str] = os.getenv("CURSOR_AGENT_PATH")
        self.default_months: int = int(os.getenv("DEFAULT_MONTHS", "3"))
        self.default_repo_path: str = os.getenv("DEFAULT_REPO_PATH", ".")

    def validate(self) -> tuple[bool, list[str]]:
        """
        validate the configuration.

        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []

        if self.cursor_agent_path:
            cursor_path = Path(self.cursor_agent_path)
            if not cursor_path.exists():
                errors.append(f"cursor-agent not found at: {self.cursor_agent_path}")

        if self.default_months < 1:
            errors.append("DEFAULT_MONTHS must be at least 1")

        return (len(errors) == 0, errors)


# global configuration instance
config = Config()
