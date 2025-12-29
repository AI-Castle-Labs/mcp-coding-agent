# MCP Coding Agent

A powerful tool for analyzing GitHub repositories and generating Abstract Syntax Tree (AST) representations with dependency tracking and LLM-powered code summaries.

## Features

- 🔍 **GitHub Repository Analysis**: Fetch and analyze Python codebases directly from GitHub
- 🌳 **AST Generation**: Build comprehensive AST structures (File → Class → Function → Code)
- 🔗 **Dependency Tracking**: Extract inward dependencies (imports, function calls) and outward dependencies (callers)
- 🤖 **LLM Summarization**: Generate code summaries and dependency descriptions using OpenAI (optional)
- 📊 **JSON Export**: Export complete AST graphs with metadata
- 📖 **Markdown Reports**: Generate beautiful markdown reports viewable in your IDE
- 💬 **Interactive Q&A**: Ask questions about the analyzed codebase using AI

## Installation

1. Clone the repository:

```bash
git clone https://github.com/AI-Castle-Labs/mcp-coding-agent.git
cd mcp-coding-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.template .env
# Edit .env and add your GitHub token and OpenAI API key
```

## Configuration

Create a `.env` file in the `mcp-coding-agent` directory:

```env
# Required: GitHub Personal Access Token
GITHUB_TOKEN=your_github_token_here

# Optional: OpenAI API Key (for LLM summarization)
OPENAI_API_KEY=your_openai_api_key_here
```

### Getting a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (for private repositories)
   - `public_repo` (for public repositories only)
4. Copy the token and add it to your `.env` file

## Usage

### Interactive Mode

Run the analyzer with a beautiful terminal interface:

```bash
python3 run_analysis.py
```

This opens an interactive menu where you can:
1. Analyze a GitHub repository with AI summaries
2. Quick scan without AI summaries (faster)
3. Ask questions about analyzed code
4. View previous analysis reports

### Command-Line Mode

```bash
# Full analysis with LLM summaries
python3 run_analysis.py --full --owner <owner> --repo <repo>

# Quick scan (no LLM - faster)
python3 run_analysis.py --quick --owner <owner> --repo <repo>

# Ask a question about the codebase
python3 run_analysis.py --ask "What does this codebase do?"

# Analyze a specific branch
python3 run_analysis.py --full --owner openai --repo whisper --branch main
```

### Examples

```bash
# Analyze VentureBot (default)
python3 run_analysis.py --full

# Analyze Flask
python3 run_analysis.py --full --owner pallets --repo flask

# Quick scan a large repo
python3 run_analysis.py --quick --owner microsoft --repo vscode
```

## Output

The analyzer generates two types of output:

1. **JSON File** (`<repo>_analysis.json`): Complete AST data with all summaries
2. **Markdown Report** (`<owner>_<repo>_REPORT.md`): Beautiful formatted report for viewing in IDE

### Example JSON Output

```json
{
  "repository": "owner/repo-name",
  "branch": "main",
  "analyzed_at": "2025-01-01T12:00:00",
  "total_files": 10,
  "files": [
    {
      "path": "path/to/file.py",
      "classes": [...],
      "functions": [...],
      "imports": [...],
      "code_summary": "This file implements...",
      "dependency_summary": "Relies on requests, json..."
    }
  ]
}
```

## Project Structure

```
mcp-coding-agent/
├── src/
│   ├── main.py                 # Core analysis logic
│   ├── second_builder.py       # AST builder with LLM integration
│   ├── dependency_visitor.py   # Dependency extraction visitor
│   └── devanalyzer.py          # GitHub API integration
├── test/
│   ├── test_second_builder.py
│   └── test_dependency_visitor.py
├── asset/
│   └── ast_builder.py          # Alternative AST builder
├── run_analysis.py             # Main entry point with beautiful UI
├── .env                        # Environment variables (not in git)
├── .env.template               # Template for .env file
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Workflow

The analysis follows these steps:

1. **Connect to GitHub**: Authenticate and fetch repository information
2. **Fetch Python Files**: Recursively find all `.py` files in the repository
3. **Build AST Structure**: Parse each file and extract classes, functions, and code
4. **Extract Dependencies**: Identify imports, function calls, and class references
5. **Build Call Graph**: Map function call relationships
6. **Generate Summaries** (optional): Use LLM to summarize code and dependencies
7. **Output Results**: Export as JSON and Markdown

## Dependencies

- `requests`: HTTP requests to GitHub API
- `python-dotenv`: Load environment variables from `.env` file
- `openai`: OpenAI API client for LLM summarization (optional)

## Security

⚠️ **Important**: Never commit your `.env` file or expose tokens in code. The `.gitignore` file is configured to exclude `.env` files.

## Contributing

Contributions are welcome! Please ensure:

- No hardcoded tokens or secrets
- Code follows Python best practices
- Tests pass before submitting PRs

## License

MIT License

## Support

For issues or questions, please open an issue on GitHub.

