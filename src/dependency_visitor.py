import ast
import os
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from openai import OpenAI



class DependencyVisitor(ast.NodeVisitor):
    """
    AST visitor to extract dependenies from a function or class
    """

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
    
    def get_dependencies(self) -> List[str]:
        """
        Combine all dependices
        """
        deps = []

        deps.extend(sorted(self.imports))
        deps.extend(sorted(self.function_calls))
        deps.extend(sorted(self.class_references))
        deps.extend(sorted(self.attributes))

        return deps


