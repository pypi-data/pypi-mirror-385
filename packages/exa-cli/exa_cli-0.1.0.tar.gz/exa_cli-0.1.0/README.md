# exa-cli

A command-line interface for the [Exa](https://exa.ai) neural search API. Search the web, find similar content, fetch clean page text, and get AI-powered answers with citations.

## Features

- 🔍 **Neural search** with domain filtering and autoprompt optimization
- 🔗 **Find similar pages** using semantic similarity
- 📄 **Batch fetch content** from multiple URLs in one call
- 🤖 **AI answers** with citations for quick research

## Installation

```bash
pip install exa-cli
```

## Setup

Get an API key from [Exa](https://exa.ai) and set it as an environment variable:

```bash
export EXA_API_KEY="your-api-key-here"
```

Or create a `.env` file in your project:

```
EXA_API_KEY=your-api-key-here
```

## Usage

### Search

Search the web using Exa's neural search:

```bash
# Basic search
exa search "best linux window managers"

# Limit results
exa search "rust async programming" --num 5

# Filter by domain
exa search "machine learning tutorials" --include github.com,arxiv.org

# Exclude domains
exa search "python frameworks" --exclude stackoverflow.com

# Disable autoprompt
exa search "exact query" --no-autoprompt
```

### Find Similar Pages

Find pages similar to a given URL:

```bash
exa similar "https://swaywm.org" --num 5
```

### Fetch Page Content

Get clean, readable text from one or more URLs:

```bash
# Single URL
exa contents "https://archlinux.org"

# Multiple URLs (batch fetch)
exa contents "https://archlinux.org" "https://swaywm.org" "https://github.com/linux-surface"

# Without full text
exa contents "https://example.com" --no-text
```

### Get AI Answers

Ask a question and get an AI-generated answer with citations:

```bash
exa answer "what is the linux surface project"

# Include full text from citations
exa answer "how to install arch linux" --text
```

## Command Reference

```bash
exa search <query>              # Search the web
exa similar <url>               # Find similar pages
exa contents <url> [<url>...]   # Fetch page content (supports multiple URLs)
exa answer <question>           # Get AI answer with citations
```

### Common Options

- `--num, -n`: Number of results (default: 10)
- `--include`: Comma-separated domains to include
- `--exclude`: Comma-separated domains to exclude
- `--text/--no-text`: Include/exclude full text content
- `--autoprompt/--no-autoprompt`: Enable/disable query optimization

Run `exa --help` or `exa <command> --help` for more details.

## Development

```bash
git clone https://github.com/yourusername/exa-cli.git
cd exa-cli
uv sync
uv run pytest
```

## License

MIT
