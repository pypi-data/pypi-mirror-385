"""
File Tools for File System Operations

Provides tools for reading, writing, deleting files and listing directories.

Example:
    >>> from kaizen.tools import ToolRegistry, ToolExecutor
    >>> from kaizen.tools.builtin.file import register_file_tools
    >>>
    >>> registry = ToolRegistry()
    >>> register_file_tools(registry)
    >>>
    >>> executor = ToolExecutor(registry=registry)
    >>> result = await executor.execute("read_file", {"path": "/tmp/test.txt"})
    >>> print(result.result["content"])
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict

from kaizen.tools import DangerLevel, ToolCategory, ToolParameter
from kaizen.tools.registry import ToolRegistry


class ReadFileResult(TypedDict, total=False):
    """Type definition for read_file tool results."""
    content: str
    size: int
    exists: bool
    error: str  # Optional


class WriteFileResult(TypedDict, total=False):
    """Type definition for write_file tool results."""
    written: bool
    size: int
    path: str
    error: str  # Optional


class DeleteFileResult(TypedDict, total=False):
    """Type definition for delete_file tool results."""
    deleted: bool
    existed: bool
    path: str
    error: str  # Optional


class ListDirectoryResult(TypedDict, total=False):
    """Type definition for list_directory tool results."""
    files: List[str]
    directories: List[str]
    count: int
    path: str
    error: str  # Optional


class FileExistsResult(TypedDict, total=False):
    """Type definition for file_exists tool results."""
    exists: bool
    is_file: bool
    is_directory: bool
    path: str
    error: str  # Optional

# Security constants
DANGEROUS_SYSTEM_PATHS = {
    "/etc",  # System configuration
    "/sys",  # Kernel interface
    "/proc",  # Process information
    "/dev",  # Device files
    "/boot",  # Boot files
    "/root",  # Root user home
}


def validate_safe_path(path: str, allowed_base: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate file path for security (path traversal protection).

    Validates that:
    1. Path does not contain '..' (path traversal)
    2. Path does not target dangerous system directories
    3. Path is within allowed_base if specified (sandboxing)

    Args:
        path: File path to validate
        allowed_base: Optional base directory for sandboxing (path must be within this)

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if path is safe, False otherwise
        - error_message: None if valid, error description otherwise

    Example:
        >>> is_valid, error = validate_safe_path("/tmp/test.txt")
        >>> assert is_valid is True
        >>> is_valid, error = validate_safe_path("../etc/passwd")
        >>> assert is_valid is False
    """
    if not path:
        return False, "Path cannot be empty"

    try:
        # Normalize path (resolves .., //, etc.)
        normalized_path = Path(path)

        # Convert to absolute path for security checks
        # Note: We use os.path.abspath instead of Path.resolve() to avoid
        # following symlinks, which could be used for attacks
        abs_path_str = os.path.abspath(str(normalized_path))
        abs_path = Path(abs_path_str)

        # Check for path traversal attempts (..)
        # After normalization, any remaining .. indicates traversal attempt
        path_parts = abs_path.parts
        for part in path_parts:
            if part == "..":
                return False, f"Path traversal detected (contains '..'): {path}"

        # Also check the original path string for .. patterns
        # This catches cases where normalization might not fully resolve traversal
        if ".." in path:
            return False, f"Path traversal detected (contains '..'): {path}"

        # Check for dangerous system paths
        for dangerous_path in DANGEROUS_SYSTEM_PATHS:
            # Check if path starts with or is within a dangerous directory
            try:
                # Use relative_to to check if path is within dangerous directory
                abs_path.relative_to(dangerous_path)
                return False, f"Access to system path is not allowed: {dangerous_path}"
            except ValueError:
                # Path is not within this dangerous directory, continue checking
                continue

        # Optional: Check sandboxing (path must be within allowed_base)
        if allowed_base is not None:
            allowed_base_path = Path(os.path.abspath(allowed_base))
            try:
                abs_path.relative_to(allowed_base_path)
            except ValueError:
                return (
                    False,
                    f"Path is outside allowed base directory. Path: {abs_path_str}, Allowed base: {allowed_base}",
                )

        return True, None

    except Exception as e:
        return False, f"Invalid path: {str(e)}"


def read_file_tool(params: Dict[str, Any]) -> ReadFileResult:
    """
    Read file contents.

    Args:
        params: Dictionary with:
            - path (str): File path to read
            - encoding (str, optional): File encoding (default 'utf-8')

    Returns:
        Dictionary with:
            - content (str): File contents
            - size (int): File size in bytes
            - exists (bool): True if file exists
    """
    path = params["path"]
    encoding = params.get("encoding", "utf-8")

    # Security validation: path safety
    is_valid, error = validate_safe_path(path)
    if not is_valid:
        return {
            "content": "",
            "size": 0,
            "exists": False,
            "error": f"Path validation failed: {error}",
        }

    try:
        file_path = Path(path)
        if not file_path.exists():
            return {"content": "", "size": 0, "exists": False, "error": "File not found"}

        if not file_path.is_file():
            return {
                "content": "",
                "size": 0,
                "exists": True,
                "error": "Path is not a file",
            }

        content = file_path.read_text(encoding=encoding)
        size = file_path.stat().st_size

        return {"content": content, "size": size, "exists": True}

    except Exception as e:
        return {"content": "", "size": 0, "exists": False, "error": str(e)}


def write_file_tool(params: Dict[str, Any]) -> WriteFileResult:
    """
    Write content to a file.

    Args:
        params: Dictionary with:
            - path (str): File path to write
            - content (str): Content to write
            - encoding (str, optional): File encoding (default 'utf-8')
            - create_dirs (bool, optional): Create parent directories if needed (default True)

    Returns:
        Dictionary with:
            - written (bool): True if write succeeded
            - size (int): Bytes written
            - path (str): Absolute file path
    """
    path = params["path"]
    content = params["content"]
    encoding = params.get("encoding", "utf-8")
    create_dirs = params.get("create_dirs", True)

    # Security validation: path safety
    is_valid, error = validate_safe_path(path)
    if not is_valid:
        return {
            "written": False,
            "size": 0,
            "path": path,
            "error": f"Path validation failed: {error}",
        }

    try:
        file_path = Path(path)

        # Create parent directories if needed
        if create_dirs and not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        file_path.write_text(content, encoding=encoding)
        size = file_path.stat().st_size

        return {
            "written": True,
            "size": size,
            "path": str(file_path.absolute()),
        }

    except Exception as e:
        return {"written": False, "size": 0, "path": path, "error": str(e)}


def delete_file_tool(params: Dict[str, Any]) -> DeleteFileResult:
    """
    Delete a file.

    Args:
        params: Dictionary with:
            - path (str): File path to delete

    Returns:
        Dictionary with:
            - deleted (bool): True if deletion succeeded
            - existed (bool): True if file existed before deletion
            - path (str): File path
    """
    path = params["path"]

    # Security validation: path safety
    is_valid, error = validate_safe_path(path)
    if not is_valid:
        return {
            "deleted": False,
            "existed": False,
            "path": path,
            "error": f"Path validation failed: {error}",
        }

    try:
        file_path = Path(path)
        existed = file_path.exists()

        if existed:
            if file_path.is_file():
                file_path.unlink()
                return {"deleted": True, "existed": True, "path": path}
            else:
                return {
                    "deleted": False,
                    "existed": True,
                    "path": path,
                    "error": "Path is not a file",
                }
        else:
            return {"deleted": False, "existed": False, "path": path}

    except Exception as e:
        return {"deleted": False, "existed": False, "path": path, "error": str(e)}


def list_directory_tool(params: Dict[str, Any]) -> ListDirectoryResult:
    """
    List files and directories in a directory.

    Args:
        params: Dictionary with:
            - path (str): Directory path to list
            - recursive (bool, optional): List recursively (default False)
            - include_hidden (bool, optional): Include hidden files (default False)

    Returns:
        Dictionary with:
            - files (list[str]): List of file paths
            - directories (list[str]): List of directory paths
            - count (int): Total number of items
            - path (str): Directory path
    """
    path = params["path"]
    recursive = params.get("recursive", False)
    include_hidden = params.get("include_hidden", False)

    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return {
                "files": [],
                "directories": [],
                "count": 0,
                "path": path,
                "error": "Directory not found",
            }

        if not dir_path.is_dir():
            return {
                "files": [],
                "directories": [],
                "count": 0,
                "path": path,
                "error": "Path is not a directory",
            }

        files = []
        directories = []

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for item in dir_path.glob(pattern):
            # Skip hidden files unless requested
            if not include_hidden and item.name.startswith("."):
                continue

            relative_path = str(item.relative_to(dir_path))

            if item.is_file():
                files.append(relative_path)
            elif item.is_dir():
                directories.append(relative_path)

        return {
            "files": sorted(files),
            "directories": sorted(directories),
            "count": len(files) + len(directories),
            "path": path,
        }

    except Exception as e:
        return {
            "files": [],
            "directories": [],
            "count": 0,
            "path": path,
            "error": str(e),
        }


def file_exists_tool(params: Dict[str, Any]) -> FileExistsResult:
    """
    Check if a file exists.

    Args:
        params: Dictionary with:
            - path (str): File path to check

    Returns:
        Dictionary with:
            - exists (bool): True if file exists
            - is_file (bool): True if path is a file
            - is_directory (bool): True if path is a directory
            - path (str): File path
    """
    path = params["path"]

    try:
        file_path = Path(path)
        exists = file_path.exists()

        return {
            "exists": exists,
            "is_file": file_path.is_file() if exists else False,
            "is_directory": file_path.is_dir() if exists else False,
            "path": path,
        }

    except Exception as e:
        return {
            "exists": False,
            "is_file": False,
            "is_directory": False,
            "path": path,
            "error": str(e),
        }


def register_file_tools(registry: ToolRegistry) -> None:
    """
    Register file tools to a registry.

    Args:
        registry: ToolRegistry instance to register tools to

    Registers:
        - read_file: Read file contents (LOW danger)
        - write_file: Write to file (MEDIUM danger)
        - delete_file: Delete file (HIGH danger)
        - list_directory: List directory contents (SAFE)
        - file_exists: Check if file exists (SAFE)

    Example:
        >>> registry = ToolRegistry()
        >>> register_file_tools(registry)
        >>> tool = registry.get("read_file")
        >>> print(tool.name)
    """
    # Read file tool
    registry.register(
        name="read_file",
        description="Read contents of a file",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.LOW,
        parameters=[
            ToolParameter("path", str, "File path to read", required=True),
            ToolParameter("encoding", str, "File encoding (default 'utf-8')", required=False),
        ],
        returns={"content": "str", "size": "int", "exists": "bool"},
        executor=read_file_tool,
    )

    # Write file tool
    registry.register(
        name="write_file",
        description="Write content to a file",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.MEDIUM,
        parameters=[
            ToolParameter("path", str, "File path to write", required=True),
            ToolParameter("content", str, "Content to write", required=True),
            ToolParameter("encoding", str, "File encoding (default 'utf-8')", required=False),
            ToolParameter("create_dirs", bool, "Create parent directories if needed (default True)", required=False),
        ],
        returns={"written": "bool", "size": "int", "path": "str"},
        executor=write_file_tool,
        approval_message_template="Write to file: {path}",
    )

    # Delete file tool
    registry.register(
        name="delete_file",
        description="Delete a file",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.HIGH,
        parameters=[
            ToolParameter(
                name="path", type=str, description="File path to delete", required=True
            ),
        ],
        returns={"deleted": "bool", "existed": "bool", "path": "str"},
        executor=delete_file_tool,
        approval_message_template="Delete file: {path}",
    )

    # List directory tool
    registry.register(
        name="list_directory",
        description="List files and directories in a directory",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.SAFE,
        parameters=[
            ToolParameter(
                name="path", type=str, description="Directory path to list", required=True
            ),
            ToolParameter(
                name="recursive",
                type=bool,
                description="List recursively (default False)",
                required=False,
            ),
            ToolParameter(
                name="include_hidden",
                type=bool,
                description="Include hidden files (default False)",
                required=False,
            ),
        ],
        returns={
            "files": "list[str]",
            "directories": "list[str]",
            "count": "int",
            "path": "str",
        },
        executor=list_directory_tool,
    )

    # File exists tool
    registry.register(
        name="file_exists",
        description="Check if a file exists",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.SAFE,
        parameters=[
            ToolParameter(
                name="path", type=str, description="File path to check", required=True
            ),
        ],
        returns={
            "exists": "bool",
            "is_file": "bool",
            "is_directory": "bool",
            "path": "str",
        },
        executor=file_exists_tool,
    )
