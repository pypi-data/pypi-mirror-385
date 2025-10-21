"""
Bash Tools for Executing Shell Commands

Provides tools for executing shell commands with safety controls and approval workflows.

⚠️ SECURITY WARNING ⚠️
======================
This tool uses shell=True and is vulnerable to command injection attacks!

**Command Injection Risk:**
- User input MUST be sanitized before being passed to bash_command
- Malicious input can execute arbitrary commands
- HIGH danger level requires approval workflow protection

**UNSAFE Examples (DO NOT USE):**
    >>> # UNSAFE: User input directly in command
    >>> user_input = "file.txt; rm -rf /"  # Malicious!
    >>> command = f"cat {user_input}"  # Command injection!
    >>> # This would execute: cat file.txt; rm -rf /

    >>> # UNSAFE: Unvalidated file paths
    >>> filename = "../../../etc/passwd"  # Path traversal!
    >>> command = f"cat {filename}"

**SAFE Examples (Use These Patterns):**
    >>> # SAFE: No user input in command
    >>> command = "ls -la /tmp"  # Hardcoded, safe

    >>> # SAFE: Validate and sanitize user input
    >>> import shlex
    >>> user_file = shlex.quote(user_input)  # Escape shell characters
    >>> command = f"cat {user_file}"

    >>> # SAFER: Use subprocess with shell=False (not available in this tool)
    >>> # subprocess.run(['cat', user_input], shell=False)  # No injection risk

**Protection Layers:**
1. HIGH danger level → Requires approval workflow
2. User review of command before execution
3. Timeout protection (default 30s, max configurable)
4. Working directory isolation (optional)

**Best Practices:**
- Avoid user input in commands when possible
- Use shlex.quote() to escape user input
- Validate all inputs against expected patterns
- Use least privilege (run as non-root user)
- Consider using safer alternatives (Python stdlib, dedicated tools)

Example:
    >>> from kaizen.tools import ToolRegistry, ToolExecutor
    >>> from kaizen.tools.builtin.bash import register_bash_tools
    >>>
    >>> registry = ToolRegistry()
    >>> register_bash_tools(registry)
    >>>
    >>> executor = ToolExecutor(registry=registry)
    >>> # SAFE: No user input, hardcoded command
    >>> result = await executor.execute("bash_command", {"command": "ls -la /tmp"})
    >>> print(result.result["stdout"])
"""

import subprocess
from typing import Any, Dict, Optional, TypedDict

from kaizen.tools import DangerLevel, ToolCategory, ToolParameter
from kaizen.tools.registry import ToolRegistry


class BashResult(TypedDict, total=False):
    """Type definition for bash_command tool results."""
    stdout: str
    stderr: str
    exit_code: int
    success: bool
    error: str  # Optional


def execute_bash_command(params: Dict[str, Any]) -> BashResult:
    """
    Execute a bash command in a subprocess.

    ⚠️ SECURITY WARNING: This function uses shell=True which is vulnerable to
    command injection attacks. User input MUST be sanitized before being
    passed to this function. Use shlex.quote() to escape user input.

    The HIGH danger level classification requires approval workflow, which
    provides a critical security layer by allowing human review before execution.

    Args:
        params: Dictionary with:
            - command (str): Shell command to execute (MUST be sanitized!)
            - timeout (int, optional): Command timeout in seconds (default 30)
            - working_dir (str, optional): Working directory for command execution

    Returns:
        Dictionary with:
            - stdout (str): Standard output from command
            - stderr (str): Standard error from command
            - exit_code (int): Process exit code
            - success (bool): True if exit_code == 0

    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout
        subprocess.SubprocessError: If command execution fails

    Security Notes:
        - Command injection risk: Malicious commands can be injected via unsanitized input
        - Privilege escalation: Commands run with same privileges as Python process
        - File system access: Commands have full access to file system (within permissions)
        - Network access: Commands can make network requests
        - Resource consumption: Commands can consume CPU/memory/disk

    Example (SAFE):
        >>> import shlex
        >>> user_file = shlex.quote(user_input)  # Escape special characters
        >>> params = {"command": f"cat {user_file}"}
        >>> result = execute_bash_command(params)

    Example (UNSAFE - DO NOT USE):
        >>> # UNSAFE: Direct user input can execute arbitrary commands!
        >>> params = {"command": f"cat {user_input}"}  # user_input = "; rm -rf /"
        >>> result = execute_bash_command(params)  # DANGER!
    """
    command = params["command"]
    timeout = params.get("timeout", 30)
    working_dir = params.get("working_dir", None)

    try:
        # SECURITY WARNING: shell=True enables command injection attacks!
        # This is inherently dangerous but necessary for shell features (pipes, wildcards, etc.)
        # HIGH danger level + approval workflow provides critical protection layer.
        # User input MUST be sanitized before reaching this function (use shlex.quote()).
        result = subprocess.run(
            command,
            shell=True,  # WARNING: Enables command injection! Protected by approval workflow.
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir,
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": result.returncode == 0,
        }

    except subprocess.TimeoutExpired as e:
        return {
            "stdout": e.stdout.decode() if e.stdout else "",
            "stderr": e.stderr.decode() if e.stderr else "",
            "exit_code": -1,
            "success": False,
            "error": f"Command timed out after {timeout}s",
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "success": False,
            "error": str(e),
        }


def register_bash_tools(registry: ToolRegistry) -> None:
    """
    Register bash tools to a registry.

    Args:
        registry: ToolRegistry instance to register tools to

    Registers:
        - bash_command: Execute shell commands (HIGH danger)

    Example:
        >>> registry = ToolRegistry()
        >>> register_bash_tools(registry)
        >>> tool = registry.get("bash_command")
        >>> print(tool.name)
    """
    # Bash command tool
    registry.register(
        name="bash_command",
        description="Execute a shell command in a subprocess",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.HIGH,
        parameters=[
            ToolParameter("command", str, "Shell command to execute", required=True),
            ToolParameter("timeout", int, "Command timeout in seconds (default 30)", required=False),
            ToolParameter("working_dir", str, "Working directory for command execution", required=False),
        ],
        returns={
            "stdout": "str",
            "stderr": "str",
            "exit_code": "int",
            "success": "bool",
        },
        executor=execute_bash_command,
        approval_message_template="Execute bash command: {command}",
    )
