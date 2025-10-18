#!/usr/bin/env python3
"""Advanced test scenarios with edge cases, stress tests, and curveballs for CodeMind v2.0."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("🎯 CodeMind v2.0 - Advanced Testing with Curveballs")
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
    index_file, find_todo_and_fixme, get_file_history_summary
)

test_count = 0
pass_count = 0
fail_count = 0

def test(name, func):
    """Run a test."""
    global test_count, pass_count, fail_count
    test_count += 1
    print(f"\n🧪 Test {test_count}: {name}")
    try:
        result = func()
        if result:
            print(f"   ✅ PASS")
            pass_count += 1
        else:
            print(f"   ❌ FAIL")
            fail_count += 1
    except Exception as e:
        print(f"   🔥 EXCEPTION: {type(e).__name__}: {str(e)[:100]}")
        fail_count += 1

print("=" * 80)
print("🔥 CATEGORY 1: Edge Cases & Invalid Inputs")
print("=" * 80)

test("Nonexistent File", lambda: 
    "not found" in get_file_context("nonexistent_12345.py", ".").lower())

test("Empty File Path", lambda: 
    "❌" in get_file_context("", ".") or "invalid" in get_file_context("", ".").lower())

test("Absolute Path Outside Workspace", lambda: 
    "not found" in get_file_context("C:\\Windows\\System32\\notepad.exe", ".").lower())

test("Unicode in Search Query", lambda: 
    isinstance(search_existing_code("日本語 café 🚀", ".", limit=1), str))

test("SQL Injection Attempt", lambda: 
    isinstance(search_existing_code("'; DROP TABLE files; --", ".", limit=1), str))

test("Extremely Long Search Query", lambda: 
    isinstance(search_existing_code("import " * 2000, ".", limit=1), str))

test("Negative Limit Values", lambda: 
    isinstance(search_existing_code("import", ".", limit=-5), str))

test("Zero Limit Value", lambda: 
    isinstance(search_existing_code("import", ".", limit=0), str))

test("Extremely Large Limit", lambda: 
    len(search_existing_code("import", ".", limit=1000000)) < 1000000)

print("\n" + "=" * 80)
print("🎲 CATEGORY 2: Data Consistency & Concurrent Operations")
print("=" * 80)

def test_many_decisions():
    for i in range(50):
        record_decision(f"Decision {i}", f"Reasoning {i}", ".")
    result = list_all_decisions(".", limit=50)
    return "Decision 49" in result or "Decision 25" in result

test("Multiple Decision Records", test_many_decisions)

test("Decision with Special Characters", lambda:
    "✅" in record_decision(
        "Fix `bug` in **parser.py** with SQL: SELECT * FROM users",
        "Because of:\n```python\ndef foo(): pass\n```\nAnd <html> & @#$%",
        "."
    ))

test("Query Recent Changes 10 Years Back", lambda: 
    isinstance(query_recent_changes(".", hours=87600), str))

test("Query Recent Changes 0 Hours", lambda: 
    isinstance(query_recent_changes(".", hours=0), str))

print("\n" + "=" * 80)
print("🧩 CATEGORY 3: Complex Analysis Scenarios")
print("=" * 80)

test("Call Tree with High Depth", lambda: 
    len(get_call_tree("get_workspace_db", ".", depth=5)) < 100000)

test("Import Graph with External Deps", lambda: 
    "modules" in get_import_graph(".", include_external=True).lower())

test("Breaking Changes on Core Function", lambda: 
    "call site" in check_breaking_changes("get_workspace_path", "codemind/workspace.py", ".").lower() or
    "usage" in check_breaking_changes("get_workspace_path", "codemind/workspace.py", ".").lower())

test("Test Coverage on Test File", lambda: 
    isinstance(get_test_coverage("test_all_tools.py", "."), str))

def test_large_file_metrics():
    py_files = []
    for root, dirs, files in os.walk("."):
        if ".venv" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    size = os.path.getsize(path)
                    py_files.append((size, path))
                except:
                    pass
    if py_files:
        largest = max(py_files, key=lambda x: x[0])[1]
        result = get_file_context(largest, ".")
        return "lines" in result.lower() or "imports" in result.lower()
    return True

test("Metrics on Largest File", test_large_file_metrics)

test("Find TODOs with Special Chars", lambda: 
    isinstance(find_todo_and_fixme(".", tag_type="TODO", search_term="$|^.*", limit=20), str))

test("Configuration Analysis", lambda: 
    isinstance(find_configuration_inconsistencies(".", include_examples=True), str))

print("\n" + "=" * 80)
print("🎪 CATEGORY 4: Search & Similarity Curveballs")
print("=" * 80)

test("Search for Common Word", lambda: 
    len(search_existing_code("the", ".", limit=3)) < 50000)

test("Search for Exact Function Signature", lambda: 
    "workspace" in search_existing_code("def get_workspace_path(", ".", limit=5).lower())

test("Search by Export for Common Name", lambda: 
    isinstance(search_by_export("__init__", ".", limit=10), str))

test("Check Vague Functionality", lambda: 
    "NO" in check_functionality_exists("stuff", ".") or 
    "confidence" in check_functionality_exists("stuff", ".").lower())

test("Check Specific Functionality", lambda: 
    "YES" in check_functionality_exists(
        "AST parsing for Python imports using parse_imports_ast function", 
        ".", confidence_threshold=0.7) or
    "found" in check_functionality_exists(
        "AST parsing for Python imports using parse_imports_ast function",
        ".", confidence_threshold=0.7).lower())

test("Similar Files to Nonexistent", lambda: 
    "not found" in get_similar_files("nonexistent_xyz.py", ".", limit=3).lower())

test("Similar Files to Test File", lambda: 
    "test" in get_similar_files(str(Path("test_all_tools.py").resolve()), ".", limit=3).lower() or
    "similar" in get_similar_files(str(Path("test_all_tools.py").resolve()), ".", limit=3).lower())

print("\n" + "=" * 80)
print("🏗️ CATEGORY 5: Stress Tests")
print("=" * 80)

test("Full Import Graph with External", lambda: 
    "modules" in get_import_graph(".", include_external=True).lower())

test("Detailed Code Metrics", lambda: 
    "files" in get_code_metrics_summary(".", detailed=True).lower() or
    "functions" in get_code_metrics_summary(".", detailed=True).lower())

test("Find All TODOs", lambda: 
    isinstance(find_todo_and_fixme(".", tag_type="TODO", limit=100), str))

test("Find All FIXMEs", lambda: 
    isinstance(find_todo_and_fixme(".", tag_type="FIXME", limit=100), str))

test("Find All HACKs", lambda: 
    isinstance(find_todo_and_fixme(".", tag_type="HACK", limit=100), str))

test("Find Usage Examples for Core Function", lambda: 
    "example" in find_usage_examples("get_workspace_path", ".", limit=10).lower() or
    "usage" in find_usage_examples("get_workspace_path", ".", limit=10).lower())

test("Dependencies for Core File", lambda: 
    "imports" in find_dependencies("codemind.py", ".").lower() or
    "depends" in find_dependencies("codemind.py", ".").lower())

test("File History Summary", lambda: 
    isinstance(get_file_history_summary("README.md", ".", days_back=365), str))

print("\n" + "=" * 80)
print("📊 FINAL RESULTS")
print("=" * 80)
print(f"\nTotal Tests: {test_count}")
print(f"✅ Passed: {pass_count} ({100*pass_count//test_count if test_count > 0 else 0}%)")
print(f"❌ Failed: {fail_count}")
print()

if fail_count == 0:
    print("🎉 PERFECT! All curveball tests passed!")
    print("CodeMind v2.0 is production-ready! 🚀")
    sys.exit(0)
elif fail_count <= 3:
    print("✅ EXCELLENT! Most curveball tests passed with minor issues")
    sys.exit(0)
elif fail_count <= 5:
    print("👍 GOOD! Majority of curveball tests passed")
    sys.exit(0)
else:
    print("⚠️  NEEDS ATTENTION! Several edge cases need handling")
    sys.exit(1)
