"""Comprehensive tests for MCP tool implementations following best practices.

This test suite validates:
- Pydantic input validation
- Tool functionality with valid inputs
- Error handling and actionable error messages
- Response format variations (minimal/detailed, json/markdown)
- Edge cases and boundary conditions
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from workflows_mcp.context import AppContext
from workflows_mcp.engine.executor import WorkflowExecutor
from workflows_mcp.engine.executor_base import create_default_registry
from workflows_mcp.engine.registry import WorkflowRegistry
from workflows_mcp.engine.response import WorkflowResponse
from workflows_mcp.engine.schema import WorkflowSchema
from workflows_mcp.models import (
    DeleteCheckpointInput,
    ExecuteInlineWorkflowInput,
    ExecuteWorkflowInput,
    GetCheckpointInfoInput,
    GetWorkflowInfoInput,
    ListCheckpointsInput,
    ListWorkflowsInput,
    ValidateWorkflowYamlInput,
)
from workflows_mcp.tools import (
    delete_checkpoint,
    execute_inline_workflow,
    execute_workflow,
    get_checkpoint_info,
    get_workflow_info,
    get_workflow_schema,
    list_checkpoints,
    list_workflows,
    validate_workflow_yaml,
)


def to_dict(result: WorkflowResponse | dict[str, Any] | list[Any]) -> dict[str, Any] | list[Any]:
    """Convert WorkflowResponse or dict to dict for testing."""
    if isinstance(result, WorkflowResponse):
        return result.model_dump()
    return result


@pytest.fixture
def mock_context():
    """Create mock MCP context with app context."""
    registry = WorkflowRegistry()
    executor_registry = create_default_registry()
    executor = WorkflowExecutor(registry=executor_registry)

    # Register a test workflow
    test_workflow = WorkflowSchema(
        name="test-workflow",
        description="Test workflow for unit tests",
        blocks=[
            {
                "id": "step1",
                "type": "Shell",
                "inputs": {"command": "echo 'Hello ${inputs.message}'"},
            }
        ],
        inputs={
            "message": {"type": "string", "description": "Message to echo", "default": "World"}
        },
        outputs={"result": "${blocks.step1.outputs.stdout}"},
    )

    registry.register(test_workflow)
    executor.load_workflow(test_workflow)

    app_context = AppContext(registry=registry, executor=executor)

    mock_ctx = MagicMock()
    mock_ctx.request_context.lifespan_context = app_context

    return mock_ctx


# =============================================================================
# Workflow Execution Tests
# =============================================================================


class TestExecuteWorkflow:
    """Test execute_workflow tool with Pydantic input validation."""

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, mock_context):
        """Test successful workflow execution with valid inputs."""
        params = ExecuteWorkflowInput(
            workflow="test-workflow", inputs={"message": "Test"}, response_format="minimal"
        )

        result = to_dict(await execute_workflow(params=params, ctx=mock_context))

        assert result["status"] == "success"
        assert "outputs" in result
        # Minimal format should have empty blocks/metadata
        assert result["blocks"] == {}
        assert result["metadata"] == {}

    @pytest.mark.asyncio
    async def test_execute_workflow_detailed_format(self, mock_context):
        """Test workflow execution with detailed response format."""
        params = ExecuteWorkflowInput(
            workflow="test-workflow", inputs={"message": "Test"}, response_format="detailed"
        )

        result = to_dict(await execute_workflow(params=params, ctx=mock_context))

        assert result["status"] == "success"
        # Detailed format should include blocks and metadata
        assert len(result["blocks"]) > 0
        assert len(result["metadata"]) > 0

    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, mock_context):
        """Test execute_workflow with non-existent workflow returns actionable error."""
        params = ExecuteWorkflowInput(workflow="non-existent-workflow")

        result = to_dict(await execute_workflow(params=params, ctx=mock_context))

        assert result["status"] == "failure"
        assert "not found" in result["error"].lower()
        # Actionable error message - includes available workflows
        assert "available_workflows" in result["outputs"]
        assert isinstance(result["outputs"]["available_workflows"], list)

    @pytest.mark.asyncio
    async def test_pydantic_validation_empty_workflow_name(self):
        """Test Pydantic validation rejects empty workflow name."""
        from pydantic import ValidationError

        # After stripping, empty string fails min_length=1 validation
        with pytest.raises(ValidationError, match="at least 1 character"):
            ExecuteWorkflowInput(workflow="  ")

    @pytest.mark.asyncio
    async def test_pydantic_validation_workflow_name_max_length(self):
        """Test Pydantic validation enforces max length."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ExecuteWorkflowInput(workflow="a" * 201)


class TestExecuteInlineWorkflow:
    """Test execute_inline_workflow tool."""

    @pytest.mark.asyncio
    async def test_execute_inline_workflow_success(self, mock_context):
        """Test successful inline workflow execution."""
        yaml_content = """
name: inline-test
description: Inline test workflow
blocks:
  - id: echo
    type: Shell
    inputs:
      command: echo "Hello Inline"
outputs:
  result: "${blocks.echo.outputs.stdout}"
"""
        params = ExecuteInlineWorkflowInput(workflow_yaml=yaml_content)

        result = to_dict(await execute_inline_workflow(params=params, ctx=mock_context))

        assert result["status"] == "success"
        assert "outputs" in result

    @pytest.mark.asyncio
    async def test_pydantic_validation_empty_yaml(self):
        """Test Pydantic validation rejects empty YAML."""
        from pydantic import ValidationError

        # After stripping, empty string fails min_length=10 validation
        with pytest.raises(ValidationError, match="at least 10 characters"):
            ExecuteInlineWorkflowInput(workflow_yaml="   ")


# =============================================================================
# Workflow Discovery Tests
# =============================================================================


class TestListWorkflows:
    """Test list_workflows tool."""

    @pytest.mark.asyncio
    async def test_list_workflows_json_format(self, mock_context):
        """Test list_workflows returns JSON list by default."""
        params = ListWorkflowsInput(format="json")

        result = await list_workflows(params=params, ctx=mock_context)

        assert isinstance(result, list)
        assert "test-workflow" in result

    @pytest.mark.asyncio
    async def test_list_workflows_markdown_format(self, mock_context):
        """Test list_workflows markdown format."""
        params = ListWorkflowsInput(format="markdown")

        result = await list_workflows(params=params, ctx=mock_context)

        assert isinstance(result, str)
        assert "Available Workflows" in result
        assert "test-workflow" in result

    @pytest.mark.asyncio
    async def test_list_workflows_with_tag_filter(self, mock_context):
        """Test workflow filtering by tags."""
        params = ListWorkflowsInput(tags=["nonexistent-tag"], format="json")

        result = await list_workflows(params=params, ctx=mock_context)

        # Should return empty list when no workflows match tags
        assert isinstance(result, list)


class TestGetWorkflowInfo:
    """Test get_workflow_info tool."""

    @pytest.mark.asyncio
    async def test_get_workflow_info_json_format(self, mock_context):
        """Test get_workflow_info returns structured data."""
        params = GetWorkflowInfoInput(workflow="test-workflow", format="json")

        result = to_dict(await get_workflow_info(params=params, ctx=mock_context))

        assert isinstance(result, dict)
        assert result["name"] == "test-workflow"
        assert "description" in result
        assert "blocks" in result
        assert result["total_blocks"] > 0

    @pytest.mark.asyncio
    async def test_get_workflow_info_markdown_format(self, mock_context):
        """Test get_workflow_info markdown format."""
        params = GetWorkflowInfoInput(workflow="test-workflow", format="markdown")

        result = await get_workflow_info(params=params, ctx=mock_context)

        assert isinstance(result, str)
        assert "# Workflow: test-workflow" in result
        assert "## Blocks" in result

    @pytest.mark.asyncio
    async def test_get_workflow_info_not_found(self, mock_context):
        """Test get_workflow_info with non-existent workflow returns helpful error."""
        params = GetWorkflowInfoInput(workflow="non-existent", format="json")

        result = to_dict(await get_workflow_info(params=params, ctx=mock_context))

        assert "error" in result
        assert "available_workflows" in result


# =============================================================================
# Schema and Validation Tests
# =============================================================================


class TestGetWorkflowSchema:
    """Test get_workflow_schema tool."""

    @pytest.mark.asyncio
    async def test_get_workflow_schema_returns_valid_schema(self):
        """Test schema generation returns valid JSON Schema."""
        schema = await get_workflow_schema()

        assert isinstance(schema, dict)
        assert "$schema" in schema or "type" in schema
        assert "properties" in schema

    @pytest.mark.asyncio
    async def test_get_workflow_schema_includes_block_types(self):
        """Test schema includes registered block types."""
        schema = await get_workflow_schema()

        # Schema should describe workflow structure
        assert "properties" in schema
        assert "blocks" in schema["properties"]


class TestValidateWorkflowYaml:
    """Test validate_workflow_yaml tool."""

    @pytest.mark.asyncio
    async def test_validate_valid_workflow(self):
        """Test validation of valid workflow YAML."""
        yaml_content = """
name: valid-workflow
description: A valid workflow
blocks:
  - id: step1
    type: Shell
    inputs:
      command: echo "test"
"""
        params = ValidateWorkflowYamlInput(yaml_content=yaml_content)

        result = await validate_workflow_yaml(params=params)

        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert "Shell" in result["block_types_used"]

    @pytest.mark.asyncio
    async def test_validate_invalid_yaml_syntax(self):
        """Test validation catches YAML syntax errors."""
        params = ValidateWorkflowYamlInput(yaml_content="invalid: [yaml: syntax")

        result = await validate_workflow_yaml(params=params)

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_pydantic_validation_empty_yaml(self):
        """Test Pydantic validation rejects empty YAML."""
        from pydantic import ValidationError

        # After stripping, empty string fails min_length=10 validation
        with pytest.raises(ValidationError, match="at least 10 characters"):
            ValidateWorkflowYamlInput(yaml_content="  ")


# =============================================================================
# Checkpoint Management Tests
# =============================================================================


class TestCheckpointManagement:
    """Test checkpoint-related tools."""

    @pytest.mark.asyncio
    async def test_list_checkpoints_json_format(self, mock_context):
        """Test list_checkpoints returns structured data."""
        params = ListCheckpointsInput(format="json")

        result = to_dict(await list_checkpoints(params=params, ctx=mock_context))

        assert "checkpoints" in result
        assert "total" in result
        assert isinstance(result["checkpoints"], list)

    @pytest.mark.asyncio
    async def test_list_checkpoints_markdown_format(self, mock_context):
        """Test list_checkpoints markdown format."""
        params = ListCheckpointsInput(format="markdown")

        result = await list_checkpoints(params=params, ctx=mock_context)

        assert isinstance(result, str)
        # Should handle empty checkpoints gracefully
        assert "checkpoints" in result.lower() or "no" in result.lower()

    @pytest.mark.asyncio
    async def test_get_checkpoint_info_not_found(self, mock_context):
        """Test get_checkpoint_info with non-existent checkpoint."""
        params = GetCheckpointInfoInput(checkpoint_id="nonexistent", format="json")

        result = to_dict(await get_checkpoint_info(params=params, ctx=mock_context))

        assert result["found"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_delete_checkpoint_not_found(self, mock_context):
        """Test delete_checkpoint with non-existent checkpoint."""
        params = DeleteCheckpointInput(checkpoint_id="nonexistent")

        result = await delete_checkpoint(params=params, ctx=mock_context)

        assert result["deleted"] is False

    @pytest.mark.asyncio
    async def test_pydantic_validation_empty_checkpoint_id(self):
        """Test Pydantic validation rejects empty checkpoint ID."""
        from pydantic import ValidationError

        # After stripping, empty string fails min_length=1 validation
        with pytest.raises(ValidationError, match="at least 1 character"):
            DeleteCheckpointInput(checkpoint_id="  ")


# =============================================================================
# Input Validation Tests
# =============================================================================


class TestPydanticValidation:
    """Test Pydantic input validation across all models."""

    def test_execute_workflow_input_validation(self):
        """Test ExecuteWorkflowInput validation."""
        # Valid input
        valid = ExecuteWorkflowInput(workflow="test", inputs={"key": "value"})
        assert valid.workflow == "test"
        assert valid.inputs == {"key": "value"}

        # Invalid: empty workflow name
        with pytest.raises(ValueError):
            ExecuteWorkflowInput(workflow="")

        # Invalid: workflow name too long
        with pytest.raises(ValueError):
            ExecuteWorkflowInput(workflow="a" * 201)

    def test_list_workflows_input_validation(self):
        """Test ListWorkflowsInput validation."""
        # Valid input with tags
        valid = ListWorkflowsInput(tags=["python", "ci"], format="json")
        assert valid.tags == ["python", "ci"]

        # Valid: empty tags list
        valid_empty = ListWorkflowsInput()
        assert valid_empty.tags == []

    def test_response_format_validation(self):
        """Test response_format field validation."""
        # Valid formats
        ExecuteWorkflowInput(workflow="test", response_format="minimal")
        ExecuteWorkflowInput(workflow="test", response_format="detailed")

        # Invalid format should be caught by Literal type
        with pytest.raises(ValueError):
            ExecuteWorkflowInput(workflow="test", response_format="invalid")  # type: ignore

    def test_format_field_validation(self):
        """Test format field validation (json/markdown)."""
        # Valid formats
        ListWorkflowsInput(format="json")
        ListWorkflowsInput(format="markdown")

        # Invalid format
        with pytest.raises(ValueError):
            ListWorkflowsInput(format="invalid")  # type: ignore


# =============================================================================
# Error Message Quality Tests
# =============================================================================


class TestErrorMessages:
    """Test that error messages are actionable and educational."""

    @pytest.mark.asyncio
    async def test_workflow_not_found_error_includes_suggestions(self, mock_context):
        """Test workflow not found error includes helpful suggestions."""
        params = ExecuteWorkflowInput(workflow="typo-workflow")

        result = to_dict(await execute_workflow(params=params, ctx=mock_context))

        assert result["status"] == "failure"
        # Error should mention available workflows
        assert "available" in result["error"].lower() or "list_workflows" in result["error"]
        # Should provide list of available workflows
        assert "available_workflows" in result["outputs"]

    @pytest.mark.asyncio
    async def test_validation_error_provides_guidance(self):
        """Test YAML validation errors provide clear guidance."""
        params = ValidateWorkflowYamlInput(yaml_content="invalid: yaml: [syntax")

        result = await validate_workflow_yaml(params=params)

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        # Error messages should be descriptive
        assert any("YAML" in error or "parsing" in error for error in result["errors"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
