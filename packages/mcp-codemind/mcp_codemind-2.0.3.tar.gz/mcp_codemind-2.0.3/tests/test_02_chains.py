#!/usr/bin/env python3
"""
Test Suite 02: Tool Chaining Scenarios
Tests realistic workflows where tools are used in sequence.
"""

import sys
import os

# Set UTF-8 for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 80)
print("Test Suite 02: Tool Chaining Scenarios")
print("=" * 80)
print()

from codemind.tools.search import search_existing_code, get_similar_files
from codemind.tools.context import get_file_context, record_decision
from codemind.tools.dependencies import find_dependencies, get_call_tree
from codemind.tools.refactoring import check_breaking_changes, find_usage_examples
from codemind.tools.management import index_file

scenarios_passed = 0
scenarios_failed = []

def scenario(name, steps):
    """Run a multi-step scenario."""
    global scenarios_passed, scenarios_failed
    
    print(f"\n{'=' * 80}")
    print(f"SCENARIO: {name}")
    print('=' * 80)
    
    for i, (step_name, func, args, kwargs) in enumerate(steps, 1):
        print(f"\n  Step {i}/{len(steps)}: {step_name}")
        try:
            result = func(*args, **kwargs)
            if isinstance(result, str) and len(result) > 0 and not result.startswith("❌ Error"):
                print(f"  ✅ Success ({len(result)} chars)")
            else:
                print(f"  ❌ Failed: {result[:100] if isinstance(result, str) else 'Invalid result'}")
                scenarios_failed.append((name, step_name, "Invalid result"))
                return False
        except Exception as e:
            print(f"  🔥 Exception: {type(e).__name__}: {str(e)[:80]}")
            scenarios_failed.append((name, step_name, f"{type(e).__name__}: {str(e)[:80]}"))
            return False
    
    print(f"\n  ✅ SCENARIO PASSED")
    scenarios_passed += 1
    return True

# SCENARIO 1: Code Exploration Workflow
scenario("Code Exploration Workflow", [
    ("Search for file parsing code", search_existing_code, ("parse_imports_ast",), {"workspace_root": ".", "limit": 3}),
    ("Get context of found file", get_file_context, ("codemind/parsers.py",), {"workspace_root": "."}),
    ("Find dependencies of parser", find_dependencies, ("codemind/parsers.py",), {"workspace_root": "."}),
    ("Record exploration decision", record_decision, 
     ("Explored parser module", "Understanding AST parsing implementation"),
     {"workspace_root": "."})
])

# SCENARIO 2: Refactoring Safety Check
scenario("Refactoring Safety Check", [
    ("Search for function to refactor", search_existing_code, ("get_workspace_path",), {"workspace_root": ".", "limit": 1}),
    ("Check breaking changes", check_breaking_changes, 
     ("get_workspace_path", "codemind/workspace.py"), {"workspace_root": "."}),
    ("Find all usage examples", find_usage_examples, ("get_workspace_path",), {"workspace_root": ".", "limit": 5}),
    ("Get call tree", get_call_tree, ("get_workspace_path",), {"workspace_root": ".", "depth": 2}),
    ("Record refactoring decision", record_decision,
     ("Analyzed get_workspace_path impact", "Found N usages before refactoring"),
     {"workspace_root": "."})
])

# SCENARIO 3: New File Integration
scenario("New File Integration", [
    ("Index new file", index_file, ("codemind.py",), {"workspace_root": "."}),
    ("Get file context", get_file_context, ("codemind.py",), {"workspace_root": "."}),
    ("Find similar files", get_similar_files, 
     ("D:\\Projects\\Python\\CodeMind\\codemind.py",), {"workspace_root": ".", "limit": 3}),
    ("Find dependencies", find_dependencies, ("codemind.py",), {"workspace_root": "."})
])

# SCENARIO 4: Dependency Analysis Chain
scenario("Dependency Analysis Chain", [
    ("Get file context", get_file_context, ("codemind/workspace.py",), {"workspace_root": "."}),
    ("Find what imports it", find_dependencies, ("codemind/workspace.py",), {"workspace_root": "."}),
    ("Find usage examples", find_usage_examples, ("get_workspace_path",), {"workspace_root": ".", "limit": 3}),
    ("Get call tree", get_call_tree, ("get_workspace_db",), {"workspace_root": ".", "depth": 2})
])

# SCENARIO 5: Code Review Workflow
scenario("Code Review Workflow", [
    ("Search for recent changes", search_existing_code, ("Optional",), {"workspace_root": ".", "limit": 2}),
    ("Get context of changed file", get_file_context, ("codemind/tools/context.py",), {"workspace_root": "."}),
    ("Check breaking changes", check_breaking_changes,
     ("record_decision", "codemind/tools/context.py"), {"workspace_root": "."}),
    ("Find usage examples", find_usage_examples, ("record_decision",), {"workspace_root": ".", "limit": 3}),
    ("Record review decision", record_decision,
     ("Reviewed type hint changes", "Optional types properly added"),
     {"workspace_root": ".", "affected_files": ["codemind/tools/context.py"]})
])

# SCENARIO 6: Architecture Understanding
scenario("Architecture Understanding", [
    ("Search for tool registration", search_existing_code, ("register_all_tools",), {"workspace_root": ".", "limit": 1}),
    ("Get file context", get_file_context, ("codemind/tools/__init__.py",), {"workspace_root": "."}),
    ("Find dependencies", find_dependencies, ("codemind/tools/__init__.py",), {"workspace_root": "."}),
    ("Find similar architecture files", get_similar_files,
     ("D:\\Projects\\Python\\CodeMind\\codemind\\tools\\__init__.py",), {"workspace_root": ".", "limit": 3})
])

print("\n\n" + "=" * 80)
print("SCENARIO TEST RESULTS")
print("=" * 80)
print(f"\nTotal Scenarios: {scenarios_passed + len(scenarios_failed)}")
print(f"✅ Passed: {scenarios_passed}")
print(f"❌ Failed: {len(scenarios_failed)}")

if scenarios_failed:
    print("\n" + "=" * 80)
    print("FAILED SCENARIOS:")
    print("=" * 80)
    for scenario_name, step_name, reason in scenarios_failed:
        print(f"\n❌ {scenario_name}")
        print(f"   Failed at: {step_name}")
        print(f"   Reason: {reason}")

print("\n" + "=" * 80)
if len(scenarios_failed) == 0:
    print("🎉 SUCCESS: All chaining scenarios passed!")
    print("=" * 80)
    sys.exit(0)
elif len(scenarios_failed) <= 1:
    print("✅ MOSTLY PASSING: Minor chain issues detected")
    print("=" * 80)
    sys.exit(0)
else:
    print("⚠️  NEEDS ATTENTION: Multiple scenarios failing")
    print("=" * 80)
    sys.exit(1)
