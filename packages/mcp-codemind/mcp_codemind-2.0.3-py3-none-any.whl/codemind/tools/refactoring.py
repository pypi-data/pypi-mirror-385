"""Refactoring and impact analysis tools for CodeMind."""

import re
import json
from pathlib import Path
from typing import Optional

from ..workspace import get_workspace_db, get_workspace_path, lazy_scan


def check_breaking_changes(function_name: str, file_path: str, workspace_root: str = ".") -> str:
    """
    Analyze impact of modifying a function/class signature.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User wants to rename/modify/refactor any function or class
    - User asks to change a function signature
    - User says "let's change...", "modify...", "rename...", "refactor..."
    - Before suggesting any code modifications to functions
    - User asks "what uses this function?"
    - Planning any code changes
    
    ALWAYS check this BEFORE suggesting refactoring changes!
    This prevents breaking existing code.
    
    Args:
        function_name: Name of function/class to analyze
        file_path: File containing the function (absolute or relative to workspace)
        workspace_root: Root directory of workspace (default: current directory)
    
    Returns:
    - Number of call sites
    - List of affected files
    - Severity rating (safe/moderate/dangerous)
    - Public API status
    """
    ws_path = get_workspace_path(workspace_root)
    conn = get_workspace_db(workspace_root)
    lazy_scan(workspace_root)
    
    result = [f"🔍 Breaking Change Analysis for '{function_name}':\n"]
    
    # Check if it's exported (public API)
    is_public = False
    cursor = conn.execute(
        "SELECT key_exports FROM files WHERE path LIKE ?",
        (f"%{file_path}%",)
    )
    row = cursor.fetchone()
    if row and row[0]:
        exports = json.loads(row[0])
        is_public = function_name in exports
    
    # Find all call sites
    call_sites = []
    cursor = conn.execute('SELECT path FROM files')
    
    for (path,) in cursor.fetchall():
        fpath = ws_path / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            # Find calls to this function
            pattern = rf'\b{re.escape(function_name)}\s*\('
            matches = list(re.finditer(pattern, content))
            
            if matches:
                # Get line numbers
                lines = content.split('\n')
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    # Get surrounding context
                    context_start = max(0, line_num - 2)
                    context_end = min(len(lines), line_num + 1)
                    context = '\n    '.join(lines[context_start:context_end])
                    
                    call_sites.append({
                        'file': path,
                        'line': line_num,
                        'context': context[:200]
                    })
        except:
            continue
    
    # Calculate severity
    num_sites = len(call_sites)
    if num_sites == 0:
        severity = "✅ SAFE"
        severity_desc = "No call sites found - safe to modify"
    elif num_sites <= 3:
        severity = "⚠️ LOW RISK"
        severity_desc = f"Only {num_sites} call sites - easy to fix"
    elif num_sites <= 10:
        severity = "⚠️ MODERATE RISK"
        severity_desc = f"{num_sites} call sites - needs careful review"
    else:
        severity = "🔴 HIGH RISK"
        severity_desc = f"{num_sites} call sites - major refactoring needed"
    
    # Build report
    result.append(f"🎯 **Function**: {function_name}")
    result.append(f"📁 **Defined in**: {file_path}")
    result.append(f"🌐 **Public API**: {'Yes' if is_public else 'No'}")
    result.append(f"🎯 **Severity**: {severity}")
    result.append(f"📊 **Call Sites**: {num_sites}")
    result.append(f"📝 **Assessment**: {severity_desc}\n")
    
    if call_sites:
        # Group by file
        by_file = {}
        for site in call_sites:
            by_file.setdefault(site['file'], []).append(site)
        
        result.append(f"📁 **Affected Files** ({len(by_file)} files):\n")
        
        for file, sites in sorted(by_file.items())[:10]:
            result.append(f"  • {file} ({len(sites)} occurrences)")
            for site in sites[:2]:
                result.append(f"    Line {site['line']}")
        
        if len(by_file) > 10:
            result.append(f"\n  ... and {len(by_file) - 10} more files")
    else:
        result.append("✅ No call sites found - safe to modify or remove")
    
    result.append(f"\n💡 Tip: Use get_call_tree() for detailed call flow analysis")
    
    return "\n".join(result)


def find_usage_examples(
    function_name: str,
    workspace_root: str = ".",
    file_path: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Find real usage examples of a function/class across the codebase.
    
    Args:
        function_name: Function or class name to find examples for
        workspace_root: Root directory of workspace (default: current directory)
        file_path: Optional file containing the function (helps filter)
        limit: Maximum number of examples (default: 5)
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks "how is [function] used?"
    - User asks "show me examples of [function]"
    - User wants to understand how to call a function
    - Before modifying function signature (see current usage)
    - User asks about parameter patterns or conventions
    - Learning how an API works in practice
    
    This provides real-world usage examples from the actual codebase.
    
    Returns:
        Examples with file, line number, and surrounding context
    """
    ws_path = get_workspace_path(workspace_root)
    conn = get_workspace_db(workspace_root)
    lazy_scan(workspace_root)
    
    result = [f"📚 Usage Examples for '{function_name}':\n"]
    
    examples = []
    cursor = conn.execute('SELECT path FROM files')
    
    # Skip the definition file if provided
    skip_file = file_path
    
    for (path,) in cursor.fetchall():
        if path == skip_file:
            continue  # Skip definition file, show usage elsewhere
        
        fpath = ws_path / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Find usage (not definition)
            pattern = rf'\b{re.escape(function_name)}\s*\('
            
            for i, line in enumerate(lines):
                # Skip if this is the definition line
                if re.match(rf'\s*(def|class)\s+{re.escape(function_name)}\b', line):
                    continue
                
                if re.search(pattern, line):
                    # Get surrounding context
                    context_start = max(0, i - 1)
                    context_end = min(len(lines), i + 2)
                    context_lines = lines[context_start:context_end]
                    
                    examples.append({
                        'file': path,
                        'line': i + 1,
                        'context': '\n'.join(context_lines),
                        'usage_line': line.strip()
                    })
                    
                    if len(examples) >= limit * 3:
                        break
        except:
            continue
        
        if len(examples) >= limit * 3:
            break
    
    if not examples:
        result.append(f"❌ No usage examples found for '{function_name}'")
        result.append(f"\nPossible reasons:")
        result.append(f"  • Function is defined but not yet used")
        result.append(f"  • Function name is incorrect")
        result.append(f"  • Files haven't been indexed yet")
        result.append(f"\n💡 Try: search_by_export('{function_name}') to verify it exists")
        return "\n".join(result)
    
    # Show top examples
    for i, ex in enumerate(examples[:limit], 1):
        result.append(f"\n**Example {i}**: {ex['file']}:{ex['line']}")
        result.append(f"```")
        result.append(ex['context'])
        result.append(f"```")
    
    if len(examples) > limit:
        result.append(f"\n... found {len(examples) - limit} more examples")
        result.append(f"(use limit parameter to see more)")
    
    result.append(f"\n💡 Found {min(limit, len(examples))} of {len(examples)} total usages")
    
    return "\n".join(result)


def get_test_coverage(file_path: str, workspace_root: str = ".") -> str:
    """
    Show test coverage for a specific file/module.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User wants to modify/refactor code (check if tested!)
    - User asks "is this tested?", "where are the tests?"
    - Before suggesting changes to critical code
    - User mentions "test coverage", "unit tests"
    - Risk assessment for changes
    - User asks "is it safe to change [file]?"
    
    This helps assess the safety of making changes to code.
    IMPORTANT: Check this before suggesting refactoring untested code.
    
    Args:
        file_path: File to check coverage for (absolute or relative to workspace)
        workspace_root: Root directory of workspace (default: current directory)
    
    Returns:
        Coverage estimate, test file locations, and recommendations
    """
    ws_path = get_workspace_path(workspace_root)
    conn = get_workspace_db(workspace_root)
    lazy_scan(workspace_root)
    
    result = [f"🧪 Test Coverage Analysis for '{file_path}':\n"]
    
    # Resolve file path
    if not Path(file_path).is_absolute():
        search_pattern = f"%{file_path}%"
    else:
        search_pattern = file_path
    
    # Find the file
    cursor = conn.execute('SELECT path FROM files WHERE path LIKE ?', (search_pattern,))
    row = cursor.fetchone()
    
    if not row:
        return f"❌ File not found: {file_path}"
    
    actual_path = row[0]
    file_name = Path(actual_path).stem
    
    # Search for test files
    test_patterns = [
        f"test_{file_name}.py",
        f"{file_name}_test.py",
        f"tests/test_{file_name}.py",
        f"test/test_{file_name}.py",
        f"**/test_{file_name}.py",
    ]
    
    test_files = []
    cursor = conn.execute('SELECT path FROM files')
    
    for (path,) in cursor.fetchall():
        if 'test' in path.lower() and file_name in path:
            test_files.append(path)
    
    # Analyze test files
    test_count = 0
    test_functions = []
    
    for test_file in test_files:
        try:
            content = (ws_path / test_file).read_text(encoding='utf-8', errors='ignore')
            # Count test functions
            tests = re.findall(r'def (test_\w+)\s*\(', content)
            test_count += len(tests)
            test_functions.extend(tests[:5])
        except:
            continue
    
    # Estimate coverage
    if test_count == 0:
        coverage = "❌ NO TESTS FOUND"
        coverage_desc = "High risk - no automated testing detected"
        recommendation = "🚨 Create tests before refactoring this file"
    elif test_count < 5:
        coverage = "🟡 LOW COVERAGE"
        coverage_desc = f"Only {test_count} test(s) found"
        recommendation = "⚠️ Add more tests for safer refactoring"
    elif test_count < 15:
        coverage = "🟢 MODERATE COVERAGE"
        coverage_desc = f"{test_count} tests found"
        recommendation = "✅ Reasonable coverage, refactor with caution"
    else:
        coverage = "✅ GOOD COVERAGE"
        coverage_desc = f"{test_count} tests found"
        recommendation = "✅ Well tested, safer to refactor"
    
    # Build report
    result.append(f"📊 **Coverage Level**: {coverage}")
    result.append(f"🧪 **Test Count**: {test_count}")
    result.append(f"📝 **Assessment**: {coverage_desc}")
    result.append(f"💡 **Recommendation**: {recommendation}\n")
    
    if test_files:
        result.append(f"📁 **Test Files** ({len(test_files)}):")
        for tf in test_files[:5]:
            result.append(f"  • {tf}")
        if len(test_files) > 5:
            result.append(f"  ... and {len(test_files) - 5} more")
    
    if test_functions:
        result.append(f"\n🔬 **Sample Tests**:")
        for func in test_functions[:5]:
            result.append(f"  • {func}()")
    
    if test_count == 0:
        result.append(f"\n💡 Consider creating: tests/test_{file_name}.py")
    
    result.append(f"\n📚 Note: This is a heuristic estimate based on test file naming patterns")
    
    return "\n".join(result)
