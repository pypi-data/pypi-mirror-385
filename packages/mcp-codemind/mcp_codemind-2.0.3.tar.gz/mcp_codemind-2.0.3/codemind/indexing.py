"""File indexing and scanning functionality."""
import hashlib
import logging
from datetime import datetime
from pathlib import Path

from .workspace import get_workspace_path, get_workspace_config, get_workspace_db, get_workspace_embedding
from .parsers import extract_purpose, extract_key_exports
import json

logger = logging.getLogger(__name__)


def _index_file_internal(file_path: str, conn, embedding_model=None):
    """Internal function to index a file - called by scan_project."""
    try:
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        file_hash = hashlib.md5(content.encode()).hexdigest()
        cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (file_path,))
        result = cursor.fetchone()
        if result and result[0] == file_hash:
            return  # Already indexed with same hash
        
        purpose = extract_purpose(content, file_path)
        key_exports = extract_key_exports(content, file_path)
        embedding_blob = None
        
        if embedding_model:
            embedding_blob = embedding_model.encode(purpose, convert_to_numpy=True).tobytes()
        
        conn.execute("""INSERT OR REPLACE INTO files 
            (path, purpose, last_scanned, embedding, key_exports, file_hash, size_kb) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (file_path, purpose, datetime.now(), embedding_blob, json.dumps(key_exports),
             file_hash, len(content.encode()) // 1024))
        conn.commit()
    except Exception as e:
        logger.debug(f"Error indexing {file_path}: {e}")


def scan_project(workspace_root: str) -> int:
    """Scan a workspace and index all files.
    
    Args:
        workspace_root: Path to the workspace to scan
        
    Returns:
        Number of files indexed
    """
    ws_path = get_workspace_path(workspace_root)
    config = get_workspace_config(workspace_root)
    conn = get_workspace_db(workspace_root)
    embedding_model = get_workspace_embedding(workspace_root)
    
    indexed = 0
    for ext in config["watched_extensions"]:
        for fp in ws_path.rglob(f"*{ext}"):
            if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                try:
                    if fp.stat().st_size // 1024 <= config["max_file_size_kb"]:
                        _index_file_internal(str(fp), conn, embedding_model)
                        indexed += 1
                except OSError:
                    pass
    
    logger.info(f"✓ Indexed {indexed} files in {ws_path}")
    return indexed


def scan_modified_files(workspace_root: str) -> int:
    """Scan workspace and re-index only modified files.
    
    Uses file modification time and content hash to efficiently detect changes.
    This is called automatically on every tool invocation to keep embeddings fresh.
    
    Args:
        workspace_root: Path to the workspace to scan
        
    Returns:
        Number of files re-indexed
    """
    ws_path = get_workspace_path(workspace_root)
    config = get_workspace_config(workspace_root)
    conn = get_workspace_db(workspace_root)
    embedding_model = get_workspace_embedding(workspace_root)
    
    # Get all indexed files with their last scan time and hash
    cursor = conn.execute('SELECT path, last_scanned, file_hash FROM files')
    indexed_files = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    re_indexed = 0
    for ext in config["watched_extensions"]:
        for fp in ws_path.rglob(f"*{ext}"):
            if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                try:
                    file_path = str(fp)
                    file_size = fp.stat().st_size // 1024
                    file_mtime = datetime.fromtimestamp(fp.stat().st_mtime)
                    
                    # Skip if file is too large
                    if file_size > config["max_file_size_kb"]:
                        continue
                    
                    # Check if file is new or potentially modified
                    if file_path in indexed_files:
                        last_scanned, old_hash = indexed_files[file_path]
                        
                        # Quick check: has file been modified since last scan?
                        if isinstance(last_scanned, str):
                            last_scanned = datetime.fromisoformat(last_scanned.replace('Z', '+00:00'))
                        
                        if file_mtime <= last_scanned:
                            continue  # File hasn't been modified, skip
                        
                        # File was modified - verify with hash comparison
                        with open(file_path, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        new_hash = hashlib.md5(content.encode()).hexdigest()
                        
                        if new_hash == old_hash:
                            continue  # False positive from mtime, content unchanged
                    
                    # File is new or modified - re-index it
                    _index_file_internal(file_path, conn, embedding_model)
                    re_indexed += 1
                    
                except OSError:
                    pass
    
    if re_indexed > 0:
        logger.info(f"🔄 Re-indexed {re_indexed} modified file(s)")
    
    return re_indexed
