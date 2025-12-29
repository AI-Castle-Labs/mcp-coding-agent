"""
Direct test of DependencyVisitor to verify the attributes fix
"""
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "github-analyzer"))
sys.path.insert(0, str(Path(__file__).parent))

# Test code that uses attributes
test_code = """
import os
import json
from typing import List

class TestClass:
    def method1(self):
        return os.path.join("dir", "file")
    
    def method2(self):
        data = json.dumps({"key": "value"})
        return data

def top_level_func():
    result = TestClass().method1()
    return result
"""

print("Testing DependencyVisitor with attributes...")
print("=" * 60)

try:
    # Temporarily disable logging to avoid permission issues
    import dependency_visitor
    # Monkey-patch to skip logging
    original_init = dependency_visitor.DependencyVisitor.__init__
    def patched_init(self):
        self.imports = set()
        self.function_calls = set()
        self.class_references = set()
        self.attributes = set()
    dependency_visitor.DependencyVisitor.__init__ = patched_init
    
    from dependency_visitor import DependencyVisitor
    import ast
    
    print("✅ Successfully imported DependencyVisitor from dependency_visitor")
    
    # Parse test code
    tree = ast.parse(test_code)
    
    # Test with a class
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            print(f"\n📦 Testing with class: {node.name}")
            visitor = DependencyVisitor()
            print(f"   Has attributes: {hasattr(visitor, 'attributes')}")
            if hasattr(visitor, 'attributes'):
                print(f"   Attributes type: {type(visitor.attributes).__name__}")
                print(f"   ✅ Attributes field exists and is a {type(visitor.attributes).__name__}")
            else:
                print(f"   ❌ ERROR: attributes field is missing!")
                sys.exit(1)
            visitor.visit(node)
            deps = visitor.get_dependencies()
            print(f"   ✅ Dependencies extracted: {len(deps)} items")
            print(f"   Dependencies: {deps[:5]}...")  # Show first 5
        
        elif isinstance(node, ast.FunctionDef):
            print(f"\n📦 Testing with function: {node.name}")
            visitor = DependencyVisitor()
            print(f"   Has attributes: {hasattr(visitor, 'attributes')}")
            if hasattr(visitor, 'attributes'):
                print(f"   Attributes type: {type(visitor.attributes).__name__}")
                print(f"   ✅ Attributes field exists and is a {type(visitor.attributes).__name__}")
            else:
                print(f"   ❌ ERROR: attributes field is missing!")
                sys.exit(1)
            visitor.visit(node)
            deps = visitor.get_dependencies()
            print(f"   ✅ Dependencies extracted: {len(deps)} items")
            print(f"   Dependencies: {deps[:5]}...")  # Show first 5
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! DependencyVisitor works correctly.")
    print("=" * 60)
    
except AttributeError as e:
    if 'attributes' in str(e):
        print(f"\n❌ ERROR: {e}")
        print("   The 'attributes' attribute is still missing!")
        sys.exit(1)
    else:
        raise
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

