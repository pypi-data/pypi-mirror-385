#!/usr/bin/env python3
"""Comprehensive debugging and testing suite for CodeMind v2.0."""

import sys
import os
import traceback
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("🔍 CodeMind v2.0 - Comprehensive Testing & Debugging Suite")
print("=" * 80)
print()

# Phase 1: Import Test
print("Phase 1: Testing Imports")
print("-" * 80)

try:
    from codemind.workspace import (
        get_workspace_path, get_workspace_db, get_workspace_config,
        get_workspace_embedding, lazy_scan
    )
    print("✅ workspace module imported")
    
    from codemind.parsers import (
        parse_imports_ast, parse_calls_ast, parse_functions_ast,
        extract_purpose, extract_key_exports
    )
    print("✅ parsers module imported")
    
    from codemind.indexing import scan_project, _index_file_internal
    print("✅ indexing module imported")
    
    # Import all 20 tools
    from codemind.tools.search import (
        search_existing_code, check_functionality_exists,
        search_by_export, get_similar_files
    )
    print("✅ search tools imported (4)")
    
    from codemind.tools.context import (
        get_file_context, query_recent_changes,
        record_decision, list_all_decisions
    )
    print("✅ context tools imported (4)")
    
    from codemind.tools.dependencies import (
        find_dependencies, get_import_graph, get_call_tree
    )
    print("✅ dependencies tools imported (3)")
    
    from codemind.tools.analysis import (
        get_code_metrics_summary, find_configuration_inconsistencies
    )
    print("✅ analysis tools imported (2)")
    
    from codemind.tools.refactoring import (
        check_breaking_changes, find_usage_examples, get_test_coverage
    )
    print("✅ refactoring tools imported (3)")
    
    from codemind.tools.management import (
        force_reindex, index_file, find_todo_and_fixme, get_file_history_summary
    )
    print("✅ management tools imported (4)")
    
    print("\n✅ All 20 tools imported successfully!\n")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Phase 2: Workspace Infrastructure Test
print("\nPhase 2: Testing Workspace Infrastructure")
print("-" * 80)

try:
    # Test workspace path resolution
    ws_path = get_workspace_path(".")
    print(f"✅ Workspace path: {ws_path}")
    
    # Test config loading
    config = get_workspace_config(".")
    print(f"✅ Config loaded: {len(config)} settings")
    
    # Test database connection
    conn = get_workspace_db(".")
    cursor = conn.execute("SELECT COUNT(*) FROM files")
    file_count = cursor.fetchone()[0]
    print(f"✅ Database connected: {file_count} files indexed")
    
    # Test embedding model
    try:
        embedding_model = get_workspace_embedding(".")
        if embedding_model:
            print(f"✅ Embedding model loaded: {type(embedding_model).__name__}")
        else:
            print(f"⚠️  Embeddings disabled (sentence-transformers not available)")
    except Exception as e:
        print(f"⚠️  Embeddings disabled: {e}")
    
    print()
    
except Exception as e:
    print(f"\n❌ Workspace infrastructure test failed: {e}")
    traceback.print_exc()

# Phase 3: Ensure Database is Indexed
print("\nPhase 3: Ensuring Database is Indexed")
print("-" * 80)

try:
    cursor = conn.execute("SELECT COUNT(*) FROM files")
    file_count = cursor.fetchone()[0]
    
    if file_count == 0:
        print("⚠️  Database is empty, scanning workspace...")
        indexed_count = scan_project(".")
        print(f"✅ Indexed {indexed_count} files")
    else:
        print(f"✅ Database already has {file_count} files indexed")
    
    # Show sample of indexed files
    cursor = conn.execute("SELECT path, purpose FROM files LIMIT 5")
    print("\nSample indexed files:")
    for path, purpose in cursor.fetchall():
        purpose_short = (purpose[:50] + "...") if purpose and len(purpose) > 50 else (purpose or "N/A")
        print(f"  • {path}: {purpose_short}")
    
    print()
    
except Exception as e:
    print(f"\n❌ Indexing test failed: {e}")
    traceback.print_exc()

# Phase 4: Test Core Infrastructure Functions
print("\nPhase 4: Testing Core Functions")
print("-" * 80)

try:
    # Test AST parsing
    test_code = '''
def example_function(param1, param2):
    """Example function."""
    import os
    return param1 + param2
'''
    
    imports = parse_imports_ast(test_code)
    print(f"✅ parse_imports_ast: found {len(imports)} import(s)")
    
    funcs = parse_functions_ast(test_code)
    print(f"✅ parse_functions_ast: found {len(funcs)} function(s)")
    
    purpose = extract_purpose(test_code, "test.py")
    print(f"✅ extract_purpose: extracted purpose")
    
    exports = extract_key_exports(test_code, "test.py")
    print(f"✅ extract_key_exports: found {len(exports)} export(s)")
    
    print()
    
except Exception as e:
    print(f"\n❌ Core function test failed: {e}")
    traceback.print_exc()

# Phase 5: Test Each Tool Category
print("\nPhase 5: Testing All 20 Tools")
print("-" * 80)

def test_tool(name, func, *args, **kwargs):
    """Test a tool and return detailed results."""
    try:
        result = func(*args, **kwargs)
        
        # Check if result indicates an error
        if result.startswith("❌"):
            return "error", result[:100]
        elif result.startswith("⚠️"):
            return "warning", result[:100]
        else:
            # Count lines for success indicator
            lines = len(result.split('\n'))
            return "success", f"{lines} lines returned"
    
    except Exception as e:
        return "exception", f"{type(e).__name__}: {str(e)[:50]}"

results = {
    "success": [],
    "warning": [],
    "error": [],
    "exception": []
}

# Search & Discovery Tools
print("\n📋 Search & Discovery Tools (4):")
status, msg = test_tool("search_existing_code", search_existing_code, 
                       query="import", workspace_root=".", limit=2)
print(f"  {status:10s} search_existing_code: {msg}")
results[status].append("search_existing_code")

status, msg = test_tool("check_functionality_exists", check_functionality_exists,
                       feature_description="file indexing", workspace_root=".")
print(f"  {status:10s} check_functionality_exists: {msg}")
results[status].append("check_functionality_exists")

status, msg = test_tool("search_by_export", search_by_export,
                       export_name="get_workspace_path", workspace_root=".", limit=5)
print(f"  {status:10s} search_by_export: {msg}")
results[status].append("search_by_export")

status, msg = test_tool("get_similar_files", get_similar_files,
                       file_path="codemind.py", workspace_root=".", limit=3)
print(f"  {status:10s} get_similar_files: {msg}")
results[status].append("get_similar_files")

# Context & History Tools
print("\n📋 Context & History Tools (4):")
status, msg = test_tool("get_file_context", get_file_context,
                       file_path="codemind.py", workspace_root=".")
print(f"  {status:10s} get_file_context: {msg}")
results[status].append("get_file_context")

status, msg = test_tool("query_recent_changes", query_recent_changes,
                       workspace_root=".", hours=48)
print(f"  {status:10s} query_recent_changes: {msg}")
results[status].append("query_recent_changes")

status, msg = test_tool("record_decision", record_decision,
                       description="Test decision",
                       reasoning="Testing the tool",
                       workspace_root=".")
print(f"  {status:10s} record_decision: {msg}")
results[status].append("record_decision")

status, msg = test_tool("list_all_decisions", list_all_decisions,
                       workspace_root=".", limit=5)
print(f"  {status:10s} list_all_decisions: {msg}")
results[status].append("list_all_decisions")

# Dependency Analysis Tools
print("\n📋 Dependency Analysis Tools (3):")
status, msg = test_tool("find_dependencies", find_dependencies,
                       file_path="codemind.py", workspace_root=".")
print(f"  {status:10s} find_dependencies: {msg}")
results[status].append("find_dependencies")

status, msg = test_tool("get_import_graph", get_import_graph,
                       workspace_root=".", include_external=False)
print(f"  {status:10s} get_import_graph: {msg}")
results[status].append("get_import_graph")

status, msg = test_tool("get_call_tree", get_call_tree,
                       function_name="scan_project", workspace_root=".")
print(f"  {status:10s} get_call_tree: {msg}")
results[status].append("get_call_tree")

# Code Analysis Tools
print("\n📋 Code Analysis Tools (2):")
status, msg = test_tool("get_code_metrics_summary", get_code_metrics_summary,
                       workspace_root=".", detailed=False)
print(f"  {status:10s} get_code_metrics_summary: {msg}")
results[status].append("get_code_metrics_summary")

status, msg = test_tool("find_configuration_inconsistencies", find_configuration_inconsistencies,
                       workspace_root=".", include_examples=False)
print(f"  {status:10s} find_configuration_inconsistencies: {msg}")
results[status].append("find_configuration_inconsistencies")

# Refactoring Safety Tools
print("\n📋 Refactoring Safety Tools (3):")
status, msg = test_tool("check_breaking_changes", check_breaking_changes,
                       function_name="scan_project",
                       file_path="codemind/indexing.py",
                       workspace_root=".")
print(f"  {status:10s} check_breaking_changes: {msg}")
results[status].append("check_breaking_changes")

status, msg = test_tool("find_usage_examples", find_usage_examples,
                       function_name="get_workspace_path",
                       workspace_root=".", limit=3)
print(f"  {status:10s} find_usage_examples: {msg}")
results[status].append("find_usage_examples")

status, msg = test_tool("get_test_coverage", get_test_coverage,
                       file_path="codemind.py", workspace_root=".")
print(f"  {status:10s} get_test_coverage: {msg}")
results[status].append("get_test_coverage")

# Index Management Tools
print("\n📋 Index Management Tools (4):")
status, msg = test_tool("index_file", index_file,
                       file_path="codemind.py", workspace_root=".")
print(f"  {status:10s} index_file: {msg}")
results[status].append("index_file")

status, msg = test_tool("find_todo_and_fixme", find_todo_and_fixme,
                       workspace_root=".", tag_type="TODO", limit=10)
print(f"  {status:10s} find_todo_and_fixme: {msg}")
results[status].append("find_todo_and_fixme")

status, msg = test_tool("get_file_history_summary", get_file_history_summary,
                       file_path="README.md", workspace_root=".", days_back=30)
print(f"  {status:10s} get_file_history_summary: {msg}")
results[status].append("get_file_history_summary")

print(f"  {'skip':10s} force_reindex: (skipped to preserve data)")

# Summary
print("\n" + "=" * 80)
print("📊 Test Summary")
print("=" * 80)
print(f"✅ Success:   {len(results['success'])} tools")
print(f"⚠️  Warning:   {len(results['warning'])} tools")
print(f"❌ Error:     {len(results['error'])} tools")
print(f"🔥 Exception: {len(results['exception'])} tools")
print()

if results['exception']:
    print("🔥 Tools with exceptions:")
    for tool in results['exception']:
        print(f"  • {tool}")
    print()

if results['error']:
    print("❌ Tools with errors:")
    for tool in results['error']:
        print(f"  • {tool}")
    print()

if len(results['success']) >= 18:  # 20 - 2 (skipped force_reindex + expected warnings)
    print("🎉 EXCELLENT! Most tools working correctly!")
    sys.exit(0)
elif len(results['success']) >= 15:
    print("✅ GOOD! Majority of tools working, some need attention")
    sys.exit(0)
else:
    print("⚠️  NEEDS WORK! Multiple tools need debugging")
    sys.exit(1)
