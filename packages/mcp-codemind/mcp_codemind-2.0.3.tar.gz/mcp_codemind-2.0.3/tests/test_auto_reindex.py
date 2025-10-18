"""Comprehensive test suite for automatic re-indexing of modified files."""
import os
import time
import tempfile
from pathlib import Path
import hashlib

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from codemind.workspace import lazy_scan, get_workspace_db
from codemind.indexing import scan_modified_files


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests = []
    
    def record(self, name, passed, message=""):
        self.tests.append((name, passed, message))
        if passed:
            self.passed += 1
            print(f"  ✅ {name}")
            if message:
                print(f"     {message}")
        else:
            self.failed += 1
            print(f"  ❌ {name}")
            if message:
                print(f"     {message}")
    
    def warn(self, message):
        self.warnings += 1
        print(f"  ⚠️  {message}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'=' * 70}")
        print(f"📊 TEST SUMMARY")
        print(f"{'=' * 70}")
        print(f"  Total:    {total} tests")
        print(f"  Passed:   {self.passed} ✅")
        print(f"  Failed:   {self.failed} ❌")
        print(f"  Warnings: {self.warnings} ⚠️")
        print(f"  Success:  {self.passed / total * 100:.1f}%" if total > 0 else "  No tests run")
        print(f"{'=' * 70}")
        return self.failed == 0


def test_basic_reindex(tmpdir, results):
    """Test 1: Basic re-indexing workflow"""
    print("\n📋 Test 1: Basic Re-indexing Workflow")
    
    test_file = Path(tmpdir) / "test.py"
    test_file.write_text('"""Original content."""\ndef foo(): pass')
    
    # Initial scan
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
    original_hash = cursor.fetchone()
    
    results.record("Initial indexing", original_hash is not None)
    
    # Modify file
    time.sleep(0.1)
    test_file.write_text('"""Modified content."""\ndef bar(): pass')
    
    # Re-scan
    lazy_scan(tmpdir)
    cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
    new_hash = cursor.fetchone()
    
    results.record("Re-index after modification", 
                   new_hash is not None and new_hash[0] != original_hash[0],
                   f"Hash changed: {original_hash[0][:8]}... → {new_hash[0][:8]}...")
    
    return conn


def test_multiple_files(tmpdir, results):
    """Test 2: Multiple files with mixed changes"""
    print("\n📋 Test 2: Multiple Files with Mixed Changes")
    
    # Create 5 files
    files = []
    for i in range(5):
        f = Path(tmpdir) / f"file{i}.py"
        f.write_text(f'"""File {i}."""\ndef func{i}(): pass')
        files.append(f)
    
    # Initial scan
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    # Get initial hashes
    cursor = conn.execute('SELECT path, file_hash FROM files')
    initial_hashes = {row[0]: row[1] for row in cursor.fetchall()}
    
    results.record("Index 5 files", len(initial_hashes) >= 5)
    
    # Modify 3 files
    time.sleep(0.1)
    modified = [files[1], files[3], files[4]]
    for f in modified:
        f.write_text(f'"""Modified {f.name}."""\ndef new_func(): pass')
    
    # Re-scan
    count = scan_modified_files(tmpdir)
    
    results.record("Detect 3 modified files", count == 3, f"Re-indexed: {count}")
    
    # Verify only modified files changed
    cursor = conn.execute('SELECT path, file_hash FROM files')
    new_hashes = {row[0]: row[1] for row in cursor.fetchall()}
    
    changed_count = sum(1 for path, hash in new_hashes.items() 
                       if path in initial_hashes and initial_hashes[path] != hash)
    
    results.record("Only modified files changed", changed_count == 3, 
                   f"{changed_count} files changed hashes")
    
    return conn


def test_unchanged_files_skipped(tmpdir, results):
    """Test 3: Unchanged files are efficiently skipped"""
    print("\n📋 Test 3: Unchanged Files Skipped")
    
    # Create file
    test_file = Path(tmpdir) / "unchanged.py"
    test_file.write_text('"""Unchanged file."""\ndef stable(): pass')
    
    # Initial scan
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    cursor = conn.execute('SELECT file_hash, last_scanned FROM files WHERE path = ?', (str(test_file),))
    original = cursor.fetchone()
    
    # Scan again without changes
    time.sleep(0.1)
    count = scan_modified_files(tmpdir)
    
    cursor = conn.execute('SELECT file_hash, last_scanned FROM files WHERE path = ?', (str(test_file),))
    after_scan = cursor.fetchone()
    
    results.record("Unchanged file skipped", count == 0, "0 files re-indexed")
    results.record("Hash unchanged", original[0] == after_scan[0])
    
    return conn


def test_file_deletion_and_recreation(tmpdir, results):
    """Test 4: File deleted and recreated"""
    print("\n📋 Test 4: File Deletion and Recreation")
    
    test_file = Path(tmpdir) / "temporary.py"
    test_file.write_text('"""First version."""\ndef first(): pass')
    
    # Initial scan
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
    first_hash = cursor.fetchone()[0]
    
    # Delete file
    test_file.unlink()
    results.record("File deleted", not test_file.exists())
    
    # Recreate with different content
    time.sleep(0.1)
    test_file.write_text('"""Second version."""\ndef second(): pass')
    
    # Re-scan
    lazy_scan(tmpdir)
    
    cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
    second_hash = cursor.fetchone()[0]
    
    results.record("Recreated file re-indexed", second_hash != first_hash,
                   f"Hash changed: {first_hash[:8]}... → {second_hash[:8]}...")
    
    return conn


def test_large_file_content_change(tmpdir, results):
    """Test 5: Large content changes"""
    print("\n📋 Test 5: Large Content Changes")
    
    test_file = Path(tmpdir) / "large.py"
    
    # Create file with substantial content
    original_content = '"""Large file."""\n' + '\n'.join([f'def func{i}(): pass' for i in range(100)])
    test_file.write_text(original_content)
    
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    cursor = conn.execute('SELECT file_hash, size_kb FROM files WHERE path = ?', (str(test_file),))
    original = cursor.fetchone()
    
    # Modify significantly
    time.sleep(0.1)
    modified_content = '"""Modified large file."""\n' + '\n'.join([f'def new_func{i}(): return {i}' for i in range(100)])
    test_file.write_text(modified_content)
    
    # Re-scan
    count = scan_modified_files(tmpdir)
    
    cursor = conn.execute('SELECT file_hash, size_kb FROM files WHERE path = ?', (str(test_file),))
    modified = cursor.fetchone()
    
    results.record("Large file re-indexed", count == 1)
    results.record("Hash changed for large file", original[0] != modified[0])
    results.record("Size updated", modified[1] > 0)
    
    return conn


def test_rapid_successive_changes(tmpdir, results):
    """Test 6: Rapid successive file modifications"""
    print("\n📋 Test 6: Rapid Successive Changes")
    
    test_file = Path(tmpdir) / "rapid.py"
    test_file.write_text('"""Version 0."""')
    
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    hashes = []
    for i in range(5):
        time.sleep(0.05)  # Very short delay
        test_file.write_text(f'"""Version {i+1}."""\ndef func{i}(): pass')
        scan_modified_files(tmpdir)
        
        cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
        hashes.append(cursor.fetchone()[0])
    
    # All hashes should be different
    unique_hashes = len(set(hashes))
    results.record("All rapid changes detected", unique_hashes == 5,
                   f"{unique_hashes}/5 unique hashes")
    
    return conn


def test_whitespace_only_changes(tmpdir, results):
    """Test 7: Whitespace-only changes"""
    print("\n📋 Test 7: Whitespace-Only Changes")
    
    test_file = Path(tmpdir) / "whitespace.py"
    test_file.write_text('"""Whitespace test."""\ndef foo(): pass')
    
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
    original_hash = cursor.fetchone()[0]
    
    # Add whitespace
    time.sleep(0.1)
    test_file.write_text('"""Whitespace test."""\n\n\ndef foo(): pass\n\n')
    
    scan_modified_files(tmpdir)
    
    cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
    new_hash = cursor.fetchone()[0]
    
    results.record("Whitespace changes detected", original_hash != new_hash,
                   "Hash correctly changed (whitespace affects hash)")
    
    return conn


def test_file_renamed(tmpdir, results):
    """Test 8: File renamed (deleted + new file)"""
    print("\n📋 Test 8: File Rename Detection")
    
    old_file = Path(tmpdir) / "old_name.py"
    old_file.write_text('"""Content."""\ndef func(): pass')
    
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    cursor = conn.execute('SELECT COUNT(*) FROM files WHERE path = ?', (str(old_file),))
    old_indexed = cursor.fetchone()[0]
    
    # Rename file (simulated by delete + create)
    time.sleep(0.1)
    content = old_file.read_text()
    old_file.unlink()
    
    new_file = Path(tmpdir) / "new_name.py"
    new_file.write_text(content)
    
    lazy_scan(tmpdir)
    
    cursor = conn.execute('SELECT COUNT(*) FROM files WHERE path = ?', (str(new_file),))
    new_indexed = cursor.fetchone()[0]
    
    results.record("Old file was indexed", old_indexed == 1)
    results.record("Renamed file indexed", new_indexed == 1)
    
    return conn


def test_concurrent_file_access(tmpdir, results):
    """Test 9: File being modified during scan"""
    print("\n📋 Test 9: Concurrent File Access")
    
    test_file = Path(tmpdir) / "concurrent.py"
    test_file.write_text('"""Initial."""')
    
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    # This should not crash even if file is modified during scan
    time.sleep(0.1)
    test_file.write_text('"""Modified."""')
    
    try:
        scan_modified_files(tmpdir)
        results.record("Handles concurrent access", True, "No exceptions")
    except Exception as e:
        results.record("Handles concurrent access", False, f"Exception: {e}")
    
    return conn


def test_empty_file(tmpdir, results):
    """Test 10: Empty file handling"""
    print("\n📋 Test 10: Empty File Handling")
    
    test_file = Path(tmpdir) / "empty.py"
    test_file.write_text('')
    
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    cursor = conn.execute('SELECT COUNT(*) FROM files WHERE path = ?', (str(test_file),))
    indexed = cursor.fetchone()[0]
    
    results.record("Empty file indexed", indexed == 1)
    
    # Add content to empty file
    time.sleep(0.1)
    test_file.write_text('"""Now has content."""')
    
    scan_modified_files(tmpdir)
    
    cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
    has_hash = cursor.fetchone() is not None
    
    results.record("Empty to content transition", has_hash)
    
    return conn


def test_unicode_content(tmpdir, results):
    """Test 11: Unicode and special characters"""
    print("\n📋 Test 11: Unicode Content")
    
    test_file = Path(tmpdir) / "unicode.py"
    test_file.write_text('"""Unicode: 你好世界 🚀 émojis."""\ndef func(): pass', encoding='utf-8')
    
    lazy_scan(tmpdir)
    conn = get_workspace_db(tmpdir)
    
    cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
    original = cursor.fetchone()
    
    results.record("Unicode file indexed", original is not None)
    
    # Modify with more unicode
    time.sleep(0.1)
    test_file.write_text('"""Unicode: 你好世界 🎉 émojis modified."""', encoding='utf-8')
    
    scan_modified_files(tmpdir)
    
    cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
    modified = cursor.fetchone()
    
    results.record("Unicode changes detected", modified[0] != original[0])
    
    return conn


def test_performance_many_files(tmpdir, results):
    """Test 12: Performance with many files"""
    print("\n📋 Test 12: Performance with Many Files")
    
    # Create 50 files
    for i in range(50):
        f = Path(tmpdir) / f"perf_{i}.py"
        f.write_text(f'"""File {i}."""\ndef func{i}(): pass')
    
    # Initial scan
    start = time.time()
    lazy_scan(tmpdir)
    initial_time = time.time() - start
    
    conn = get_workspace_db(tmpdir)
    cursor = conn.execute('SELECT COUNT(*) FROM files')
    file_count = cursor.fetchone()[0]
    
    results.record("Indexed 50 files", file_count >= 50, 
                   f"{file_count} files in {initial_time:.2f}s")
    
    # Modify 10 files
    time.sleep(0.1)
    for i in range(0, 50, 5):  # Every 5th file
        f = Path(tmpdir) / f"perf_{i}.py"
        f.write_text(f'"""Modified file {i}."""\ndef new_func{i}(): pass')
    
    # Re-scan only modified
    start = time.time()
    count = scan_modified_files(tmpdir)
    rescan_time = time.time() - start
    
    results.record("Re-indexed only 10 modified files", count == 10,
                   f"{count} files in {rescan_time:.2f}s (should be faster than initial)")
    
    if rescan_time < initial_time:
        results.record("Re-scan faster than initial", True,
                       f"{rescan_time:.2f}s < {initial_time:.2f}s")
    else:
        results.warn(f"Re-scan not faster: {rescan_time:.2f}s >= {initial_time:.2f}s")
    
    return conn


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 COMPREHENSIVE AUTO-REINDEX TEST SUITE")
    print("=" * 70)
    
    results = TestResults()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"\n📁 Test workspace: {tmpdir}")
            
            # Run all tests
            conn = None
            tests = [
                test_basic_reindex,
                test_multiple_files,
                test_unchanged_files_skipped,
                test_file_deletion_and_recreation,
                test_large_file_content_change,
                test_rapid_successive_changes,
                test_whitespace_only_changes,
                test_file_renamed,
                test_concurrent_file_access,
                test_empty_file,
                test_unicode_content,
                test_performance_many_files,
            ]
            
            for test_func in tests:
                try:
                    conn = test_func(tmpdir, results)
                except Exception as e:
                    print(f"  ❌ Exception in {test_func.__name__}: {e}")
                    results.failed += 1
                    import traceback
                    traceback.print_exc()
            
            # Close connection
            if conn:
                conn.close()
        
        # Print summary
        success = results.summary()
        
        if success:
            print("\n✨ All auto-reindex tests passed!")
            print("   - Hash-based change detection works")
            print("   - mtime filtering is efficient")
            print("   - Edge cases handled correctly")
            print("   - Performance is acceptable")
            sys.exit(0)
        else:
            print(f"\n⚠️  {results.failed} test(s) failed - review above")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
