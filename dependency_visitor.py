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
        # #region agent log
        try:
            import json
            with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"FIX","location":"dependency_visitor.py:19","message":"DependencyVisitor __init__","data":{"initializing_attributes":True},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except (PermissionError, OSError):
            pass  # Skip logging if file is protected
        # #endregion
        self.imports: Set[str] = set()
        self.function_calls: Set[str] = set()
        self.class_references: Set[str] = set()
        self.attributes: Set[str] = set()  # Fixed: missing attribute initialization
        # #region agent log
        try:
            import json
            with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"FIX","location":"dependency_visitor.py:25","message":"DependencyVisitor initialized","data":{"has_attributes":hasattr(self,"attributes")},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except (PermissionError, OSError):
            pass  # Skip logging if file is protected
        # #endregion
    
    def visit_Import(self, node: ast.Import):  # Fixed: should be visit_Import (capital I)
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
            # #region agent log
            try:
                import json
                with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"FIX","location":"dependency_visitor.py:42","message":"before attributes.add","data":{"has_attributes":hasattr(self,"attributes"),"attr_name":node.func.attr},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except (PermissionError, OSError):
                pass  # Skip logging if file is protected
            # #endregion
            self.attributes.add(node.func.attr)
            # #region agent log
            try:
                import json
                with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"FIX","location":"dependency_visitor.py:47","message":"after attributes.add success","data":{"attributes_count":len(self.attributes)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except (PermissionError, OSError):
                pass  # Skip logging if file is protected
            # #endregion
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute):
        if isinstance(node.value, ast.Name):
            self.class_references.add(node.value.id)
        self.attributes.add(node.attr)
        self.generic_visit(node)
    
    def get_dependencies(self) -> List[str]:
        """
        Combine all dependencies into a single list.
        """
        deps = []
        deps.extend(sorted(self.imports))
        deps.extend(sorted(self.function_calls))
        deps.extend(sorted(self.class_references))
        deps.extend(sorted(self.attributes))  # Fixed: include attributes
        return deps
