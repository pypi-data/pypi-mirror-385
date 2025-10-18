"""File context and metadata tools."""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..workspace import lazy_scan, get_workspace_db, get_workspace_path


def get_file_context(file_path: str, workspace_root: str = ".") -> str:
    """Get detailed information about a file.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User mentions any file name or path
    - User asks about what a file does
    - User wants to understand, modify, or work with a file
    - Before explaining code in a file
    - User references a module or component
    
    This provides context about file purpose, exports, and metadata.
    
    Args:
        file_path: Path to the file (relative or absolute)
        workspace_root: Path to the project workspace (default: current directory)
    """
    lazy_scan(workspace_root)
    conn = get_workspace_db(workspace_root)
    ws_path = get_workspace_path(workspace_root)
    
    # Try to resolve the file path - handle both relative and absolute paths
    file_path_obj = Path(file_path)
    
    # If it's a relative path, try to resolve it relative to workspace_root
    if not file_path_obj.is_absolute():
        resolved_path = (ws_path / file_path).resolve()
    else:
        resolved_path = file_path_obj.resolve()
    
    # Convert to string for database lookup
    search_path = str(resolved_path)
    
    # Try exact match first
    row = conn.execute('SELECT path, purpose, last_scanned, key_exports, size_kb FROM files WHERE path = ?', 
                      (search_path,)).fetchone()
    
    # If not found, try searching by filename (basename match)
    if not row:
        filename = os.path.basename(file_path)
        rows = conn.execute('SELECT path, purpose, last_scanned, key_exports, size_kb FROM files WHERE path LIKE ?', 
                           (f'%{filename}',)).fetchall()
        if rows:
            if len(rows) == 1:
                row = rows[0]
            else:
                matches = '\n  '.join([r[0] for r in rows])
                return f"⚠ Multiple files found matching '{filename}' in {workspace_root}:\n  {matches}\n\nPlease specify the full path."
    
    if not row:
        return f"❌ File not found: {file_path}\n  Searched for: {search_path}\n  Workspace: {workspace_root}\n  Tip: Try using the full path or check if the file has been indexed."
    
    p, pu, ls, ke, sz = row
    exports = json.loads(ke) if ke else []
    return f"📄 {p}\n  Purpose: {pu}\n  Last scanned: {ls}\n  Size: {sz} KB\n  Exports: {', '.join(exports) or 'None'}\n  Workspace: {workspace_root}"


def query_recent_changes(workspace_root: str = ".", hours: int = 24) -> str:
    """See recent file modifications.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks "what changed?", "what's new?", "recent updates?"
    - Preparing for code review
    - User mentions "latest changes", "modified files"
    - Understanding recent development activity
    - User asks about recent work or progress
    - Onboarding to see what's been done lately
    
    This shows a timeline of recent file modifications and changes.
    
    Args:
        workspace_root: Path to the project workspace (default: current directory)
        hours: Number of hours to look back
    """
    conn = get_workspace_db(workspace_root)
    changes = conn.execute(
        'SELECT file_path, timestamp, change_summary FROM changes WHERE timestamp > ? ORDER BY timestamp DESC',
        (datetime.now() - timedelta(hours=hours),)
    ).fetchall()
    
    if not changes:
        return f"ℹ No changes in last {hours} hours in {workspace_root}"
    
    lines = [f"📅 Changes in last {hours} hours in {workspace_root}:\n"]
    for fp, ts, cs in changes:
        lines.append(f"  📝 {fp}\n    {ts}: {cs or 'Modified'}\n")
    return "\n".join(lines)


def record_decision(description: str, reasoning: str, workspace_root: str = ".", affected_files: Optional[list] = None) -> str:
    """Store architectural decisions.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User makes an important technical choice
    - User explains "we chose X because Y"
    - After discussing architecture or design patterns
    - User says "let's document this decision"
    - Important tradeoffs or alternatives are discussed
    - User wants to record rationale for future reference
    
    This preserves the context and reasoning behind architectural decisions.
    IMPORTANT: Only record when user explicitly states a decision was made.
    
    Args:
        description: Brief description of the decision
        reasoning: Detailed reasoning behind the decision
        workspace_root: Path to the project workspace (default: current directory)
        affected_files: List of files affected by this decision
    """
    conn = get_workspace_db(workspace_root)
    affected_files = affected_files or []
    cursor = conn.execute(
        'INSERT INTO decisions (description, reasoning, affected_files) VALUES (?, ?, ?)',
        (description, reasoning, json.dumps(affected_files))
    )
    conn.commit()
    
    files_str = ', '.join(affected_files) if affected_files else 'None'
    return f"✅ Decision #{cursor.lastrowid} recorded in {workspace_root}\n  📋 {description}\n  💭 {reasoning}\n  📁 Files: {files_str}"


def list_all_decisions(workspace_root: str = ".", keyword: Optional[str] = None, limit: int = 10) -> str:
    """Query architectural decisions, optionally filtered by keyword.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks "why did we choose...?"
    - User asks about past decisions or rationale
    - User mentions "architectural decisions", "design choices"
    - Understanding historical context of the codebase
    - User asks "show me decisions about [topic]"
    - Onboarding new team members to understand history
    
    This retrieves the documented reasoning behind past technical choices.
    
    Args:
        workspace_root: Path to the project workspace (default: current directory)
        keyword: Optional keyword to filter decisions
        limit: Maximum number of results to return
    """
    conn = get_workspace_db(workspace_root)
    
    if keyword:
        query = 'SELECT id, description, reasoning, timestamp, affected_files FROM decisions WHERE description LIKE ? OR reasoning LIKE ? ORDER BY timestamp DESC LIMIT ?'
        pattern = f'%{keyword}%'
        decisions = conn.execute(query, (pattern, pattern, limit)).fetchall()
    else:
        query = 'SELECT id, description, reasoning, timestamp, affected_files FROM decisions ORDER BY timestamp DESC LIMIT ?'
        decisions = conn.execute(query, (limit,)).fetchall()
    
    if not decisions:
        suffix = f" matching '{keyword}'" if keyword else ""
        return f"ℹ No decisions found{suffix} in {workspace_root}"
    
    lines = [f"📋 Architectural Decisions in {workspace_root}"]
    if keyword:
        lines[0] += f" (matching '{keyword}')"
    lines[0] += ":\n"
    
    for id, desc, reason, ts, files in decisions:
        affected = json.loads(files) if files else []
        lines.append(f"\n#{id} - {desc}")
        lines.append(f"  📅 {ts}")
        lines.append(f"  💭 {reason}")
        if affected:
            lines.append(f"  📁 Affects: {', '.join(affected[:5])}")
            if len(affected) > 5:
                lines.append(f"     ... and {len(affected) - 5} more")
    
    return "\n".join(lines)
