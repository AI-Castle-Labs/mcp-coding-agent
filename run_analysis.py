#!/usr/bin/env python3
"""
GitHub Codebase Analyzer - Interactive Terminal Experience
A beautiful, user-friendly terminal interface for analyzing any GitHub repository.
Now with markdown reports and interactive Q&A!
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

# Add paths for imports
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir / "src"))
sys.path.insert(0, str(parent_dir.parent / "github-analyzer"))

# API keys from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# ANSI color codes for beautiful terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Background colors
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_CYAN = '\033[46m'


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_banner():
    """Print a beautiful ASCII banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║   {Colors.WHITE}🔍 GITHUB CODEBASE ANALYZER{Colors.CYAN}                                 ║
    ║   {Colors.DIM}Powered by AST Analysis & LLM Summaries{Colors.CYAN}{Colors.BOLD}                    ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)


def print_section(title, icon="📦"):
    """Print a section header"""
    width = 60
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'─' * width}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}  {icon} {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─' * width}{Colors.END}\n")


def print_step(step_num, total, message):
    """Print a step indicator"""
    progress = f"[{step_num}/{total}]"
    print(f"{Colors.CYAN}{Colors.BOLD}{progress}{Colors.END} {Colors.WHITE}{message}{Colors.END}")


def print_success(message):
    """Print success message"""
    print(f"  {Colors.GREEN}✓{Colors.END} {message}")


def print_warning(message):
    """Print warning message"""
    print(f"  {Colors.YELLOW}⚠{Colors.END} {message}")


def print_error(message):
    """Print error message"""
    print(f"  {Colors.RED}✗{Colors.END} {message}")


def print_info(message):
    """Print info message"""
    print(f"  {Colors.BLUE}ℹ{Colors.END} {message}")


def print_progress_bar(current, total, width=40, label="Progress"):
    """Print a progress bar"""
    if total == 0:
        return
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    percent = current / total * 100
    print(f"\r  {Colors.CYAN}{label}: [{bar}] {percent:.0f}%{Colors.END}", end='', flush=True)
    if current == total:
        print()


def get_file_icon(path):
    """Get an appropriate icon for the file type"""
    path_lower = path.lower()
    
    if 'test' in path_lower or 'spec' in path_lower:
        return "🧪"
    if path_lower.endswith('main.py') or path_lower.endswith('app.py') or path_lower.endswith('run.py'):
        return "🚀"
    if 'config' in path_lower or 'settings' in path_lower or 'env' in path_lower:
        return "⚙️"
    if 'model' in path_lower or 'schema' in path_lower or 'database' in path_lower or 'db' in path_lower:
        return "📊"
    if 'route' in path_lower or 'api' in path_lower or 'endpoint' in path_lower or 'view' in path_lower:
        return "🌐"
    if 'util' in path_lower or 'helper' in path_lower or 'common' in path_lower:
        return "🔧"
    if 'service' in path_lower or 'handler' in path_lower or 'controller' in path_lower:
        return "⚡"
    if 'auth' in path_lower or 'security' in path_lower or 'permission' in path_lower:
        return "🔐"
    if 'agent' in path_lower or 'llm' in path_lower or 'ai' in path_lower or 'crew' in path_lower:
        return "🤖"
    if 'task' in path_lower or 'job' in path_lower or 'worker' in path_lower or 'celery' in path_lower:
        return "📋"
    if '__init__' in path:
        return "📁"
    if 'cli' in path_lower or 'command' in path_lower:
        return "💻"
    if 'middleware' in path_lower:
        return "🔄"
    if 'log' in path_lower:
        return "📝"
    return "📄"


def print_file_card(file_info, index):
    """Print a beautiful file info card"""
    path = file_info.get('path', 'Unknown')
    classes = file_info.get('classes', [])
    functions = file_info.get('functions', [])
    imports = file_info.get('imports', [])
    
    num_classes = len(classes) if isinstance(classes, list) else classes
    num_functions = len(functions) if isinstance(functions, list) else functions
    num_imports = len(imports) if isinstance(imports, list) else imports
    
    icon = get_file_icon(path)
    
    print(f"""
  {Colors.BOLD}{Colors.WHITE}{icon} {path}{Colors.END}
  {Colors.DIM}├── Classes: {Colors.CYAN}{num_classes}{Colors.DIM}  │  Functions: {Colors.GREEN}{num_functions}{Colors.DIM}  │  Imports: {Colors.YELLOW}{num_imports}{Colors.END}""")


def print_summary_card(title, summary, icon="💡"):
    """Print a summary in a nice card format"""
    if not summary:
        return
    
    max_width = 70
    words = str(summary).split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + 1 <= max_width:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    print(f"\n  {Colors.BOLD}{icon} {title}{Colors.END}")
    print(f"  {Colors.DIM}{'─' * 50}{Colors.END}")
    for line in lines[:3]:
        print(f"  {Colors.WHITE}{line}{Colors.END}")
    if len(lines) > 3:
        print(f"  {Colors.DIM}... (truncated){Colors.END}")


def print_class_details(cls_info):
    """Print class details beautifully"""
    if isinstance(cls_info, dict):
        name = cls_info.get('name', 'Unknown')
        methods = cls_info.get('methods', [])
        code_summary = cls_info.get('code_summary')
        dep_summary = cls_info.get('dependency_summary')
    else:
        return
    
    print(f"\n    {Colors.BOLD}{Colors.HEADER}🏛️  class {name}{Colors.END}")
    print(f"    {Colors.DIM}Methods: {len(methods)}{Colors.END}")
    
    if code_summary:
        summary_text = str(code_summary)[:100]
        if len(str(code_summary)) > 100:
            summary_text += "..."
        print(f"    {Colors.GREEN}📝 {summary_text}{Colors.END}")
    
    if dep_summary:
        dep_text = str(dep_summary)[:100]
        if len(str(dep_summary)) > 100:
            dep_text += "..."
        print(f"    {Colors.YELLOW}🔗 {dep_text}{Colors.END}")
    
    if isinstance(methods, list):
        for method in methods[:3]:
            if isinstance(method, dict):
                method_name = method.get('name', 'Unknown')
                method_summary = method.get('code_summary', '')
                print(f"      {Colors.CYAN}├── {method_name}(){Colors.END}")
                if method_summary:
                    short_summary = str(method_summary)[:60]
                    if len(str(method_summary)) > 60:
                        short_summary += "..."
                    print(f"      {Colors.DIM}│   {short_summary}{Colors.END}")
        
        if len(methods) > 3:
            print(f"      {Colors.DIM}└── ... and {len(methods) - 3} more methods{Colors.END}")


def print_function_details(func_info):
    """Print function details beautifully"""
    if isinstance(func_info, dict):
        name = func_info.get('name', 'Unknown')
        code_summary = func_info.get('code_summary')
        inward_deps = func_info.get('inward_dependencies', [])
    else:
        return
    
    print(f"\n    {Colors.BOLD}{Colors.GREEN}⚡ def {name}(){Colors.END}")
    
    if code_summary:
        summary_text = str(code_summary)[:100]
        if len(str(code_summary)) > 100:
            summary_text += "..."
        print(f"    {Colors.WHITE}   {summary_text}{Colors.END}")
    
    if inward_deps and isinstance(inward_deps, list):
        deps_str = ", ".join(str(d) for d in inward_deps[:5])
        if len(inward_deps) > 5:
            deps_str += f" +{len(inward_deps) - 5} more"
        print(f"    {Colors.DIM}   Dependencies: {deps_str}{Colors.END}")


def interactive_menu():
    """Show interactive menu"""
    print(f"\n{Colors.BOLD}{Colors.WHITE}What would you like to do?{Colors.END}\n")
    print(f"  {Colors.CYAN}[1]{Colors.END} 🔍 Analyze a GitHub repository (with AI summaries)")
    print(f"  {Colors.CYAN}[2]{Colors.END} 📊 Quick scan (no AI summaries - faster)")
    print(f"  {Colors.CYAN}[3]{Colors.END} 💬 Ask questions about analyzed code")
    print(f"  {Colors.CYAN}[4]{Colors.END} 📖 View previous analysis report")
    print(f"  {Colors.CYAN}[5]{Colors.END} ❌ Exit")
    print()
    
    choice = input(f"{Colors.BOLD}{Colors.WHITE}Enter your choice (1-5): {Colors.END}").strip()
    return choice


def get_repo_info():
    """Get repository info from user with helpful prompts"""
    print(f"\n{Colors.BOLD}{Colors.WHITE}📦 Enter Repository Details{Colors.END}")
    print(f"{Colors.DIM}  (Press Enter to use default values){Colors.END}\n")
    
    owner = input(f"  {Colors.CYAN}GitHub Owner/Org:{Colors.END} ").strip()
    if not owner:
        print(f"  {Colors.DIM}(Using default: ashcastelinocs124){Colors.END}")
        owner = "ashcastelinocs124"
    
    repo = input(f"  {Colors.CYAN}Repository Name:{Colors.END} ").strip()
    if not repo:
        print(f"  {Colors.DIM}(Using default: VentureBot){Colors.END}")
        repo = "VentureBot"
    
    branch = input(f"  {Colors.CYAN}Branch (default: main):{Colors.END} ").strip()
    if not branch:
        branch = "main"
    
    print()
    return owner, repo, branch


def run_analysis(owner, repo, branch, summarize=True):
    """Run the actual analysis with beautiful output"""
    
    try:
        if 'discord_pr_bot' not in sys.modules:
            discord_pr_bot = type(sys)('discord_pr_bot')
            discord_pr_bot.run_discord_analyzer = lambda *args, **kwargs: None
            sys.modules['discord_pr_bot'] = discord_pr_bot
        
        if 'velocity_agent' not in sys.modules:
            velocity_agent = type(sys)('velocity_agent')
            velocity_agent.VelocityComplexityAgent = type('VelocityComplexityAgent', (), {})
            velocity_agent.print_velocity_complexity_score = lambda *args, **kwargs: None
            sys.modules['velocity_agent'] = velocity_agent
        
        from second_builder import AstBuilder, FileNode
        from devanalyzer import githubanalyzer
    except ImportError as e:
        print_error(f"Failed to import required modules: {e}")
        print_info("Make sure you're running from the mcp-coding-agent directory")
        return None
    
    print_section(f"Analyzing: {owner}/{repo}", "🔬")
    
    print_step(1, 5, "Connecting to GitHub...")
    time.sleep(0.3)
    
    try:
        github_analyzer = githubanalyzer()
        github_analyzer.owner = owner
    except Exception as e:
        print_error(f"Failed to initialize GitHub analyzer: {e}")
        return None
    
    if not github_analyzer.token:
        print_error("GitHub token not set!")
        print_info("Please set GITHUB_TOKEN environment variable:")
        print(f"  {Colors.DIM}export GITHUB_TOKEN='your_token_here'{Colors.END}")
        return None
    
    print_success("Connected to GitHub API")
    
    print_step(2, 5, f"Fetching Python files from '{branch}' branch...")
    time.sleep(0.2)
    
    try:
        python_files = github_analyzer.get_repo_files(repo, path="", branch=branch, file_extension=".py")
    except Exception as e:
        print_error(f"Failed to fetch files: {e}")
        print_info("Check if the repository and branch exist")
        return None
    
    if not python_files:
        print_error(f"No Python files found in {owner}/{repo}")
        print_info("Make sure the repository contains .py files")
        return None
    
    print_success(f"Found {len(python_files)} Python files")
    
    print_step(3, 5, "Initializing AST builder...")
    time.sleep(0.2)
    
    api_key = OPENAI_API_KEY
    if summarize and not api_key:
        print_warning("OPENAI_API_KEY not set. Running without AI summaries.")
        summarize = False
    
    try:
        ast_builder = AstBuilder(openai_api_key=api_key if summarize else "")
    except Exception as e:
        print_error(f"Failed to initialize AST builder: {e}")
        return None
    
    if summarize:
        print_success("AI summarization enabled")
    else:
        print_info("Running in quick mode (no AI summaries)")
    
    print_step(4, 5, "Building AST structure...")
    print()
    
    file_nodes = []
    total_files = len(python_files)
    errors = 0
    
    for idx, file_info in enumerate(python_files, 1):
        file_path = file_info["path"]
        print_progress_bar(idx, total_files, label="Analyzing")
        
        try:
            content = github_analyzer.get_file_content(repo, file_path, branch)
        except Exception:
            errors += 1
            continue
        
        if not content:
            continue
        
        try:
            file_node = ast_builder.build_file_ast(
                source_code=content,
                file_path=file_path,
                summarize=summarize
            )
            if file_node:
                file_nodes.append(file_node)
        except Exception as e:
            errors += 1
            continue
    
    if errors > 0:
        print_warning(f"Skipped {errors} files due to errors")
    print_success(f"Processed {len(file_nodes)} files successfully")
    
    print_step(5, 5, "Generating analysis report...")
    time.sleep(0.3)
    
    output = {
        "repository": f"{owner}/{repo}",
        "branch": branch,
        "analyzed_at": datetime.now().isoformat(),
        "total_files": len(file_nodes),
        "files": [file_node.to_dict() for file_node in file_nodes]
    }
    
    print_success("Analysis complete!")
    
    return output


def generate_markdown_report(results, output_path=None):
    """Generate a beautiful markdown report for viewing in IDE"""
    if not results:
        return None
    
    repo = results.get('repository', 'Unknown')
    branch = results.get('branch', 'main')
    files = results.get('files', [])
    analyzed_at = results.get('analyzed_at', datetime.now().isoformat())
    
    # Calculate stats
    total_classes = 0
    total_functions = 0
    total_imports = 0
    
    for f in files:
        classes = f.get('classes', [])
        functions = f.get('functions', [])
        imports = f.get('imports', [])
        
        total_classes += len(classes) if isinstance(classes, list) else classes
        total_functions += len(functions) if isinstance(functions, list) else functions
        total_imports += len(imports) if isinstance(imports, list) else imports
    
    md = []
    md.append(f"# 🔍 Codebase Analysis Report")
    md.append(f"")
    md.append(f"## 📦 Repository: `{repo}`")
    md.append(f"")
    md.append(f"| Property | Value |")
    md.append(f"|----------|-------|")
    md.append(f"| **Branch** | `{branch}` |")
    md.append(f"| **Analyzed** | {analyzed_at[:19].replace('T', ' ')} |")
    md.append(f"| **Files** | {len(files)} |")
    md.append(f"| **Classes** | {total_classes} |")
    md.append(f"| **Functions** | {total_functions} |")
    md.append(f"| **Imports** | {total_imports} |")
    md.append(f"")
    md.append(f"---")
    md.append(f"")
    md.append(f"## 📊 Summary Statistics")
    md.append(f"")
    md.append(f"```")
    md.append(f"📁 Total Files Analyzed:    {len(files):>6}")
    md.append(f"🏛️  Total Classes:           {total_classes:>6}")
    md.append(f"⚡ Total Functions:          {total_functions:>6}")
    md.append(f"📦 Total Imports:            {total_imports:>6}")
    md.append(f"```")
    md.append(f"")
    md.append(f"---")
    md.append(f"")
    
    # Sort files by importance
    def get_importance(x):
        classes = x.get('classes', [])
        functions = x.get('functions', [])
        c = len(classes) if isinstance(classes, list) else classes
        f = len(functions) if isinstance(functions, list) else functions
        return c + f
    
    files_sorted = sorted(files, key=get_importance, reverse=True)
    
    md.append(f"## 📁 File Analysis")
    md.append(f"")
    
    for file_info in files_sorted:
        path = file_info.get('path', 'Unknown')
        classes = file_info.get('classes', [])
        functions = file_info.get('functions', [])
        imports = file_info.get('imports', [])
        code_summary = file_info.get('code_summary', '')
        dep_summary = file_info.get('dependency_summary', '')
        
        icon = get_file_icon(path)
        num_classes = len(classes) if isinstance(classes, list) else classes
        num_functions = len(functions) if isinstance(functions, list) else functions
        num_imports = len(imports) if isinstance(imports, list) else imports
        
        md.append(f"### {icon} `{path}`")
        md.append(f"")
        md.append(f"| Metric | Count |")
        md.append(f"|--------|-------|")
        md.append(f"| Classes | {num_classes} |")
        md.append(f"| Functions | {num_functions} |")
        md.append(f"| Imports | {num_imports} |")
        md.append(f"")
        
        if code_summary:
            md.append(f"#### 📝 Code Summary")
            md.append(f"")
            md.append(f"> {code_summary}")
            md.append(f"")
        
        if dep_summary:
            md.append(f"#### 🔗 Dependencies")
            md.append(f"")
            md.append(f"> {dep_summary}")
            md.append(f"")
        
        # Classes
        if isinstance(classes, list) and classes:
            md.append(f"#### 🏛️ Classes")
            md.append(f"")
            for cls in classes:
                if isinstance(cls, dict):
                    cls_name = cls.get('name', 'Unknown')
                    cls_summary = cls.get('code_summary', '')
                    cls_deps = cls.get('dependency_summary', '')
                    methods = cls.get('methods', [])
                    
                    md.append(f"<details>")
                    md.append(f"<summary><strong>{cls_name}</strong> ({len(methods)} methods)</summary>")
                    md.append(f"")
                    
                    if cls_summary:
                        md.append(f"**Summary:** {cls_summary}")
                        md.append(f"")
                    
                    if cls_deps:
                        md.append(f"**Dependencies:** {cls_deps}")
                        md.append(f"")
                    
                    if isinstance(methods, list) and methods:
                        md.append(f"**Methods:**")
                        for method in methods:
                            if isinstance(method, dict):
                                m_name = method.get('name', 'Unknown')
                                m_summary = method.get('code_summary', '')
                                if m_summary:
                                    md.append(f"- `{m_name}()` - {m_summary[:100]}{'...' if len(str(m_summary)) > 100 else ''}")
                                else:
                                    md.append(f"- `{m_name}()`")
                        md.append(f"")
                    
                    md.append(f"</details>")
                    md.append(f"")
        
        # Functions
        if isinstance(functions, list) and functions:
            md.append(f"#### ⚡ Functions")
            md.append(f"")
            for func in functions:
                if isinstance(func, dict):
                    func_name = func.get('name', 'Unknown')
                    func_summary = func.get('code_summary', '')
                    inward_deps = func.get('inward_dependencies', [])
                    
                    md.append(f"<details>")
                    md.append(f"<summary><strong>{func_name}()</strong></summary>")
                    md.append(f"")
                    
                    if func_summary:
                        md.append(f"**Summary:** {func_summary}")
                        md.append(f"")
                    
                    if inward_deps and isinstance(inward_deps, list):
                        deps_str = ", ".join(f"`{d}`" for d in inward_deps[:10])
                        if len(inward_deps) > 10:
                            deps_str += f" +{len(inward_deps) - 10} more"
                        md.append(f"**Uses:** {deps_str}")
                        md.append(f"")
                    
                    md.append(f"</details>")
                    md.append(f"")
        
        md.append(f"---")
        md.append(f"")
    
    # Footer
    md.append(f"")
    md.append(f"---")
    md.append(f"")
    md.append(f"*Generated by GitHub Codebase Analyzer*")
    
    content = "\n".join(md)
    
    # Save to file
    if output_path is None:
        safe_repo = repo.replace("/", "_").replace("\\", "_")
        output_path = parent_dir / f"{safe_repo}_REPORT.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path


def ask_question_about_code(results, question):
    """Use LLM to answer questions about the analyzed codebase"""
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not configured. Cannot answer questions."
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        return "Error: openai package not installed. Run: pip install openai"
    except Exception as e:
        return f"Error initializing OpenAI client: {e}"
    
    # Build context from analysis
    repo = results.get('repository', 'Unknown')
    files = results.get('files', [])
    
    context_parts = []
    context_parts.append(f"Repository: {repo}")
    context_parts.append(f"Total Files: {len(files)}")
    context_parts.append("")
    
    for file_info in files:
        path = file_info.get('path', 'Unknown')
        code_summary = file_info.get('code_summary', '')
        dep_summary = file_info.get('dependency_summary', '')
        classes = file_info.get('classes', [])
        functions = file_info.get('functions', [])
        
        context_parts.append(f"## File: {path}")
        if code_summary:
            context_parts.append(f"Purpose: {code_summary}")
        if dep_summary:
            context_parts.append(f"Dependencies: {dep_summary}")
        
        if isinstance(classes, list):
            for cls in classes:
                if isinstance(cls, dict):
                    cls_name = cls.get('name', '')
                    cls_summary = cls.get('code_summary', '')
                    context_parts.append(f"  - Class {cls_name}: {cls_summary}")
        
        if isinstance(functions, list):
            for func in functions:
                if isinstance(func, dict):
                    func_name = func.get('name', '')
                    func_summary = func.get('code_summary', '')
                    context_parts.append(f"  - Function {func_name}(): {func_summary}")
        
        context_parts.append("")
    
    context = "\n".join(context_parts)
    
    # Limit context length
    max_context = 12000
    if len(context) > max_context:
        context = context[:max_context] + "\n... (truncated)"
    
    system_prompt = """You are a helpful assistant that answers questions about a Python codebase.
You have been given an analysis of the codebase including file summaries, class descriptions, and function descriptions.
Use this information to answer the user's question clearly and concisely.
If you don't have enough information to answer, say so.
Format your response in a clear, readable way using bullet points or code blocks where appropriate."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the codebase analysis:\n\n{context}\n\n---\n\nQuestion: {question}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting response: {e}"


def interactive_qa(results):
    """Interactive Q&A session about the codebase"""
    print_section("Ask Questions About the Codebase", "💬")
    
    print(f"{Colors.WHITE}I can answer questions about the analyzed repository.{Colors.END}")
    print(f"{Colors.DIM}Type 'exit' or 'q' to return to main menu.{Colors.END}")
    print()
    
    repo = results.get('repository', 'the codebase')
    
    while True:
        print(f"{Colors.CYAN}╭──────────────────────────────────────────────────────────────╮{Colors.END}")
        print(f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}Ask about {repo}:{Colors.END}")
        print(f"{Colors.CYAN}╰──────────────────────────────────────────────────────────────╯{Colors.END}")
        
        try:
            question = input(f"\n{Colors.GREEN}You:{Colors.END} ").strip()
        except EOFError:
            break
        
        if not question:
            continue
        
        if question.lower() in ['exit', 'q', 'quit', 'back']:
            print(f"\n{Colors.DIM}Returning to main menu...{Colors.END}")
            break
        
        print(f"\n{Colors.DIM}Thinking...{Colors.END}")
        
        answer = ask_question_about_code(results, question)
        
        print(f"\n{Colors.BLUE}🤖 Assistant:{Colors.END}")
        print(f"{Colors.WHITE}{answer}{Colors.END}")
        print()


def display_results(results, auto_save=False, repo_name="analysis"):
    """Display results in a beautiful format"""
    if not results:
        return
    
    print_section("📊 Analysis Results", "📈")
    
    files = results.get('files', [])
    
    total_classes = 0
    total_functions = 0
    total_imports = 0
    
    for f in files:
        classes = f.get('classes', [])
        functions = f.get('functions', [])
        imports = f.get('imports', [])
        
        total_classes += len(classes) if isinstance(classes, list) else classes
        total_functions += len(functions) if isinstance(functions, list) else functions
        total_imports += len(imports) if isinstance(imports, list) else imports
    
    print(f"""
  {Colors.BOLD}{Colors.WHITE}Repository:{Colors.END} {Colors.CYAN}{results.get('repository')}{Colors.END}
  {Colors.BOLD}{Colors.WHITE}Branch:{Colors.END}     {Colors.CYAN}{results.get('branch')}{Colors.END}
  
  {Colors.BOLD}📊 Statistics:{Colors.END}
  {Colors.DIM}┌────────────────────────────────────┐{Colors.END}
  {Colors.DIM}│{Colors.END}  📁 Files Analyzed: {Colors.CYAN}{Colors.BOLD}{results.get('total_files'):>10}{Colors.END}   {Colors.DIM}│{Colors.END}
  {Colors.DIM}│{Colors.END}  🏛️  Total Classes:  {Colors.GREEN}{Colors.BOLD}{total_classes:>10}{Colors.END}   {Colors.DIM}│{Colors.END}
  {Colors.DIM}│{Colors.END}  ⚡ Total Functions: {Colors.YELLOW}{Colors.BOLD}{total_functions:>10}{Colors.END}   {Colors.DIM}│{Colors.END}
  {Colors.DIM}│{Colors.END}  📦 Total Imports:   {Colors.HEADER}{Colors.BOLD}{total_imports:>10}{Colors.END}   {Colors.DIM}│{Colors.END}
  {Colors.DIM}└────────────────────────────────────┘{Colors.END}
""")
    
    print_section("📁 File Details", "📂")
    
    def get_importance(x):
        classes = x.get('classes', [])
        functions = x.get('functions', [])
        c = len(classes) if isinstance(classes, list) else classes
        f = len(functions) if isinstance(functions, list) else functions
        return c + f
    
    files_sorted = sorted(files, key=get_importance, reverse=True)
    
    for idx, file_info in enumerate(files_sorted[:10]):
        print_file_card(file_info, idx)
        
        code_summary = file_info.get('code_summary')
        if code_summary:
            print_summary_card("Code Summary", code_summary, "📝")
        
        dep_summary = file_info.get('dependency_summary')
        if dep_summary:
            print_summary_card("Dependencies", dep_summary, "🔗")
        
        classes = file_info.get('classes', [])
        if isinstance(classes, list):
            for cls in classes[:2]:
                print_class_details(cls)
        
        functions = file_info.get('functions', [])
        if isinstance(functions, list):
            for func in functions[:2]:
                print_function_details(func)
    
    if len(files_sorted) > 10:
        print(f"\n  {Colors.DIM}... and {len(files_sorted) - 10} more files{Colors.END}")
    
    # Save results
    safe_repo_name = repo_name.replace("/", "_").replace("\\", "_")
    
    # Always save JSON
    output_path = parent_dir / f"{safe_repo_name}_analysis.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print_success(f"JSON saved: {output_path}")
    
    # Generate markdown report
    md_path = generate_markdown_report(results)
    if md_path:
        print_success(f"Markdown report: {md_path}")
        print_info(f"Open the .md file in your IDE to view the formatted report!")


def load_previous_analysis():
    """Load a previous analysis from JSON file"""
    json_files = list(parent_dir.glob("*_analysis.json"))
    
    if not json_files:
        print_warning("No previous analysis files found.")
        return None
    
    print(f"\n{Colors.BOLD}{Colors.WHITE}📂 Available Analysis Files:{Colors.END}\n")
    
    for idx, f in enumerate(json_files, 1):
        print(f"  {Colors.CYAN}[{idx}]{Colors.END} {f.name}")
    
    print()
    
    try:
        choice = input(f"{Colors.BOLD}Select file (1-{len(json_files)}): {Colors.END}").strip()
        idx = int(choice) - 1
        if 0 <= idx < len(json_files):
            with open(json_files[idx], 'r', encoding='utf-8') as f:
                return json.load(f)
    except (ValueError, EOFError):
        pass
    
    print_warning("Invalid selection.")
    return None


def main():
    """Main entry point"""
    clear_screen()
    print_banner()
    
    print(f"{Colors.WHITE}Welcome to the GitHub Codebase Analyzer! 👋{Colors.END}")
    print(f"{Colors.DIM}I'll help you understand any Python codebase with AST analysis and AI summaries.{Colors.END}")
    
    current_results = None
    
    while True:
        choice = interactive_menu()
        
        if choice == "1":
            # Full analysis with summaries
            owner, repo, branch = get_repo_info()
            current_results = run_analysis(owner, repo, branch, summarize=True)
            if current_results:
                display_results(current_results, repo_name=repo)
        
        elif choice == "2":
            # Quick scan without summaries
            owner, repo, branch = get_repo_info()
            current_results = run_analysis(owner, repo, branch, summarize=False)
            if current_results:
                display_results(current_results, repo_name=repo)
        
        elif choice == "3":
            # Q&A mode
            if current_results:
                interactive_qa(current_results)
            else:
                print_warning("No analysis loaded. Please analyze a repository first or load a previous analysis.")
                loaded = load_previous_analysis()
                if loaded:
                    current_results = loaded
                    interactive_qa(current_results)
        
        elif choice == "4":
            # View previous analysis
            loaded = load_previous_analysis()
            if loaded:
                current_results = loaded
                display_results(current_results, auto_save=False, repo_name=current_results.get('repository', 'analysis').split('/')[-1])
        
        elif choice == "5":
            print(f"\n{Colors.GREEN}Thanks for using Codebase Analyzer! Goodbye! 👋{Colors.END}\n")
            break
        
        else:
            print_warning("Invalid choice. Please enter 1-5.")
            continue
        
        # Ask to continue
        try:
            cont = input(f"\n{Colors.BOLD}Press Enter to continue or 'q' to quit: {Colors.END}").strip().lower()
            if cont == 'q':
                print(f"\n{Colors.GREEN}Thanks for using Codebase Analyzer! Goodbye! 👋{Colors.END}\n")
                break
        except EOFError:
            break
        
        clear_screen()
        print_banner()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="GitHub Codebase Analyzer - Analyze any Python repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_analysis.py                          # Interactive mode
  python3 run_analysis.py --quick                  # Quick scan (default repo)
  python3 run_analysis.py --full                   # Full analysis with AI
  python3 run_analysis.py --ask "What does this repo do?"  # Ask a question
  python3 run_analysis.py --full --owner facebook --repo react
        """
    )
    parser.add_argument("--quick", action="store_true", help="Quick scan without AI summaries (faster)")
    parser.add_argument("--full", action="store_true", help="Full analysis with AI summaries")
    parser.add_argument("--owner", default="ashcastelinocs124", help="GitHub repository owner/organization")
    parser.add_argument("--repo", default="VentureBot", help="Repository name")
    parser.add_argument("--branch", default="main", help="Branch to analyze (default: main)")
    parser.add_argument("--ask", type=str, help="Ask a question about the codebase")
    args = parser.parse_args()
    
    if args.ask:
        # Q&A mode - load previous analysis or run new one
        clear_screen()
        print_banner()
        
        # Try to load existing analysis
        safe_repo = args.repo.replace("/", "_").replace("\\", "_")
        json_path = parent_dir / f"{safe_repo}_analysis.json"
        
        if json_path.exists():
            print(f"{Colors.WHITE}Loading previous analysis for {Colors.CYAN}{args.repo}{Colors.WHITE}...{Colors.END}")
            with open(json_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
        else:
            print(f"{Colors.WHITE}Running analysis for {Colors.CYAN}{args.owner}/{args.repo}{Colors.WHITE}...{Colors.END}")
            results = run_analysis(args.owner, args.repo, args.branch, summarize=True)
            if results:
                display_results(results, auto_save=True, repo_name=args.repo)
        
        if results:
            print(f"\n{Colors.GREEN}Question:{Colors.END} {args.ask}\n")
            print(f"{Colors.DIM}Thinking...{Colors.END}\n")
            answer = ask_question_about_code(results, args.ask)
            print(f"{Colors.BLUE}🤖 Answer:{Colors.END}")
            print(f"{Colors.WHITE}{answer}{Colors.END}\n")
    
    elif args.quick or args.full:
        # Non-interactive mode
        clear_screen()
        print_banner()
        print(f"{Colors.WHITE}Running automated analysis for {Colors.CYAN}{args.owner}/{args.repo}{Colors.WHITE}...{Colors.END}")
        results = run_analysis(args.owner, args.repo, args.branch, summarize=args.full)
        if results:
            display_results(results, auto_save=True, repo_name=args.repo)
        print(f"\n{Colors.GREEN}Analysis complete! 🎉{Colors.END}\n")
    else:
        # Interactive mode
        main()
