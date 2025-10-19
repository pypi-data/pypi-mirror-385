"""
Tests for skip propagation with required dependency control.

This module tests the new flexible depends_on feature that allows:
1. String format (defaults to required=True)
2. Dict format with explicit required flag
3. Skip propagation when required dependencies fail/skip
4. No skip when dependencies are optional (required=False)
"""

import pytest

from workflows_mcp.engine.executor import WorkflowExecutor
from workflows_mcp.engine.executor_base import create_default_registry
from workflows_mcp.engine.schema import BlockDefinition, WorkflowSchema


@pytest.fixture
def executor():
    """Create executor with default registry (includes Shell executor)."""
    registry = create_default_registry()
    return WorkflowExecutor(registry=registry)


class TestSkipPropagation:
    """Test skip propagation with flexible depends_on."""

    async def _execute_workflow(self, executor, workflow_def_dict):
        """Helper to create, load, and execute a workflow from dict definition."""
        # Use WorkflowSchema for Pydantic validation and normalization
        workflow_schema = WorkflowSchema(**workflow_def_dict)
        # Load workflow schema directly into executor
        executor.load_workflow(workflow_schema)
        return await executor.execute_workflow(workflow_schema.name, {})

    @pytest.mark.asyncio
    async def test_required_dependency_skip_propagates(self, executor):
        """Test that skipped required dependency causes dependent block to skip."""
        result = await self._execute_workflow(
            executor,
            {
                "name": "test-skip-propagation",
                "description": "Test skip propagation",
                "blocks": [
                    {
                        "id": "block_a",
                        "type": "Shell",
                        "inputs": {"command": "echo 'A'"},
                        "condition": "false",  # Will skip
                    },
                    {
                        "id": "block_b",
                        "type": "Shell",
                        "inputs": {"command": "echo 'B'"},
                        "depends_on": [{"block": "block_a", "required": True}],
                    },
                ],
            },
        )

        assert result.status == "success"
        # Both blocks should be skipped
        assert result.blocks["block_a"]["metadata"]["status"] == "skipped"
        assert (
            result.blocks["block_a"]["metadata"]["skip_reason"]
            == "Condition 'false' evaluated to False"
        )

        assert result.blocks["block_b"]["metadata"]["status"] == "skipped"
        assert "block_a" in result.blocks["block_b"]["metadata"]["skip_reason"]
        assert result.blocks["block_b"]["metadata"]["skipped_by"] == "required_dependency"

    @pytest.mark.asyncio
    async def test_optional_dependency_skip_does_not_propagate(self, executor):
        """Test that skipped optional dependency does not cause dependent block to skip."""
        result = await self._execute_workflow(
            executor,
            {
                "name": "test-optional-dependency",
                "description": "Test optional dependency",
                "blocks": [
                    {
                        "id": "block_a",
                        "type": "Shell",
                        "inputs": {"command": "echo 'A'"},
                        "condition": "false",  # Will skip
                    },
                    {
                        "id": "block_b",
                        "type": "Shell",
                        "inputs": {"command": "echo 'B'"},
                        "depends_on": [{"block": "block_a", "required": False}],
                    },
                ],
            },
        )

        assert result.status == "success"
        # block_a should be skipped
        assert result.blocks["block_a"]["metadata"]["status"] == "skipped"

        # block_b should execute successfully (optional dependency)
        assert result.blocks["block_b"]["metadata"]["status"] == "success"
        assert result.blocks["block_b"]["outputs"]["success"] is True

    @pytest.mark.asyncio
    async def test_string_format_defaults_to_required(self, executor):
        """Test that string format for depends_on defaults to required=True."""
        result = await self._execute_workflow(
            executor,
            {
                "name": "test-string-format",
                "description": "Test string format",
                "blocks": [
                    {
                        "id": "block_a",
                        "type": "Shell",
                        "inputs": {"command": "echo 'A'"},
                        "condition": "false",  # Will skip
                    },
                    {
                        "id": "block_b",
                        "type": "Shell",
                        "inputs": {"command": "echo 'B'"},
                        # String format - should default to required=True
                        "depends_on": ["block_a"],
                    },
                ],
            },
        )

        assert result.status == "success"
        # Both blocks should be skipped (string format defaults to required)
        assert result.blocks["block_a"]["metadata"]["status"] == "skipped"
        assert result.blocks["block_b"]["metadata"]["status"] == "skipped"
        assert result.blocks["block_b"]["metadata"]["skipped_by"] == "required_dependency"

    @pytest.mark.asyncio
    async def test_mixed_required_and_optional_dependencies(self, executor):
        """Test block with both required and optional dependencies."""
        result = await self._execute_workflow(
            executor,
            {
                "name": "test-mixed-dependencies",
                "description": "Test mixed dependencies",
                "blocks": [
                    {
                        "id": "block_a",
                        "type": "Shell",
                        "inputs": {"command": "echo 'A'"},
                        "condition": "false",  # Will skip
                    },
                    {
                        "id": "block_b",
                        "type": "Shell",
                        "inputs": {"command": "echo 'B'"},
                    },
                    {
                        "id": "block_c",
                        "type": "Shell",
                        "inputs": {"command": "echo 'C'"},
                        "depends_on": [
                            {"block": "block_a", "required": False},  # Optional - skipped
                            {"block": "block_b", "required": True},  # Required - success
                        ],
                    },
                ],
            },
        )

        assert result.status == "success"
        # block_a skips, block_b succeeds
        assert result.blocks["block_a"]["metadata"]["status"] == "skipped"
        assert result.blocks["block_b"]["metadata"]["status"] == "success"

        # block_c should execute (only required dependency succeeded)
        assert result.blocks["block_c"]["metadata"]["status"] == "success"

    @pytest.mark.asyncio
    async def test_failed_required_dependency_causes_skip(self, executor):
        """Test that failed required dependency causes dependent block to skip."""
        result = await self._execute_workflow(
            executor,
            {
                "name": "test-failed-dependency",
                "description": "Test failed dependency",
                "blocks": [
                    {
                        "id": "block_a",
                        "type": "Shell",
                        "inputs": {"command": "exit 1"},  # Will fail
                    },
                    {
                        "id": "block_b",
                        "type": "Shell",
                        "inputs": {"command": "echo 'B'"},
                        "depends_on": [{"block": "block_a", "required": True}],
                    },
                ],
            },
        )

        # Workflow completes but block_a fails
        assert result.status == "success"  # Workflow-level status
        assert result.blocks["block_a"]["metadata"]["status"] == "failure"

        # block_b should skip due to failed required dependency
        assert result.blocks["block_b"]["metadata"]["status"] == "skipped"
        assert "block_a" in result.blocks["block_b"]["metadata"]["skip_reason"]
        assert result.blocks["block_b"]["metadata"]["skipped_by"] == "required_dependency"

    @pytest.mark.asyncio
    async def test_transitive_skip_propagation(self, executor):
        """Test that skip propagates through multiple levels."""
        result = await self._execute_workflow(
            executor,
            {
                "name": "test-transitive-skip",
                "description": "Test transitive skip",
                "blocks": [
                    {
                        "id": "block_a",
                        "type": "Shell",
                        "inputs": {"command": "echo 'A'"},
                        "condition": "false",  # Will skip
                    },
                    {
                        "id": "block_b",
                        "type": "Shell",
                        "inputs": {"command": "echo 'B'"},
                        "depends_on": ["block_a"],
                    },
                    {
                        "id": "block_c",
                        "type": "Shell",
                        "inputs": {"command": "echo 'C'"},
                        "depends_on": ["block_b"],
                    },
                ],
            },
        )

        assert result.status == "success"
        # All blocks should skip in cascade
        assert result.blocks["block_a"]["metadata"]["status"] == "skipped"
        assert result.blocks["block_b"]["metadata"]["status"] == "skipped"
        assert result.blocks["block_c"]["metadata"]["status"] == "skipped"

        # Verify skip reasons
        assert "Condition" in result.blocks["block_a"]["metadata"]["skip_reason"]
        assert "block_a" in result.blocks["block_b"]["metadata"]["skip_reason"]
        assert "block_b" in result.blocks["block_c"]["metadata"]["skip_reason"]

    @pytest.mark.asyncio
    async def test_multiple_required_dependencies_all_must_succeed(self, executor):
        """Test that all required dependencies must succeed for block to execute."""
        result = await self._execute_workflow(
            executor,
            {
                "name": "test-multiple-required",
                "description": "Test multiple required dependencies",
                "blocks": [
                    {
                        "id": "block_a",
                        "type": "Shell",
                        "inputs": {"command": "echo 'A'"},
                    },
                    {
                        "id": "block_b",
                        "type": "Shell",
                        "inputs": {"command": "echo 'B'"},
                        "condition": "false",  # Will skip
                    },
                    {
                        "id": "block_c",
                        "type": "Shell",
                        "inputs": {"command": "echo 'C'"},
                        "depends_on": [
                            {"block": "block_a", "required": True},  # Success
                            {"block": "block_b", "required": True},  # Skipped
                        ],
                    },
                ],
            },
        )

        assert result.status == "success"
        assert result.blocks["block_a"]["metadata"]["status"] == "success"
        assert result.blocks["block_b"]["metadata"]["status"] == "skipped"

        # block_c should skip because block_b (required) was skipped
        assert result.blocks["block_c"]["metadata"]["status"] == "skipped"
        assert "block_b" in result.blocks["block_c"]["metadata"]["skip_reason"]

    @pytest.mark.asyncio
    async def test_skipped_outputs_have_default_values(self, executor):
        """Test that skipped blocks have properly initialized default output values."""
        result = await self._execute_workflow(
            executor,
            {
                "name": "test-skipped-outputs",
                "description": "Test skipped outputs",
                "blocks": [
                    {
                        "id": "block_a",
                        "type": "Shell",
                        "inputs": {"command": "echo 'A'"},
                        "condition": "false",  # Will skip
                    },
                ],
            },
        )

        assert result.status == "success"
        assert result.blocks["block_a"]["metadata"]["status"] == "skipped"

        # Check that outputs have expected defaults
        outputs = result.blocks["block_a"]["outputs"]
        assert "stdout" in outputs
        assert "stderr" in outputs
        assert "exit_code" in outputs
        assert "success" in outputs
        assert outputs["skipped"] is True
        assert outputs["success"] is False


class TestDependsOnSchemaValidation:
    """Test that schema validation properly handles mixed depends_on formats."""

    def test_string_format_normalized_to_dict(self):
        """Test that string dependencies are normalized to dicts."""
        workflow_schema = WorkflowSchema(
            name="test",
            description="test",
            blocks=[
                {
                    "id": "block_a",
                    "type": "Shell",
                    "inputs": {"command": "echo 'A'"},
                },
                {
                    "id": "block_b",
                    "type": "Shell",
                    "inputs": {"command": "echo 'B'"},
                    "depends_on": ["block_a"],  # String format
                },
            ],
        )

        # Verify normalization happened - blocks are BlockDefinition objects in WorkflowSchema
        block_b = workflow_schema.blocks[1]
        assert isinstance(block_b, BlockDefinition)
        assert len(block_b.depends_on) == 1
        assert block_b.depends_on[0].block == "block_a"
        assert block_b.depends_on[0].required is True

    def test_dict_format_preserved(self):
        """Test that dict format dependencies are properly parsed."""
        workflow_schema = WorkflowSchema(
            name="test",
            description="test",
            blocks=[
                {
                    "id": "block_a",
                    "type": "Shell",
                    "inputs": {"command": "echo 'A'"},
                },
                {
                    "id": "block_b",
                    "type": "Shell",
                    "inputs": {"command": "echo 'B'"},
                    "depends_on": [{"block": "block_a", "required": False}],
                },
            ],
        )

        # Verify dict format parsed correctly
        block_b = workflow_schema.blocks[1]
        assert isinstance(block_b, BlockDefinition)
        assert len(block_b.depends_on) == 1
        assert block_b.depends_on[0].block == "block_a"
        assert block_b.depends_on[0].required is False

    def test_mixed_format_normalized(self):
        """Test that mixed string/dict formats are normalized correctly."""
        workflow_schema = WorkflowSchema(
            name="test",
            description="test",
            blocks=[
                {
                    "id": "block_a",
                    "type": "Shell",
                    "inputs": {"command": "echo 'A'"},
                },
                {
                    "id": "block_b",
                    "type": "Shell",
                    "inputs": {"command": "echo 'B'"},
                },
                {
                    "id": "block_c",
                    "type": "Shell",
                    "inputs": {"command": "echo 'C'"},
                    "depends_on": [
                        "block_a",  # String - should become required=True
                        {"block": "block_b", "required": False},  # Dict - preserve
                    ],
                },
            ],
        )

        # Verify mixed format normalized correctly
        block_c = workflow_schema.blocks[2]
        assert isinstance(block_c, BlockDefinition)
        assert len(block_c.depends_on) == 2
        assert block_c.depends_on[0].block == "block_a"
        assert block_c.depends_on[0].required is True
        assert block_c.depends_on[1].block == "block_b"
        assert block_c.depends_on[1].required is False
