"""
WorkflowGenerator - Convert signatures to Core SDK workflows.

This module provides the WorkflowGenerator class that translates
signature-based agent definitions into executable Core SDK workflows.

Key Responsibilities:
- Generate workflows from Signature definitions
- Create LLMAgentNode instances with proper configuration
- Map input/output fields to workflow parameters
- Handle both signature-based and fallback workflows

References:
- ADR-006: Agent Base Architecture design
- TODO-157: Task 1.3, 1.16a, 1.16b, 1.16c
- Core SDK: WorkflowBuilder, LLMAgentNode

Author: Kaizen Framework Team
Created: 2025-10-01
"""

from typing import Optional

from kaizen.core.config import BaseAgentConfig
from kaizen.signatures import Signature

from kailash.workflow.builder import WorkflowBuilder

# from .config import BaseAgentConfig


class WorkflowGenerator:
    """
    Generate Core SDK workflows from Kaizen signatures.

    The WorkflowGenerator is responsible for translating the high-level
    signature-based agent definitions into executable Core SDK workflows
    using WorkflowBuilder and LLMAgentNode.

    Example Usage:
        >>> from kaizen.core.workflow_generator import WorkflowGenerator
        >>> from kaizen.signatures import Signature, InputField, OutputField
        >>> from kaizen.core.config import BaseAgentConfig
        >>>
        >>> # Create signature
        >>> class QASignature(Signature):
        ...     question: str = InputField(desc="Question")
        ...     answer: str = OutputField(desc="Answer")
        >>>
        >>> # Create config
        >>> config = BaseAgentConfig(
        ...     llm_provider="openai",
        ...     model="gpt-4",
        ...     temperature=0.1
        ... )
        >>>
        >>> # Generate workflow
        >>> generator = WorkflowGenerator(config=config, signature=QASignature())
        >>> workflow = generator.generate_signature_workflow()
        >>>
        >>> # Execute workflow
        >>> from kailash.runtime.local import LocalRuntime
        >>> runtime = LocalRuntime()
        >>> results, run_id = runtime.execute(workflow.build())

    Notes:
    - This is a SKELETON implementation for TDD Phase 1
    - Implementation driven by tests in test_base_agent_workflow.py
    - Core pattern: workflow.add_node('LLMAgentNode', 'agent', {...})
    """

    def __init__(self, config: BaseAgentConfig, signature: Optional[Signature] = None):
        """
        Initialize WorkflowGenerator.

        Args:
            config: Agent configuration
            signature: Optional signature (for signature-based workflow)
        """
        self.config = config
        self.signature = signature

    def generate_signature_workflow(self) -> WorkflowBuilder:
        """
        Generate workflow from signature definition.

        Creates a Core SDK workflow that:
        1. Uses LLMAgentNode from src/kailash/nodes/ai/llm_agent.py
        2. Maps signature input fields to workflow inputs
        3. Maps signature output fields to workflow outputs
        4. Includes proper system prompt from signature

        Returns:
            WorkflowBuilder: Workflow ready for execution

        Core SDK Pattern:
            workflow.add_node('LLMAgentNode', 'agent', {
                'model': self.config.model,
                'provider': self.config.llm_provider,
                'temperature': self.config.temperature,
                'system_prompt': self._generate_system_prompt(),
            })

        Example:
            >>> workflow = generator.generate_signature_workflow()
            >>> built = workflow.build()
            >>> runtime.execute(built)
        """
        if not self.signature:
            raise ValueError(
                "Signature required for signature-based workflow generation"
            )

        # Create workflow builder
        workflow = WorkflowBuilder()

        # Build generation config (handle both dict and BaseAgentConfig)
        generation_config = {}

        # Get config values safely (handle both dict and object)
        temperature = (
            getattr(self.config, "temperature", None)
            if hasattr(self.config, "temperature")
            else self.config.get("temperature")
        )
        max_tokens = (
            getattr(self.config, "max_tokens", None)
            if hasattr(self.config, "max_tokens")
            else self.config.get("max_tokens")
        )
        llm_provider = (
            getattr(self.config, "llm_provider", None)
            if hasattr(self.config, "llm_provider")
            else self.config.get("llm_provider")
        )
        model = (
            getattr(self.config, "model", None)
            if hasattr(self.config, "model")
            else self.config.get("model")
        )
        provider_config = (
            getattr(self.config, "provider_config", None)
            if hasattr(self.config, "provider_config")
            else self.config.get("provider_config")
        )

        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_tokens is not None:
            generation_config["max_tokens"] = max_tokens

        # Create LLMAgentNode with signature-based configuration
        node_config = {
            "provider": llm_provider or "openai",
            "model": model or "gpt-4",
            "system_prompt": self._generate_system_prompt(),
            "generation_config": generation_config,
        }

        # Add provider-specific config
        if provider_config:
            for key, value in provider_config.items():
                if key not in node_config:
                    node_config[key] = value

        # Add the LLMAgentNode to workflow
        workflow.add_node("LLMAgentNode", "agent_exec", node_config)

        return workflow

    def generate_fallback_workflow(self) -> WorkflowBuilder:
        """
        Generate fallback workflow without signature compilation.

        Creates a simple workflow with direct LLM call for cases where
        signature programming is disabled or unavailable.

        Returns:
            WorkflowBuilder: Simple workflow with direct LLM call

        Example:
            >>> workflow = generator.generate_fallback_workflow()
            >>> built = workflow.build()
            >>> runtime.execute(built, parameters={'prompt': 'What is 2+2?'})
        """
        # Create workflow builder
        workflow = WorkflowBuilder()

        # Build generation config
        generation_config = {
            "temperature": self.config.temperature,
        }
        if self.config.max_tokens:
            generation_config["max_tokens"] = self.config.max_tokens

        # Create simple LLMAgentNode configuration (no signature)
        node_config = {
            "provider": self.config.llm_provider or "openai",
            "model": self.config.model or "gpt-4",
            "generation_config": generation_config,
        }

        # Add provider-specific config
        if self.config.provider_config:
            for key, value in self.config.provider_config.items():
                if key not in node_config:
                    node_config[key] = value

        # Add the LLMAgentNode to workflow (without system prompt for fallback)
        workflow.add_node("LLMAgentNode", "agent_fallback", node_config)

        return workflow

    def _generate_system_prompt(self) -> str:
        """
        Generate system prompt from signature.

        Analyzes signature input/output fields to create an appropriate
        system prompt for the LLM.

        Returns:
            str: System prompt

        Example:
            >>> prompt = generator._generate_system_prompt()
            >>> print(prompt)
            Task: Given question, produce answer.
        """
        if not self.signature:
            return "You are a helpful AI assistant."

        # Start with signature description if available
        parts = []

        if hasattr(self.signature, "description") and self.signature.description:
            parts.append(self.signature.description)
        elif hasattr(self.signature, "name") and self.signature.name:
            parts.append(f"Task: {self.signature.name}")

        # Describe inputs
        if hasattr(self.signature, "inputs") and self.signature.inputs:
            input_list = ", ".join(self.signature.inputs)
            parts.append(f"\nInputs: {input_list}")

        # Describe outputs
        if hasattr(self.signature, "outputs") and self.signature.outputs:
            output_list = ", ".join(
                self.signature.outputs
                if isinstance(self.signature.outputs, list)
                else [str(self.signature.outputs)]
            )
            parts.append(f"Outputs: {output_list}")

        # Add field descriptions if available
        if hasattr(self.signature, "input_fields") and self.signature.input_fields:
            field_descs = []
            for field_name, field_def in self.signature.input_fields.items():
                if isinstance(field_def, dict) and "desc" in field_def:
                    field_descs.append(f"  - {field_name}: {field_def['desc']}")
            if field_descs:
                parts.append("\nInput Field Descriptions:")
                parts.extend(field_descs)

        if hasattr(self.signature, "output_fields") and self.signature.output_fields:
            field_descs = []
            for field_name, field_def in self.signature.output_fields.items():
                if isinstance(field_def, dict) and "desc" in field_def:
                    field_type = field_def.get("type", str).__name__
                    field_descs.append(
                        f"  - {field_name} ({field_type}): {field_def['desc']}"
                    )
            if field_descs:
                parts.append("\nOutput Field Descriptions:")
                parts.extend(field_descs)

        # Add JSON formatting instructions
        if hasattr(self.signature, "output_fields") and self.signature.output_fields:
            parts.append("\n---")
            parts.append(
                "\nIMPORTANT: You must respond with a valid JSON object containing exactly these fields:"
            )
            json_example = {}
            for field_name, field_def in self.signature.output_fields.items():
                field_type = field_def.get("type", str)
                # Generate example values based on type
                if field_type == str:
                    json_example[field_name] = f"<your {field_name} here>"
                elif field_type == float:
                    json_example[field_name] = 0.0
                elif field_type == int:
                    json_example[field_name] = 0
                elif field_type == bool:
                    json_example[field_name] = False
                elif field_type == list:
                    json_example[field_name] = []
                elif field_type == dict:
                    json_example[field_name] = {}
                else:
                    json_example[field_name] = f"<{field_name}>"

            import json as json_module

            parts.append(
                f"\nExpected JSON format:\n```json\n{json_module.dumps(json_example, indent=2)}\n```"
            )
            parts.append(
                "\nDo not include any explanation or text outside the JSON object."
            )

        # Join all parts
        if parts:
            return "\n".join(parts)

        # Fallback
        return "You are a helpful AI assistant."
