"""
Test script for second_builder.py that reads from a GitHub repo using devanalyzer.py
"""
import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "github-analyzer"))
sys.path.insert(0, str(parent_dir / "mcp-coding-agent"))

# Import modules
from second_builder import AstBuilder, FileNode
from devanalyzer import githubanalyzer


def test_second_builder_with_github():
    """
    Test second_builder.py by reading Python files from a GitHub repo using devanalyzer.py
    """
    print("=" * 60)
    print("Testing second_builder.py with GitHub repo")
    print("=" * 60)
    
    # Initialize GitHub analyzer
    github_analyzer = githubanalyzer()
    
    # Initialize AST builder
    ast_builder = AstBuilder()
    
    # Test with a specific repo and file
    # Using VentureBot repository for testing
    test_repo = github_analyzer.reponame[0] if github_analyzer.reponame else "VentureBot"
    test_owner = "ashcastelinocs124"  # VentureBot repository owner
    github_analyzer.owner = test_owner  # Set owner for VentureBot
    print(f"\n📦 Repository: {test_owner}/{test_repo}")
    
    # Get list of Python files in the repo
    print("\n🔍 Fetching Python files from repository...")
    python_files = github_analyzer.get_repo_files(test_repo, path="", branch="main", file_extension=".py")
    
    if not python_files:
        print("❌ No Python files found in repository")
        return False
    
    print(f"✅ Found {len(python_files)} Python file(s)")
    
    # Test with first few files (limit to 3 for testing)
    test_files = python_files[:3]
    
    results = []
    
    for file_info in test_files:
        file_path = file_info["path"]
        print(f"\n📄 Processing: {file_path}")
        
        # Get file content from GitHub
        content = github_analyzer.get_file_content(test_repo, file_path)
        
        if not content:
            print(f"  ⚠️  Could not fetch content for {file_path}")
            continue
        
        print(f"  ✅ Fetched {len(content)} characters")
        
        # Build AST using second_builder
        try:
            file_node = ast_builder.build_file_ast(
                source_code=content,
                file_path=file_path,
                summarize=False  # Set to True if you have OPENAI_API_KEY
            )
            
            # Print summary
            print(f"  📊 AST Summary:")
            print(f"     - Classes: {len(file_node.classes)}")
            print(f"     - Functions: {len(file_node.functions)}")
            print(f"     - Imports: {len(file_node.imports)}")
            
            if file_node.classes:
                print(f"     - First class: {file_node.classes[0].name} ({len(file_node.classes[0].methods)} methods)")
                if file_node.classes[0].methods:
                    first_method = file_node.classes[0].methods[0]
                    print(f"       - First method: {first_method.name}")
                    print(f"         Dependencies: {len(first_method.inward_dependencies)}")
            
            if file_node.functions:
                first_func = file_node.functions[0]
                print(f"     - First function: {first_func.name}")
                print(f"       Dependencies: {len(first_func.inward_dependencies)}")
            
            results.append({
                "file": file_path,
                "classes": len(file_node.classes),
                "functions": len(file_node.functions),
                "imports": len(file_node.imports),
                "status": "success"
            })
            
        except SyntaxError as e:
            print(f"  ❌ Syntax error parsing {file_path}: {e}")
            results.append({
                "file": file_path,
                "status": "syntax_error",
                "error": str(e)
            })
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            results.append({
                "file": file_path,
                "status": "error",
                "error": str(e)
            })
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(json.dumps(results, indent=2))
    
    success_count = sum(1 for r in results if r.get("status") == "success")
    print(f"\n✅ Successfully processed: {success_count}/{len(results)} files")
    
    return success_count > 0


def test_specific_file():
    """
    Test with a specific known file path
    """
    print("\n" + "=" * 60)
    print("Testing with specific file path")
    print("=" * 60)
    
    github_analyzer = githubanalyzer()
    ast_builder = AstBuilder()
    
    # Try to get a specific file - using VentureBot repository
    test_repo = github_analyzer.reponame[0] if github_analyzer.reponame else "VentureBot"
    test_owner = "ashcastelinocs124"  # VentureBot repository owner
    github_analyzer.owner = test_owner  # Set owner for VentureBot
    
    # Common Python file paths to try (VentureBot structure)
    test_paths = [
        "main.py",
        "services/api_gateway/app/main.py",
        "services/orchestrator/chat_orchestrator.py",
        "crewai-agents/src/venturebot_crew/main.py",
    ]
    
    for test_path in test_paths:
        print(f"\n🔍 Trying: {test_path}")
        content = github_analyzer.get_file_content(test_repo, test_path)
        
        if content:
            print(f"  ✅ Found file! ({len(content)} chars)")
            
            try:
                file_node = ast_builder.build_file_ast(content, test_path, summarize=False)
                print(f"  📊 Classes: {len(file_node.classes)}, Functions: {len(file_node.functions)}")
                
                # Show detailed structure
                if file_node.classes:
                    print(f"\n  📋 Classes:")
                    for cls in file_node.classes:
                        print(f"     - {cls.name} ({len(cls.methods)} methods)")
                        for method in cls.methods[:2]:  # Show first 2 methods
                            print(f"       • {method.name} (deps: {len(method.inward_dependencies)})")
                
                if file_node.functions:
                    print(f"\n  📋 Top-level Functions:")
                    for func in file_node.functions[:3]:  # Show first 3
                        print(f"     - {func.name} (deps: {len(func.inward_dependencies)})")
                
                return True
            except Exception as e:
                print(f"  ❌ Error: {e}")
        else:
            print(f"  ⚠️  File not found")
    
    return False


if __name__ == "__main__":
    print("🧪 Testing second_builder.py with GitHub integration\n")
    
    # Check for required environment variables
    if not os.environ.get("GITHUB_TOKEN"):
        print("⚠️  Warning: GITHUB_TOKEN not set. Some operations may fail.")
    
    # Run tests
    test1_passed = test_second_builder_with_github()
    test2_passed = test_specific_file()
    
    print("\n" + "=" * 60)
    if test1_passed or test2_passed:
        print("✅ Tests completed successfully!")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    print("=" * 60)

