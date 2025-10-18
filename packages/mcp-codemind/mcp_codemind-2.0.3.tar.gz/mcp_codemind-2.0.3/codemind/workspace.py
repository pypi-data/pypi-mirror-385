"""Workspace management for CodeMind - handles multi-workspace support."""
import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Optional

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "db_path": ".codemind/memory.db",
    "watched_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".java", ".cs", ".cpp", ".go", ".rs"],
    "max_file_size_kb": 500,
    "embedding_model": "all-MiniLM-L6-v2"
}

# Workspace-specific resource caches
_workspace_dbs: Dict[str, sqlite3.Connection] = {}
_workspace_configs: Dict[str, dict] = {}
_workspace_embeddings: Dict[str, Optional[SentenceTransformer]] = {}


def get_workspace_path(workspace_root: str) -> Path:
    """Resolve and return the absolute workspace path."""
    return Path(workspace_root).resolve()


def get_workspace_config(workspace_root: str) -> dict:
    """Get or load configuration for a specific workspace."""
    ws_path = get_workspace_path(workspace_root)
    ws_key = str(ws_path)
    
    if ws_key in _workspace_configs:
        return _workspace_configs[ws_key]
    
    # Start with default config
    config = DEFAULT_CONFIG.copy()
    
    # Try to load workspace-specific config
    config_file = ws_path / "codemind_config.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config.update(json.load(f))
            logger.info(f"✓ Loaded config for workspace: {ws_path}")
        except Exception as e:
            logger.warning(f"⚠ Error loading config from {config_file}: {e}")
    
    _workspace_configs[ws_key] = config
    return config


def get_workspace_db(workspace_root: str) -> sqlite3.Connection:
    """Get or create database connection for a specific workspace."""
    ws_path = get_workspace_path(workspace_root)
    ws_key = str(ws_path)
    
    if ws_key in _workspace_dbs and _workspace_dbs[ws_key]:
        return _workspace_dbs[ws_key]
    
    # Create database in workspace
    config = get_workspace_config(workspace_root)
    db_path = ws_path / config["db_path"]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("""CREATE TABLE IF NOT EXISTS files (
        path TEXT PRIMARY KEY,
        purpose TEXT,
        last_scanned TIMESTAMP,
        embedding BLOB,
        key_exports TEXT,
        file_hash TEXT,
        size_kb INTEGER
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        reasoning TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        affected_files TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        change_summary TEXT
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_files_last_scanned ON files(last_scanned)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_changes_timestamp ON changes(timestamp)")
    conn.commit()
    
    _workspace_dbs[ws_key] = conn
    logger.info(f"✓ Initialized database for workspace: {ws_path}")
    return conn


def get_workspace_embedding(workspace_root: str) -> Optional[SentenceTransformer]:
    """Get or create embedding model for a specific workspace."""
    ws_path = get_workspace_path(workspace_root)
    ws_key = str(ws_path)
    
    if not HAS_EMBEDDINGS:
        return None
    
    if ws_key in _workspace_embeddings:
        return _workspace_embeddings[ws_key]
    
    config = get_workspace_config(workspace_root)
    try:
        model = SentenceTransformer(config['embedding_model'])
        # Monkey-patch to suppress progress bars
        original_encode = model.encode
        def encode_no_progress(*args, **kwargs):
            kwargs['show_progress_bar'] = False
            return original_encode(*args, **kwargs)
        model.encode = encode_no_progress
        
        _workspace_embeddings[ws_key] = model
        logger.info(f"✓ Loaded embedding model for workspace: {ws_path}")
        return model
    except Exception as e:
        logger.warning(f"⚠ Failed to load embedding model for {ws_path}: {e}")
        _workspace_embeddings[ws_key] = None
        return None


def lazy_scan(workspace_root: str = "."):
    """Scan workspace on first tool call and re-index modified files.
    
    This is called automatically before every tool invocation to ensure:
    - First-time users get initial index
    - Existing users get fresh data (modified files re-indexed)
    
    Uses efficient change detection via mtime + hash comparison.
    """
    from .indexing import scan_project, scan_modified_files  # Avoid circular import
    
    conn = get_workspace_db(workspace_root)
    cursor = conn.execute('SELECT COUNT(*) FROM files')
    file_count = cursor.fetchone()[0]
    
    if file_count == 0:
        # First run - full scan
        logger.info(f"🔍 First run - scanning workspace: {workspace_root}")
        scan_project(workspace_root)
        logger.info("✅ Initial scan complete!")
    else:
        # Subsequent runs - only re-index modified files
        scan_modified_files(workspace_root)
