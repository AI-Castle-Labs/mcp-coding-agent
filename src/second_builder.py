import ast
import os
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from openai import OpenAI
from dependency_visitor import DependencyVisitor


@dataclass
class FunctionNode:
    """Represents a function or method in a Python file."""

    name: str
    lineno: int
    end_lineno: int
    code: str
    code_summary: Optional[str] = None  # Summary of what the code does
    dependency_summary: Optional[str] = None  # Summary of inward and outward dependencies
    summary_func: Optional[str] = None  # Deprecated
    summary_class : Optional[str] = None  # Deprecated
    overall_summary : Optional[str] = None  # Deprecated
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
    summary: Optional[str] = None  # Deprecated
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
    summary: Optional[str] = None  # Deprecated
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


class AstBuilder:
    """AST builder that can work with source code strings from GitHub."""

    def __init__(self, openai_api_key: Optional[str] = None):
        api_key = openai_api_key or os.environ.get("OPENAI_API_KEY", "")
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key) if api_key else None

    def build_file_ast(
        self,
        source_code: str,
        file_path: str,
        summarize: bool = False
    ) -> FileNode:
        """
        Build an AST structure for a single Python file from source code string.
        
        Args:
            source_code: The Python source code as a string
            file_path: Path/name of the file (for identification)
            summarize: Whether to generate LLM summaries (requires OPENAI_API_KEY)
        
        Returns:
            FileNode containing the AST structure
        """
        tree = ast.parse(source_code, filename=file_path)
        
        imports = self._extract_imports(tree)
        classes: List[ClassNode] = []
        top_level_functions: List[FunctionNode] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_node = self.extract_class(node, source_code, summarize)
                if class_node:
                    classes.append(class_node)

            elif isinstance(node, ast.FunctionDef):
                func_node = self.extract_func(node, source_code, summarize)
                if func_node:
                    top_level_functions.append(func_node)

        # Generate file-level summaries
        code_summary = None
        dependency_summary = None
        if summarize and self.client:
            code_summary = _summarize_code_with_llm(source_code, "file", self.client)
            dependency_summary = _summarize_dependencies_with_llm(
                imports, [], "file", self.client
            )

        return FileNode(
            path=file_path,
            code_summary=code_summary,
            dependency_summary=dependency_summary,
            summary=code_summary,  # For backward compatibility
            imports=imports,
            classes=classes,
            functions=top_level_functions,
        )

    def extract_class(
        self,
        node: ast.ClassDef,
        source: str,
        summarize: bool = False
    ) -> ClassNode:
        """
        Extract a class node with its methods and dependencies.
        
        Args:
            node: AST ClassDef node
            source: Source code string
            summarize: Whether to generate LLM summaries
        
        Returns:
            ClassNode with methods and dependencies
        """
        methods: List[FunctionNode] = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                func_visitor = DependencyVisitor()
                func_visitor.visit(item)
                func_deps = func_visitor.get_dependencies()
                
                func_code = _get_source_segment(source, item)
                code_summary = None
                if summarize and self.client:
                    code_summary = _summarize_code_with_llm(
                        func_code, 
                        f"method {item.name} in class {node.name}", 
                        self.client
                    )
                
                methods.append(
                    FunctionNode(
                        name=item.name,
                        lineno=item.lineno,
                        end_lineno=getattr(item, "end_lineno", item.lineno),
                        code=func_code,
                        code_summary=code_summary,
                        dependency_summary=None,  # Will be updated later with outward deps
                        inward_dependencies=func_deps,
                        class_name=node.name,
                    )
                )

        # Extract class-level dependencies
        class_visitor = DependencyVisitor()
        class_visitor.visit(node)
        class_deps = class_visitor.get_dependencies()
        
        class_code = _get_source_segment(source, node)
        code_summary = None
        dependency_summary = None
        if summarize and self.client:
            code_summary = _summarize_code_with_llm(class_code, f"class {node.name}", self.client)
            dependency_summary = _summarize_dependencies_with_llm(
                class_deps, [], f"class {node.name}", self.client
            )

        return ClassNode(
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

    def extract_func(
        self,
        node: ast.FunctionDef,
        source: str,
        summarize: bool = False
    ) -> FunctionNode:
        """
        Extract a function node with its dependencies.
        
        Args:
            node: AST FunctionDef node
            source: Source code string
            summarize: Whether to generate LLM summaries
        
        Returns:
            FunctionNode with dependencies
        """
        func_visitor = DependencyVisitor()
        func_visitor.visit(node)
        func_deps = func_visitor.get_dependencies()
        
        func_code = _get_source_segment(source, node)
        code_summary = None
        if summarize and self.client:
            code_summary = _summarize_code_with_llm(func_code, f"function {node.name}", self.client)
        
        return FunctionNode(
            name=node.name,
            lineno=node.lineno,
            end_lineno=getattr(node, "end_lineno", node.lineno),
            code=func_code,
            code_summary=code_summary,
            dependency_summary=None,  # Will be updated later with outward deps
            inward_dependencies=func_deps,
        )

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all imports from a module"""
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
