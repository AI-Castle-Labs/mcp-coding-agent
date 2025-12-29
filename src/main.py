"""
Main entry point for codebase AST analysis from GitHub repositories.

Workflow:
1. Read GitHub repository using devanalyzer
2. Extract Python files and their content
3. Build AST structure using second_builder
4. Extract dependencies using dependency_visitor
5. Generate LLM summaries (code_summary and dependency_summary)
6. Output the complete AST graph as JSON
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

# Add parent directories to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "github-analyzer"))
sys.path.insert(0, str(parent_dir / "mcp-coding-agent"))

# Import from second_builder
from second_builder import AstBuilder, FileNode, FunctionNode, ClassNode, _summarize_dependencies_with_llm
from dependency_visitor import DependencyVisitor

# Import githubanalyzer with error handling for optional dependencies
try:
    # Create dummy modules for optional dependencies
    import sys
    if 'discord_pr_bot' not in sys.modules:
        discord_pr_bot = type(sys)('discord_pr_bot')
        discord_pr_bot.run_discord_analyzer = lambda *args, **kwargs: None
        sys.modules['discord_pr_bot'] = discord_pr_bot
    
    if 'velocity_agent' not in sys.modules:
        velocity_agent = type(sys)('velocity_agent')
        velocity_agent.VelocityComplexityAgent = type('VelocityComplexityAgent', (), {})
        velocity_agent.print_velocity_complexity_score = lambda *args, **kwargs: None
        sys.modules['velocity_agent'] = velocity_agent
    
    from devanalyzer import githubanalyzer
except ImportError as e:
    print(f"Warning: Could not import githubanalyzer: {e}")
    print("Please ensure required dependencies are installed")
    raise


def build_codebase_ast_from_github(
    repo_name: str,
    owner: str = "AgenticAI-UIUC",
    branch: str = "main",
    summarize: bool = True,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main workflow: Read GitHub repo -> Extract files -> Build AST -> Extract dependencies -> Generate summaries
    
    Args:
        repo_name: Name of the GitHub repository
        owner: Repository owner (default: "AgenticAI-UIUC")
        branch: Branch to analyze (default: "main")
        summarize: Whether to generate LLM summaries (requires OPENAI_API_KEY)
        output_file: Optional path to save JSON output
        
    Returns:
        Dictionary containing the complete AST graph with summaries
    """
    print("=" * 80)
    print(f"🔍 Analyzing GitHub Repository: {owner}/{repo_name}")
    print("=" * 80)
    
    # Step 1: Initialize GitHub analyzer
    print("\n📡 Step 1: Connecting to GitHub...")
    
    # Initialize GitHub analyzer (it will use environment variable or fallback token)
    github_analyzer = githubanalyzer()
    github_analyzer.owner = owner  # Override owner if provided
    
    # Verify token is valid by checking if it's set
    if not github_analyzer.token or github_analyzer.token == "":
        print("❌ Error: GitHub token is not set!")
        print("\nTo fix this:")
        print("1. Create a GitHub Personal Access Token:")
        print("   - Go to: https://github.com/settings/tokens")
        print("   - Click 'Generate new token (classic)'")
        print("   - Select scopes: 'repo' (for private repos) or 'public_repo' (for public repos)")
        print("   - Copy the token")
        print("2. Set the environment variable:")
        print("   export GITHUB_TOKEN='your_token_here'")
        print("\nOr add it as fallback in github-analyzer/devanalyzer.py")
        return {}
    
    # Step 2: Get all Python files from repository
    print(f"📂 Step 2: Fetching Python files from {branch} branch...")
    python_files = github_analyzer.get_repo_files(
        repo_name, 
        path="", 
        branch=branch, 
        file_extension=".py"
    )
    
    if not python_files:
        print(f"❌ No Python files found in repository {repo_name}")
        return {}
    
    print(f"✅ Found {len(python_files)} Python file(s)")
    
    # Step 3: Initialize AST builder (using second_builder)
    print("\n🏗️  Step 3: Initializing AST builder (second_builder)...")
    api_key = os.environ.get("OPENAI_API_KEY", "") if summarize else ""
    ast_builder = AstBuilder(openai_api_key=api_key)
    
    # Check if summarization is available
    if summarize:
        if not api_key:
            print("⚠️  Warning: OPENAI_API_KEY not set. Summarization will be skipped.")
            summarize = False
        else:
            print("✅ LLM summarization enabled")
    
    # Step 4: Process each file and build AST
    print(f"\n🔨 Step 4: Building AST structure for {len(python_files)} file(s)...")
    file_nodes: List[FileNode] = []
    
    for idx, file_info in enumerate(python_files, 1):
        file_path = file_info["path"]
        print(f"  [{idx}/{len(python_files)}] Processing: {file_path}")
        
        # Get file content from GitHub
        content = github_analyzer.get_file_content(repo_name, file_path, branch)
        
        if not content:
            print(f"    ⚠️  Could not fetch content for {file_path}")
            continue
        
        try:
            # Build AST for this file
            file_node = ast_builder.build_file_ast(
                source_code=content,
                file_path=file_path,
                summarize=summarize
            )
            
            if file_node:
                file_nodes.append(file_node)
                print(f"    ✅ Extracted: {len(file_node.classes)} classes, {len(file_node.functions)} functions")
            else:
                print(f"    ⚠️  No AST structure generated for {file_path}")
                
        except SyntaxError as e:
            print(f"    ❌ Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"    ❌ Error processing {file_path}: {e}")
            import traceback
            traceback.print_exc()
    
    # Step 5: Build call graph and populate outward dependencies
    print(f"\n🔗 Step 5: Building call graph and extracting dependencies...")
    # Note: ast_build_call_graph expects file paths that can be read from disk
    # Since we're working with GitHub content, we'll use a simplified approach
    # that works with the dependency information we already have
    call_graph = _build_call_graph_from_dependencies(file_nodes)
    
    # Populate outward dependencies and update dependency summaries
    for file_node in file_nodes:
        file_id = file_node.path
        
        # Process top-level functions
        for func in file_node.functions:
            func_id = f"{file_id}:{func.name}"
            if func_id in call_graph:
                func.outward_dependencies = call_graph[func_id]
            
            # Update dependency summary if summarize is enabled
            if summarize and (func.inward_dependencies or func.outward_dependencies):
                func.dependency_summary = _summarize_dependencies_with_llm(
                    func.inward_dependencies, 
                    func.outward_dependencies, 
                    f"function {func.name}",
                    ast_builder.client if ast_builder.client else None
                )
        
        # Process methods
        for cls in file_node.classes:
            for method in cls.methods:
                func_id = f"{file_id}:{cls.name}.{method.name}"
                if func_id in call_graph:
                    method.outward_dependencies = call_graph[func_id]
                
                # Update dependency summary if summarize is enabled
                if summarize and (method.inward_dependencies or method.outward_dependencies):
                    method.dependency_summary = _summarize_dependencies_with_llm(
                        method.inward_dependencies, 
                        method.outward_dependencies, 
                        f"method {method.name} in class {cls.name}",
                        ast_builder.client if ast_builder.client else None
                    )
    
    print(f"✅ Dependency analysis complete")
    
    # Step 6: Convert to JSON-serializable format
    print(f"\n📊 Step 6: Generating output...")
    output = {
        "repository": f"{owner}/{repo_name}",
        "branch": branch,
        "total_files": len(file_nodes),
        "files": [file_node.to_dict() for file_node in file_nodes]
    }
    
    # Step 7: Output results
    if output_file:
        print(f"💾 Saving to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"✅ Output saved successfully")
    else:
        # Print summary to console
        print("\n" + "=" * 80)
        print("📋 AST Graph Summary")
        print("=" * 80)
        print(json.dumps({
            "repository": output["repository"],
            "branch": output["branch"],
            "total_files": output["total_files"],
            "total_classes": sum(len(fn.classes) for fn in file_nodes),
            "total_functions": sum(len(fn.functions) for fn in file_nodes),
            "files": [
                {
                    "path": fn.path,
                    "classes": len(fn.classes),
                    "functions": len(fn.functions),
                    "imports": len(fn.imports),
                    "has_code_summary": fn.code_summary is not None,
                    "has_dependency_summary": fn.dependency_summary is not None
                }
                for fn in file_nodes
            ]
        }, indent=2))
    
    return output






def _build_call_graph_from_dependencies(file_nodes: List[FileNode]) -> Dict[str, List[str]]:
    """
    Build a simplified call graph based on function names in dependencies.
    This works with GitHub-sourced content where we don't have file system access.
    
    Returns:
        Dict mapping "file_path:class_name.function_name" or "file_path:function_name" 
        to list of callers in same format.
    """
    call_graph: Dict[str, List[str]] = {}
    
    # First pass: collect all function identifiers
    for file_node in file_nodes:
        file_id = file_node.path
        
        # Top-level functions
        for func in file_node.functions:
            func_id = f"{file_id}:{func.name}"
            call_graph[func_id] = []
        
        # Methods
        for cls in file_node.classes:
            for method in cls.methods:
                func_id = f"{file_id}:{cls.name}.{method.name}"
                call_graph[func_id] = []
    
    # Second pass: find callers by matching function names in dependencies
    for file_node in file_nodes:
        file_id = file_node.path
        
        # Check each function's inward dependencies for function calls
        for func in file_node.functions:
            caller_id = f"{file_id}:{func.name}"
            for dep in func.inward_dependencies:
                # Check if this dependency matches any function name
                for other_file_node in file_nodes:
                    other_file_id = other_file_node.path
                    
                    # Check top-level functions
                    for other_func in other_file_node.functions:
                        if dep == other_func.name:
                            callee_id = f"{other_file_id}:{other_func.name}"
                            if caller_id != callee_id and caller_id not in call_graph.get(callee_id, []):
                                call_graph[callee_id].append(caller_id)
                    
                    # Check methods
                    for other_cls in other_file_node.classes:
                        for other_method in other_cls.methods:
                            # Match by method name or "Class.method" format
                            if dep == other_method.name or dep == f"{other_cls.name}.{other_method.name}":
                                callee_id = f"{other_file_id}:{other_cls.name}.{other_method.name}"
                                if caller_id != callee_id and caller_id not in call_graph.get(callee_id, []):
                                    call_graph[callee_id].append(caller_id)
        
        # Same for methods
        for cls in file_node.classes:
            for method in cls.methods:
                caller_id = f"{file_id}:{cls.name}.{method.name}"
                for dep in method.inward_dependencies:
                    for other_file_node in file_nodes:
                        other_file_id = other_file_node.path
                        
                        # Check top-level functions
                        for other_func in other_file_node.functions:
                            if dep == other_func.name:
                                callee_id = f"{other_file_id}:{other_func.name}"
                                if caller_id != callee_id and caller_id not in call_graph.get(callee_id, []):
                                    call_graph[callee_id].append(caller_id)
                        
                        # Check methods
                        for other_cls in other_file_node.classes:
                            for other_method in other_cls.methods:
                                if dep == other_method.name or dep == f"{other_cls.name}.{other_method.name}":
                                    callee_id = f"{other_file_id}:{other_cls.name}.{other_method.name}"
                                    if caller_id != callee_id and caller_id not in call_graph.get(callee_id, []):
                                        call_graph[callee_id].append(caller_id)
    
    return call_graph


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Analyze GitHub repository and generate AST graph with LLM summaries"
    )
    parser.add_argument(
        "repo_name",
        help="Name of the GitHub repository to analyze"
    )
    parser.add_argument(
        "--owner",
        default="AgenticAI-UIUC",
        help="Repository owner (default: AgenticAI-UIUC)"
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Branch to analyze (default: main)"
    )
    parser.add_argument(
        "--no-summarize",
        action="store_true",
        help="Skip LLM summarization (faster, but no summaries)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path for JSON (default: print to console)"
    )
    
    args = parser.parse_args()
    
    # Check for GitHub token (environment variable or fallback in devanalyzer)
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        # Mask token for display (show first 4 and last 4 chars)
        masked_token = github_token[:4] + "..." + github_token[-4:] if len(github_token) > 8 else "***"
        print(f"✅ Using GitHub token from environment: {masked_token}")
    else:
        # Token might be in devanalyzer.py as fallback, try to initialize and check
        try:
            github_analyzer = githubanalyzer()
            if github_analyzer.token and github_analyzer.token != "":
                masked_token = github_analyzer.token[:4] + "..." + github_analyzer.token[-4:] if len(github_analyzer.token) > 8 else "***"
                print(f"✅ Using GitHub token from devanalyzer.py: {masked_token}")
            else:
                print("❌ Error: GITHUB_TOKEN not found in environment or devanalyzer.py!")
                print("\nTo fix this:")
                print("1. Create a GitHub Personal Access Token:")
                print("   - Go to: https://github.com/settings/tokens")
                print("   - Click 'Generate new token (classic)'")
                print("   - Select scopes: 'repo' (for private repos) or 'public_repo' (for public repos)")
                print("   - Copy the token")
                print("2. Set the environment variable:")
                print("   export GITHUB_TOKEN='your_token_here'")
                print("\nOr add it as fallback in github-analyzer/devanalyzer.py")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error initializing GitHub analyzer: {e}")
            sys.exit(1)
    
    # Run the analysis
    result = build_codebase_ast_from_github(
        repo_name=args.repo_name,
        owner=args.owner,
        branch=args.branch,
        summarize=not args.no_summarize,
        output_file=args.output
    )
    
    if not result:
        print("\n❌ Analysis failed or no files found")
        sys.exit(1)
    
    print("\n✅ Analysis complete!")
    sys.exit(0)


if __name__ == "__main__":
    main()
