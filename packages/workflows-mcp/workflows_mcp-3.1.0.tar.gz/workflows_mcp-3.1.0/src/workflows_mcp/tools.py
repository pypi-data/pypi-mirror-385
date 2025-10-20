"""MCP tool implementations for workflow execution.

This module contains all MCP tool function implementations that expose
workflow execution functionality to Claude Code via the MCP protocol.

Following official Anthropic MCP Python SDK patterns:
- Tool functions decorated with @mcp.tool()
- Pydantic models for input validation
- Type hints for automatic schema generation
- Async functions for all tools
- Clear docstrings (become tool descriptions)
"""

from datetime import datetime
from typing import Any

from mcp.types import ToolAnnotations

from .context import AppContextType
from .engine import WorkflowResponse, load_workflow_from_yaml
from .formatting import (
    format_checkpoint_info_markdown,
    format_checkpoint_list_markdown,
    format_checkpoint_not_found_error,
    format_workflow_info_markdown,
    format_workflow_list_markdown,
    format_workflow_not_found_error,
)
from .models import (
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
from .server import mcp

# =============================================================================
# MCP Tools (following official SDK decorator pattern)
# =============================================================================


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,  # Execution creates side effects
        openWorldHint=True,  # Interacts with external systems via Shell blocks
    )
)
async def execute_workflow(
    params: ExecuteWorkflowInput,
    *,
    ctx: AppContextType,
) -> WorkflowResponse:
    """Execute a DAG-based workflow with inputs.

    Supports git operations, bash commands, templates, and workflow composition.

    Args:
        params (ExecuteWorkflowInput): Validated input parameters containing:
            - workflow (str): Workflow name (e.g., 'python-ci-pipeline', 'sequential-echo')
            - inputs (dict[str, Any] | None): Runtime inputs for variable substitution
            - response_format (Literal["minimal", "detailed"]): Output verbosity control
        ctx: Server context for accessing shared resources

    Returns:
        WorkflowResponse: Workflow execution result with structure:
        {
            "status": "success" | "failure" | "paused",
            "outputs": {...},  # Workflow outputs
            "blocks": {...},   # Block execution details (detailed mode only)
            "metadata": {...}, # Execution metadata (detailed mode only)
            "error": "...",    # Error message (if status is "failure")
        }

    Examples:
        - Use when: "Execute the python-ci-pipeline workflow for my project"
          -> params with workflow="python-ci-pipeline", inputs={"project_path": "./"}
        - Use when: "Run sequential-echo with custom message"
          -> params with workflow="sequential-echo", inputs={"message": "Hello"}
        - Don't use when: You need to see available workflows first
          (use list_workflows instead)
        - Don't use when: You need workflow details before execution
          (use get_workflow_info instead)

    Error Handling:
        - Returns WorkflowResponse with status="failure" if workflow not found
        - Includes available_workflows in outputs for guidance
        - Returns error details from block execution failures
        - Pydantic validation errors are handled automatically
    """
    # Validate context availability
    if ctx is None:
        return WorkflowResponse(
            status="failure",
            error="Server context not available. Tool requires server context to access resources.",
            response_format=params.response_format,
        )

    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor
    registry = app_ctx.registry

    # Validate workflow exists
    if params.workflow not in registry:
        available = registry.list_names()
        return WorkflowResponse(
            status="failure",
            error=(
                f"Workflow '{params.workflow}' not found. "
                f"Available workflows: {', '.join(available[:5])}"
                f"{' (and more)' if len(available) > 5 else ''}. "
                "Use list_workflows() to see all workflows or filter by tags."
            ),
            outputs={"available_workflows": available},
            response_format=params.response_format,
        )

    # Execute workflow - pass response_format to executor
    response = await executor.execute_workflow(
        params.workflow, params.inputs, response_format=params.response_format
    )
    return response


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,  # Execution creates side effects
        openWorldHint=True,  # Interacts with external systems via Shell blocks
    )
)
async def execute_inline_workflow(
    params: ExecuteInlineWorkflowInput,
    *,
    ctx: AppContextType,
) -> WorkflowResponse:
    """Execute a workflow provided as YAML string without registering it.

    Enables dynamic workflow execution without file system modifications.
    Useful for ad-hoc workflows, one-off tasks, or testing workflow definitions.

    Args:
        params (ExecuteInlineWorkflowInput): Validated input parameters containing:
            - workflow_yaml (str): Complete workflow YAML definition (10-100,000 chars)
            - inputs (dict[str, Any] | None): Runtime inputs for variable substitution
            - response_format (Literal["minimal", "detailed"]): Output verbosity control
        ctx: Server context for accessing shared resources

    Returns:
        WorkflowResponse: Workflow execution result with structure:
        {
            "status": "success" | "failure" | "paused",
            "outputs": {...},       # Workflow outputs
            "blocks": {...},        # Block execution details (detailed mode only)
            "metadata": {...},      # Execution metadata (detailed mode only)
            "error": "...",         # Error message (if status is "failure")
            "checkpoint_id": "...", # Checkpoint ID (if status is "paused")
            "prompt": "...",        # Pause prompt (if status is "paused")
        }

    Examples:
        - Use when: "Run this custom workflow for quality checks"
          -> params with workflow_yaml containing complete workflow definition
        - Use when: "Execute this one-time data processing workflow"
          -> params with workflow_yaml for data transformation task
        - Don't use when: You have a registered workflow name
          (use execute_workflow instead)
        - Don't use when: You need to validate YAML before execution
          (use validate_workflow_yaml first)

    YAML Example:
        workflow_yaml='''
        name: rust-quality-check
        description: Quality checks for Rust projects
        tags: [rust, quality, linting]

        inputs:
          source_path:
            type: string
            default: "src/"

        blocks:
          - id: lint
            type: Shell
            inputs:
              command: cargo clippy -- -D warnings
              working_dir: "${inputs.source_path}"

          - id: format_check
            type: Shell
            inputs:
              command: cargo fmt -- --check
            depends_on: [lint]

        outputs:
          linting_passed: "${blocks.lint.success}"
          formatting_passed: "${blocks.format_check.success}"
        '''

    Error Handling:
        - Returns WorkflowResponse with status="failure" if YAML parsing fails
        - Includes detailed parsing error message for troubleshooting
        - Validates workflow structure before execution
        - Pydantic enforces YAML content min/max length (10-100,000 chars)
    """
    # Validate context availability
    if ctx is None:
        return WorkflowResponse(
            status="failure",
            error="Server context not available. Tool requires server context to access resources.",
            response_format=params.response_format,
        )

    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor

    # Parse YAML string to WorkflowSchema
    load_result = load_workflow_from_yaml(params.workflow_yaml, source="<inline-workflow>")

    if not load_result.is_success:
        return WorkflowResponse(
            status="failure",
            error=(
                f"Failed to parse workflow YAML: {load_result.error}. "
                "Ensure your YAML is valid and includes required fields: "
                "'name', 'description', and 'blocks'. "
                "Use validate_workflow_yaml() to check YAML syntax before execution."
            ),
            response_format=params.response_format,
        )

    workflow_def = load_result.value
    if workflow_def is None:
        return WorkflowResponse(
            status="failure",
            error=(
                "Workflow definition parsing returned None. "
                "The YAML structure may be invalid. "
                "Required fields: 'name' (string), 'description' (string), "
                "'blocks' (list of block definitions). "
                "Use validate_workflow_yaml() to validate your workflow YAML."
            ),
            response_format=params.response_format,
        )

    # Temporarily load workflow into executor
    executor.load_workflow(workflow_def)

    # Execute workflow - pass params.response_format to executor
    response = await executor.execute_workflow(
        workflow_def.name, params.inputs, response_format=params.response_format
    )
    return response


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def list_workflows(
    params: ListWorkflowsInput,
    *,
    ctx: AppContextType,
) -> list[str] | str:
    """List all available workflows, optionally filtered by tags.

    Discover workflows by name or filter by tags to find workflows for specific tasks.
    Returns workflow names only - use get_workflow_info() for detailed information.

    Args:
        params (ListWorkflowsInput): Validated input parameters containing:
            - tags (list[str]): Filter by tags (AND logic) - max 20 tags
            - format (Literal["json", "markdown"]): Response format preference
        ctx: Server context for accessing shared resources

    Returns:
        JSON format (list[str]): List of workflow names for programmatic access
            Example: ["python-ci-pipeline", "git-create-feature-branch", "sequential-echo"]

        Markdown format (str): Human-readable formatted list with headers
            Example:
            ## Available Workflows (3)
            **Filtered by tags**: python, ci

            - python-ci-pipeline
            - python-test-runner
            - python-lint

    Examples:
        - Use when: "Show me all available workflows"
          -> params with tags=[], format="json"
        - Use when: "List Python CI workflows"
          -> params with tags=["python", "ci"], format="markdown"
        - Use when: "What git workflows are available?"
          -> params with tags=["git"], format="json"
        - Don't use when: You need detailed workflow information
          (use get_workflow_info instead)
        - Don't use when: You want to execute a workflow
          (use execute_workflow instead)

    Error Handling:
        - Returns empty list (JSON) or "No workflows found" message (Markdown)
        - Tag filtering uses AND logic - all tags must match
        - Invalid tags return empty results (no error thrown)
        - Pydantic validates tags list (max 20 items)
    """
    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    registry = app_ctx.registry

    workflows = registry.list_names(tags=params.tags)

    if params.format == "markdown":
        return format_workflow_list_markdown(workflows, params.tags or None)
    else:
        return workflows


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def get_workflow_info(
    params: GetWorkflowInfoInput,
    *,
    ctx: AppContextType,
) -> dict[str, Any] | str:
    """Get detailed information about a specific workflow.

    Retrieve comprehensive metadata including description, blocks, inputs, outputs,
    and dependencies. Use before executing a workflow to understand its requirements.

    Args:
        params (GetWorkflowInfoInput): Validated input parameters containing:
            - workflow (str): Workflow name to retrieve information about
            - format (Literal["json", "markdown"]): Response format preference
        ctx: Server context for accessing shared resources

    Returns:
        JSON format (dict[str, Any]): Structured workflow metadata
            {
                "name": "python-ci-pipeline",
                "description": "CI pipeline for Python projects",
                "version": "1.0",
                "total_blocks": 3,
                "blocks": [
                    {"id": "lint", "type": "Shell", "depends_on": []},
                    {"id": "test", "type": "Shell", "depends_on": ["lint"]},
                    {"id": "build", "type": "Shell", "depends_on": ["test"]}
                ],
                "inputs": {
                    "project_path": {"type": "string", "description": "Path to project"}
                },
                "outputs": {
                    "success": "${blocks.build.success}"
                },
                "tags": ["python", "ci"],
                "author": "..."
            }

        Markdown format (str): Human-readable formatted description with sections

        Error response:
            JSON: {"error": "Workflow not found: ...", "available_workflows": [...]}
            Markdown: "**Error**: Workflow not found: ..."

    Examples:
        - Use when: "Tell me about the python-ci-pipeline workflow"
          -> params with workflow="python-ci-pipeline", format="markdown"
        - Use when: "What inputs does git-create-feature-branch need?"
          -> params with workflow="git-create-feature-branch", format="json"
        - Use when: "Show me the workflow structure before executing"
          -> params with workflow="...", format="json" (check inputs/outputs)
        - Don't use when: You just need a list of workflow names
          (use list_workflows instead)
        - Don't use when: You're ready to execute the workflow
          (use execute_workflow instead)

    Error Handling:
        - Returns error dict/message if workflow not found
        - Includes list of available workflows for discovery
        - Validates workflow name via Pydantic (non-empty, max 200 chars)
        - Format validation ensures "json" or "markdown" only
    """
    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    registry = app_ctx.registry

    # Get params.workflow from registry
    if params.workflow not in registry:
        return format_workflow_not_found_error(
            params.workflow, registry.list_names(), params.format
        )

    # Get metadata from registry
    metadata = registry.get_workflow_metadata(params.workflow)

    # Get params.workflow definition for block details
    workflow_def = registry.get(params.workflow)

    # Build comprehensive info dictionary
    info: dict[str, Any] = {
        "name": metadata["name"],
        "description": metadata["description"],
        "version": metadata.get("version", "1.0"),
        "total_blocks": len(workflow_def.blocks),
        "blocks": [
            {
                "id": block.id,
                "type": block.type,
                "depends_on": [dep.block for dep in block.depends_on],
            }
            for block in workflow_def.blocks
        ],
    }

    # Add optional metadata fields
    if "author" in metadata:
        info["author"] = metadata["author"]
    if "tags" in metadata:
        info["tags"] = metadata["tags"]

    # Add input/output schema if available
    if workflow_def:
        # Convert input declarations to simple type mapping
        if workflow_def.inputs:
            info["inputs"] = {
                name: {"type": decl.type.value, "description": decl.description}
                for name, decl in workflow_def.inputs.items()
            }

        # Add output mappings if available
        if workflow_def.outputs:
            info["outputs"] = workflow_def.outputs

    # Format as markdown if requested
    if params.format == "markdown":
        return format_workflow_info_markdown(info)

    return info


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def get_workflow_schema() -> dict[str, Any]:
    """Get complete JSON Schema for workflow validation.

    Returns the auto-generated JSON Schema that describes the structure of
    workflow YAML files, including all registered block types and their inputs.

    This schema can be used for:
    - Pre-execution validation
    - Editor autocomplete (VS Code YAML extension)
    - Documentation generation
    - Client-side validation

    Returns:
        Complete JSON Schema for workflow definitions
    """
    # Schema can be generated from executor registry without context
    from .engine.executor_base import create_default_registry

    # Create registry with all built-in executors and generate schema
    registry = create_default_registry()
    schema: dict[str, Any] = registry.generate_workflow_schema()
    return schema


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def validate_workflow_yaml(
    params: ValidateWorkflowYamlInput,
) -> dict[str, Any]:
    """Validate workflow YAML against schema before execution.

    Performs comprehensive validation without executing the workflow. Use before
    execute_inline_workflow to catch errors early and get clear validation feedback.

    Args:
        params (ValidateWorkflowYamlInput): Validated input parameters containing:
            - yaml_content (str): Complete workflow YAML definition (10-100,000 chars)

    Returns:
        dict[str, Any]: Validation result with detailed feedback
        {
            "valid": bool,                    # True if all validation passes
            "errors": list[str],              # List of validation errors (empty if valid)
            "warnings": list[str],            # List of warnings (non-blocking issues)
            "block_types_used": list[str]     # List of block types found in workflow
        }

    Examples:
        - Use when: "Check if this workflow YAML is valid before executing"
          -> params with yaml_content containing workflow definition
        - Use when: "Validate workflow syntax and structure"
          -> params with yaml_content to check for YAML parsing errors
        - Use when: "Verify all block types are registered"
          -> params with yaml_content to validate block type availability
        - Don't use when: You're ready to execute the workflow
          (use execute_inline_workflow instead)
        - Don't use when: You just want to check YAML syntax
          (this does full workflow validation)

    Validation Checks:
        1. YAML syntax validation - ensures parseable YAML
        2. Schema compliance - validates workflow structure and required fields
        3. Block type validation - checks all block types are registered
        4. Input schema validation - validates block input parameters (per block type)

    Error Handling:
        - YAML parsing errors reported in "errors" list
        - Unknown block types reported with block ID for easy location
        - Schema violations include field names and expected types
        - Pydantic validates yaml_content min/max length (10-100,000 chars)
    """
    # Validation works without context

    # Parse workflow YAML
    load_result = load_workflow_from_yaml(params.yaml_content, source="<validation>")

    if not load_result.is_success:
        return {
            "valid": False,
            "errors": [
                f"YAML parsing error: {load_result.error}",
                "Common issues: Invalid YAML syntax, missing required fields "
                "('name', 'description', 'blocks'), or incorrect indentation. "
                "Check your YAML syntax with a YAML validator.",
            ],
            "warnings": [],
            "block_types_used": [],
        }

    workflow_def = load_result.value
    if workflow_def is None:
        return {
            "valid": False,
            "errors": [
                "Workflow definition parsing returned None - YAML structure is invalid.",
                "Required fields: 'name' (string), 'description' (string), "
                "'blocks' (list of block definitions with 'id', 'type', and 'inputs').",
                "Each block must have: id (unique identifier), type (executor type), "
                "and inputs (parameters for the executor).",
            ],
            "warnings": [],
            "block_types_used": [],
        }

    # Extract block types used
    block_types_used = list({block.type for block in workflow_def.blocks})

    # Validate block types against executor registry
    from .engine.executor_base import create_default_registry

    errors: list[str] = []
    warnings: list[str] = []

    registry = create_default_registry()
    registered_types = registry.list_types()

    for block in workflow_def.blocks:
        block_type = block.type
        if block_type not in registered_types:
            errors.append(
                f"Unknown block type '{block_type}' in block '{block.id}'. "
                f"Available block types: {', '.join(sorted(registered_types))}. "
                "Check for typos or use get_workflow_schema() to see all valid block types."
            )

    # If no errors, workflow is valid
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "block_types_used": block_types_used,
    }


# =============================================================================
# Checkpoint Management Tools
# =============================================================================


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    )
)
async def resume_workflow(
    params: ResumeWorkflowInput,
    *,
    ctx: AppContextType,
) -> WorkflowResponse:
    """Resume a paused or checkpointed workflow.

    Continue workflow execution from a checkpoint created during pause (interactive blocks)
    or automatic checkpointing. Provides crash recovery and interactive workflow support.

    Args:
        params (ResumeWorkflowInput): Validated input parameters containing:
            - checkpoint_id (str): Checkpoint token from pause or list_checkpoints
            - llm_response (str): Response to pause prompt (required for paused workflows)
            - response_format (Literal["minimal", "detailed"]): Output verbosity control
        ctx: Server context for accessing shared resources

    Returns:
        WorkflowResponse: Workflow execution result with structure:
        {
            "status": "success" | "failure" | "paused",
            "outputs": {...},  # Workflow outputs (when complete)
            "blocks": {...},   # Block execution details (detailed mode only)
            "metadata": {...}, # Execution metadata (detailed mode only)
            "error": "...",    # Error message (if status is "failure")
        }

    Examples:
        - Use when: "Continue the paused workflow with 'yes' response"
          -> params with checkpoint_id="pause_abc123", llm_response="yes"
        - Use when: "Resume workflow from crash checkpoint"
          -> params with checkpoint_id="auto_def456", llm_response=""
        - Use when: "Provide response to a Prompt block"
          -> params with checkpoint_id="...", llm_response="user provided value"
        - Don't use when: You need to list available checkpoints first
          (use list_checkpoints instead)
        - Don't use when: You need checkpoint details before resuming
          (use get_checkpoint_info instead)

    Interactive Block Pattern:
        - Prompt: Pauses workflow with a prompt. Respond with appropriate text based on the prompt.
          The workflow interprets your response using conditions or subsequent blocks.

    Error Handling:
        - Returns WorkflowResponse with status="failure" if checkpoint not found
        - Validates checkpoint_id via Pydantic (non-empty, max 100 chars)
        - llm_response max length is 10,000 chars
        - Checkpoint may expire after some time (implementation-dependent)
    """
    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor

    # Resume workflow - pass params.response_format to executor
    response = await executor.resume_workflow(
        params.checkpoint_id, params.llm_response, response_format=params.response_format
    )
    return response


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def list_checkpoints(
    params: ListCheckpointsInput,
    *,
    ctx: AppContextType,
) -> dict[str, Any] | str:
    """List available workflow checkpoints.

    Shows all checkpoints, including both automatic checkpoints (for crash recovery)
    and pause checkpoints (for interactive workflows).

    Args:
        workflow_name: Filter by workflow name (empty = all workflows)
        format: Response format (default: "json")
            - "json": Returns structured data for programmatic access
            - "markdown": Returns human-readable formatted list with details
        ctx: Server context for accessing shared resources

    Returns:
        JSON format: Dictionary with checkpoints list and total count
        Markdown format: Formatted string with headers and checkpoint details

    Example:
        list_checkpoints(workflow_name="python-ci-pipeline")
    """
    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor

    filter_name = params.workflow_name if params.workflow_name else None
    checkpoints = await executor.checkpoint_store.list_checkpoints(filter_name)

    checkpoint_data = [
        {
            "checkpoint_id": c.checkpoint_id,
            "workflow": c.workflow_name,
            "created_at": c.created_at,
            "created_at_iso": datetime.fromtimestamp(c.created_at).isoformat(),
            "is_paused": c.paused_block_id is not None,
            "pause_prompt": c.pause_prompt,
            "type": "pause" if c.paused_block_id is not None else "automatic",
        }
        for c in checkpoints
    ]

    if params.format == "markdown":
        return format_checkpoint_list_markdown(checkpoint_data, params.workflow_name or None)
    else:
        return {
            "checkpoints": checkpoint_data,
            "total": len(checkpoints),
        }


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def get_checkpoint_info(
    params: GetCheckpointInfoInput,
    *,
    ctx: AppContextType,
) -> dict[str, Any] | str:
    """Get detailed information about a specific checkpoint.

    Useful for inspecting checkpoint state before resuming.

    Args:
        checkpoint_id: Checkpoint token
        format: Response format (default: "json")
            - "json": Returns structured data for programmatic access
            - "markdown": Returns human-readable formatted details
        ctx: Server context for accessing shared resources

    Returns:
        JSON format: Dictionary with detailed checkpoint information
        Markdown format: Formatted string with sections and progress details
    """
    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor

    state = await executor.checkpoint_store.load_checkpoint(params.checkpoint_id)
    if state is None:
        return format_checkpoint_not_found_error(params.checkpoint_id, params.format)

    # Calculate progress percentage
    total_blocks = sum(len(wave) for wave in state.execution_waves)
    if total_blocks > 0:
        progress_percentage = len(state.completed_blocks) / total_blocks * 100
    else:
        progress_percentage = 0

    info = {
        "found": True,
        "checkpoint_id": state.checkpoint_id,
        "workflow_name": state.workflow_name,
        "created_at": state.created_at,
        "created_at_iso": datetime.fromtimestamp(state.created_at).isoformat(),
        "is_paused": state.paused_block_id is not None,
        "paused_block_id": state.paused_block_id,
        "pause_prompt": state.pause_prompt,
        "completed_blocks": state.completed_blocks,
        "current_wave": state.current_wave_index,
        "total_waves": len(state.execution_waves),
        "progress_percentage": round(progress_percentage, 1),
    }

    if params.format == "markdown":
        return format_checkpoint_info_markdown(state)

    return info


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,  # Deletes checkpoint
        idempotentHint=True,  # Same result if called multiple times
    )
)
async def delete_checkpoint(
    params: DeleteCheckpointInput,
    *,
    ctx: AppContextType,
) -> dict[str, Any]:
    """Delete a checkpoint.

    Useful for cleaning up paused workflows that are no longer needed.

    Args:
        checkpoint_id: Checkpoint token to delete
        ctx: Server context for accessing shared resources

    Returns:
        Deletion status
    """
    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor

    deleted = await executor.checkpoint_store.delete_checkpoint(params.checkpoint_id)

    return {
        "deleted": deleted,
        "params.checkpoint_id": params.checkpoint_id,
        "message": "Checkpoint deleted successfully" if deleted else "Checkpoint not found",
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Response model (for executor imports)
    "WorkflowResponse",
    # Tool functions (all MCP tools)
    "execute_workflow",
    "execute_inline_workflow",
    "list_workflows",
    "get_workflow_info",
    "get_workflow_schema",
    "validate_workflow_yaml",
    "resume_workflow",
    "list_checkpoints",
    "get_checkpoint_info",
    "delete_checkpoint",
]
