import ast
import os
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from openai import OpenAI


@dataclass
class FunctionNode:
    """Represents a function or method in a Python file."""

    name: str
    lineno: int
    end_lineno: int
    code: str
    code_summary: Optional[str] = None  # Summary of what the code does
    dependency_summary: Optional[str] = None  # Summary of inward and outward dependencies
    summary: Optional[str] = None  # Deprecated: kept for backward compatibility
    inward_dependencies: List[str] = field(default_factory=list)  # What this function uses
    outward_dependencies: List[str] = field(default_factory=list)  # What uses this function
    class_name: Optional[str] = None  # If this is a method, which class it belongs to

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "code": self.code,
            "code_summary": self.code_summary,
            "dependency_summary": self.dependency_summary,
            "summary": self.summary,  # Deprecated
            "inward_dependencies": self.inward_dependencies,
            "outward_dependencies": self.outward_dependencies,
            "class_name": self.class_name,
        }


@dataclass
class ClassNode:
    """Represents a class in a Python file, with its methods."""

    name: str
    lineno: int
    end_lineno: int
    code: str
    methods: List[FunctionNode]
    code_summary: Optional[str] = None  # Summary of what the code does
    dependency_summary: Optional[str] = None  # Summary of inward dependencies
    summary: Optional[str] = None  # Deprecated: kept for backward compatibility
    inward_dependencies: List[str] = field(default_factory=list)  # What this class uses

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "code": self.code,
            "code_summary": self.code_summary,
            "dependency_summary": self.dependency_summary,
            "summary": self.summary,  # Deprecated
            "inward_dependencies": self.inward_dependencies,
            "methods": [m.to_dict() for m in self.methods],
        }


@dataclass
class FileNode:
    """Top-level node: one per Python file."""

    path: str
    classes: List[ClassNode]
    functions: List[FunctionNode]  # top-level functions
    code_summary: Optional[str] = None  # Summary of what the code does
    dependency_summary: Optional[str] = None  # Summary of imports and dependencies
    summary: Optional[str] = None  # Deprecated: kept for backward compatibility
    imports: List[str] = field(default_factory=list)  # Module-level imports

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "code_summary": self.code_summary,
            "dependency_summary": self.dependency_summary,
            "summary": self.summary,  # Deprecated
            "imports": self.imports,
            "classes": [c.to_dict() for c in self.classes],
            "functions": [f.to_dict() for f in self.functions],
        }


def _get_source_segment(source: str, node: ast.AST) -> str:
    """
    Safely slice out the original source code for a node using lineno/end_lineno.
    Falls back to empty string if those attributes are missing.
    """
    lineno: Optional[int] = getattr(node, "lineno", None)
    end_lineno: Optional[int] = getattr(node, "end_lineno", None)
    if lineno is None or end_lineno is None:
        return ""

    lines = source.splitlines()
    # ast line numbers are 1-based
    start = max(lineno - 1, 0)
    end = min(end_lineno, len(lines))
    return "\n".join(lines[start:end])


class DependencyVisitor(ast.NodeVisitor):
    """AST visitor to extract dependencies from a function or class."""

    def __init__(self):
        self.imports: Set[str] = set()
        self.function_calls: Set[str] = set()
        self.class_references: Set[str] = set()
        self.attributes: Set[str] = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.add(node.module)
        for alias in node.names:
            self.imports.add(f"{node.module}.{alias.name}" if node.module else alias.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                self.class_references.add(node.func.value.id)
            self.attributes.add(node.func.attr)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if isinstance(node.value, ast.Name):
            self.class_references.add(node.value.id)
        self.attributes.add(node.attr)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            # Could be a function call or class reference
            pass
        self.generic_visit(node)

    def get_dependencies(self) -> List[str]:
        """Combine all dependencies into a single list."""
        deps = []
        deps.extend(sorted(self.imports))
        deps.extend(sorted(self.function_calls))
        deps.extend(sorted(self.class_references))
        return deps


def _extract_imports(tree: ast.AST) -> List[str]:
    """Extract all imports from a module."""
    imports: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
            for alias in node.names:
                imports.add(f"{node.module}.{alias.name}" if node.module else alias.name)
    return sorted(imports)


def _summarize_code_with_llm(code: str, context: str, openai_client: Optional[OpenAI] = None) -> Optional[str]:
    """
    Use LLM to summarize what a code chunk does.
    
    Args:
        code: The code to summarize
        context: Context like "function", "class", or "file"
        openai_client: Optional OpenAI client. If None, tries to get from env.
    
    Returns:
        Summary string or None if LLM unavailable
    """
    if not openai_client:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        openai_client = OpenAI(api_key=api_key)

    prompt = f"""Analyze this Python {context} and provide a concise summary (2-3 sentences) describing:
1. What it does
2. Its main purpose/responsibility
3. Key behavior or logic

Code:
```python
{code}
```

Summary:"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a code analysis assistant. Provide concise, technical summaries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM code summarization failed: {e}")
        return None


def _summarize_dependencies_with_llm(
    inward_deps: List[str], 
    outward_deps: List[str], 
    context: str,
    openai_client: Optional[OpenAI] = None
) -> Optional[str]:
    """
    Use LLM to summarize the dependencies of a code chunk.
    
    Args:
        inward_deps: List of dependencies this code uses (imports, function calls, etc.)
        outward_deps: List of functions/classes that use this code
        context: Context like "function", "class", or "file"
        openai_client: Optional OpenAI client. If None, tries to get from env.
    
    Returns:
        Summary string or None if LLM unavailable
    """
    if not openai_client:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        openai_client = OpenAI(api_key=api_key)

    inward_str = ", ".join(inward_deps[:20])  # Limit to first 20 for prompt size
    if len(inward_deps) > 20:
        inward_str += f" (and {len(inward_deps) - 20} more)"
    
    outward_str = ", ".join(outward_deps[:20]) if outward_deps else "none"
    if outward_deps and len(outward_deps) > 20:
        outward_str += f" (and {len(outward_deps) - 20} more)"

    prompt = f"""Analyze the dependencies of this Python {context} and provide a concise summary (2-3 sentences) describing:
1. What external dependencies it relies on (inward dependencies)
2. What other code depends on it (outward dependencies)
3. The nature of these dependencies (e.g., data processing, API calls, utility functions)

Inward dependencies (what this {context} uses): {inward_str if inward_deps else "none"}
Outward dependencies (what uses this {context}): {outward_str}

Summary:"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a code analysis assistant. Provide concise, technical summaries about code dependencies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM dependency summarization failed: {e}")
        return None


def _build_call_graph(file_nodes: List[FileNode]) -> Dict[str, List[str]]:
    """
    Build a call graph mapping function identifiers to lists of functions that call them.
    
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
    
    # Second pass: find callers by analyzing each function's calls
    for file_node in file_nodes:
        try:
            source = Path(file_node.path).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=file_node.path)
            
            class CallTracker(ast.NodeVisitor):
                def __init__(self, file_path: str, current_class: Optional[str], current_func: str):
                    self.file_path = file_path
                    self.current_class = current_class
                    self.current_func = current_func
                    self.caller_id = (
                        f"{file_path}:{current_class}.{current_func}" 
                        if current_class 
                        else f"{file_path}:{current_func}"
                    )
                
                def visit_Call(self, node: ast.Call):
                    # Extract called function name
                    called_func = None
                    called_class = None
                    
                    if isinstance(node.func, ast.Name):
                        # Direct function call: func_name()
                        called_func = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        # Method call: obj.method() or Class.method()
                        if isinstance(node.func.value, ast.Name):
                            called_class = node.func.value.id
                            called_func = node.func.attr
                        elif isinstance(node.func.value, ast.Attribute):
                            # Handle nested attributes like self.obj.method()
                            called_func = node.func.attr
                    
                    # Find matching function in call graph
                    if called_func:
                        for func_id in call_graph.keys():
                            # Match format: "file_path:class.func" or "file_path:func"
                            if func_id.endswith(f":{called_func}") or func_id.endswith(f":{called_class}.{called_func}"):
                                if self.caller_id not in call_graph[func_id]:
                                    call_graph[func_id].append(self.caller_id)
                    
                    self.generic_visit(node)
            
            # Track calls from each function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Find parent class if this is a method
                    parent_class = None
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef):
                            if node in parent.body:
                                parent_class = parent.name
                                break
                    
                    tracker = CallTracker(file_node.path, parent_class, node.name)
                    tracker.visit(node)
        except Exception as e:
            print(f"Error building call graph for {file_node.path}: {e}")
            continue
    
    return call_graph


def build_file_ast(
    path: Path, 
    summarize: bool = False, 
    openai_client: Optional[OpenAI] = None
) -> FileNode:
    """
    Build an AST structure for a single Python file with dependencies and optional LLM summaries.

    Structure: FileNode -> [ClassNode -> [FunctionNode], FunctionNode]
    
    Args:
        path: Path to Python file
        summarize: Whether to generate LLM summaries (requires OPENAI_API_KEY)
        openai_client: Optional OpenAI client for summarization
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    imports = _extract_imports(tree)
    classes: List[ClassNode] = []
    top_level_functions: List[FunctionNode] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            # Extract class dependencies
            class_visitor = DependencyVisitor()
            class_visitor.visit(node)
            class_deps = class_visitor.get_dependencies()
            
            # Collect methods inside the class
            methods: List[FunctionNode] = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    # Extract function dependencies
                    func_visitor = DependencyVisitor()
                    func_visitor.visit(item)
                    func_deps = func_visitor.get_dependencies()
                    
                    func_code = _get_source_segment(source, item)
                    code_summary = None
                    dependency_summary = None
                    if summarize:
                        code_summary = _summarize_code_with_llm(func_code, f"method {item.name} in class {node.name}", openai_client)
                        # Dependency summary will be generated later in build_codebase_ast after outward deps are populated
                        dependency_summary = None
                    
                    methods.append(
                        FunctionNode(
                            name=item.name,
                            lineno=item.lineno,
                            end_lineno=getattr(item, "end_lineno", item.lineno),
                            code=func_code,
                            code_summary=code_summary,
                            dependency_summary=dependency_summary,
                            summary=code_summary,  # For backward compatibility
                            inward_dependencies=func_deps,
                            class_name=node.name,
                        )
                    )

            class_code = _get_source_segment(source, node)
            code_summary = None
            dependency_summary = None
            if summarize:
                code_summary = _summarize_code_with_llm(class_code, f"class {node.name}", openai_client)
                dependency_summary = _summarize_dependencies_with_llm(
                    class_deps, [], f"class {node.name}", openai_client
                    )

            classes.append(
                ClassNode(
                    name=node.name,
                    lineno=node.lineno,
                    end_lineno=getattr(node, "end_lineno", node.lineno),
                    code=class_code,
                    code_summary=code_summary,
                    dependency_summary=dependency_summary,
                    summary=code_summary,  # For backward compatibility
                    inward_dependencies=class_deps,
                    methods=methods,
                )
            )

        elif isinstance(node, ast.FunctionDef):
            # Top-level function
            func_visitor = DependencyVisitor()
            func_visitor.visit(node)
            func_deps = func_visitor.get_dependencies()
            
            func_code = _get_source_segment(source, node)
            code_summary = None
            dependency_summary = None
            if summarize:
                code_summary = _summarize_code_with_llm(func_code, f"function {node.name}", openai_client)
                # Dependency summary will be generated later in build_codebase_ast after outward deps are populated
                dependency_summary = None
            
            top_level_functions.append(
                FunctionNode(
                    name=node.name,
                    lineno=node.lineno,
                    end_lineno=getattr(node, "end_lineno", node.lineno),
                    code=func_code,
                    code_summary=code_summary,
                    dependency_summary=dependency_summary,
                    summary=code_summary,  # For backward compatibility
                    inward_dependencies=func_deps,
                )
            )

    file_code = source
    code_summary = None
    dependency_summary = None
    if summarize:
        code_summary = _summarize_code_with_llm(file_code, "file", openai_client)
        # Summarize file-level dependencies (imports)
        dependency_summary = _summarize_dependencies_with_llm(
            imports, [], "file", openai_client
            )

    return FileNode(
        path=str(path),
        code_summary=code_summary,
        dependency_summary=dependency_summary,
        summary=code_summary,  # For backward compatibility
        imports=imports,
        classes=classes,
        functions=top_level_functions,
    )


def build_codebase_ast(
    root: str, 
    summarize: bool = False,
    openai_client: Optional[OpenAI] = None
) -> List[FileNode]:
    """
    Walk a directory tree and build an AST structure for all `.py` files with dependencies.

    Args:
        root: Root directory of the codebase.
        summarize: Whether to generate LLM summaries (requires OPENAI_API_KEY)
        openai_client: Optional OpenAI client for summarization

    Returns:
        List[FileNode]: one entry per Python file, each containing its classes
        and functions (with source code, dependencies, and optional summaries).
    """
    root_path = Path(root)
    file_nodes: List[FileNode] = []

    for py_path in root_path.rglob("*.py"):
        # Skip hidden/virtual-env directories by convention
        parts = set(py_path.parts)
        if any(p in {".git", "__pycache__", "venv", ".venv", "node_modules"} for p in parts):
            continue

        try:
            file_nodes.append(build_file_ast(py_path, summarize=summarize, openai_client=openai_client))
        except SyntaxError as e:
            # Log or collect errors if needed; for now we just skip invalid files
            print(f"Skipping {py_path} due to SyntaxError: {e}")
        except OSError as e:
            print(f"Skipping {py_path} due to read error: {e}")

    # Build call graph and populate outward dependencies
    call_graph = _build_call_graph(file_nodes)
    
    # Map function identifiers back to FunctionNode objects and update dependency summaries
    for file_node in file_nodes:
        file_id = file_node.path
        
        # Process top-level functions
        for func in file_node.functions:
            func_id = f"{file_id}:{func.name}"
            if func_id in call_graph:
                func.outward_dependencies = call_graph[func_id]
            
            # Update dependency summary if summarize is enabled (regenerate with outward deps now available)
            if summarize and (func.inward_dependencies or func.outward_dependencies):
                func.dependency_summary = _summarize_dependencies_with_llm(
                    func.inward_dependencies, func.outward_dependencies, f"function {func.name}", openai_client
                )
        
        # Process methods
        for cls in file_node.classes:
            for method in cls.methods:
                func_id = f"{file_id}:{cls.name}.{method.name}"
                if func_id in call_graph:
                    method.outward_dependencies = call_graph[func_id]
                
                # Update dependency summary if summarize is enabled (regenerate with outward deps now available)
                if summarize and (method.inward_dependencies or method.outward_dependencies):
                    method.dependency_summary = _summarize_dependencies_with_llm(
                        method.inward_dependencies, method.outward_dependencies, 
                        f"method {method.name} in class {cls.name}", openai_client
                    )

    return file_nodes


def build_codebase_ast_json(
    root: str, 
    summarize: bool = False,
    openai_client: Optional[OpenAI] = None
) -> Dict[str, Any]:
    """
    Convenience helper: same as build_codebase_ast but returns JSON-serializable dict.

    Structure:
    {
      "files": [
        {
          "path": "...",
          "summary": "...",
          "imports": [...],
          "classes": [
            {
              "name": "...",
              "summary": "...",
              "inward_dependencies": [...],
              "methods": [
                {
                  "name": "...", 
                  "code": "...",
                  "summary": "...",
                  "inward_dependencies": [...],
                  "outward_dependencies": [...]
                },
                ...
              ]
            },
            ...
          ],
          "functions": [...]
        },
        ...
      ]
    }
    
    Args:
        root: Root directory of the codebase
        summarize: Whether to generate LLM summaries
        openai_client: Optional OpenAI client for summarization
    """
    files = build_codebase_ast(root, summarize=summarize, openai_client=openai_client)
    return {"files": [f.to_dict() for f in files]}


if __name__ == "__main__":
    # Example usage: build AST with dependencies and optional LLM summaries
    import json
    import sys

    root_dir = "." if len(sys.argv) < 2 else sys.argv[1]
    summarize = "--summarize" in sys.argv or "-s" in sys.argv
    
    print(f"Building AST for: {root_dir}")
    if summarize:
        print("LLM summarization enabled (requires OPENAI_API_KEY)")
    
    ast_tree = build_codebase_ast(root_dir, summarize=summarize)
    
    # Print summary
    summary = {
        "file_count": len(ast_tree),
        "files": [
            {
                "path": f.path,
                "summary": f.summary[:100] + "..." if f.summary and len(f.summary) > 100 else f.summary,
                "imports_count": len(f.imports),
                "class_count": len(f.classes),
                "function_count": len(f.functions),
                "classes": [
                    {
                        "name": c.name,
                        "summary": c.summary[:80] + "..." if c.summary and len(c.summary) > 80 else c.summary,
                        "methods": len(c.methods),
                        "dependencies": c.inward_dependencies[:5],  # Show first 5
                    }
                    for c in f.classes[:2]  # Show first 2 classes
                ],
                "functions": [
                    {
                        "name": func.name,
                        "summary": func.summary[:80] + "..." if func.summary and len(func.summary) > 80 else func.summary,
                        "inward_deps": len(func.inward_dependencies),
                        "outward_deps": len(func.outward_dependencies),
                    }
                    for func in f.functions[:2]  # Show first 2 functions
                ],
            }
            for f in ast_tree[:3]  # Show first 3 files
        ],
    }
    print(json.dumps(summary, indent=2))
    
    # Optionally save full AST to JSON
    if "--json" in sys.argv:
        output_file = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv and len(sys.argv) > sys.argv.index("--json") + 1 else "ast_output.json"
        full_ast = build_codebase_ast_json(root_dir, summarize=summarize)
        with open(output_file, "w") as f:
            json.dump(full_ast, f, indent=2)
        print(f"\nFull AST saved to {output_file}")


