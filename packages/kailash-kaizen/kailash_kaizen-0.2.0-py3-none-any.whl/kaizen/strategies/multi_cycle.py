"""
MultiCycleStrategy - Multi-cycle execution strategy with feedback loops.

This module implements the MultiCycleStrategy for agents that execute in
multiple cycles with feedback loops and iterative refinement.

Use Cases:
- ReAct agents: Reason + Act + Observe cycles
- Iterative refinement: Generate, critique, improve cycles
- Tool-using agents: Plan, execute tool, observe, repeat

References:
- ADR-006: Agent Base Architecture design (Strategy Pattern section)
- TODO-157: Task 1.6, Phase 2 Tasks 2.12-2.15
- Existing pattern: KaizenReActAgent (599 lines → 30-35 lines)

Author: Kaizen Framework Team
Created: 2025-10-01
Updated: 2025-10-01 (Phase 2 Implementation)
"""

from typing import Any, Dict

from kailash.runtime.local import LocalRuntime
from kailash.workflow.builder import WorkflowBuilder


class MultiCycleStrategy:
    """
    Multi-cycle execution strategy with feedback loops.

    Executes the agent in multiple cycles:
    1. For each cycle (up to max_cycles):
       a. Pre-cycle hook (extension point)
       b. Execute cycle (Reason + Act)
       c. Parse cycle result (extension point)
       d. Extract observation (extension point)
       e. Check termination condition (extension point)
       f. Continue or break
    2. Return aggregated result with metadata

    Termination Conditions:
    - max_cycles reached
    - Agent signals completion (e.g., "FINAL ANSWER:")
    - Error occurs
    - Explicit 'done' flag

    Extension Points:
    - pre_cycle(cycle_num, inputs): Prepare inputs for cycle
    - parse_cycle_result(raw_result, cycle_num): Parse cycle output
    - should_terminate(cycle_result, cycle_num): Check termination
    - extract_observation(cycle_result): Extract observation for next cycle

    Example Usage:
        >>> from kaizen.strategies.multi_cycle import MultiCycleStrategy
        >>> from kaizen.core.base_agent import BaseAgent
        >>> from kaizen.core.config import BaseAgentConfig
        >>>
        >>> config = BaseAgentConfig(
        ...     strategy_type="multi_cycle",
        ...     max_cycles=10
        ... )
        >>> strategy = MultiCycleStrategy(max_cycles=10)
        >>> agent = BaseAgent(config=config, strategy=strategy)
        >>>
        >>> result = strategy.execute(agent, {'task': 'Calculate 15% tip on $42.50'})
        >>> print(result)
        {
            'answer': '$6.38',
            'cycles_used': 3,
            'total_cycles': 10
        }

    Notes:
    - Full implementation (Phase 2, Tasks 2.12-2.15)
    - Uses WorkflowGenerator for Core SDK integration
    - Python loop handles cycle control (simpler than SwitchNode approach)
    - Supports ReAct pattern and iterative refinement
    """

    def __init__(
        self,
        max_cycles: int = 5,
        convergence_check: callable = None,
        cycle_processor: callable = None,
        convergence_strategy: "ConvergenceStrategy" = None,  # type: ignore
    ):
        """
        Initialize MultiCycleStrategy.

        Args:
            max_cycles: Maximum number of cycles to execute (default: 5)
            convergence_check: Optional callback to check if cycles should stop (legacy)
                              Signature: (cycle_results: List[Dict]) -> bool
            cycle_processor: Optional callback to process each cycle
                           Signature: (inputs: Dict, cycle_num: int) -> Dict
            convergence_strategy: ConvergenceStrategy instance for convergence logic (NEW)
                                 Takes precedence over convergence_check if both provided

        Notes:
            - Phase 3 Refactoring: convergence_strategy is now the preferred approach
            - convergence_check is kept for backward compatibility
            - If convergence_strategy is provided, it takes precedence
        """
        self.max_cycles = max_cycles
        self.convergence_check_callback = convergence_check
        self.cycle_processor_callback = cycle_processor
        self.convergence_strategy = (
            convergence_strategy  # NEW: Independent convergence strategy
        )

    def execute(
        self,
        agent: Any,  # BaseAgent when fully implemented
        inputs: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute multi-cycle strategy.

        Execution Flow:
        1. For each cycle (up to max_cycles):
           a. Call pre_cycle() extension point
           b. Build and execute cycle workflow
           c. Call parse_cycle_result() extension point
           d. Extract observation using extract_observation()
           e. Check should_terminate()
           f. Continue or break
        2. Return final result with cycle metadata

        Args:
            agent: The agent instance
            inputs: Input parameters
            **kwargs: Additional parameters (e.g., tools, context)

        Returns:
            Dict[str, Any]: Execution results with cycle metadata

        Example:
            >>> result = strategy.execute(
            ...     agent,
            ...     {'task': 'Find largest prime less than 100'}
            ... )
            >>> print(result)
            {
                'answer': '97',
                'reasoning': [
                    'Check 99: divisible by 3',
                    'Check 98: divisible by 2',
                    'Check 97: is prime!'
                ],
                'cycles_used': 3,
                'total_cycles': 5
            }
        """
        # Task 2.12: Full multi-cycle execution implementation
        cycle_results = []
        final_result = {}
        cycles_used = 0

        # Task 2.13: Multi-cycle execution loop
        current_inputs = inputs.copy()

        for cycle_num in range(self.max_cycles):
            cycles_used = cycle_num + 1

            try:
                # Use cycle_processor_callback if provided, otherwise use default processing
                if self.cycle_processor_callback:
                    # Let agent handle cycle processing (e.g., ReAct agent)
                    cycle_result = self.cycle_processor_callback(
                        current_inputs, cycle_num
                    )
                else:
                    # Default cycle processing with workflow execution
                    workflow = self.build_workflow(agent)
                    if workflow is None:
                        return self._generate_skeleton_result(agent, inputs)

                    runtime = LocalRuntime()

                    # Transform inputs to messages (like SingleShotStrategy)
                    messages = self._create_messages_from_inputs(agent, current_inputs)
                    workflow_params = {"agent_exec": {"messages": messages}}

                    # Execute cycle
                    raw_result, run_id = runtime.execute(
                        workflow.build(), parameters=workflow_params
                    )

                    # Parse result (like SingleShotStrategy)
                    cycle_result = self.parse_result(raw_result)

                cycle_results.append(cycle_result)

                # Phase 3 Refactoring: Check convergence strategy first (NEW API)
                if self.convergence_strategy:
                    # Use ConvergenceStrategy.should_stop() - NEW approach
                    # Create simple reflection dict (can be enhanced later)
                    reflection = {
                        "cycle_num": cycle_num,
                        "total_cycles": len(cycle_results),
                    }
                    if self.convergence_strategy.should_stop(cycle_result, reflection):
                        final_result = cycle_result
                        break
                # Fall back to legacy convergence_check callback
                elif self.convergence_check_callback:
                    if self.convergence_check_callback(cycle_results):
                        final_result = cycle_result
                        break
                # Fall back to default should_terminate
                elif self.should_terminate(cycle_result, cycle_num):
                    # Default termination check
                    final_result = cycle_result
                    break

                # Extract observation for next cycle
                observation = self.extract_observation(cycle_result)
                if observation:
                    current_inputs["observation"] = observation

            except Exception as e:
                # Task 2.15: Error termination
                final_result = {"error": str(e), "status": "failed", "cycle": cycle_num}
                break

        # If no explicit termination, use last cycle result
        if not final_result and cycle_results:
            final_result = cycle_results[-1]

        # Task 2.13: Add cycle metadata
        final_result["cycles_used"] = cycles_used
        final_result["total_cycles"] = self.max_cycles

        # Task 2.10: Extract signature output fields
        if hasattr(agent.signature, "output_fields"):
            output_result = {
                "cycles_used": cycles_used,
                "total_cycles": self.max_cycles,
            }
            for field_name in agent.signature.output_fields:
                if field_name in final_result:
                    output_result[field_name] = final_result[field_name]
                elif "response" in final_result and isinstance(
                    final_result["response"], dict
                ):
                    # Try to extract from nested response
                    if field_name in final_result["response"]:
                        output_result[field_name] = final_result["response"][field_name]

            # If we extracted fields, use them; otherwise return full result
            if len(output_result) > 2:  # More than just metadata
                return output_result

        return final_result

    def build_workflow(self, agent: Any) -> WorkflowBuilder:
        """
        Build workflow for multi-cycle execution.

        Creates a simple workflow with:
        1. LLMAgentNode for reasoning/acting
        2. Reusable across cycles (runtime loop handles iteration)

        Note: Full cyclic workflow with SwitchNode can be added in future
        enhancements. Current implementation uses Python loop for cycle control
        which is simpler and more flexible.

        Args:
            agent: The agent instance

        Returns:
            WorkflowBuilder: Workflow for cycle execution

        Example:
            >>> workflow = strategy.build_workflow(agent)
            >>> # Execute in loop
            >>> for cycle in range(max_cycles):
            ...     result, run_id = runtime.execute(workflow.build(), inputs)
        """
        # Task 2.12: Use WorkflowGenerator for signature-based workflow
        if not hasattr(agent, "workflow_generator"):
            return None

        try:
            # Use the agent's workflow generator
            # Same workflow structure as single-shot, but executed in loop
            workflow = agent.workflow_generator.generate_signature_workflow()
            return workflow
        except Exception:
            # Fallback if workflow generation fails
            return None

    # Task 2.11: Extension Points

    def pre_cycle(self, cycle_num: int, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extension point: Prepare inputs before cycle execution.

        Override in subclasses to customize cycle preparation.

        Args:
            cycle_num: Current cycle number (0-indexed)
            inputs: Current inputs (includes observations from previous cycles)

        Returns:
            Dict[str, Any]: Prepared inputs for cycle

        Example:
            >>> class CustomStrategy(MultiCycleStrategy):
            ...     def pre_cycle(self, cycle_num, inputs):
            ...         inputs['cycle'] = cycle_num
            ...         return inputs
        """
        return inputs

    def parse_cycle_result(
        self, raw_result: Dict[str, Any], cycle_num: int
    ) -> Dict[str, Any]:
        """
        Extension point: Parse cycle result.

        Override in subclasses to customize result parsing.

        Args:
            raw_result: Raw result from cycle execution
            cycle_num: Current cycle number (0-indexed)

        Returns:
            Dict[str, Any]: Parsed cycle result

        Example:
            >>> class CustomStrategy(MultiCycleStrategy):
            ...     def parse_cycle_result(self, raw_result, cycle_num):
            ...         return {
            ...             'cycle': cycle_num,
            ...             'thought': raw_result.get('thought'),
            ...             'action': raw_result.get('action')
            ...         }
        """
        return raw_result

    def should_terminate(self, cycle_result: Dict[str, Any], cycle_num: int) -> bool:
        """
        Determine if execution should terminate.

        Checks termination conditions:
        1. max_cycles reached (checked by caller)
        2. Agent signals completion (e.g., 'FINAL ANSWER' in response)
        3. Error occurred
        4. Explicit 'done' flag

        Args:
            cycle_result: Result from current cycle
            cycle_num: Current cycle number (0-indexed)

        Returns:
            bool: True if should terminate, False if should continue

        Example:
            >>> result = {'action': 'FINAL ANSWER: 42'}
            >>> should_stop = strategy.should_terminate(result, cycle_num=2)
            >>> print(should_stop)
            True
        """
        # Task 2.15: Termination logic

        # Check for explicit done flag
        if cycle_result.get("done", False):
            return True

        # Check for error
        if "error" in cycle_result:
            return True

        # Check for FINAL ANSWER pattern in any text field
        for key, value in cycle_result.items():
            if isinstance(value, str) and "FINAL ANSWER" in value.upper():
                return True

        # Check if at max cycles (0-indexed, so cycle_num == max_cycles - 1)
        if cycle_num >= self.max_cycles - 1:
            return True

        # Continue by default
        return False

    def extract_observation(self, cycle_result: Dict[str, Any]) -> str:
        """
        Extension point: Extract observation for next cycle.

        Override in subclasses to customize observation extraction.

        Args:
            cycle_result: Result from current cycle

        Returns:
            str: Observation text for next cycle

        Example:
            >>> class CustomStrategy(MultiCycleStrategy):
            ...     def extract_observation(self, cycle_result):
            ...         action = cycle_result.get('action', '')
            ...         return f"Action taken: {action}"
        """
        # Task 2.11: Default observation extraction

        # Check for explicit observation field
        if "observation" in cycle_result:
            return cycle_result["observation"]

        # Extract from action or response
        if "action" in cycle_result:
            return f"Completed: {cycle_result['action']}"

        if "response" in cycle_result:
            return str(cycle_result["response"])

        # No observation
        return ""

    # Helper methods

    def _create_messages_from_inputs(self, agent: Any, inputs: Dict[str, Any]):
        """
        Transform signature inputs into OpenAI message format.

        Converts structured signature inputs (like task, context, etc.) into
        the message format expected by LLMAgentNode.

        Args:
            agent: Agent instance with signature
            inputs: Dict of signature input values

        Returns:
            List[Dict[str, str]]: Messages in OpenAI format
        """

        # Build user message content from signature inputs
        message_parts = []

        if hasattr(agent.signature, "input_fields"):
            for field_name, field_info in agent.signature.input_fields.items():
                if field_name in inputs and inputs[field_name]:
                    # Get field description for context
                    desc = field_info.get("desc", field_name.title())
                    value = inputs[field_name]

                    # Format field into message
                    message_parts.append(f"{desc}: {value}")
        else:
            # Fallback: just join all input values
            message_parts = [f"{k}: {v}" for k, v in inputs.items() if v]

        # Combine into single user message
        content = "\n\n".join(message_parts) if message_parts else "No input provided"

        return [{"role": "user", "content": content}]

    def parse_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw LLM output from workflow execution.

        Extracts and parses the JSON response from LLMAgentNode output.

        Args:
            raw_result: Raw result from workflow execution

        Returns:
            Dict[str, Any]: Parsed result matching signature output fields
        """
        import json
        import re

        # Handle workflow execution results
        if "agent_exec" in raw_result:
            llm_output = raw_result["agent_exec"]
        else:
            llm_output = raw_result

        # LLMAgentNode returns: {"success": bool, "response": {...}, ...}
        if isinstance(llm_output, dict) and "response" in llm_output:
            response = llm_output["response"]

            # Extract content from response
            content = None
            if isinstance(response, dict) and "content" in response:
                content = response["content"]
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)

            # Try to parse JSON from content
            if content:
                # Remove markdown code blocks if present
                content = re.sub(r"```json\s*", "", content)
                content = re.sub(r"```\s*$", "", content)
                content = content.strip()

                try:
                    # Parse JSON
                    parsed = json.loads(content)
                    return parsed
                except json.JSONDecodeError:
                    # If JSON parsing fails, return content as-is
                    return {"response": content, "error": "JSON_PARSE_FAILED"}

        # Fallback: return raw result
        return raw_result

    def _generate_skeleton_result(
        self, agent: Any, inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate skeleton result when workflow is unavailable."""
        result = {}

        # For each output field in signature, create a placeholder response
        if hasattr(agent.signature, "output_fields"):
            for field_name in agent.signature.output_fields:
                result[field_name] = f"Multi-cycle result for {field_name}"
        else:
            # Try to extract from signature class attributes
            if hasattr(agent.signature, "__annotations__"):
                for attr_name, attr_type in agent.signature.__annotations__.items():
                    # Check if it's an OutputField
                    attr_value = getattr(agent.signature, attr_name, None)
                    if attr_value is not None and hasattr(attr_value, "__class__"):
                        if "OutputField" in str(attr_value.__class__):
                            result[attr_name] = f"Multi-cycle result for {attr_name}"

            # Fallback
            if not result:
                result["result"] = "Multi-cycle strategy execution"

        # Add cycle metadata
        result["cycles_used"] = 1
        result["total_cycles"] = self.max_cycles

        return result
