#!/usr/bin/env python3
"""
Resilient File Handler

Provides graceful error handling for file operations with automatic fallbacks.
Instead of failing hard, creates missing files and provides alternatives.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager


class ResilientFileHandler:
    """Handle file operations with automatic fallbacks and recovery."""

    def __init__(self, create_missing: bool = True, default_content: str = ""):
        """
        Initialize handler.

        Args:
            create_missing: Automatically create missing files
            default_content: Default content for created files
        """
        self.create_missing = create_missing
        self.default_content = default_content
        self.operations_log = []

    def read_file(
        self,
        path: str,
        default: Optional[str] = None,
        encoding: str = "utf-8"
    ) -> str:
        """
        Read file with automatic fallback.

        Args:
            path: File path to read
            default: Default content if file doesn't exist (overrides instance default)
            encoding: File encoding

        Returns:
            File content or default
        """
        default_content = default if default is not None else self.default_content

        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
                self._log("read", path, "success")
                return content

        except FileNotFoundError:
            self._log("read", path, "not_found")
            if self.create_missing:
                print(f"📝 File {path} not found, creating with default content")
                self.write_file(path, default_content, create_dirs=True)
                return default_content
            else:
                print(f"⚠️  File {path} not found, using default")
                return default_content

        except PermissionError:
            self._log("read", path, "permission_denied")
            print(f"🔒 Cannot access {path}, using default")
            return default_content

        except UnicodeDecodeError as e:
            self._log("read", path, f"encoding_error: {e}")
            print(f"⚠️  Encoding error in {path}, trying binary mode")
            try:
                with open(path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    return content
            except Exception:
                return default_content

        except Exception as e:
            self._log("read", path, f"error: {e}")
            print(f"❌ Error reading {path}: {e}")
            return default_content

    def write_file(
        self,
        path: str,
        content: str,
        create_dirs: bool = True,
        backup: bool = False,
        encoding: str = "utf-8"
    ) -> bool:
        """
        Write file with automatic directory creation and backup.

        Args:
            path: File path to write
            content: Content to write
            create_dirs: Create parent directories if missing
            backup: Create backup of existing file
            encoding: File encoding

        Returns:
            True if successful
        """
        try:
            # Create parent directories
            if create_dirs:
                Path(path).parent.mkdir(parents=True, exist_ok=True)

            # Backup existing file
            if backup and os.path.exists(path):
                backup_path = f"{path}.backup"
                shutil.copy2(path, backup_path)
                self._log("backup", path, f"created: {backup_path}")

            # Write file
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

            self._log("write", path, "success")
            return True

        except PermissionError:
            self._log("write", path, "permission_denied")
            print(f"🔒 Cannot write to {path}, permission denied")
            return False

        except Exception as e:
            self._log("write", path, f"error: {e}")
            print(f"❌ Error writing {path}: {e}")
            return False

    def read_json(
        self,
        path: str,
        default: Optional[Dict] = None,
        create_missing: bool = True
    ) -> Dict:
        """
        Read JSON file with fallback.

        Args:
            path: JSON file path
            default: Default dict if file doesn't exist
            create_missing: Create file with default if missing

        Returns:
            Parsed JSON or default
        """
        default_dict = default if default is not None else {}

        content = self.read_file(path, default=json.dumps(default_dict, indent=2))

        try:
            return json.loads(content) if content else default_dict
        except json.JSONDecodeError as e:
            self._log("parse_json", path, f"invalid_json: {e}")
            print(f"⚠️  Invalid JSON in {path}, using default")
            if create_missing:
                self.write_file(path, json.dumps(default_dict, indent=2))
            return default_dict

    def write_json(
        self,
        path: str,
        data: Dict,
        create_dirs: bool = True,
        backup: bool = False,
        indent: int = 2
    ) -> bool:
        """
        Write JSON file with formatting.

        Args:
            path: JSON file path
            data: Dictionary to write
            create_dirs: Create parent directories
            backup: Backup existing file
            indent: JSON indentation

        Returns:
            True if successful
        """
        try:
            content = json.dumps(data, indent=indent)
            return self.write_file(path, content, create_dirs=create_dirs, backup=backup)
        except Exception as e:
            self._log("write_json", path, f"error: {e}")
            print(f"❌ Error writing JSON to {path}: {e}")
            return False

    def ensure_file_exists(
        self,
        path: str,
        default_content: str = "",
        overwrite: bool = False
    ) -> bool:
        """
        Ensure file exists, creating if needed.

        Args:
            path: File path
            default_content: Content for new file
            overwrite: Overwrite if exists

        Returns:
            True if file exists or was created
        """
        if os.path.exists(path) and not overwrite:
            return True

        return self.write_file(path, default_content, create_dirs=True)

    def safe_delete(
        self,
        path: str,
        backup: bool = True
    ) -> bool:
        """
        Safely delete file with optional backup.

        Args:
            path: File path to delete
            backup: Create backup before deleting

        Returns:
            True if deleted
        """
        try:
            if not os.path.exists(path):
                print(f"ℹ️  File {path} doesn't exist")
                return True

            if backup:
                backup_path = f"{path}.deleted"
                shutil.copy2(path, backup_path)
                self._log("backup", path, f"before_delete: {backup_path}")

            os.remove(path)
            self._log("delete", path, "success")
            return True

        except Exception as e:
            self._log("delete", path, f"error: {e}")
            print(f"❌ Error deleting {path}: {e}")
            return False

    @contextmanager
    def atomic_write(self, path: str):
        """
        Context manager for atomic file writes.

        Usage:
            with handler.atomic_write("config.json") as f:
                f.write(content)
        """
        temp_path = f"{path}.tmp"
        try:
            # Create parent directories
            Path(path).parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file
            with open(temp_path, 'w') as f:
                yield f

            # Atomic rename
            os.replace(temp_path, path)
            self._log("atomic_write", path, "success")

        except Exception as e:
            self._log("atomic_write", path, f"error: {e}")
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def with_retry(
        self,
        operation: Callable,
        max_retries: int = 3,
        backoff: float = 0.5
    ) -> Any:
        """
        Execute operation with retry logic.

        Args:
            operation: Function to execute
            max_retries: Maximum retry attempts
            backoff: Delay between retries (seconds)

        Returns:
            Operation result
        """
        import time

        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(backoff * (attempt + 1))
                else:
                    self._log("retry", "operation", f"failed_after_{max_retries}_attempts")
                    raise

    def _log(self, operation: str, path: str, status: str):
        """Log operation."""
        self.operations_log.append({
            "operation": operation,
            "path": path,
            "status": status
        })

    def get_log(self) -> list:
        """Get operations log."""
        return self.operations_log

    def print_log(self):
        """Print operations log."""
        print("\n📊 Operations Log:")
        for entry in self.operations_log:
            print(f"  {entry['operation']:15} {entry['path']:40} → {entry['status']}")


# Convenience functions
def safe_read(path: str, default: str = "") -> str:
    """Quick safe file read."""
    handler = ResilientFileHandler()
    return handler.read_file(path, default=default)


def safe_write(path: str, content: str) -> bool:
    """Quick safe file write."""
    handler = ResilientFileHandler()
    return handler.write_file(path, content)


def safe_read_json(path: str, default: Optional[Dict] = None) -> Dict:
    """Quick safe JSON read."""
    handler = ResilientFileHandler()
    return handler.read_json(path, default=default)


def safe_write_json(path: str, data: Dict) -> bool:
    """Quick safe JSON write."""
    handler = ResilientFileHandler()
    return handler.write_json(path, data)


# Example usage
if __name__ == "__main__":
    # Create handler
    handler = ResilientFileHandler(create_missing=True, default_content="# Default content\n")

    # Example 1: Read with auto-create
    print("\n=== Example 1: Read with Auto-Create ===")
    content = handler.read_file("test_files/config.txt", default="# Default config\n")
    print(f"Content: {content[:50]}...")

    # Example 2: JSON operations
    print("\n=== Example 2: JSON Operations ===")
    config = handler.read_json("test_files/settings.json", default={"version": "1.0"})
    print(f"Config: {config}")

    config["updated"] = True
    handler.write_json("test_files/settings.json", config)

    # Example 3: Atomic writes
    print("\n=== Example 3: Atomic Write ===")
    try:
        with handler.atomic_write("test_files/important.txt") as f:
            f.write("Critical data\n")
            f.write("More data\n")
        print("✓ Atomic write successful")
    except Exception as e:
        print(f"✗ Atomic write failed: {e}")

    # Example 4: Retry logic
    print("\n=== Example 4: With Retry ===")
    def flaky_operation():
        import random
        if random.random() < 0.7:
            raise IOError("Simulated failure")
        return "Success!"

    try:
        result = handler.with_retry(flaky_operation, max_retries=5)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed after retries: {e}")

    # Show log
    handler.print_log()

    # Cleanup
    import shutil
    if os.path.exists("test_files"):
        shutil.rmtree("test_files")
        print("\n🧹 Cleaned up test files")
