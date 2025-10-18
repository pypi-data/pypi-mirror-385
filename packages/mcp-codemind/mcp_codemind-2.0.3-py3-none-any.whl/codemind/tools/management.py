"""Index management and maintenance tools for CodeMind."""

import re
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..workspace import get_workspace_db, get_workspace_path, get_workspace_config, lazy_scan
from ..indexing import scan_project, _index_file_internal
from ..workspace import get_workspace_embedding


def force_reindex(workspace_root: str = ".") -> str:
    """
    Force a complete re-scan of the entire project.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User says "reindex", "refresh", "rescan"
    - User reports search not finding recently added files
    - User mentions database seems out of sync
    - After major file operations (bulk add/delete/rename)
    - User asks "why isn't my new file showing up?"
    
    This rebuilds the entire index from scratch.
    NOTE: Can be slow for large projects - use sparingly.
    
    Args:
        workspace_root: Root directory of workspace (default: current directory)
    
    Returns:
        Summary of indexing operation
    """
    conn = get_workspace_db(workspace_root)
    lazy_scan(workspace_root)
    
    start_time = datetime.now()
    
    # Clear existing data
    conn.execute('DELETE FROM files')
    conn.execute('DELETE FROM changes')
    conn.commit()
    
    # Re-scan everything
    file_count = scan_project(workspace_root)
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    return f"✅ Re-indexed {file_count} files in {elapsed:.1f} seconds\n" + \
           f"📊 Database refreshed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def index_file(file_path: str, workspace_root: str = ".") -> str:
    """
    Index or re-index a specific file immediately.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User just created a new file and wants to use it
    - User says "index [filename]"
    - User made major changes and wants immediate reindex
    - Search not finding a specific newly created file
    - User asks "why isn't [file] showing up in search?"
    
    This indexes a single file without full project rescan.
    Faster than force_reindex for single file updates.
    
    Args:
        file_path: Path to file to index (relative to project root or absolute)
        workspace_root: Root directory of workspace (default: current directory)
    
    Returns:
        Confirmation with file details
    """
    ws_path = get_workspace_path(workspace_root)
    conn = get_workspace_db(workspace_root)
    config = get_workspace_config(workspace_root)
    lazy_scan(workspace_root)
    
    # Resolve absolute path
    if Path(file_path).is_absolute():
        full_path = Path(file_path)
    else:
        full_path = ws_path / file_path
    
    if not full_path.exists():
        return f"❌ File not found: {file_path}"
    
    if not full_path.is_file():
        return f"❌ Not a file: {file_path}"
    
    # Check if it's a supported file type
    if full_path.suffix.lower() not in config['watched_extensions']:
        return f"⚠️ File type {full_path.suffix} not in supported extensions\n" + \
               f"Supported: {', '.join(config['watched_extensions'])}"
    
    # Index the file
    try:
        embedding_model = get_workspace_embedding(workspace_root)
        _index_file_internal(str(full_path), conn, embedding_model)
        
        # Get updated info
        try:
            rel_path = str(full_path.relative_to(ws_path))
        except ValueError:
            rel_path = str(full_path)
        
        cursor = conn.execute(
            'SELECT purpose, key_exports, size_kb, last_scanned FROM files WHERE path = ?',
            (rel_path,)
        )
        row = cursor.fetchone()
        
        if row:
            purpose, exports, size, scanned = row
            exports_list = json.loads(exports) if exports else []
            
            return f"✅ Indexed: {file_path}\n" + \
                   f"📝 Purpose: {purpose or 'Not determined'}\n" + \
                   f"📦 Exports: {', '.join(exports_list[:5])}\n" + \
                   f"📏 Size: {size:.1f} KB\n" + \
                   f"🕐 Scanned: {scanned}"
        else:
            return f"✅ File indexed but details not available: {file_path}"
            
    except Exception as e:
        return f"❌ Error indexing file: {str(e)}"


def find_todo_and_fixme(
    workspace_root: str = ".",
    tag_type: str = "TODO",
    search_term: Optional[str] = None,
    limit: int = 20
) -> str:
    """
    Search all TODO, FIXME, HACK, XXX comments with context.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks "what needs to be done?", "show todos"
    - User asks "what's broken?", "show fixmes"
    - Planning work or sprint
    - User mentions "technical debt", "pending tasks"
    - Understanding known issues before making changes
    - User asks "what are the known problems?"
    
    This finds all marked comments indicating work needed.
    Critical for understanding what's on the radar.
    
    Args:
        workspace_root: Root directory of workspace (default: current directory)
        tag_type: Type of tag (TODO/FIXME/HACK/XXX/NOTE)
        search_term: Optional keyword to filter results
        limit: Maximum results (default: 20)
    
    Returns:
        Grouped comments with file, line, and context
    """
    ws_path = get_workspace_path(workspace_root)
    conn = get_workspace_db(workspace_root)
    lazy_scan(workspace_root)
    
    tag_type = tag_type.upper()
    valid_tags = ["TODO", "FIXME", "HACK", "XXX", "NOTE", "BUG"]
    
    if tag_type not in valid_tags:
        return f"❌ Invalid tag type. Use one of: {', '.join(valid_tags)}"
    
    result = [f"🔍 Searching for {tag_type} comments" + (f" matching '{search_term}'" if search_term else "") + ":\n"]
    
    findings = []
    cursor = conn.execute('SELECT path FROM files')
    
    for (path,) in cursor.fetchall():
        fpath = ws_path / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Match comments with tag
            pattern = rf'#.*{tag_type}:?\s*(.+)$'
            
            for i, line in enumerate(lines):
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    comment_text = match.group(1).strip()
                    
                    # Filter by search term if provided
                    if search_term and search_term.lower() not in comment_text.lower():
                        continue
                    
                    # Get surrounding context (code being marked)
                    context_start = max(0, i - 1)
                    context_end = min(len(lines), i + 2)
                    context = '\n    '.join(lines[context_start:context_end])
                    
                    findings.append({
                        'file': path,
                        'line': i + 1,
                        'comment': comment_text,
                        'context': context[:300]
                    })
                    
                    if len(findings) >= limit * 2:
                        break
        except:
            continue
        
        if len(findings) >= limit * 2:
            break
    
    if not findings:
        result.append(f"✅ No {tag_type} comments found" + (f" matching '{search_term}'" if search_term else ""))
        result.append(f"\nThis could mean:")
        result.append(f"  • Clean codebase (good!)")
        result.append(f"  • Different tag conventions used")
        result.append(f"  • Files not yet indexed")
        return "\n".join(result)
    
    # Group by file
    by_file = {}
    for finding in findings:
        if finding['file'] not in by_file:
            by_file[finding['file']] = []
        by_file[finding['file']].append(finding)
    
    result.append(f"📊 Found {len(findings)} {tag_type} comments in {len(by_file)} files:\n")
    
    # Show findings grouped by file
    for file, items in sorted(by_file.items())[:limit]:
        result.append(f"\n📁 **{file}** ({len(items)} items):")
        for item in items[:3]:
            result.append(f"  • Line {item['line']}: {item['comment']}")
    
    if len(findings) > limit:
        result.append(f"\n... {len(findings) - limit} more {tag_type} comments found")
        result.append(f"(increase limit parameter to see more)")
    
    # Priority hints
    if tag_type == "FIXME":
        result.append(f"\n⚠️ FIXME comments indicate bugs or issues that need attention")
    elif tag_type == "HACK":
        result.append(f"\n⚠️ HACK comments indicate technical debt or workarounds")
    elif tag_type == "XXX":
        result.append(f"\n🚨 XXX comments often indicate critical issues")
    
    result.append(f"\n💡 Tip: Use search_term parameter to filter by keyword")
    
    return "\n".join(result)


async def _get_file_history_summary_async(file_path: str, workspace_root: str, days_back: int) -> str:
    """Async implementation using git log."""
    ws_path = get_workspace_path(workspace_root)
    
    result = [f"📜 Git History for '{file_path}' (last {days_back} days):\n"]
    
    # Resolve file path
    if Path(file_path).is_absolute():
        fpath = Path(file_path)
    else:
        fpath = ws_path / file_path
    
    if not fpath.exists():
        return f"❌ File not found: {file_path}"
    
    try:
        # Quick check: is git available?
        try:
            proc = await asyncio.create_subprocess_exec(
                'git', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await asyncio.wait_for(proc.communicate(), timeout=2)
            if proc.returncode != 0:
                return f"❌ Git not found\n💡 Install Git to use this tool"
        except (FileNotFoundError, asyncio.TimeoutError):
            return f"❌ Git not found\n💡 Install Git to use this tool"
        
        # Make path relative to workspace for git
        try:
            rel_path = str(fpath.relative_to(ws_path))
        except ValueError:
            rel_path = str(fpath)
        
        # Get commit count
        proc = await asyncio.create_subprocess_exec(
            'git', 'log', '--oneline', f'--since={days_back} days ago', '--', rel_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(ws_path)
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)
        
        if proc.returncode != 0:
            return f"❌ Git not available or not a git repository\n💡 This tool requires Git"
        
        commits = stdout.decode().strip().split('\n')
        commit_count = len([c for c in commits if c])
        
        # Get contributors
        proc = await asyncio.create_subprocess_exec(
            'git', 'log', '--format=%an', f'--since={days_back} days ago', '--', rel_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(ws_path)
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        
        authors = [a for a in stdout.decode().strip().split('\n') if a]
        author_counts = {}
        for author in authors:
            author_counts[author] = author_counts.get(author, 0) + 1
        
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Get last modified date
        proc = await asyncio.create_subprocess_exec(
            'git', 'log', '-1', '--format=%ar', '--', rel_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(ws_path)
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        last_modified = stdout.decode().strip() or "Unknown"
        
        # Calculate metrics
        months = days_back / 30
        commits_per_month = commit_count / months if months > 0 else 0
        
        # Risk rating
        if commits_per_month >= 10:
            risk = "🔴 HIGH"
            risk_desc = "Very frequently changed - high fragility risk"
        elif commits_per_month >= 5:
            risk = "🟡 MEDIUM"
            risk_desc = "Moderately active - some risk of conflicts"
        elif commits_per_month >= 1:
            risk = "🟢 LOW"
            risk_desc = "Stable with occasional updates"
        else:
            risk = "✅ VERY LOW"
            risk_desc = "Rarely changed - very stable"
        
        # Build report
        result.append(f"📊 **Commits** ({days_back} days): {commit_count}")
        result.append(f"📈 **Change Rate**: {commits_per_month:.1f} commits/month")
        result.append(f"🕐 **Last Modified**: {last_modified}")
        result.append(f"⚡ **Risk Level**: {risk}")
        result.append(f"📝 **Assessment**: {risk_desc}\n")
        
        if top_authors:
            result.append(f"👥 **Top Contributors**:")
            for author, count in top_authors:
                result.append(f"  • {author} ({count} commits)")
        
        result.append(f"\n💡 Tip: Files with high change rates may be fragile or in active development")
        
        return "\n".join(result)
        
    except asyncio.TimeoutError:
        return f"⏱️ Git command timed out\n💡 Repository may be too large or git is slow"
    except Exception as e:
        return f"❌ Error analyzing git history: {str(e)}"


def get_file_history_summary(file_path: str, workspace_root: str = ".", days_back: int = 90) -> str:
    """
    Git history analysis - who changes this file, how often, recent activity.
    
    Args:
        file_path: File to analyze (absolute or relative to workspace)
        workspace_root: Root directory of workspace (default: current directory)
        days_back: How many days of history (default: 90)
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks "who worked on [file]?", "who wrote this?"
    - User asks "how often does [file] change?"
    - Risk assessment before modifying file
    - User asks "who to ask about [file]?"
    - Understanding file stability and maturity
    - User mentions "git history", "contributors", "blame"
    
    This provides git-based change history and ownership info.
    Requires git repository and git installed.
    
    Returns:
        Commit count, contributors, frequency, and risk rating
    """
    lazy_scan(workspace_root)
    
    # Run async function in event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context, try nest_asyncio if available
            try:
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(_get_file_history_summary_async(file_path, workspace_root, days_back))
            except ImportError:
                # nest_asyncio not available, return message
                return "⚠️ Tool requires nest_asyncio when called from async context\nRun: pip install nest_asyncio"
        else:
            return asyncio.run(_get_file_history_summary_async(file_path, workspace_root, days_back))
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(_get_file_history_summary_async(file_path, workspace_root, days_back))
