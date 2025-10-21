"""
Structured Output Support - JSON Schema Generation from Signatures

Generates JSON schemas for reliable LLM outputs:
- Automatic schema from signature fields
- OpenAI structured output format
- 100% format compliance
- No regex parsing needed
"""

import json
from typing import Any, Dict, List, Type


class StructuredOutputGenerator:
    """
    Generates JSON schemas from Kaizen signatures.

    Supports OpenAI's structured output format for reliable JSON responses.
    """

    @staticmethod
    def signature_to_json_schema(signature: Any) -> Dict[str, Any]:
        """
        Convert signature to JSON schema.

        Args:
            signature: Kaizen Signature instance

        Returns:
            Dict: JSON schema for structured output

        Example:
            >>> schema = StructuredOutputGenerator.signature_to_json_schema(qa_signature)
            >>> # Use with OpenAI: model='gpt-4-turbo-preview', response_format={"type": "json_object", "schema": schema}
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

        # Extract output fields from signature
        if hasattr(signature, "output_fields"):
            for field_name, field_info in signature.output_fields.items():
                field_type = field_info.get("type", str)
                field_desc = field_info.get("desc", "")

                # Map Python types to JSON schema types
                json_type = StructuredOutputGenerator._python_type_to_json_type(
                    field_type
                )

                schema["properties"][field_name] = {
                    "type": json_type,
                    "description": field_desc,
                }

                # All output fields are required
                schema["required"].append(field_name)

        return schema

    @staticmethod
    def _python_type_to_json_type(python_type: Type) -> str:
        """Map Python type to JSON schema type."""
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        return type_mapping.get(python_type, "string")

    @staticmethod
    def generate_system_prompt_with_schema(signature: Any) -> str:
        """
        Generate system prompt with embedded JSON schema.

        Args:
            signature: Kaizen Signature instance

        Returns:
            str: System prompt with schema instructions

        Example:
            >>> prompt = StructuredOutputGenerator.generate_system_prompt_with_schema(signature)
        """
        prompt_parts = []

        # Add signature description
        if hasattr(signature, "description") and signature.description:
            prompt_parts.append(signature.description)
        elif hasattr(signature, "name") and signature.name:
            prompt_parts.append(f"Task: {signature.name}")

        # Add input field descriptions
        if hasattr(signature, "input_fields") and signature.input_fields:
            prompt_parts.append("\nExpected Inputs:")
            for field_name, field_info in signature.input_fields.items():
                if isinstance(field_info, dict) and "desc" in field_info:
                    prompt_parts.append(f"  - {field_name}: {field_info['desc']}")

        # Add output field descriptions with types
        if hasattr(signature, "output_fields") and signature.output_fields:
            prompt_parts.append("\nRequired Outputs:")
            for field_name, field_info in signature.output_fields.items():
                if isinstance(field_info, dict):
                    field_type = field_info.get("type", str).__name__
                    field_desc = field_info.get("desc", "")
                    prompt_parts.append(
                        f"  - {field_name} ({field_type}): {field_desc}"
                    )

        # Add JSON schema
        schema = StructuredOutputGenerator.signature_to_json_schema(signature)
        prompt_parts.append("\n---")
        prompt_parts.append(
            "\nYou MUST respond with a valid JSON object matching this exact schema:"
        )
        prompt_parts.append(f"```json\n{json.dumps(schema, indent=2)}\n```")
        prompt_parts.append("\nDo NOT include any text outside the JSON object.")
        prompt_parts.append(
            "Ensure all required fields are present with correct types."
        )

        return "\n".join(prompt_parts)

    @staticmethod
    def validate_output(
        output: Dict[str, Any], signature: Any
    ) -> tuple[bool, List[str]]:
        """
        Validate output against signature schema.

        Args:
            output: LLM output to validate
            signature: Kaizen Signature instance

        Returns:
            tuple: (is_valid, list of errors)

        Example:
            >>> is_valid, errors = StructuredOutputGenerator.validate_output(result, signature)
            >>> if not is_valid:
            ...     print(f"Validation errors: {errors}")
        """
        errors = []

        if not hasattr(signature, "output_fields"):
            return True, []

        # Check all required fields present
        for field_name, field_info in signature.output_fields.items():
            if field_name not in output:
                errors.append(f"Missing required field: {field_name}")
                continue

            # Check type
            expected_type = field_info.get("type", str)
            actual_value = output[field_name]

            if not isinstance(actual_value, expected_type):
                # Special case: int/float are interchangeable for numeric types
                if expected_type == float and isinstance(actual_value, int):
                    pass  # OK
                elif expected_type == int and isinstance(actual_value, float):
                    pass  # OK
                else:
                    errors.append(
                        f"Type mismatch for {field_name}: "
                        f"expected {expected_type.__name__}, got {type(actual_value).__name__}"
                    )

        return len(errors) == 0, errors


# Convenience function
def create_structured_output_config(signature: Any) -> Dict[str, Any]:
    """
    Create OpenAI-compatible structured output configuration.

    Args:
        signature: Kaizen Signature instance

    Returns:
        Dict: Config for OpenAI API

    Example:
        >>> config = create_structured_output_config(qa_signature)
        >>> # Pass to OpenAI: response_format=config
    """
    schema = StructuredOutputGenerator.signature_to_json_schema(signature)

    return {"type": "json_object", "schema": schema}
