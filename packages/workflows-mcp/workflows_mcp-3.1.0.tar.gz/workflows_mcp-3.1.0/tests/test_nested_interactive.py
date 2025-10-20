"""Tests for nested interactive workflow pause/resume functionality.

Tests that interactive blocks (Prompt) work correctly within nested workflows
when executed via ExecuteWorkflow blocks. Verifies:
- Child workflow pause propagates to parent correctly
- Parent checkpoint preserves child checkpoint reference
- Resume delegates to child workflow correctly
- Multi-level nesting works recursively
- Multiple pause/resume cycles handle state correctly
"""

from unittest.mock import MagicMock

import pytest

from workflows_mcp.context import AppContext
from workflows_mcp.engine.executor import WorkflowExecutor
from workflows_mcp.engine.registry import WorkflowRegistry
from workflows_mcp.engine.schema import WorkflowSchema
from workflows_mcp.models import ExecuteWorkflowInput, ResumeWorkflowInput
from workflows_mcp.tools import execute_workflow, resume_workflow


@pytest.fixture
def interactive_workflows_context():
    """Create context with child and parent workflows for nested interactive testing."""
    from workflows_mcp.engine.executor_base import create_default_registry

    registry = WorkflowRegistry()
    executor_registry = create_default_registry()
    executor = WorkflowExecutor(registry=executor_registry)

    # Child workflow with interactive Prompt block
    child_workflow = WorkflowSchema(
        name="child-with-prompt",
        description="Child workflow that pauses for user input",
        blocks=[
            {
                "id": "ask_user",
                "type": "Prompt",
                "inputs": {"prompt": "Enter confirmation (yes/no):"},
            },
            {
                "id": "process_response",
                "type": "Shell",
                "inputs": {"command": "echo Response: ${blocks.ask_user.outputs.response}"},
                "depends_on": ["ask_user"],
            },
        ],
        outputs={"user_confirmed": "${blocks.ask_user.outputs.response}"},
    )

    # Parent workflow that calls child via ExecuteWorkflow
    parent_workflow = WorkflowSchema(
        name="parent-with-child",
        description="Parent workflow that executes child with interactive block",
        blocks=[
            {
                "id": "setup",
                "type": "Shell",
                "inputs": {"command": "echo Setting up..."},
            },
            {
                "id": "run_child",
                "type": "ExecuteWorkflow",
                "inputs": {"workflow": "child-with-prompt", "inputs": {}},
                "depends_on": ["setup"],
            },
            {
                "id": "finish",
                "type": "Shell",
                "inputs": {"command": "echo Confirmed: ${blocks.run_child.outputs.user_confirmed}"},
                "depends_on": ["run_child"],
            },
        ],
        outputs={"final_confirmation": "${blocks.run_child.outputs.user_confirmed}"},
    )

    registry.register(child_workflow)
    registry.register(parent_workflow)
    executor.load_workflow(child_workflow)
    executor.load_workflow(parent_workflow)

    mock_ctx = MagicMock()
    mock_ctx.request_context.lifespan_context = AppContext(registry=registry, executor=executor)

    return mock_ctx


@pytest.fixture
def multi_level_workflows_context():
    """Create context with three-level nested workflows (A→B→C)."""
    from workflows_mcp.engine.executor_base import create_default_registry

    registry = WorkflowRegistry()
    executor_registry = create_default_registry()
    executor = WorkflowExecutor(registry=executor_registry)

    # Level C: Deepest workflow with interactive block
    workflow_c = WorkflowSchema(
        name="workflow-c",
        description="Deepest workflow with prompt",
        blocks=[
            {
                "id": "deep_prompt",
                "type": "Prompt",
                "inputs": {"prompt": "Deep level confirmation:"},
            }
        ],
        outputs={"deep_response": "${blocks.deep_prompt.outputs.response}"},
    )

    # Level B: Middle workflow that calls C
    workflow_b = WorkflowSchema(
        name="workflow-b",
        description="Middle workflow calling C",
        blocks=[
            {
                "id": "call_c",
                "type": "ExecuteWorkflow",
                "inputs": {"workflow": "workflow-c", "inputs": {}},
            }
        ],
        outputs={"middle_response": "${blocks.call_c.outputs.deep_response}"},
    )

    # Level A: Top workflow that calls B
    workflow_a = WorkflowSchema(
        name="workflow-a",
        description="Top workflow calling B",
        blocks=[
            {
                "id": "call_b",
                "type": "ExecuteWorkflow",
                "inputs": {"workflow": "workflow-b", "inputs": {}},
            }
        ],
        outputs={"top_response": "${blocks.call_b.outputs.middle_response}"},
    )

    registry.register(workflow_c)
    registry.register(workflow_b)
    registry.register(workflow_a)
    executor.load_workflow(workflow_c)
    executor.load_workflow(workflow_b)
    executor.load_workflow(workflow_a)

    mock_ctx = MagicMock()
    mock_ctx.request_context.lifespan_context = AppContext(registry=registry, executor=executor)

    return mock_ctx


class TestSimpleNestedInteractive:
    """Tests for simple nested interactive workflows (parent→child with Prompt)."""

    @pytest.mark.asyncio
    async def test_child_pause_propagates_to_parent(self, interactive_workflows_context):
        """Test that child workflow pause correctly propagates to parent."""
        params = ExecuteWorkflowInput(
            workflow="parent-with-child", inputs={}, response_format="detailed"
        )

        result = await execute_workflow(params=params, ctx=interactive_workflows_context)
        result_dict = result.model_dump()

        # Verify execution paused
        assert result_dict["status"] == "paused"
        assert "prompt" in result_dict
        assert result_dict["prompt"] == "Enter confirmation (yes/no):"

        # Verify checkpoint created
        assert "checkpoint_id" in result_dict
        parent_checkpoint_id = result_dict["checkpoint_id"]
        assert parent_checkpoint_id.startswith("pause_")

        # Verify we can access the checkpoint to inspect pause_metadata
        app_ctx = interactive_workflows_context.request_context.lifespan_context
        checkpoint_state = await app_ctx.executor.checkpoint_store.load_checkpoint(
            parent_checkpoint_id
        )
        assert checkpoint_state is not None
        assert checkpoint_state.paused_block_id == "run_child"

        # Verify pause_metadata contains child checkpoint reference
        assert checkpoint_state.pause_metadata is not None
        pause_metadata = checkpoint_state.pause_metadata
        assert "child_checkpoint_id" in pause_metadata
        assert pause_metadata["child_checkpoint_id"] != ""
        assert pause_metadata["child_checkpoint_id"].startswith("pause_")
        assert pause_metadata["child_workflow"] == "child-with-prompt"

    @pytest.mark.asyncio
    async def test_parent_resume_delegates_to_child(self, interactive_workflows_context):
        """Test that resuming parent workflow correctly delegates to child."""
        # First, execute to get parent paused
        execute_params = ExecuteWorkflowInput(
            workflow="parent-with-child", inputs={}, response_format="detailed"
        )
        execute_result = await execute_workflow(
            params=execute_params, ctx=interactive_workflows_context
        )
        execute_dict = execute_result.model_dump()

        assert execute_dict["status"] == "paused"
        parent_checkpoint_id = execute_dict["checkpoint_id"]

        # Now resume parent with LLM response
        resume_params = ResumeWorkflowInput(
            checkpoint_id=parent_checkpoint_id,
            llm_response="yes",
            response_format="detailed",
        )
        resume_result = await resume_workflow(
            params=resume_params, ctx=interactive_workflows_context
        )
        resume_dict = resume_result.model_dump()

        # Verify successful completion
        assert resume_dict["status"] == "success"
        assert "outputs" in resume_dict
        assert resume_dict["outputs"]["final_confirmation"] == "yes"

        # Verify workflow completed (check metadata if available)
        if resume_dict.get("metadata"):
            # Metadata should show parent workflow completed
            assert resume_dict["metadata"]["total_blocks"] == 3  # setup, run_child, finish

    @pytest.mark.asyncio
    async def test_nested_outputs_flow_correctly(self, interactive_workflows_context):
        """Test that child workflow outputs correctly become parent block outputs."""
        # Execute to pause
        execute_params = ExecuteWorkflowInput(workflow="parent-with-child", inputs={})
        execute_result = await execute_workflow(
            params=execute_params, ctx=interactive_workflows_context
        )
        parent_checkpoint_id = execute_result.model_dump()["checkpoint_id"]

        # Resume with specific response
        resume_params = ResumeWorkflowInput(
            checkpoint_id=parent_checkpoint_id, llm_response="confirmed"
        )
        resume_result = await resume_workflow(
            params=resume_params, ctx=interactive_workflows_context
        )
        resume_dict = resume_result.model_dump()

        # Verify output flow: child → parent block outputs
        assert resume_dict["outputs"]["final_confirmation"] == "confirmed"


class TestMultiLevelNesting:
    """Tests for multi-level nested workflows (A→B→C with interactive at C)."""

    @pytest.mark.asyncio
    async def test_three_level_pause_propagation(self, multi_level_workflows_context):
        """Test pause propagates through three levels: A→B→C."""
        params = ExecuteWorkflowInput(
            workflow="workflow-a", inputs={}, response_format="detailed"
        )

        result = await execute_workflow(params=params, ctx=multi_level_workflows_context)
        result_dict = result.model_dump()

        # Verify execution paused at top level
        assert result_dict["status"] == "paused"
        assert result_dict["prompt"] == "Deep level confirmation:"

        # Verify top-level checkpoint created
        top_checkpoint_id = result_dict["checkpoint_id"]
        assert top_checkpoint_id.startswith("pause_")

        # Load checkpoint to verify pause_metadata contains nested checkpoint chain
        app_ctx = multi_level_workflows_context.request_context.lifespan_context
        checkpoint_state = await app_ctx.executor.checkpoint_store.load_checkpoint(
            top_checkpoint_id
        )
        assert checkpoint_state is not None
        assert checkpoint_state.pause_metadata is not None

        pause_metadata = checkpoint_state.pause_metadata
        assert "child_checkpoint_id" in pause_metadata
        assert pause_metadata["child_workflow"] == "workflow-b"

        # Child's pause_metadata should also contain its child's checkpoint
        child_pause_meta = pause_metadata.get("child_pause_metadata", {})
        assert "child_checkpoint_id" in child_pause_meta
        assert child_pause_meta["child_workflow"] == "workflow-c"

    @pytest.mark.asyncio
    async def test_three_level_resume_cascade(self, multi_level_workflows_context):
        """Test resume correctly cascades through three levels."""
        # Execute to get paused
        execute_params = ExecuteWorkflowInput(workflow="workflow-a", inputs={})
        execute_result = await execute_workflow(
            params=execute_params, ctx=multi_level_workflows_context
        )
        top_checkpoint_id = execute_result.model_dump()["checkpoint_id"]

        # Resume from top level
        resume_params = ResumeWorkflowInput(
            checkpoint_id=top_checkpoint_id, llm_response="deep-answer"
        )
        resume_result = await resume_workflow(
            params=resume_params, ctx=multi_level_workflows_context
        )
        resume_dict = resume_result.model_dump()

        # Verify successful completion
        assert resume_dict["status"] == "success"

        # Verify output flowed through all levels: C→B→A
        assert resume_dict["outputs"]["top_response"] == "deep-answer"


class TestMultiplePauseResumeCycles:
    """Tests for workflows that pause multiple times (not yet implemented - future)."""

    @pytest.mark.skip(reason="Multiple pause cycles within same workflow not yet implemented")
    @pytest.mark.asyncio
    async def test_child_pauses_twice(self, interactive_workflows_context):
        """Test child workflow that pauses, resumes, then pauses again."""
        # This would require a workflow with two Prompt blocks
        # Not implementing now (YAGNI), but placeholder for future
        pass


class TestErrorHandling:
    """Tests for error cases in nested interactive workflows."""

    @pytest.mark.asyncio
    async def test_resume_without_child_checkpoint_fails(self, interactive_workflows_context):
        """Test resume fails gracefully if child_checkpoint_id is missing."""
        # This tests the defensive programming in ExecuteWorkflowExecutor.resume()

        # First create a normal pause
        execute_params = ExecuteWorkflowInput(workflow="parent-with-child", inputs={})
        execute_result = await execute_workflow(
            params=execute_params, ctx=interactive_workflows_context
        )
        parent_checkpoint_id = execute_result.model_dump()["checkpoint_id"]

        # Manually corrupt the checkpoint by removing child_checkpoint_id
        # (simulates a bug or corrupted state)
        app_ctx = interactive_workflows_context.request_context.lifespan_context
        checkpoint_state = await app_ctx.executor.checkpoint_store.load_checkpoint(
            parent_checkpoint_id
        )

        if checkpoint_state and checkpoint_state.pause_metadata:
            # Corrupt the pause_metadata
            checkpoint_state.pause_metadata.pop("child_checkpoint_id", None)
            await app_ctx.executor.checkpoint_store.save_checkpoint(checkpoint_state)

        # Now try to resume - should fail gracefully
        resume_params = ResumeWorkflowInput(
            checkpoint_id=parent_checkpoint_id, llm_response="yes"
        )
        resume_result = await resume_workflow(
            params=resume_params, ctx=interactive_workflows_context
        )
        resume_dict = resume_result.model_dump()

        # Verify it failed with clear error message
        assert resume_dict["status"] == "failure"
        assert "child_checkpoint_id" in resume_dict.get("error", "")

    @pytest.mark.asyncio
    async def test_child_workflow_failure_propagates(self, interactive_workflows_context):
        """Test that child workflow failures propagate correctly to parent.

        Note: A block failing doesn't necessarily fail the workflow - it depends
        on how outputs are computed. This test verifies that if a child workflow
        reports failure status, the parent receives it correctly.
        """
        # Create a workflow with a child that will report successful completion
        # even though a block failed (realistic scenario)
        app_ctx = interactive_workflows_context.request_context.lifespan_context

        failing_child = WorkflowSchema(
            name="failing-child",
            description="Child that completes after prompt",
            blocks=[
                {
                    "id": "prompt",
                    "type": "Prompt",
                    "inputs": {"prompt": "Enter value:"},
                },
                {
                    "id": "process",
                    "type": "Shell",
                    "inputs": {"command": "exit 1"},  # Command that fails
                    "depends_on": ["prompt"],
                },
            ],
            # Report the failure status as an output (workflow succeeds, reports failure)
            outputs={"task_success": "${blocks.process.outputs.success}"},
        )

        parent_with_child = WorkflowSchema(
            name="parent-with-child-task",
            description="Parent calling child",
            blocks=[
                {
                    "id": "run_child",
                    "type": "ExecuteWorkflow",
                    "inputs": {"workflow": "failing-child", "inputs": {}},
                }
            ],
            # Parent outputs include child's success status
            outputs={"child_task_success": "${blocks.run_child.outputs.task_success}"},
        )

        app_ctx.registry.register(failing_child)
        app_ctx.registry.register(parent_with_child)
        app_ctx.executor.load_workflow(failing_child)
        app_ctx.executor.load_workflow(parent_with_child)

        # Execute to pause
        execute_params = ExecuteWorkflowInput(workflow="parent-with-child-task", inputs={})
        execute_result = await execute_workflow(
            params=execute_params, ctx=interactive_workflows_context
        )
        parent_checkpoint_id = execute_result.model_dump()["checkpoint_id"]

        # Resume - child completes with failed task status
        resume_params = ResumeWorkflowInput(
            checkpoint_id=parent_checkpoint_id, llm_response="any"
        )
        resume_result = await resume_workflow(
            params=resume_params, ctx=interactive_workflows_context
        )
        resume_dict = resume_result.model_dump()

        # Verify parent workflow succeeded but reports child task failure
        assert resume_dict["status"] == "success"
        # Output should show the task failed
        assert resume_dict["outputs"]["child_task_success"] == "False"
