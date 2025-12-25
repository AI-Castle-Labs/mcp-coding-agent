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
    summary_func: Optional[str] = None
    summary_class : Optional[str] = None
    overall_summary : Optional[str] = None
    inward_dependencies: List[str] = field(default_factory=list)  # What this function uses
    outward_dependencies: List[str] = field(default_factory=list)  # What uses this function
    class_name: Optional[str] = None  # If this is a method, which class it belongs to

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "code": self.code,
            "summary": self.summary,
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
    summary: Optional[str] = None
    inward_dependencies: List[str] = field(default_factory=list)  # What this class uses

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "code": self.code,
            "summary": self.summary,
            "inward_dependencies": self.inward_dependencies,
            "methods": [m.to_dict() for m in self.methods],
        }


@dataclass
class FileNode:
    """Top-level node: one per Python file."""

    path: str
    classes: List[ClassNode]
    functions: List[FunctionNode]  # top-level functions
    summary: Optional[str] = None
    imports: List[str] = field(default_factory=list)  # Module-level imports

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "summary": self.summary,
            "imports": self.imports,
            "classes": [c.to_dict() for c in self.classes],
            "functions": [f.to_dict() for f in self.functions],
        }


 
class AstBuilder(self):

    def __init__(self):

        self.api_key = ""
        self.client = OpenAI(api_key = self.api_key)
    
    

    def extract_class(
        self,
        node : node,
    ) -> FileNode:
        """
        Builds an AST structure for a single file for class with AI summaries
        
        Structure: FileNode -> [ClassNode -> FunctionNode]

        This focuses on both the classes and the code within it, which includes function
        
        """

        source = path.read_text(encoding = "utf-8")
        tree = ast.parse(source, filename = str(path))

        imports = self._extract_imports(tree)
        classes: List[ClassNode] = []
        class_function: List[FunctionNode] = []

        for node in tree.body:
            if isinstance(node, ast.class_func):
                func_visitor = DependencyVisitor()
                func_visitor.viist(item)
                func_deps = func_visitor.get_dependencies()

                return func_deps
                


    def extract_func(
        self,
        node,
    ) ->FileNode :
        """
        Builds an AST structure for a single file for func with AI summaries

        Structure: Filenode -> FunctionnODE
        """
        return 0 




    def build_file_ast(
        self,
        repo_link : repo,
    ) -> FileNode:
        tree = ast.parse(repo)
        self.imports = self._extract_imports(tree)

        classes: List[ClassNode] = []
        class_func: List[FunctionNode] = []

        func : List[FunctionNode] = []

        for node in tree.body:
            if instance(node, ast.ClassDef):
                self.extract_class(node)
            
            elif instance(node, ast.FunctionDef):
                self.extract_func(node)






    def _extract_imports(self,tree: ast.Ast) -> List[str]:
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
 





        