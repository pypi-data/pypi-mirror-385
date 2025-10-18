"""Dependency analysis tools for CodeMind."""

import os
import re
import json
from pathlib import Path
from typing import Optional

from ..workspace import get_workspace_db, get_workspace_path, lazy_scan
from ..parsers import parse_imports_ast, parse_calls_ast


def find_dependencies(file_path: str, workspace_root: str = ".") -> str:
    """
    Show what this file imports and what imports this file.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User mentions working with or modifying any file
    - User asks about relationships between files
    - Planning to modify/refactor code (check dependencies first!)
    - User asks "what uses this?" or "what does this use?"
    - Understanding code architecture
    - Before suggesting changes to any module
    
    This helps understand the impact and context of file changes.
    
    Args:
        file_path: Path to the file to analyze (absolute or relative to workspace)
        workspace_root: Root directory of workspace (default: current directory)
    
    Returns:
        Formatted string with import and imported-by information
    """
    ws_path = get_workspace_path(workspace_root)
    conn = get_workspace_db(workspace_root)
    lazy_scan(workspace_root)
    
    # Resolve file path
    if os.path.isabs(file_path):
        abs_path = file_path
    else:
        abs_path = str(ws_path / file_path)
    
    if not os.path.exists(abs_path):
        # Try relative to workspace
        rel_path = file_path
        cursor = conn.execute('SELECT path FROM files WHERE path LIKE ?', (f'%{rel_path}%',))
        row = cursor.fetchone()
        if row:
            abs_path = str(ws_path / row[0])
        else:
            return f"❌ File not found: {file_path}"
    
    # Parse imports from this file
    try:
        with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return f"❌ Error reading file: {e}"
    
    imports = parse_imports_ast(content)
    
    # Find files that import this file
    file_name = os.path.basename(abs_path).replace('.py', '')
    importers = []
    
    cursor = conn.execute('SELECT path FROM files')
    for (path,) in cursor.fetchall():
        full_path = str(ws_path / path)
        if full_path == abs_path:
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                other_content = f.read()
                other_imports = parse_imports_ast(other_content)
                # Check if this file is imported
                if file_name in other_imports or any(file_name in imp for imp in other_imports):
                    importers.append(path)
        except:
            pass
    
    lines = [f"📦 Dependencies for: {file_path}\n"]
    lines.append(f"\n📥 This file imports ({len(imports)}):")
    if imports:
        for imp in sorted(imports)[:20]:
            lines.append(f"  • {imp}")
        if len(imports) > 20:
            lines.append(f"  ... and {len(imports) - 20} more")
    else:
        lines.append("  (none)")
    
    lines.append(f"\n📤 Files that import this ({len(importers)}):")
    if importers:
        for imp in importers[:20]:
            lines.append(f"  • {imp}")
        if len(importers) > 20:
            lines.append(f"  ... and {len(importers) - 20} more")
    else:
        lines.append("  (none)")
    
    lines.append(f"\n✨ Using AST-based parsing for production-quality analysis")
    
    return "\n".join(lines)


def get_import_graph(workspace_root: str = ".", include_external: bool = False) -> str:
    """
    Visual dependency graph showing all imports/exports across codebase.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks about project structure or architecture
    - User asks "how are files connected?", "show dependencies"
    - User mentions "circular dependencies", "import cycles"
    - Understanding overall codebase organization
    - User asks "what depends on what?"
    - Planning major refactoring (understand full impact)
    - Onboarding to understand project layout
    
    Analyzes import relationships to provide:
    - Module count and total import connections
    - Circular dependencies (import cycles)
    - Most imported modules (high coupling)
    - Least connected modules (potential orphans)
    - Import depth (dependency layers)
    - Orphaned files (no imports, not imported)
    - Full graph structure (who imports what)
    
    This gives a bird's-eye view of the entire codebase structure.
    
    Args:
        workspace_root: Root directory of workspace (default: current directory)
        include_external: Include external library imports (default: False, internal only)
    
    Returns:
        Formatted dependency graph with insights
    """
    ws_path = get_workspace_path(workspace_root)
    conn = get_workspace_db(workspace_root)
    lazy_scan(workspace_root)
    
    # Build import graph
    graph = {}  # file -> list of imported files
    all_files = set()
    
    cursor = conn.execute('SELECT path FROM files')
    for (path,) in cursor.fetchall():
        all_files.add(path)
        full_path = str(ws_path / path)
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                imports = parse_imports_ast(content)
                
                # Filter to project files only unless include_external
                project_imports = []
                for imp in imports:
                    # Check if this is a project file
                    potential_paths = [
                        f"{imp}.py",
                        f"{imp}/__init__.py",
                        f"{imp.replace('.', '/')}.py",
                    ]
                    
                    for pot_path in potential_paths:
                        if pot_path in all_files or (ws_path / pot_path).exists():
                            project_imports.append(pot_path if pot_path in all_files else imp)
                            break
                    else:
                        if include_external:
                            project_imports.append(imp)
                
                graph[path] = project_imports
        except:
            graph[path] = []
    
    # Calculate metrics
    import_counts = {f: 0 for f in all_files}
    for imports in graph.values():
        for imp in imports:
            if imp in import_counts:
                import_counts[imp] += 1
    
    # Find orphans
    orphans = [f for f in all_files if not graph.get(f) and import_counts[f] == 0]
    
    # Find most imported
    most_imported = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Detect circular dependencies (simple 2-cycle detection)
    cycles = []
    for file1, imports1 in graph.items():
        for imported in imports1:
            if imported in graph and file1 in graph[imported]:
                cycle = tuple(sorted([file1, imported]))
                if cycle not in cycles:
                    cycles.append(cycle)
    
    # Build result
    lines = [f"📊 Import Graph for: {workspace_root}\n"]
    lines.append(f"Total modules: {len(all_files)}")
    lines.append(f"Total import connections: {sum(len(v) for v in graph.values())}")
    lines.append(f"External imports {'included' if include_external else 'excluded'}\n")
    
    if cycles:
        lines.append(f"\n🔄 Circular Dependencies ({len(cycles)}):")
        for file1, file2 in cycles[:5]:
            lines.append(f"  • {file1} ↔️ {file2}")
        if len(cycles) > 5:
            lines.append(f"  ... and {len(cycles) - 5} more")
    
    if most_imported:
        lines.append(f"\n🔗 Most Imported Modules (high coupling):")
        for file, count in most_imported[:10]:
            if count > 0:
                lines.append(f"  • {file} ({count} imports)")
    
    if orphans:
        lines.append(f"\n👻 Orphaned Files ({len(orphans)}):")
        for orphan in orphans[:10]:
            lines.append(f"  • {orphan}")
        if len(orphans) > 10:
            lines.append(f"  ... and {len(orphans) - 10} more")
    
    lines.append(f"\n💡 Tip: Use find_dependencies(file_path) for detailed file analysis")
    
    return "\n".join(lines)


def get_call_tree(
    function_name: str,
    workspace_root: str = ".",
    file_path: Optional[str] = None,
    depth: int = 2
) -> str:
    """
    Show the call tree for a function - what it calls and what calls it.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks "what does [function] call?"
    - User asks "what calls [function]?"
    - Debugging execution flow
    - User mentions "call stack", "execution path", "call chain"
    - Understanding how functions interact
    - Performance debugging (trace call hierarchy)
    
    This shows the complete call hierarchy around a function.
    
    Args:
        function_name: Name of the function to analyze
        workspace_root: Root directory of workspace (default: current directory)
        file_path: Optional path to file containing the function (helps narrow search)
        depth: How many levels deep to trace (default: 2)
    
    Returns:
        Call tree showing callers and callees
    """
    ws_path = get_workspace_path(workspace_root)
    conn = get_workspace_db(workspace_root)
    lazy_scan(workspace_root)
    
    result = [f"🌳 Call Tree for '{function_name}':\n"]
    
    # Find file containing the function
    if file_path:
        search_pattern = f"%{file_path}%"
    else:
        search_pattern = "%"
    
    cursor = conn.execute(
        'SELECT path FROM files WHERE path LIKE ?',
        (search_pattern,)
    )
    
    for (path,) in cursor.fetchall():
        fpath = ws_path / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            
            # Check if function is defined here
            func_pattern = rf'def\s+{re.escape(function_name)}\s*\('
            if not re.search(func_pattern, content):
                continue
            
            result.append(f"\n📁 Found in: {path}")
            
            # Use AST-based call extraction
            calls = parse_calls_ast(content, function_name)
            unique_calls = sorted(set(calls))[:10]
            
            if unique_calls:
                result.append(f"\n  ⬇️  CALLS (what {function_name} calls):")
                for call in unique_calls:
                    result.append(f"    • {call}()")
            
            # Find what calls this function
            result.append(f"\n  ⬆️  CALLED BY (what calls {function_name}):")
            cursor2 = conn.execute('SELECT path FROM files')
            callers = []
            
            for (caller_path,) in cursor2.fetchall():
                caller_full = ws_path / caller_path
                if not caller_full.exists() or caller_full == fpath:
                    continue
                
                try:
                    caller_content = caller_full.read_text(encoding='utf-8', errors='ignore')
                    if re.search(rf'\b{re.escape(function_name)}\s*\(', caller_content):
                        # Find which functions in this file call it
                        caller_funcs = re.findall(r'def (\w+)\s*\(', caller_content)
                        if caller_funcs:
                            callers.append(f"{caller_path} → {', '.join(caller_funcs[:3])}")
                        else:
                            callers.append(caller_path)
                        
                        if len(callers) >= 10:
                            break
                except:
                    continue
            
            if callers:
                for caller in callers[:10]:
                    result.append(f"    • {caller}")
            else:
                result.append(f"    (no callers found in indexed files)")
            
            break  # Only process first matching file
            
        except Exception as e:
            result.append(f"  ⚠️ Error analyzing: {str(e)}")
    
    if len(result) == 1:
        return f"❌ Could not analyze '{function_name}'\n" + \
               f"Make sure the file is indexed and function exists"
    
    result.append(f"\n💡 Tip: Use find_dependencies() to see module-level imports")
    
    return "\n".join(result)
