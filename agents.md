# Repository Overview
- Goal: analyze Python codebases by building an AST with dependency info and optional LLM summaries.
- Main implementation lives in `ast_builder.py`; it walks a directory, captures imports, classes, functions, and can call OpenAI for summaries.
- `dependency_visitor.py` is an older, incomplete visitor (missing `attributes` setup and `get_dependencies` logic); treat it as legacy.
- `second_builder.py` is a rough WIP (invalid `class AstBuilder(self):`, bad types, missing symbols); do not rely on it without a rewrite.
- `main.py` is currently a stub.

# Running the Tooling
- Standard entry point: `python ast_builder.py <root_dir> [--summarize] [--json output.json]`.
- Summaries require `OPENAI_API_KEY` and network access; skip `--summarize` if API access is unavailable/undesired.
- Outputs a printed summary; `--json` additionally writes the full AST structure to a file.

# Tests and Caveats
- `python test_dependency_visitor.py` is a print-style check that the visitor exposes an `attributes` set; the current `dependency_visitor.py` will need fixes for this to be meaningful.
- `python test_second_builder.py` tests the AST builder with GitHub repositories. Currently configured to test with VentureBot (`ashcastelinocs124/VentureBot`). Requires `devanalyzer/githubanalyzer` module and GitHub access with `GITHUB_TOKEN` configured.
- No pytest suite is configured; add targeted tests near new logic.

# Development Notes
- Prefer extending `ast_builder.py` for new features; its data classes (`FunctionNode`, `ClassNode`, `FileNode`) are the stable shapes.
- Keep edits ASCII-only and lightweight on comments; explain only non-obvious logic.
- Avoid destructive git commands; the repo may already be dirty.
