"""Search and discovery tools."""
import json
import numpy as np

from ..workspace import lazy_scan, get_workspace_db, get_workspace_embedding

try:
    import numpy as np
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False


def cosine_similarity(a, b):
    """Calculate cosine similarity between two embedding vectors."""
    if not HAS_EMBEDDINGS:
        return 0.0
    va, vb = np.frombuffer(a, dtype=np.float32), np.frombuffer(b, dtype=np.float32)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def search_existing_code(query: str, workspace_root: str = ".", limit: int = 5) -> str:
    """Search for existing functionality before creating new files.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks about implementing/adding/creating any feature
    - User wants to modify or extend functionality
    - User asks "how to" or "where is" questions
    - Starting any coding task to check if code already exists
    - User mentions any technical concept or feature name
    
    This prevents duplicate code and finds relevant existing implementations.
    
    Args:
        query: Semantic search query describing the functionality
        workspace_root: Path to the project workspace (default: current directory)
        limit: Maximum number of results to return
    """
    lazy_scan(workspace_root)
    embedding_model = get_workspace_embedding(workspace_root)
    if not embedding_model:
        return "❌ Semantic search not available (no embeddings)"
    
    conn = get_workspace_db(workspace_root)
    query_blob = embedding_model.encode(query, convert_to_numpy=True).tobytes()
    results = [(p, pu, cosine_similarity(query_blob, e)) 
               for p, pu, e in conn.execute('SELECT path, purpose, embedding FROM files WHERE embedding IS NOT NULL').fetchall() 
               if e]
    results.sort(key=lambda x: x[2], reverse=True)
    
    if not results[:limit]:
        return f"❌ No code found for: {query}"
    
    lines = [f"✅ Found {len(results[:limit])} files for '{query}' in {workspace_root}:\n"]
    for i, (p, pu, s) in enumerate(results[:limit], 1):
        lines.append(f"{i}. {p} ({int(s*100)}% match)\n   Purpose: {pu}\n")
    return "\n".join(lines)


def check_functionality_exists(feature_description: str, workspace_root: str = ".", confidence_threshold: float = 0.7) -> str:
    """Check if functionality exists in the workspace.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks "do we have...", "is there...", "does this project..."
    - Before suggesting to create any new code/file/function
    - User asks about implementing something (check first!)
    - Making architectural decisions (verify what exists)
    
    This prevents duplicate implementations and finds existing solutions.
    
    Args:
        feature_description: Description of the functionality to check
        workspace_root: Path to the project workspace (default: current directory)
        confidence_threshold: Minimum similarity threshold (0.0-1.0)
    """
    lazy_scan(workspace_root)
    embedding_model = get_workspace_embedding(workspace_root)
    if not embedding_model:
        return "❌ Check not available (no embeddings)"
    
    conn = get_workspace_db(workspace_root)
    query_blob = embedding_model.encode(feature_description, convert_to_numpy=True).tobytes()
    best, best_sim = None, 0.0
    
    for p, pu, e in conn.execute('SELECT path, purpose, embedding FROM files WHERE embedding IS NOT NULL').fetchall():
        if e:
            sim = cosine_similarity(query_blob, e)
            if sim > best_sim:
                best_sim, best = sim, (p, pu)
    
    if best_sim >= confidence_threshold and best:
        return f"✅ YES! Found in {workspace_root}:\n  📁 {best[0]}\n  📝 {best[1]}\n  🎯 {int(best_sim*100)}% match"
    
    if best:
        return f"❌ NO\n  Searched: {feature_description}\n  Closest: {best[0]} ({int(best_sim*100)}%)"
    return "❌ NO - nothing similar found"


def search_by_export(export_name: str, workspace_root: str = ".", limit: int = 10) -> str:
    """Find files that export a specific function, class, or variable.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks "where is [ClassName] defined?"
    - User asks "which file has [function_name]?"
    - User mentions a class/function name without specifying location
    - User wants to import or use a specific symbol
    - Debugging import errors or "undefined" issues
    - User asks "where can I find [symbol]?"
    
    This locates the definition of any exported symbol in the codebase.
    
    Args:
        export_name: Name of the export to search for
        workspace_root: Path to the project workspace (default: current directory)
        limit: Maximum number of results to return
    """
    lazy_scan(workspace_root)
    conn = get_workspace_db(workspace_root)
    results = []
    
    for path, ke in conn.execute('SELECT path, key_exports FROM files WHERE key_exports IS NOT NULL').fetchall():
        exports = json.loads(ke) if ke else []
        if export_name in exports:
            results.append(path)
    
    if not results:
        return f"❌ '{export_name}' not found in any exports in {workspace_root}"
    
    lines = [f"✅ Found '{export_name}' in {len(results)} file(s) in {workspace_root}:\n"]
    for i, p in enumerate(results[:limit], 1):
        lines.append(f"{i}. {p}\n")
    
    if len(results) > limit:
        lines.append(f"... and {len(results) - limit} more")
    
    return "\n".join(lines)


def get_similar_files(file_path: str, workspace_root: str = ".", limit: int = 5) -> str:
    """Find files similar to the given file (based on purpose/content).
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks "are there similar files to [filename]?"
    - User wants to follow existing patterns/conventions
    - Creating new files (find examples to follow)
    - User asks "show me examples like [file]"
    - Understanding code organization patterns
    - User mentions "similar", "like this", "same pattern"
    
    This helps maintain consistency by finding files with similar structure/purpose.
    
    Args:
        file_path: Path to the file to compare against
        workspace_root: Path to the project workspace (default: current directory)
        limit: Maximum number of results to return
    """
    lazy_scan(workspace_root)
    embedding_model = get_workspace_embedding(workspace_root)
    if not embedding_model:
        return "❌ Similarity search not available (embeddings disabled)"
    
    conn = get_workspace_db(workspace_root)
    row = conn.execute('SELECT embedding, purpose FROM files WHERE path = ? AND embedding IS NOT NULL', 
                      (file_path,)).fetchone()
    if not row:
        return f"❌ File not found or not indexed: {file_path}"
    
    target_embedding, target_purpose = row
    results = []
    
    for p, pu, e in conn.execute('SELECT path, purpose, embedding FROM files WHERE path != ? AND embedding IS NOT NULL', 
                                 (file_path,)).fetchall():
        if e:
            sim = cosine_similarity(target_embedding, e)
            results.append((p, pu, sim))
    
    results.sort(key=lambda x: x[2], reverse=True)
    
    if not results[:limit]:
        return f"❌ No similar files found for: {file_path}"
    
    lines = [f"📊 Files similar to: {file_path} in {workspace_root}\n"]
    lines.append(f"Purpose: {target_purpose}\n")
    for i, (p, pu, s) in enumerate(results[:limit], 1):
        lines.append(f"{i}. {p} ({int(s*100)}% similar)\n   {pu}\n")
    
    return "\n".join(lines)
