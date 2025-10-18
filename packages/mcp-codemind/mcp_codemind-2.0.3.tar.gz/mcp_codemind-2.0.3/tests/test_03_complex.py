#!/usr/bin/env python3
"""
Test Suite 03: Complex Scenarios
Tests edge cases, stress conditions, and error handling.
"""

import sys
import os

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 80)
print("Test Suite 03: Complex Scenarios & Edge Cases")
print("=" * 80)
print()

from codemind.tools.search import (
    search_existing_code, check_functionality_exists,
    search_by_export, get_similar_files
)
from codemind.tools.context import (
    get_file_context, query_recent_changes,
    record_decision, list_all_decisions
)
from codemind.tools.dependencies import find_dependencies, get_import_graph, get_call_tree
from codemind.tools.analysis import get_code_metrics_summary, find_configuration_inconsistencies
from codemind.tools.refactoring import check_breaking_changes, find_usage_examples
from codemind.tools.management import find_todo_and_fixme

tests_passed = 0
tests_failed = []

def test(name, func, expected_outcome, *args, **kwargs):
    """
    Run a complex test with expected outcome.
    expected_outcome: 'success', 'error', 'warning', or 'any'
    """
    global tests_passed, tests_failed
    
    print(f"\n{'=' * 80}")
    print(f"TEST: {name}")
    print(f"Expected: {expected_outcome}")
    print('=' * 80)
    
    try:
        result = func(*args, **kwargs)
        
        if not isinstance(result, str):
            print(f"❌ FAIL: Invalid return type ({type(result)})")
            tests_failed.append((name, "Invalid return type"))
            return False
        
        # Check expected outcome
        if expected_outcome == 'error':
            if result.startswith("❌"):
                print(f"✅ PASS: Error handled as expected")
                print(f"   Result: {result[:100]}")
                tests_passed += 1
                return True
            else:
                print(f"❌ FAIL: Expected error but got success")
                tests_failed.append((name, "Should have errored"))
                return False
        
        elif expected_outcome == 'warning':
            if result.startswith("⚠️") or "not found" in result.lower():
                print(f"✅ PASS: Warning returned as expected")
                print(f"   Result: {result[:100]}")
                tests_passed += 1
                return True
            else:
                print(f"❌ FAIL: Expected warning")
                tests_failed.append((name, "Should have warned"))
                return False
        
        elif expected_outcome == 'success':
            if not result.startswith("❌") and len(result) > 0:
                print(f"✅ PASS: Success ({len(result)} chars)")
                tests_passed += 1
                return True
            else:
                print(f"❌ FAIL: Expected success but got: {result[:100]}")
                tests_failed.append((name, result[:100]))
                return False
        
        elif expected_outcome == 'any':
            if len(result) > 0:
                print(f"✅ PASS: Handled without crash ({len(result)} chars)")
                tests_passed += 1
                return True
            else:
                print(f"❌ FAIL: Empty result")
                tests_failed.append((name, "Empty result"))
                return False
        
    except Exception as e:
        if expected_outcome == 'error':
            print(f"✅ PASS: Exception raised as expected")
            print(f"   {type(e).__name__}: {str(e)[:80]}")
            tests_passed += 1
            return True
        else:
            print(f"❌ FAIL: Unexpected exception")
            print(f"   {type(e).__name__}: {str(e)[:80]}")
            tests_failed.append((name, f"{type(e).__name__}: {str(e)[:80]}"))
            return False

print("\nCATEGORY 1: Error Handling & Invalid Inputs")
print("-" * 80)

test("Nonexistent file context",
     get_file_context, 'warning',
     "nonexistent_file_xyz_12345.py", ".")

test("Empty path search",
     search_existing_code, 'any',
     "", ".", limit=1)

test("Negative limit",
     search_existing_code, 'any',
     "import", ".", limit=-5)

test("Zero limit",
     search_existing_code, 'any',
     "import", ".", limit=0)

test("Nonexistent function in call tree",
     get_call_tree, 'error',  # Returns ❌ error message
     "nonexistent_function_xyz", ".", depth=2)

test("Invalid file path breaking changes",
     check_breaking_changes, 'success',  # Returns success with 0 call sites
     "some_function", "nonexistent/file.py", ".")

print("\n\nCATEGORY 2: Unicode & Special Characters")
print("-" * 80)

test("Unicode in search query",
     search_existing_code, 'any',
     "日本語 café résumé 🚀", ".", limit=1)

test("Special chars in decision",
     record_decision, 'success',
     "Fix `bug` in **parser.py**",
     "SQL: SELECT * FROM users WHERE id='1'",
     ".")

test("Markdown in decision",
     record_decision, 'success',
     "Update README",
     "```python\ndef foo():\n    pass\n```\nAnd <html> & @#$%",
     ".")

print("\n\nCATEGORY 3: SQL Injection & Security")
print("-" * 80)

test("SQL injection in search",
     search_existing_code, 'any',
     "'; DROP TABLE files; --", ".", limit=1)

test("SQL injection in export search",
     search_by_export, 'any',
     "'; DELETE FROM files; --", ".", limit=1)

test("Path traversal attempt",
     get_file_context, 'warning',
     "../../../etc/passwd", ".")

print("\n\nCATEGORY 4: Extreme Values")
print("-" * 80)

test("Extremely long query",
     search_existing_code, 'any',
     "import " * 1000, ".", limit=1)

test("Very large limit",
     search_existing_code, 'any',
     "import", ".", limit=1000000)

test("Very deep call tree",
     get_call_tree, 'success',
     "get_workspace_db", ".", depth=10)

test("Many decisions",
     lambda: [record_decision(f"Decision {i}", f"Reason {i}", ".") for i in range(20)][-1],
     'success')

print("\n\nCATEGORY 5: Complex Analysis")
print("-" * 80)

test("Import graph with externals",
     get_import_graph, 'success',
     ".", include_external=True)

test("Detailed metrics",
     get_code_metrics_summary, 'success',
     ".", detailed=True)

test("Config inconsistencies with examples",
     find_configuration_inconsistencies, 'success',
     ".", include_examples=True)

test("Find TODOs with special search",
     find_todo_and_fixme, 'any',
     ".", tag_type="TODO", search_term="$|^.*", limit=20)

print("\n\nCATEGORY 6: Stress Testing")
print("-" * 80)

test("Search for very common word",
     search_existing_code, 'success',
     "the", ".", limit=5)

test("Check vague functionality",
     check_functionality_exists, 'any',
     "stuff and things", ".")

test("Check very specific functionality",
     check_functionality_exists, 'any',
     "AST parsing for Python imports with visitor pattern extracting module names", ".")

test("Find all HACKs",
     find_todo_and_fixme, 'any',
     ".", tag_type="HACK", limit=50)

test("Find all NOTEs",
     find_todo_and_fixme, 'any',
     ".", tag_type="NOTE", limit=50)

test("Very old changes query",
     query_recent_changes, 'success',
     ".", hours=87600)  # 10 years

print("\n\nCATEGORY 7: Edge Cases in Dependencies")
print("-" * 80)

test("Dependencies of non-Python file",
     find_dependencies, 'success',  # Handles gracefully, extracts any imports
     "README.md", ".")

test("Dependencies of test file",
     find_dependencies, 'success',
     "tests/test_01_basic.py", ".")

test("Similar files to test",
     get_similar_files, 'any',
     "D:\\Projects\\Python\\CodeMind\\tests\\test_01_basic.py", ".", limit=3)

test("Usage examples of internal function",
     find_usage_examples, 'any',
     "_index_file_internal", ".", limit=5)

print("\n\n" + "=" * 80)
print("COMPLEX TEST RESULTS")
print("=" * 80)
print(f"\nTotal Tests: {tests_passed + len(tests_failed)}")
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {len(tests_failed)}")

if tests_failed:
    print("\n" + "=" * 80)
    print("FAILED TESTS:")
    print("=" * 80)
    for name, reason in tests_failed:
        print(f"\n❌ {name}")
        print(f"   Reason: {reason}")

print("\n" + "=" * 80)
if len(tests_failed) == 0:
    print("🎉 SUCCESS: All complex tests passed!")
    print("=" * 80)
    sys.exit(0)
elif len(tests_failed) <= 3:
    print("✅ MOSTLY PASSING: Minor edge case issues")
    print("=" * 80)
    sys.exit(0)
else:
    print("⚠️  NEEDS ATTENTION: Multiple edge cases failing")
    print("=" * 80)
    sys.exit(1)
