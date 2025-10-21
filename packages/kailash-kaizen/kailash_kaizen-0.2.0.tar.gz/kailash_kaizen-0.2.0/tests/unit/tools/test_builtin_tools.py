"""
Unit Tests for Builtin Tools (Tier 1)

Tests all 12 builtin tools without real Control Protocol integration.
Validates tool execution, parameter handling, and error cases.

Test Coverage:
    - Tool registration (all 12 tools)
    - Bash tools: bash_command
    - File tools: read_file, write_file, delete_file, list_directory, file_exists
    - API tools: http_get, http_post, http_put, http_delete
    - Web tools: fetch_url, extract_links
"""

import tempfile
from pathlib import Path

import pytest

from kaizen.tools import ToolExecutor, ToolRegistry
from kaizen.tools.builtin import register_builtin_tools


@pytest.fixture
def registry():
    """Create registry with all builtin tools."""
    reg = ToolRegistry()
    register_builtin_tools(reg)
    return reg


@pytest.fixture
def executor(registry):
    """Create executor without control protocol (autonomous mode)."""
    return ToolExecutor(registry=registry)


@pytest.mark.asyncio
async def test_builtin_tools_registration(registry):
    """Test that all 12 builtin tools are registered correctly."""
    assert registry.count() == 12

    # Bash tools
    assert registry.get("bash_command") is not None

    # File tools
    assert registry.get("read_file") is not None
    assert registry.get("write_file") is not None
    assert registry.get("delete_file") is not None
    assert registry.get("list_directory") is not None
    assert registry.get("file_exists") is not None

    # API tools
    assert registry.get("http_get") is not None
    assert registry.get("http_post") is not None
    assert registry.get("http_put") is not None
    assert registry.get("http_delete") is not None

    # Web tools
    assert registry.get("fetch_url") is not None
    assert registry.get("extract_links") is not None


# ============================================================================
# Bash Tools Tests
# ============================================================================


@pytest.mark.asyncio
async def test_bash_command_success(executor):
    """Test successful bash command execution."""
    result = await executor.execute("bash_command", {"command": "echo 'Hello World'"})

    assert result.success is True
    assert result.result["success"] is True
    assert result.result["exit_code"] == 0
    assert "Hello World" in result.result["stdout"]
    assert result.result["stderr"] == ""


@pytest.mark.asyncio
async def test_bash_command_failure(executor):
    """Test bash command that fails."""
    result = await executor.execute(
        "bash_command", {"command": "exit 1"}  # Command that exits with error
    )

    assert result.success is True  # Tool executed successfully
    assert result.result["success"] is False  # But command failed
    assert result.result["exit_code"] == 1


@pytest.mark.asyncio
async def test_bash_command_with_working_dir(executor):
    """Test bash command with custom working directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await executor.execute(
            "bash_command", {"command": "pwd", "working_dir": tmpdir}
        )

        assert result.success is True
        assert tmpdir in result.result["stdout"]


# ============================================================================
# File Tools Tests
# ============================================================================


@pytest.mark.asyncio
async def test_read_file_success(executor):
    """Test reading a file that exists."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Test content")
        temp_path = f.name

    try:
        result = await executor.execute("read_file", {"path": temp_path})

        assert result.success is True
        assert result.result["exists"] is True
        assert result.result["content"] == "Test content"
        assert result.result["size"] == len("Test content")
    finally:
        Path(temp_path).unlink()


@pytest.mark.asyncio
async def test_read_file_not_found(executor):
    """Test reading a file that doesn't exist."""
    result = await executor.execute("read_file", {"path": "/nonexistent/file.txt"})

    assert result.success is True  # Tool executed successfully
    assert result.result["exists"] is False
    assert result.result["content"] == ""


@pytest.mark.asyncio
async def test_write_file_success(executor):
    """Test writing to a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.txt"

        result = await executor.execute(
            "write_file", {"path": str(file_path), "content": "Hello World"}
        )

        assert result.success is True
        assert result.result["written"] is True
        assert result.result["size"] == len("Hello World")

        # Verify file was actually written
        assert file_path.exists()
        assert file_path.read_text() == "Hello World"


@pytest.mark.asyncio
async def test_write_file_create_dirs(executor):
    """Test writing file with automatic directory creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "subdir" / "test.txt"

        result = await executor.execute(
            "write_file",
            {"path": str(file_path), "content": "Test", "create_dirs": True},
        )

        assert result.success is True
        assert result.result["written"] is True
        assert file_path.exists()


@pytest.mark.asyncio
async def test_delete_file_success(executor):
    """Test deleting a file that exists."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name

    result = await executor.execute("delete_file", {"path": temp_path})

    assert result.success is True
    assert result.result["deleted"] is True
    assert result.result["existed"] is True
    assert not Path(temp_path).exists()


@pytest.mark.asyncio
async def test_delete_file_not_found(executor):
    """Test deleting a file that doesn't exist."""
    result = await executor.execute("delete_file", {"path": "/nonexistent/file.txt"})

    assert result.success is True
    assert result.result["deleted"] is False
    assert result.result["existed"] is False


@pytest.mark.asyncio
async def test_list_directory_success(executor):
    """Test listing directory contents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        (Path(tmpdir) / "file1.txt").write_text("test1")
        (Path(tmpdir) / "file2.txt").write_text("test2")
        (Path(tmpdir) / "subdir").mkdir()

        result = await executor.execute("list_directory", {"path": tmpdir})

        assert result.success is True
        assert "file1.txt" in result.result["files"]
        assert "file2.txt" in result.result["files"]
        assert "subdir" in result.result["directories"]
        assert result.result["count"] == 3


@pytest.mark.asyncio
async def test_list_directory_recursive(executor):
    """Test listing directory contents recursively."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create nested structure
        (Path(tmpdir) / "file.txt").write_text("test")
        subdir = Path(tmpdir) / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested")

        result = await executor.execute(
            "list_directory", {"path": tmpdir, "recursive": True}
        )

        assert result.success is True
        assert "file.txt" in result.result["files"]
        assert any("nested.txt" in f for f in result.result["files"])


@pytest.mark.asyncio
async def test_file_exists_true(executor):
    """Test checking if file exists (true case)."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name

    try:
        result = await executor.execute("file_exists", {"path": temp_path})

        assert result.success is True
        assert result.result["exists"] is True
        assert result.result["is_file"] is True
        assert result.result["is_directory"] is False
    finally:
        Path(temp_path).unlink()


@pytest.mark.asyncio
async def test_file_exists_false(executor):
    """Test checking if file exists (false case)."""
    result = await executor.execute("file_exists", {"path": "/nonexistent/file.txt"})

    assert result.success is True
    assert result.result["exists"] is False
    assert result.result["is_file"] is False
    assert result.result["is_directory"] is False


# ============================================================================
# API Tools Tests (Mock-based - no real HTTP requests)
# ============================================================================


@pytest.mark.asyncio
async def test_http_tools_parameter_validation(registry):
    """Test that HTTP tools have correct parameters."""
    http_get = registry.get("http_get")
    assert http_get is not None
    assert len(http_get.parameters) == 3  # url, headers, timeout

    http_post = registry.get("http_post")
    assert http_post is not None
    assert len(http_post.parameters) == 4  # url, data, headers, timeout


# ============================================================================
# Web Tools Tests
# ============================================================================


@pytest.mark.asyncio
async def test_extract_links_success(executor):
    """Test extracting links from HTML."""
    html = """
    <html>
        <body>
            <a href="https://example.com">Link 1</a>
            <a href="/path/to/page">Link 2</a>
            <a href="#anchor">Anchor</a>
        </body>
    </html>
    """

    result = await executor.execute("extract_links", {"html": html})

    assert result.success is True
    assert "https://example.com" in result.result["links"]
    assert "/path/to/page" in result.result["links"]
    assert result.result["count"] >= 2
    # Anchor links should be skipped
    assert "#anchor" not in result.result["links"]


@pytest.mark.asyncio
async def test_extract_links_with_base_url(executor):
    """Test extracting links with base URL for relative links."""
    html = '<a href="/page">Link</a>'

    result = await executor.execute(
        "extract_links", {"html": html, "base_url": "https://example.com"}
    )

    assert result.success is True
    assert any("https://example.com/page" in link for link in result.result["links"])


@pytest.mark.asyncio
async def test_extract_links_empty_html(executor):
    """Test extracting links from empty HTML."""
    result = await executor.execute("extract_links", {"html": ""})

    assert result.success is True
    assert result.result["count"] == 0
    assert result.result["links"] == []


# ============================================================================
# Parameter Validation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_missing_required_parameter(executor):
    """Test tool execution with missing required parameter."""
    result = await executor.execute("read_file", {})  # Missing 'path' parameter

    assert result.success is False
    assert "Required parameter 'path' missing" in result.error


@pytest.mark.asyncio
async def test_unknown_parameter(executor):
    """Test tool execution with unknown parameter."""
    result = await executor.execute(
        "read_file", {"path": "/tmp/test.txt", "unknown_param": "value"}
    )

    assert result.success is False
    assert "Unknown parameter 'unknown_param'" in result.error
