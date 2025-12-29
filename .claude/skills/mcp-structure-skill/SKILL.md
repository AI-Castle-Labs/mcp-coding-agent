---
name: mcp-structure-skill
description: Guidance and snippets for creating/updating Codex skills tailored to the mcp-coding-agent project (AST/dependency tooling). Use when asked to build a new skill or refine one for this repo’s workflows and structure.
---

# Purpose
Use this skill to design or refresh skills that help agents work on the `mcp-coding-agent` codebase. This project analyzes Python codebases by building AST structures with dependency tracking and optional LLM summaries.

# Project Architecture

## Core Components

### 1. **ast_builder.py** - Primary Stable Implementation
The main, production-ready AST builder with complete functionality:
- **Data Classes**: `FunctionNode`, `ClassNode`, `FileNode` with comprehensive fields
  - Tracks code, line numbers, summaries (code_summary, dependency_summary)
  - Inward dependencies (what code uses) and outward dependencies (what uses this code)
- **DependencyVisitor**: AST visitor extracting imports, function calls, class references, attributes
- **LLM Integration**: Optional OpenAI integration for code and dependency summarization
- **Call Graph Building**: `_build_call_graph()` maps function relationships across files
- **Directory Walking**: `build_codebase_ast()` processes all Python files in a directory tree
- **CLI**: `python ast_builder.py <root_dir> [--summarize] [--json output.json]`
- **Requirements**: Optional `OPENAI_API_KEY` for summaries

### 2. **dependency_visitor.py** - Standalone Visitor
Legacy/standalone version of DependencyVisitor class:
- Extracts imports, function calls, class references, attributes from AST nodes
- Used by `second_builder.py`
- Has identical structure to DependencyVisitor in `ast_builder.py`

### 3. **second_builder.py** - Alternative Builder (GitHub-focused)
Alternative implementation designed for string-based source code:
- **AstBuilder Class**: Works with source code strings (useful for GitHub content)
- Uses `DependencyVisitor` from `dependency_visitor.py`
- Similar data classes but slightly different field names
- Methods: `build_file_ast()`, `extract_class()`, `extract_func()`
- Less complete than `ast_builder.py` (no built-in call graph in class)

### 4. **main.py** - GitHub Repository Integration
Entry point for analyzing GitHub repositories:
- Integrates with `devanalyzer.githubanalyzer` to fetch code from GitHub
- Uses `second_builder.py`'s AstBuilder class
- Implements `_build_call_graph_from_dependencies()` for GitHub-sourced content
- **CLI**: `python main.py <repo_name> [--owner OWNER] [--branch BRANCH] [--no-summarize] [-o output.json]`
- **Requirements**: `GITHUB_TOKEN` (environment variable), optional `OPENAI_API_KEY`
- **Dependencies**: Requires `devanalyzer` module with GitHub integration

### 5. **agents.md** - Project Documentation
High-level overview of repository structure, usage, and caveats

## Quickstart for Skill Creation

1) **Understand the ask**: Determine if the skill is for:
   - AST/dependency analysis workflows
   - Local directory analysis (use `ast_builder.py`)
   - GitHub repository analysis (use `main.py` + `second_builder.py`)
   - LLM summarization features
   - Testing or validation

2) **Load context appropriately**:
   - Always check `agents.md` first for current project status
   - For local analysis: reference `ast_builder.py`
   - For GitHub integration: reference `main.py` and `second_builder.py`
   - For visitor patterns: reference `dependency_visitor.py`

3) **Name the skill**: hyphen-case, verb-led, <64 chars (e.g., `analyze-ast-dependencies`)

4) **Structure the skill**:
   - Frontmatter: name, description with clear triggers and scope
   - Content sections: Purpose, When to Use, Workflow, Examples
   - Keep under ~500 lines for maintainability

5) **Decide resources**:
   - `scripts/`: Only for truly reusable automation
   - `references/`: Brief domain notes, API references, examples
   - `assets/`: Rarely needed

6) **Test scripts**: If adding scripts, test locally with appropriate environment variables set

# Common Usage Patterns

## Local Directory Analysis
```bash
# Basic AST analysis
python ast_builder.py /path/to/codebase

# With LLM summaries
python ast_builder.py /path/to/codebase --summarize

# Export to JSON
python ast_builder.py /path/to/codebase --summarize --json output.json
```

## GitHub Repository Analysis
```bash
# Requires GITHUB_TOKEN environment variable
export GITHUB_TOKEN='your_token_here'
export OPENAI_API_KEY='your_key_here'  # Optional

# Analyze repository
python main.py repo-name --owner username --branch main -o output.json
```

# Key Data Structures

## FileNode
- path, code_summary, dependency_summary, imports
- classes: List[ClassNode]
- functions: List[FunctionNode] (top-level only)

## ClassNode
- name, lineno, end_lineno, code, code_summary, dependency_summary
- inward_dependencies: List[str]
- methods: List[FunctionNode]

## FunctionNode
- name, lineno, end_lineno, code, code_summary, dependency_summary
- inward_dependencies: List[str] (what this uses)
- outward_dependencies: List[str] (what uses this)
- class_name: Optional[str] (if method)

# Development Guidelines

- **Stable foundation**: Build on `ast_builder.py` for new local analysis features
- **GitHub workflows**: Extend `main.py` for repository-based features
- **ASCII-only**: Keep all code and docs ASCII-only
- **Lightweight comments**: Comment only non-obvious logic
- **No destructive git**: Avoid force pushes, resets, etc.
- **Testing**: No pytest suite yet; test manually or add targeted tests

# SKILL.md Template (minimal)
```
---
name: <skill-name>
description: <what it does + when to trigger, specific to mcp-coding-agent>
---

# Usage
- What problems this skill solves in this repo.
- When to invoke it (match triggers).
- Key steps (1-2-3) and any scripts/references to load.

# Resources
- scripts/<file> — what it does, how to run.
- references/<file> — when to read.
```

# Packaging/Delivery
- Keep files ASCII-only. No extra READMEs/CHANGELOGs.  
- If packaging is needed, zip the skill folder as `<name>.skill` mirroring structure (no special tooling required here).  
- Remind users to restart Codex after installing the packaged skill.
