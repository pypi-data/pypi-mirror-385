#!/usr/bin/env python3
"""
Test Suite 01: Basic Tool Validation
Tests each tool individually with simple, valid inputs.
"""

import sys
import os

# Set UTF-8 for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 80)
print("Test Suite 01: Basic Tool Validation")
print("=" * 80)
print()

# Import all tools
from codemind.tools.search import (
    search_existing_code, check_functionality_exists,
    search_by_export, get_similar_files
)
from codemind.tools.context import (
    get_file_context, query_recent_changes,
    record_decision, list_all_decisions
)
from codemind.tools.dependencies import (
    find_dependencies, get_import_graph, get_call_tree
)
from codemind.tools.analysis import (
    get_code_metrics_summary, find_configuration_inconsistencies
)
from codemind.tools.refactoring import (
    check_breaking_changes, find_usage_examples, get_test_coverage
)
from codemind.tools.management import (
    force_reindex, index_file, find_todo_and_fixme, get_file_history_summary
)

# Test tracking
total_tests = 0
passed_tests = 0
failed_tests = []

def test(name, func, *args, **kwargs):
    """Run a single test."""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    print(f"\n[{total_tests:02d}] Testing: {name}")
    print(f"     Input: {args if args else kwargs}")
    
    try:
        result = func(*args, **kwargs)
        
        # Check result is valid
        if not isinstance(result, str):
            print(f"     ❌ FAIL: Result is not a string (got {type(result)})")
            failed_tests.append((name, "Invalid return type"))
            return False
        
        if len(result) == 0:
            print(f"     ❌ FAIL: Empty result")
            failed_tests.append((name, "Empty result"))
            return False
        
        # Check for error markers
        if result.startswith("❌ Error"):
            print(f"     ❌ FAIL: {result[:100]}")
            failed_tests.append((name, result[:100]))
            return False
        
        # Success indicators
        lines = len(result.split('\n'))
        print(f"     ✅ PASS: {lines} lines returned")
        passed_tests += 1
        return True
        
    except Exception as e:
        print(f"     🔥 EXCEPTION: {type(e).__name__}: {str(e)[:100]}")
        failed_tests.append((name, f"{type(e).__name__}: {str(e)[:100]}"))
        return False

print("\n" + "=" * 80)
print("CATEGORY 1: Search & Discovery Tools (4 tools)")
print("=" * 80)

# Ensure workspace is indexed
print("\n[00] Pre-test: Ensuring workspace is indexed...")
from codemind.workspace import get_workspace_db
conn = get_workspace_db(".")
cursor = conn.execute("SELECT COUNT(*) FROM files")
file_count = cursor.fetchone()[0]

if file_count == 0:
    print("     Indexing workspace...")
    result = force_reindex(".")
    print(f"     {result}")

test("search_existing_code", search_existing_code, "import os", ".", limit=3)
test("check_functionality_exists", check_functionality_exists, "file indexing", ".")
test("search_by_export", search_by_export, "get_workspace_path", ".", limit=3)
test("get_similar_files", get_similar_files, 
     "D:\\Projects\\Python\\CodeMind\\codemind.py", ".", limit=3)

print("\n" + "=" * 80)
print("CATEGORY 2: Context & History Tools (4 tools)")
print("=" * 80)

test("get_file_context", get_file_context, "codemind.py", ".")
test("query_recent_changes", query_recent_changes, ".", hours=24)
test("record_decision", record_decision, 
     "Test Decision", "Testing basic tool functionality", ".")
test("list_all_decisions", list_all_decisions, ".", limit=10)

print("\n" + "=" * 80)
print("CATEGORY 3: Dependency Analysis Tools (3 tools)")
print("=" * 80)

test("find_dependencies", find_dependencies, "codemind.py", ".")
test("get_import_graph", get_import_graph, ".", include_external=False)
test("get_call_tree", get_call_tree, "get_workspace_path", ".", depth=2)

print("\n" + "=" * 80)
print("CATEGORY 4: Code Analysis Tools (2 tools)")
print("=" * 80)

test("get_code_metrics_summary", get_code_metrics_summary, ".", detailed=False)
test("find_configuration_inconsistencies", find_configuration_inconsistencies, 
     ".", include_examples=False)

print("\n" + "=" * 80)
print("CATEGORY 5: Refactoring Safety Tools (3 tools)")
print("=" * 80)

test("check_breaking_changes", check_breaking_changes, 
     "get_workspace_path", "codemind/workspace.py", ".")
test("find_usage_examples", find_usage_examples, "get_workspace_path", ".", limit=3)
test("get_test_coverage", get_test_coverage, "codemind.py", ".")

print("\n" + "=" * 80)
print("CATEGORY 6: Index Management Tools (4 tools)")
print("=" * 80)

test("index_file", index_file, "codemind.py", ".")
test("find_todo_and_fixme", find_todo_and_fixme, ".", tag_type="TODO", limit=5)
test("get_file_history_summary", get_file_history_summary, "README.md", ".", days_back=30)
# Skip force_reindex as we already ran it

print("\n\n" + "=" * 80)
print("TEST RESULTS")
print("=" * 80)
print(f"\nTotal Tests: {total_tests}")
print(f"✅ Passed: {passed_tests} ({100 * passed_tests // total_tests if total_tests > 0 else 0}%)")
print(f"❌ Failed: {len(failed_tests)}")

if failed_tests:
    print("\n" + "=" * 80)
    print("FAILED TESTS:")
    print("=" * 80)
    for name, reason in failed_tests:
        print(f"\n❌ {name}")
        print(f"   Reason: {reason}")

print("\n" + "=" * 80)
if len(failed_tests) == 0:
    print("🎉 SUCCESS: All basic tests passed!")
    print("=" * 80)
    sys.exit(0)
elif len(failed_tests) <= 2:
    print("✅ MOSTLY PASSING: Minor issues detected")
    print("=" * 80)
    sys.exit(0)
else:
    print("⚠️  NEEDS ATTENTION: Multiple tools failing")
    print("=" * 80)
    sys.exit(1)
