"""
TrustCall-style JSON validation and repair system.

Uses JSON Patch to iteratively fix validation errors instead of wrapping in text.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import jsonpatch

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a JSON validation error."""
    path: str
    message: str
    expected_type: Optional[str] = None


class TrustCallValidator:
    """
    Validates and repairs JSON outputs using iterative JSON Patch approach.

    Instead of giving up on malformed JSON, we:
    1. Attempt to parse and identify specific errors
    2. Prompt LLM to generate JSON Patch to fix errors
    3. Apply patch and re-validate
    4. Repeat until valid or max retries
    """

    def __init__(self, max_repair_attempts: int = 3):
        self.max_repair_attempts = max_repair_attempts

    def validate_and_repair(self, raw_output: str, expected_schema: Dict[str, Any],
                           repair_fn, agent_name: str = "Agent") -> Dict[str, Any]:
        """
        Validate JSON output and repair if needed using JSON Patch.

        Args:
            raw_output: Raw text output from LLM
            expected_schema: Expected JSON structure/schema
            repair_fn: Function to call LLM for repair (takes prompt, returns text)
            agent_name: Name of agent for logging

        Returns:
            Valid JSON dict or original with error info
        """
        # First, try to extract and parse JSON
        parsed_json, errors = self._try_parse_json(raw_output)

        if parsed_json and not errors:
            logger.info(f"✅ {agent_name} - Valid JSON output")
            return parsed_json

        # If parsing failed completely, try to extract JSON from text
        if not parsed_json:
            logger.warning(f"⚠️  {agent_name} - Failed to parse JSON, attempting extraction")
            parsed_json = self._extract_json_from_text(raw_output)

            # If extraction also failed, attempt regeneration up to max_repair_attempts
            if not parsed_json:
                logger.warning(f"⚠️  {agent_name} - Extraction failed, attempting regeneration")

                for attempt in range(1, self.max_repair_attempts + 1):
                    logger.info(f"🔄 {agent_name} - Regeneration attempt {attempt}/{self.max_repair_attempts}")

                    # Build regeneration prompt
                    regen_prompt = self._build_regeneration_prompt(
                        raw_output,
                        expected_schema,
                        attempt
                    )

                    # Get new response from LLM
                    new_output = repair_fn(regen_prompt)

                    # Try to parse the regenerated output
                    parsed_json, errors = self._try_parse_json(new_output)

                    if not parsed_json:
                        # Try extraction again
                        parsed_json = self._extract_json_from_text(new_output)

                    if parsed_json:
                        logger.info(f"✅ {agent_name} - Regeneration successful on attempt {attempt}")
                        break

                    logger.warning(f"⚠️  {agent_name} - Regeneration attempt {attempt} failed")

                # If still no valid JSON after all attempts
                if not parsed_json:
                    logger.error(f"❌ {agent_name} - Could not extract JSON after {self.max_repair_attempts} regeneration attempts")
                    return {
                        "agent": agent_name,
                        "status": "error",
                        "format": "text",
                        "data": raw_output,
                        "error": f"Could not extract valid JSON after {self.max_repair_attempts} attempts"
                    }

        # Validate against schema
        validation_errors = self._validate_against_schema(parsed_json, expected_schema)

        if not validation_errors:
            logger.info(f"✅ {agent_name} - JSON validated against schema")
            return parsed_json

        # Attempt repairs using JSON Patch
        logger.info(f"🔧 {agent_name} - Starting JSON Patch repair ({len(validation_errors)} issues)")

        current_json = parsed_json
        for attempt in range(1, self.max_repair_attempts + 1):
            # Generate repair prompt
            repair_prompt = self._build_repair_prompt(
                current_json,
                validation_errors,
                expected_schema,
                attempt
            )

            # Get JSON Patch from LLM
            logger.info(f"🔄 {agent_name} - Repair attempt {attempt}/{self.max_repair_attempts}")
            patch_response = repair_fn(repair_prompt)

            # Parse patch
            try:
                patch_ops = json.loads(patch_response)
                if not isinstance(patch_ops, list):
                    patch_ops = [patch_ops]

                # Apply patch
                patch = jsonpatch.JsonPatch(patch_ops)
                repaired_json = patch.apply(current_json)

                # Re-validate
                validation_errors = self._validate_against_schema(repaired_json, expected_schema)

                if not validation_errors:
                    logger.info(f"✅ {agent_name} - JSON repaired successfully on attempt {attempt}")
                    return repaired_json

                current_json = repaired_json
                logger.warning(f"⚠️  {agent_name} - Repair attempt {attempt} reduced errors to {len(validation_errors)}")

            except Exception as e:
                logger.error(f"❌ {agent_name} - Patch application failed: {e}")
                continue

        # Max retries reached, return best effort
        logger.warning(f"⚠️  {agent_name} - Max repair attempts reached, returning last state")
        return current_json

    def _try_parse_json(self, text: str) -> tuple[Optional[Dict], List[str]]:
        """Try to parse JSON and return errors if any."""
        errors = []
        try:
            parsed = json.loads(text)
            return parsed, []
        except json.JSONDecodeError as e:
            errors.append(f"JSON decode error at position {e.pos}: {e.msg}")
            return None, errors

    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from text that may contain markdown or other wrapper."""
        import re

        # Try to find JSON in code blocks (both ```json and ``` variants)
        code_block_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
        ]
        for pattern in code_block_patterns:
            code_block_match = re.search(pattern, text, re.DOTALL)
            if code_block_match:
                try:
                    return json.loads(code_block_match.group(1))
                except:
                    pass

        # Try multiple strategies to find raw JSON object
        # Strategy 1: Find the first complete { } block
        stack = []
        start_idx = None
        for i, char in enumerate(text):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append('{')
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack and start_idx is not None:
                        # Found complete JSON object
                        try:
                            return json.loads(text[start_idx:i+1])
                        except:
                            # Continue searching for next JSON object
                            start_idx = None

        # Strategy 2: Try regex patterns of increasing complexity
        patterns = [
            r'\{[^{}]*\}',  # Simple object without nesting
            r'\{(?:[^{}]|\{[^{}]*\})*\}',  # One level of nesting
            r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}',  # Two levels of nesting
        ]
        for pattern in patterns:
            json_match = re.search(pattern, text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass

        return None

    def _validate_against_schema(self, data: Dict, schema: Dict[str, Any]) -> List[ValidationError]:
        """Validate JSON against expected schema structure."""
        errors = []

        # Simple validation - check required fields and types
        for field, field_type in schema.items():
            if field not in data:
                errors.append(ValidationError(
                    path=f"/{field}",
                    message=f"Missing required field: {field}",
                    expected_type=str(field_type)
                ))
            elif field_type and not isinstance(data[field], field_type):
                errors.append(ValidationError(
                    path=f"/{field}",
                    message=f"Type mismatch: expected {field_type.__name__}, got {type(data[field]).__name__}",
                    expected_type=field_type.__name__
                ))

        return errors

    def _build_repair_prompt(self, current_json: Dict, errors: List[ValidationError],
                            expected_schema: Dict, attempt: int) -> str:
        """Build prompt for LLM to generate JSON Patch."""
        return f"""The following JSON has validation errors:

Current JSON:
{json.dumps(current_json, indent=2)}

Validation Errors:
{chr(10).join(f"- {e.path}: {e.message}" for e in errors)}

Expected Schema:
{json.dumps({k: v.__name__ if hasattr(v, '__name__') else str(v) for k, v in expected_schema.items()}, indent=2)}

Generate a JSON Patch (RFC 6902) to fix these validation errors.

Your response must be ONLY a valid JSON array of patch operations.
Use operations: add, remove, replace, move, copy, test

Example format:
[
  {{"op": "add", "path": "/missing_field", "value": "some value"}},
  {{"op": "replace", "path": "/wrong_field", "value": "corrected value"}}
]

Attempt {attempt}/{self.max_repair_attempts}. Provide the JSON Patch now:"""

    def _build_regeneration_prompt(self, failed_output: str, expected_schema: Dict, attempt: int) -> str:
        """Build prompt for LLM to regenerate response in correct JSON format."""
        schema_desc = json.dumps(
            {k: v.__name__ if hasattr(v, '__name__') else str(v) for k, v in expected_schema.items()},
            indent=2
        )

        return f"""Your previous response did not contain valid JSON. Please regenerate your response in the correct format.

Expected JSON Schema:
{schema_desc}

CRITICAL REQUIREMENTS:
1. Your response MUST be ONLY valid JSON - no markdown, no code blocks, no explanation
2. The JSON must match the schema exactly
3. Do NOT wrap the JSON in ```json``` code blocks
4. Do NOT include any text before or after the JSON

Example of correct format:
{{"context": "your detailed explanation here as a single string"}}

Attempt {attempt}/{self.max_repair_attempts}. Generate the response now in valid JSON:"""


# Global instance for easy access
trust_validator = TrustCallValidator(max_repair_attempts=3)
