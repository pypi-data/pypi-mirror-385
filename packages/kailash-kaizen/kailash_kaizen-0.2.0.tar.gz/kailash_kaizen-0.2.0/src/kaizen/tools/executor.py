"""
Tool Executor for Safe Tool Execution

Executes tools with approval workflows based on danger levels.
Integrates with ControlProtocol for interactive approval requests.

Architecture:
    ToolExecutor manages execution of registered tools with automatic
    approval workflows based on DangerLevel. For dangerous tools (HIGH/CRITICAL),
    it uses ControlProtocol to request user approval before execution.

Example:
    >>> from kaizen.tools.executor import ToolExecutor
    >>> from kaizen.tools.registry import ToolRegistry
    >>> from kaizen.core.autonomy.control.protocol import ControlProtocol
    >>>
    >>> registry = ToolRegistry()
    >>> protocol = ControlProtocol(transport)
    >>> executor = ToolExecutor(registry=registry, control_protocol=protocol)
    >>>
    >>> # Execute safe tool (no approval needed)
    >>> result = await executor.execute("read_file", {"path": "data.txt"})
    >>> print(result.success)  # True
    >>> print(result.result)  # {"content": "...", "size": 123}
    >>>
    >>> # Execute dangerous tool (approval requested)
    >>> result = await executor.execute("bash_command", {"command": "rm -rf /"})
    >>> print(result.approved)  # False (user denied)
    >>> print(result.success)  # False
"""

import logging
import time
from typing import Any, Dict, Optional

from kaizen.core.autonomy.control.protocol import ControlProtocol, ControlRequest
from kaizen.tools.registry import ToolRegistry
from kaizen.tools.types import DangerLevel, ToolResult

# Configure structured logger
logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executes tools with approval workflows based on danger levels.

    Manages tool execution with automatic approval requests for dangerous
    operations. Integrates with ControlProtocol for interactive user approval.

    Attributes:
        registry: ToolRegistry instance for tool lookup
        control_protocol: Optional ControlProtocol for approval workflows
        auto_approve_safe: Auto-approve SAFE tools (default True)
        timeout: Default approval timeout in seconds (default 30.0)

    Approval Workflow:
        - SAFE: Auto-approved, no user interaction
        - LOW: Auto-approved for single operations, batch operations may require approval
        - MEDIUM: Requires approval for write operations
        - HIGH: Always requires approval
        - CRITICAL: Requires explicit confirmation

    Example:
        >>> executor = ToolExecutor(registry=registry, control_protocol=protocol)
        >>> result = await executor.execute("bash_command", {"command": "ls -la"})
        >>> if result.success:
        ...     print(result.result)
        ... else:
        ...     print(f"Error: {result.error}")
    """

    def __init__(
        self,
        registry: ToolRegistry,
        control_protocol: Optional[ControlProtocol] = None,
        auto_approve_safe: bool = True,
        timeout: float = 30.0,
    ):
        """
        Initialize ToolExecutor.

        Args:
            registry: ToolRegistry instance for tool lookup
            control_protocol: Optional ControlProtocol for approval workflows
            auto_approve_safe: Auto-approve SAFE tools (default True)
            timeout: Default approval timeout in seconds (default 30.0)

        Example:
            >>> from kaizen.tools.registry import get_global_registry
            >>> registry = get_global_registry()
            >>> executor = ToolExecutor(registry=registry)
        """
        self.registry = registry
        self.control_protocol = control_protocol
        self.auto_approve_safe = auto_approve_safe
        self.timeout = timeout

        # Log executor initialization
        logger.info(
            "ToolExecutor initialized",
            extra={
                "tool_count": registry.count(),
                "has_control_protocol": control_protocol is not None,
                "auto_approve_safe": auto_approve_safe,
                "default_timeout": timeout,
            },
        )

    async def execute(
        self,
        tool_name: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> ToolResult:
        """
        Execute a tool with approval workflow based on danger level.

        Args:
            tool_name: Name of tool to execute
            params: Parameters to pass to tool
            timeout: Optional approval timeout (uses default if None)

        Returns:
            ToolResult with execution status and result/error

        Raises:
            No exceptions raised - all errors returned in ToolResult

        Example:
            >>> result = await executor.execute("read_file", {"path": "data.txt"})
            >>> if result.success:
            ...     print(f"File content: {result.result['content']}")
            ... else:
            ...     print(f"Error: {result.error}")
        """
        start_time = time.perf_counter()

        # Log tool execution start
        logger.info(
            "Tool execution started",
            extra={
                "tool_name": tool_name,
                "param_count": len(params) if params is not None else 0,
            },
        )

        # Get tool definition
        tool = self.registry.get(tool_name)
        if tool is None:
            logger.error(
                "Tool not found in registry",
                extra={
                    "tool_name": tool_name,
                    "error_type": "ToolNotFoundError",
                },
            )
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' not found in registry",
                error_type="ToolNotFoundError",
                execution_time_ms=0.0,
            )

        # Validate parameters
        try:
            tool.validate_parameters(params)
        except (ValueError, TypeError) as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "Parameter validation failed",
                extra={
                    "tool_name": tool_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time_ms": elapsed_ms,
                },
            )
            return ToolResult.from_exception(
                tool_name=tool_name,
                exception=e,
                execution_time_ms=elapsed_ms,
            )

        # Request approval if needed
        approval_result = await self._request_approval(tool, params, timeout)
        if not approval_result["approved"]:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.warning(
                "Tool execution denied - approval not granted",
                extra={
                    "tool_name": tool_name,
                    "reason": approval_result.get("reason", "User denied approval"),
                    "danger_level": tool.danger_level.value,
                    "execution_time_ms": elapsed_ms,
                },
            )
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=approval_result.get("reason", "User denied approval"),
                error_type="ApprovalDeniedError",
                execution_time_ms=elapsed_ms,
                approved=False,
            )

        # Execute tool
        try:
            result = tool.executor(params)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "Tool execution completed successfully",
                extra={
                    "tool_name": tool_name,
                    "execution_time_ms": elapsed_ms,
                    "danger_level": tool.danger_level.value,
                    "approved": approval_result.get("approved"),
                },
            )

            return ToolResult(
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time_ms=elapsed_ms,
                approved=approval_result.get("approved"),
            )

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "Tool execution failed with exception",
                extra={
                    "tool_name": tool_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time_ms": elapsed_ms,
                    "danger_level": tool.danger_level.value,
                },
                exc_info=True,  # Include stack trace
            )
            return ToolResult.from_exception(
                tool_name=tool_name,
                exception=e,
                execution_time_ms=elapsed_ms,
                approved=approval_result.get("approved"),
            )

    async def _request_approval(
        self,
        tool: "ToolDefinition",  # type: ignore # noqa: F821
        params: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Request user approval for tool execution based on danger level.

        Args:
            tool: ToolDefinition to request approval for
            params: Parameters being passed to tool
            timeout: Optional approval timeout (uses default if None)

        Returns:
            Dict with "approved" (bool) and optional "reason" (str)

        Approval Logic:
            - SAFE: Auto-approved if auto_approve_safe=True
            - LOW: Auto-approved for single operations
            - MEDIUM: Requires approval if ControlProtocol available
            - HIGH: Requires approval if ControlProtocol available
            - CRITICAL: Requires explicit confirmation if ControlProtocol available

        Example:
            >>> approval = await executor._request_approval(tool, params)
            >>> if approval["approved"]:
            ...     # Proceed with execution
        """
        # Auto-approve safe tools
        if tool.danger_level == DangerLevel.SAFE and self.auto_approve_safe:
            logger.debug(
                "Tool auto-approved (SAFE danger level)",
                extra={"tool_name": tool.name, "danger_level": "SAFE"},
            )
            return {"approved": True}

        # Auto-approve low danger tools (single operations)
        if tool.danger_level == DangerLevel.LOW:
            logger.debug(
                "Tool auto-approved (LOW danger level)",
                extra={"tool_name": tool.name, "danger_level": "LOW"},
            )
            return {"approved": True}

        # If no control protocol, auto-approve (autonomous mode)
        if self.control_protocol is None:
            logger.warning(
                "Tool auto-approved - no control protocol (autonomous mode)",
                extra={"tool_name": tool.name, "danger_level": tool.danger_level.value},
            )
            return {"approved": True}

        # For MEDIUM/HIGH/CRITICAL, request user approval
        approval_message = tool.get_approval_message(params)
        approval_details = tool.get_approval_details(params)

        logger.info(
            "Requesting user approval for tool execution",
            extra={
                "tool_name": tool.name,
                "danger_level": tool.danger_level.value,
                "approval_message": approval_message,
            },
        )

        # Create approval request
        request = ControlRequest.create(
            type="approval",
            data={
                "message": approval_message,
                "details": approval_details,
            },
        )

        # Send approval request
        use_timeout = timeout if timeout is not None else self.timeout
        try:
            response = await self.control_protocol.send_request(
                request, timeout=use_timeout
            )

            # Check response
            if response is None:
                logger.warning(
                    "Approval request timed out",
                    extra={
                        "tool_name": tool.name,
                        "timeout": use_timeout,
                    },
                )
                return {
                    "approved": False,
                    "reason": "Approval request timed out",
                }

            approved = response.data.get("approved", False)
            reason = response.data.get("reason", "")

            logger.info(
                "Approval response received",
                extra={
                    "tool_name": tool.name,
                    "approved": approved,
                    "reason": reason,
                },
            )

            return {
                "approved": approved,
                "reason": reason,
            }

        except Exception as e:
            # If approval fails, deny by default (fail-safe)
            logger.error(
                "Approval request failed with exception",
                extra={
                    "tool_name": tool.name,
                    "error": str(e),
                },
                exc_info=True,
            )
            return {
                "approved": False,
                "reason": f"Approval request failed: {str(e)}",
            }

    async def execute_batch(
        self,
        executions: list[Dict[str, Any]],
        timeout: Optional[float] = None,
    ) -> list[ToolResult]:
        """
        Execute multiple tools in sequence.

        Args:
            executions: List of dicts with "tool_name" and "params" keys
            timeout: Optional approval timeout for each tool

        Returns:
            List of ToolResult objects (one per execution)

        Example:
            >>> executions = [
            ...     {"tool_name": "read_file", "params": {"path": "a.txt"}},
            ...     {"tool_name": "read_file", "params": {"path": "b.txt"}},
            ... ]
            >>> results = await executor.execute_batch(executions)
            >>> for result in results:
            ...     print(f"{result.tool_name}: {result.success}")
        """
        logger.info(
            "Batch execution started",
            extra={
                "execution_count": len(executions),
                "timeout": timeout,
            },
        )

        results = []
        start_time = time.perf_counter()

        for i, execution in enumerate(executions):
            tool_name = execution.get("tool_name")
            params = execution.get("params", {})

            if tool_name is None:
                logger.error(
                    "Invalid batch execution item - missing tool_name",
                    extra={"batch_index": i},
                )
                results.append(
                    ToolResult(
                        tool_name="unknown",
                        success=False,
                        error="Missing 'tool_name' in execution",
                        error_type="InvalidExecutionError",
                        execution_time_ms=0.0,
                    )
                )
                continue

            result = await self.execute(tool_name, params, timeout=timeout)
            results.append(result)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        success_count = sum(1 for r in results if r.success)
        failure_count = len(results) - success_count

        logger.info(
            "Batch execution completed",
            extra={
                "total_executions": len(results),
                "successful": success_count,
                "failed": failure_count,
                "total_time_ms": elapsed_ms,
            },
        )

        return results

    def set_control_protocol(self, control_protocol: ControlProtocol) -> None:
        """
        Set or update the control protocol for approval workflows.

        Args:
            control_protocol: ControlProtocol instance

        Example:
            >>> executor = ToolExecutor(registry=registry)  # No protocol
            >>> executor.set_control_protocol(protocol)  # Add protocol later
        """
        self.control_protocol = control_protocol

    def has_control_protocol(self) -> bool:
        """
        Check if executor has a control protocol configured.

        Returns:
            True if control_protocol is set, False otherwise

        Example:
            >>> if not executor.has_control_protocol():
            ...     print("Running in autonomous mode (no approvals)")
        """
        return self.control_protocol is not None

    def get_registry(self) -> ToolRegistry:
        """
        Get the tool registry.

        Returns:
            ToolRegistry instance

        Example:
            >>> registry = executor.get_registry()
            >>> print(f"Total tools: {registry.count()}")
        """
        return self.registry
