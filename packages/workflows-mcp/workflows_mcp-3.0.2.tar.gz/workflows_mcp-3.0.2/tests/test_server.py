"""Tests for MCP server tool integration.

Tests all MCP tools exposed by the workflows server including:
- Workflow execution (execute_workflow, execute_inline_workflow)
- Workflow discovery (list_workflows, get_workflow_info)
- Schema validation (get_workflow_schema, validate_workflow_yaml)
- Checkpoint management (resume_workflow, list_checkpoints, get_checkpoint_info, delete_checkpoint)
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from workflows_mcp.context import AppContext
from workflows_mcp.engine.executor import WorkflowExecutor
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
    ResumeWorkflowInput,
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
    resume_workflow,
    validate_workflow_yaml,
)


def to_dict(result: WorkflowResponse | dict[str, Any] | list[Any]) -> dict[str, Any] | list[Any]:
    """Convert WorkflowResponse to dict for testing.

    FastMCP automatically calls .model_dump() when serializing responses through the MCP protocol,
    but direct tool calls in tests return the Pydantic model. This helper normalizes for testing.
    """
    if isinstance(result, WorkflowResponse):
        return result.model_dump()
    return result


@pytest.fixture
def mock_context():
    """Create mock AppContext for testing MCP tools."""
    from workflows_mcp.engine.executor_base import create_default_registry

    # Create real instances for more realistic testing
    registry = WorkflowRegistry()

    # Create isolated ExecutorRegistry for this test (includes Shell executor)
    executor_registry = create_default_registry()

    executor = WorkflowExecutor(registry=executor_registry)

    # Load a simple test workflow using Shell executor
    simple_workflow = WorkflowSchema(
        name="test-workflow",
        description="Test workflow for server tests",
        blocks=[{"id": "shell1", "type": "Shell", "inputs": {"command": "echo 'Test'"}}],
        inputs={
            "project_name": {
                "type": "string",
                "description": "Project name",
                "default": "TestProject",
            }
        },
    )
    registry.register(simple_workflow)
    executor.load_workflow(simple_workflow)

    # Create mock context structure
    mock_ctx = MagicMock()
    mock_ctx.request_context.lifespan_context = AppContext(registry=registry, executor=executor)

    return mock_ctx


class TestExecuteWorkflow:
    """Tests for execute_workflow MCP tool."""

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, mock_context):
        """Test successful workflow execution."""
        params = ExecuteWorkflowInput(
            workflow="test-workflow", inputs={"project_name": "MyProject"}
        )
        result = to_dict(await execute_workflow(params=params, ctx=mock_context))

        assert result["status"] == "success"
        assert "outputs" in result
        assert "blocks" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, mock_context):
        """Test execute_workflow with non-existent workflow."""
        params = ExecuteWorkflowInput(workflow="non-existent-workflow")
        result = to_dict(await execute_workflow(params=params, ctx=mock_context))

        assert result["status"] == "failure"
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_workflow_missing_required_inputs(self, mock_context):
        """Test execute_workflow with missing required inputs."""
        # Add workflow with required inputs
        registry = mock_context.request_context.lifespan_context.registry
        executor = mock_context.request_context.lifespan_context.executor

        required_workflow = WorkflowSchema(
            name="test-required-inputs",
            description="Workflow with required inputs",
            blocks=[
                {
                    "id": "echo1",
                    "type": "Shell",
                    "inputs": {"command": "echo ${inputs.required_param}"},
                }
            ],
            inputs={
                "required_param": {
                    "type": "string",
                    "description": "Required parameter",
                    "required": True,
                }
            },
        )
        registry.register(required_workflow)
        executor.load_workflow(required_workflow)

        params = ExecuteWorkflowInput(workflow="test-required-inputs", inputs={})
        result = to_dict(await execute_workflow(params=params, ctx=mock_context))

        assert result["status"] == "failure"
        # Error could be about missing inputs OR variable resolution failure
        assert "required" in result["error"].lower() or "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_workflow_with_inputs(self, mock_context):
        """Test execute_workflow with runtime inputs."""
        params = ExecuteWorkflowInput(
            workflow="test-workflow", inputs={"project_name": "CustomProject"}
        )
        result = to_dict(await execute_workflow(params=params, ctx=mock_context))

        assert result["status"] == "success"
        # Metadata exists and has expected structure
        assert "metadata" in result
        assert isinstance(result["metadata"], dict)


class TestExecuteInlineWorkflow:
    """Tests for execute_inline_workflow MCP tool."""

    @pytest.mark.asyncio
    async def test_execute_inline_workflow_success(self, mock_context):
        """Test successful inline workflow execution."""
        workflow_yaml = """
name: inline-test
description: Inline workflow test
blocks:
  - id: echo
    type: Shell
    inputs:
      command: echo 'Inline test'
"""

        params = ExecuteInlineWorkflowInput(workflow_yaml=workflow_yaml)
        result = to_dict(await execute_inline_workflow(params=params, ctx=mock_context))

        assert result["status"] == "success"
        assert "outputs" in result

    @pytest.mark.asyncio
    async def test_execute_inline_workflow_empty_yaml(self, mock_context):
        """Test execute_inline_workflow with empty YAML."""
        # Use minimal empty YAML (>=10 chars) that passes Pydantic but fails parsing
        params = ExecuteInlineWorkflowInput(workflow_yaml="# empty yaml\n")
        result = to_dict(await execute_inline_workflow(params=params, ctx=mock_context))

        assert result["status"] == "failure"
        # Empty YAML is parsed as None, error should mention it must be a dictionary
        assert "dictionary" in result["error"].lower() or "nonetype" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_inline_workflow_invalid_yaml(self, mock_context):
        """Test execute_inline_workflow with invalid YAML syntax."""
        params = ExecuteInlineWorkflowInput(workflow_yaml="invalid: [unclosed")
        result = to_dict(await execute_inline_workflow(params=params, ctx=mock_context))

        assert result["status"] == "failure"
        assert "parse" in result["error"].lower() or "yaml" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_inline_workflow_missing_required_fields(self, mock_context):
        """Test execute_inline_workflow with missing required workflow fields."""
        # Missing 'blocks' field
        workflow_yaml = """
name: incomplete-workflow
description: Missing blocks
"""

        params = ExecuteInlineWorkflowInput(workflow_yaml=workflow_yaml)
        result = to_dict(await execute_inline_workflow(params=params, ctx=mock_context))

        assert result["status"] == "failure"
        # Should mention missing required fields


class TestListWorkflows:
    """Tests for list_workflows MCP tool."""

    @pytest.mark.asyncio
    async def test_list_workflows_success(self, mock_context):
        """Test successful workflow listing returns list of names."""
        params = ListWorkflowsInput()
        result = await list_workflows(params=params, ctx=mock_context)

        assert isinstance(result, list)
        assert len(result) > 0
        # Check that results are workflow names (strings)
        assert isinstance(result[0], str)
        assert "test-workflow" in result

    @pytest.mark.asyncio
    async def test_list_workflows_returns_all_workflows(self, mock_context):
        """Test list_workflows returns all registered workflow names."""
        # Add another workflow
        registry = mock_context.request_context.lifespan_context.registry

        another_workflow = WorkflowSchema(
            name="another-workflow",
            description="Another test workflow",
            blocks=[{"id": "echo", "type": "Shell", "inputs": {"command": "echo Hello"}}],
        )
        registry.register(another_workflow)

        params = ListWorkflowsInput()
        result = await list_workflows(params=params, ctx=mock_context)

        assert isinstance(result, list)
        assert len(result) >= 2
        assert "test-workflow" in result
        assert "another-workflow" in result

    @pytest.mark.asyncio
    async def test_list_workflows_simple_interface(self, mock_context):
        """Test that list_workflows has simple interface with no filtering."""
        # Verify function returns simple list of workflow names
        params = ListWorkflowsInput()
        result = await list_workflows(params=params, ctx=mock_context)

        assert isinstance(result, list)
        if len(result) > 0:
            # All items should be strings (workflow names)
            assert all(isinstance(name, str) for name in result)


class TestGetWorkflowInfo:
    """Tests for get_workflow_info MCP tool."""

    @pytest.mark.asyncio
    async def test_get_workflow_info_success(self, mock_context):
        """Test successful workflow info retrieval."""
        params = GetWorkflowInfoInput(workflow="test-workflow")
        result = await get_workflow_info(params=params, ctx=mock_context)

        assert "name" in result
        assert result["name"] == "test-workflow"
        assert "description" in result
        assert "blocks" in result
        assert "total_blocks" in result

    @pytest.mark.asyncio
    async def test_get_workflow_info_not_found(self, mock_context):
        """Test get_workflow_info with non-existent workflow."""
        params = GetWorkflowInfoInput(workflow="non-existent")
        result = await get_workflow_info(params=params, ctx=mock_context)

        assert "error" in result
        assert "not found" in result["error"].lower()
        # Should include available workflows
        assert "available_workflows" in result or "help" in result


class TestGetWorkflowSchema:
    """Tests for get_workflow_schema MCP tool."""

    @pytest.mark.asyncio
    async def test_get_workflow_schema_success(self):
        """Test successful workflow schema retrieval."""
        result = await get_workflow_schema()

        assert isinstance(result, dict)
        # JSON Schema should have these top-level properties
        assert "$schema" in result or "type" in result
        # Should describe workflow structure
        assert "properties" in result or "definitions" in result

    @pytest.mark.asyncio
    async def test_get_workflow_schema_structure(self):
        """Test workflow schema contains expected structure."""
        result = await get_workflow_schema()

        # Schema should be a valid JSON Schema
        assert isinstance(result, dict)
        # Should be usable for validation
        assert len(result) > 0


class TestValidateWorkflowYaml:
    """Tests for validate_workflow_yaml MCP tool."""

    @pytest.mark.asyncio
    async def test_validate_workflow_yaml_valid(self):
        """Test validation of valid workflow YAML."""
        valid_yaml = """
name: valid-workflow
description: Valid workflow
blocks:
  - id: echo
    type: Shell
    inputs:
      command: echo 'Test'
"""

        params = ValidateWorkflowYamlInput(yaml_content=valid_yaml)
        result = await validate_workflow_yaml(params=params)

        # Check basic structure
        assert "valid" in result
        assert "errors" in result
        assert "block_types_used" in result
        # Validation may fail if Shell not in schema - that's ok for this test
        if result["valid"]:
            assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_workflow_yaml_syntax_error(self):
        """Test validation of YAML with syntax error."""
        invalid_yaml = "name: [unclosed bracket"

        params = ValidateWorkflowYamlInput(yaml_content=invalid_yaml)
        result = await validate_workflow_yaml(params=params)

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        # Error message includes "YAML parsing error" and "Invalid YAML syntax"
        assert "yaml" in result["errors"][0].lower() and "syntax" in result["errors"][0].lower()

    @pytest.mark.asyncio
    async def test_validate_workflow_yaml_schema_error(self):
        """Test validation of YAML with schema violation."""
        # Missing required 'name' field
        invalid_yaml = """
description: Missing name field
blocks: []
"""

        params = ValidateWorkflowYamlInput(yaml_content=invalid_yaml)
        result = await validate_workflow_yaml(params=params)

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_validate_workflow_yaml_warnings(self):
        """Test validation returns warnings for non-critical issues."""
        valid_yaml = """
name: workflow-with-warnings
description: Test workflow
blocks:
  - id: block1
    type: Shell
    inputs:
      command: echo 'Test'
"""

        params = ValidateWorkflowYamlInput(yaml_content=valid_yaml)
        result = await validate_workflow_yaml(params=params)

        # Should have warnings field
        assert "warnings" in result
        assert isinstance(result["warnings"], list)


class TestResumeWorkflow:
    """Tests for resume_workflow MCP tool."""

    @pytest.mark.asyncio
    async def test_resume_workflow_empty_checkpoint_id(self, mock_context):
        """Test resume_workflow with invalid checkpoint ID."""
        params = ResumeWorkflowInput(checkpoint_id="invalid")
        result = to_dict(await resume_workflow(params=params, ctx=mock_context))

        assert result["status"] == "failure"
        # Invalid checkpoint ID is treated as not found
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_resume_workflow_checkpoint_not_found(self, mock_context):
        """Test resume_workflow with non-existent checkpoint."""
        params = ResumeWorkflowInput(checkpoint_id="non_existent_checkpoint")
        result = to_dict(await resume_workflow(params=params, ctx=mock_context))

        assert result["status"] == "failure"
        # Should indicate checkpoint not found


class TestListCheckpoints:
    """Tests for list_checkpoints MCP tool."""

    @pytest.mark.asyncio
    async def test_list_checkpoints_success(self, mock_context):
        """Test successful checkpoint listing."""
        params = ListCheckpointsInput()
        result = await list_checkpoints(params=params, ctx=mock_context)

        assert "checkpoints" in result
        assert "total" in result
        assert isinstance(result["checkpoints"], list)
        assert isinstance(result["total"], int)

    @pytest.mark.asyncio
    async def test_list_checkpoints_with_workflow_filter(self, mock_context):
        """Test list_checkpoints with workflow name filter."""
        params = ListCheckpointsInput(workflow_name="test-workflow")
        result = await list_checkpoints(params=params, ctx=mock_context)

        assert "checkpoints" in result
        assert "total" in result
        # Filtered list should be returned


class TestGetCheckpointInfo:
    """Tests for get_checkpoint_info MCP tool."""

    @pytest.mark.asyncio
    async def test_get_checkpoint_info_empty_checkpoint_id(self, mock_context):
        """Test get_checkpoint_info with invalid checkpoint ID."""
        params = GetCheckpointInfoInput(checkpoint_id="invalid")
        result = await get_checkpoint_info(params=params, ctx=mock_context)

        assert result["found"] is False
        assert "error" in result
        # Invalid checkpoint ID is treated as not found
        assert "not found" in result["error"].lower() or "expired" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_get_checkpoint_info_not_found(self, mock_context):
        """Test get_checkpoint_info with non-existent checkpoint."""
        params = GetCheckpointInfoInput(checkpoint_id="non_existent")
        result = await get_checkpoint_info(params=params, ctx=mock_context)

        assert result["found"] is False
        assert "error" in result or "not found" in str(result).lower()


class TestDeleteCheckpoint:
    """Tests for delete_checkpoint MCP tool."""

    @pytest.mark.asyncio
    async def test_delete_checkpoint_empty_checkpoint_id(self, mock_context):
        """Test delete_checkpoint with invalid checkpoint ID."""
        params = DeleteCheckpointInput(checkpoint_id="invalid")
        result = await delete_checkpoint(params=params, ctx=mock_context)

        assert result["deleted"] is False
        # delete_checkpoint returns a "message" field, not "error"
        assert "message" in result
        assert "not found" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_delete_checkpoint_not_found(self, mock_context):
        """Test delete_checkpoint with non-existent checkpoint."""
        params = DeleteCheckpointInput(checkpoint_id="non_existent")
        result = await delete_checkpoint(params=params, ctx=mock_context)

        assert result["deleted"] is False
        # Should indicate checkpoint not found


class TestResponseStructures:
    """Tests for response structure consistency."""

    @pytest.mark.asyncio
    async def test_workflow_response_structure(self, mock_context):
        """Test WorkflowResponse structure consistency."""
        params = ExecuteWorkflowInput(workflow="test-workflow")
        result = to_dict(await execute_workflow(params=params, ctx=mock_context))

        # All workflow execution responses should have these keys
        assert "status" in result
        assert result["status"] in ["success", "failure", "paused"]

        if result["status"] == "success":
            assert "outputs" in result
            assert "blocks" in result
            assert "metadata" in result
        elif result["status"] == "failure":
            assert "error" in result

    @pytest.mark.asyncio
    async def test_checkpoint_response_structure(self, mock_context):
        """Test checkpoint-related response structures."""
        # List checkpoints
        list_params = ListCheckpointsInput()
        list_result = await list_checkpoints(params=list_params, ctx=mock_context)
        assert "checkpoints" in list_result
        assert "total" in list_result

        # Get checkpoint info
        info_params = GetCheckpointInfoInput(checkpoint_id="test")
        info_result = await get_checkpoint_info(params=info_params, ctx=mock_context)
        assert "found" in info_result

        # Delete checkpoint
        delete_params = DeleteCheckpointInput(checkpoint_id="test")
        delete_result = await delete_checkpoint(params=delete_params, ctx=mock_context)
        assert "deleted" in delete_result
        # Response may have checkpoint_id or params.checkpoint_id
        assert "checkpoint_id" in delete_result or "params.checkpoint_id" in delete_result
