# GitHub PR & Commit Analyzer

[中文文档](README.cn.md) | English

A powerful command-line tool for intelligently collecting, analyzing, and summarizing GitHub Pull Requests and commit records. Supports keyword-based smart search and AI-powered analysis features.

## ✨ Key Features

- 🔍 **Smart Search**: Intelligent PR/Commit search based on fuzzy matching and keywords
- 📊 **Data Collection**: Automatically collect open and merged PRs, as well as merge commits
- 🔄 **Diff Viewing**: Complete code change viewing functionality
- 🤖 **AI Analysis**: Integrated with cursor-agent CLI for intelligent change summarization
- 💼 **Production Quality**: Complete error handling, logging, and user experience
- 🎨 **Beautiful Output**: Professional terminal output using Rich library

## 📋 Prerequisites

Before using this tool, ensure the following dependencies are installed:

### Required Dependencies

1. **Python 3.8+**
   ```bash
   python --version  # should be >= 3.8
   ```

2. **Git**
   ```bash
   git --version
   ```

3. **GitHub CLI (gh)**
   ```bash
   # Ubuntu/Debian
   sudo apt install gh
   
   # macOS
   brew install gh
   
   # Windows
   choco install gh
   ```
   
   After installation, you need to login:
   ```bash
   gh auth login
   ```

### Optional Dependencies

4. **cursor-agent CLI** (for AI analysis features)
   - If you need AI analysis features, please deploy cursor-agent in advance
   - Configure the path in the `.env` file

## 🚀 Installation

### Method 1: Install from Source

```bash
# Clone or download the project
cd github-pr-analyzer

# Install dependencies
pip install -r requirements.txt

# Or install using setup.py
pip install -e .
```

### Method 2: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Copy the configuration template:
```bash
cp .env.example .env
```

2. Edit the `.env` file:
```bash
# GitHub Configuration
# gh CLI must be installed and authenticated

# AI Configuration (Optional)
CURSOR_AGENT_PATH=/path/to/cursor-agent

# Default Settings
DEFAULT_MONTHS=3
DEFAULT_REPO_PATH=.
```

## 📖 Usage

### Basic Commands

#### 1. Collect PRs and Commits

```bash
# Auto-detect current repository
python main.py collect

# Specify repository
python main.py collect --repo owner/repo

# Specify time range (months)
python main.py collect --months 6
```

#### 2. Search for Relevant Changes

```bash
# Basic search
python main.py search "bug fix authentication"

# With AI analysis
python main.py search "add new feature" --analyze

# Show diff
python main.py search "optimization" --show-diff

# Advanced options
python main.py search "refactor" \
  --repo owner/repo \
  --months 6 \
  --min-score 50 \
  --max-results 10 \
  --analyze
```

#### 3. View Specific PR

```bash
# View PR details
python main.py view-pr 123

# View PR with AI analysis
python main.py view-pr 123 --analyze

# Specify repository
python main.py view-pr 123 --repo owner/repo
```

#### 4. View Specific Commit

```bash
# View commit details
python main.py view-commit abc1234

# View and analyze
python main.py view-commit abc1234 --analyze
```

#### 5. Interactive Mode

```bash
# Launch interactive interface
python main.py interactive
```

## 🎯 Use Cases

### Scenario 1: Find All Changes Related to Specific Feature

```bash
# Search for all PRs and commits related to "authentication"
python main.py search "authentication" --months 3 --analyze

# Output:
# - List of matching PRs and commits (sorted by relevance)
# - AI-generated summary for each change
# - Option to save analysis report
```

### Scenario 2: Review Recent Merges

```bash
# Collect all merges from the last 3 months
python main.py collect --months 3

# Then search for specific types of changes
python main.py search "performance optimization" --show-diff
```

### Scenario 3: Deep Dive into Specific PR

```bash
# View complete information for PR #456
python main.py view-pr 456 --analyze

# Output includes:
# - PR basic information
# - Complete diff
# - AI analysis: purpose, impact, technical details
```

## 🛠️ Development

### Project Structure

```
github-pr-analyzer/
├── main.py                 # Program entry point
├── setup.py               # Installation configuration
├── requirements.txt       # Dependency list
├── .env.example          # Configuration template
├── .gitignore            # Git ignore rules
├── README.md             # This document
└── src/
    ├── __init__.py
    ├── config.py         # Configuration management
    ├── utils.py          # Utility functions
    ├── pr_collector.py   # PR collection module
    ├── commit_collector.py  # Commit collection module
    ├── diff_viewer.py    # Diff viewing module
    ├── matcher.py        # Smart matching module
    ├── ai_analyzer.py    # AI analysis module
    └── cli.py            # Command-line interface
```

### Running Tests

```bash
# Basic functionality test
python main.py --help

# Check dependencies
python test_installation.py
```

## 📝 FAQ

### Q: Getting "gh CLI not authenticated"
A: Run `gh auth login` and complete GitHub authentication.

### Q: Repository not found
A: Make sure you're in a Git repository directory, or use `--repo owner/repo` to specify explicitly.

### Q: AI analysis not available
A: Configure `CURSOR_AGENT_PATH` in the `.env` file. AI features are optional.

### Q: Too many/too few search results
A: Adjust the `--min-score` parameter (lower for more results, higher for more precise results).

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

This project is licensed under the MIT License - free for commercial and personal use.

Copyright (c) 2025 GitHub PR Analyzer Team

## 🔗 Related Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [Rich Library Documentation](https://rich.readthedocs.io/)

## 📧 Contact

For questions or suggestions, please contact us via Issues.

---

**Enjoy analyzing! 🎉**
