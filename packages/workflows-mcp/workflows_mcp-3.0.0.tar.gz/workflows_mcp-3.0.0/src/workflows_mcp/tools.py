"""MCP tool implementations for workflow execution.

This module contains all MCP tool function implementations that expose
workflow execution functionality to Claude Code via the MCP protocol.

Following official Anthropic MCP Python SDK patterns:
- Tool functions decorated with @mcp.tool()
- Type hints for automatic schema generation
- Async functions for all tools
- Clear docstrings (become tool descriptions)
"""

from datetime import datetime
from typing import Any, Literal

from mcp.types import ToolAnnotations

from .context import AppContextType
from .engine import WorkflowResponse, load_workflow_from_yaml
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
    workflow: str,
    inputs: dict[str, Any] | None = None,
    response_format: Literal["minimal", "detailed"] = "minimal",
    *,
    ctx: AppContextType,
) -> WorkflowResponse:
    """Execute a DAG-based workflow with inputs.

    Supports git operations, bash commands, templates, and workflow composition.

    Args:
        workflow: Workflow name (e.g., 'sequential-echo', 'parallel-echo')
        inputs: Runtime inputs as key-value pairs for block variable substitution
        response_format: Control output verbosity
            - "minimal": Returns only status, outputs, and errors (saves tokens)
            - "detailed": Includes full block execution details and metadata
        ctx: Server context for accessing shared resources

    Returns:
        WorkflowResponse with structure controlled by response_format:
        {"status": "success", "outputs": {...}, "blocks": {...}, "metadata": {...}}
        - blocks/metadata are empty dicts when response_format="minimal"
        - blocks/metadata are fully populated when response_format="detailed"
    """
    # Validate context availability
    if ctx is None:
        return WorkflowResponse(
            status="failure",
            error="Server context not available. Tool requires server context to access resources.",
            response_format=response_format,
        )

    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor
    registry = app_ctx.registry

    # Validate workflow exists
    if workflow not in registry:
        return WorkflowResponse(
            status="failure",
            error=(
                f"Workflow '{workflow}' not found. "
                "Use list_workflows() to see all available workflows"
            ),
            outputs={"available_workflows": registry.list_names()},
            response_format=response_format,
        )

    # Execute workflow - pass response_format to executor
    response = await executor.execute_workflow(workflow, inputs, response_format=response_format)
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
    workflow_yaml: str,
    inputs: dict[str, Any] | None = None,
    response_format: Literal["minimal", "detailed"] = "minimal",
    *,
    ctx: AppContextType,
) -> WorkflowResponse:
    """Execute a workflow provided as YAML string without registering it.

    Enables dynamic workflow execution without file system modifications.
    Useful for ad-hoc workflows or tests.

    Args:
        workflow_yaml: Complete workflow definition as YAML string including
                      name, description, blocks, etc.
        inputs: Runtime inputs as key-value pairs for block variable substitution
        response_format: Control output verbosity
            - "minimal": Returns only status, outputs, and errors (saves tokens)
            - "detailed": Includes full block execution details and metadata
        ctx: Server context for accessing shared resources

    Returns:
        WorkflowResponse with structure controlled by response_format:
        {"status": "success", "outputs": {...}, "blocks": {...}, "metadata": {...}}
        - blocks/metadata are empty dicts when response_format="minimal"
        - blocks/metadata are fully populated when response_format="detailed"

        On failure: {"status": "failure", "error": "..."}
        On pause: {"status": "paused", "checkpoint_id": "...", "prompt": "...", "message": "..."}

    Example:
        execute_inline_workflow(
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
                  working_dir: "${source_path}"

              - id: format_check
                type: Shell
                inputs:
                  command: cargo fmt -- --check
                depends_on: [lint]

            outputs:
              linting_passed: "${lint.success}"
              formatting_passed: "${format_check.success}"
            ''',
            inputs={"source_path": "/path/to/rust/project"}
        )
    """
    # Validate context availability
    if ctx is None:
        return WorkflowResponse(
            status="failure",
            error="Server context not available. Tool requires server context to access resources.",
            response_format=response_format,
        )

    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor

    # Parse YAML string to WorkflowDefinition
    load_result = load_workflow_from_yaml(workflow_yaml, source="<inline-workflow>")

    if not load_result.is_success:
        return WorkflowResponse(
            status="failure",
            error=f"Failed to parse workflow YAML: {load_result.error}",
            response_format=response_format,
        )

    workflow_def = load_result.value
    if workflow_def is None:
        return WorkflowResponse(
            status="failure",
            error="Workflow definition parsing returned None",
            response_format=response_format,
        )

    # Temporarily load workflow into executor
    executor.load_workflow(workflow_def)

    # Execute workflow - pass response_format to executor
    response = await executor.execute_workflow(
        workflow_def.name, inputs, response_format=response_format
    )
    return response


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def list_workflows(
    tags: list[str] = [],
    format: Literal["json", "markdown"] = "json",
    *,
    ctx: AppContextType,
) -> list[str] | str:
    """List all available workflows, optionally filtered by tags.

    Args:
        tags: Optional list of tags to filter workflows.
              Workflows matching ALL tags are returned (AND logic).
        format: Response format (default: "json")
            - "json": Returns list of workflow names for programmatic access
            - "markdown": Returns human-readable formatted list with headers
        ctx: Server context for accessing shared resources

    Returns:
        JSON format: List of workflow names (strings)
        Markdown format: Formatted string with headers and bullet points
        Use get_workflow_info(name) to get details about a specific workflow.
    """
    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    registry = app_ctx.registry

    workflows = registry.list_names(tags=tags)

    if format == "markdown":
        if not workflows:
            return "No workflows found" + (f" with tags: {', '.join(tags)}" if tags else "")

        header = f"## Available Workflows ({len(workflows)})"
        if tags:
            header += f"\n**Filtered by tags**: {', '.join(tags)}"

        workflow_list = "\n".join(f"- {name}" for name in workflows)
        return f"{header}\n\n{workflow_list}"
    else:
        return workflows


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def get_workflow_info(
    workflow: str,
    format: Literal["json", "markdown"] = "json",
    *,
    ctx: AppContextType,
) -> dict[str, Any] | str:
    """Get detailed information about a specific workflow.

    Retrieve comprehensive metadata about a workflow including block structure and dependencies.

    Args:
        workflow: Workflow name/identifier to retrieve information about
        format: Response format (default: "json")
            - "json": Returns structured data for programmatic access
            - "markdown": Returns human-readable formatted description
        ctx: Server context for accessing shared resources

    Returns:
        JSON format: Dictionary with workflow metadata (name, description, version, tags,
                     blocks, etc.)
        Markdown format: Formatted string with headers, sections, and lists
        Returns error dict/message if workflow not found.
    """
    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    registry = app_ctx.registry

    # Get workflow from registry
    if workflow not in registry:
        if format == "markdown":
            available = registry.list_names()
            workflow_list = "\n".join(f"- {name}" for name in available)
            return (
                f"**Error**: Workflow not found: `{workflow}`\n\n"
                f"**Available workflows:**\n{workflow_list}"
            )
        else:
            return {
                "error": f"Workflow not found: {workflow}",
                "available_workflows": registry.list_names(),
            }

    # Get metadata from registry
    metadata = registry.get_workflow_metadata(workflow)

    # Get workflow definition for block details
    workflow_def = registry.get(workflow)

    # Get schema if available for input/output information
    schema = registry.get_schema(workflow)

    # Build comprehensive info dictionary
    info: dict[str, Any] = {
        "name": metadata["name"],
        "description": metadata["description"],
        "version": metadata.get("version", "1.0"),
        "total_blocks": len(workflow_def.blocks),
        "blocks": [
            {
                "id": block["id"],
                "type": block["type"],
                "depends_on": block.get("depends_on", []),
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
    if schema:
        # Convert input declarations to simple type mapping
        if schema.inputs:
            info["inputs"] = {
                name: {"type": decl.type.value, "description": decl.description}
                for name, decl in schema.inputs.items()
            }

        # Add output mappings if available
        if schema.outputs:
            info["outputs"] = schema.outputs

    # Format as markdown if requested
    if format == "markdown":
        lines = [
            f"# Workflow: {info['name']}",
            "",
            info["description"],
            "",
            "## Configuration",
            f"- **Version**: {info.get('version', '1.0')}",
            f"- **Total Blocks**: {info['total_blocks']}",
        ]

        if "tags" in info and info["tags"]:
            lines.append(f"- **Tags**: {', '.join(info['tags'])}")

        if "author" in info:
            lines.append(f"- **Author**: {info['author']}")

        lines.append("")
        lines.append("## Blocks")
        for block in info["blocks"]:
            block_line = f"- **{block['id']}** ({block['type']})"
            if block.get("depends_on"):
                block_line += f" - depends on: {', '.join(block['depends_on'])}"
            lines.append(block_line)

        if "inputs" in info and info["inputs"]:
            lines.append("")
            lines.append("## Inputs")
            for name, spec in info["inputs"].items():
                desc = spec.get("description", "No description")
                lines.append(f"- **{name}** ({spec['type']}): {desc}")

        if "outputs" in info and info["outputs"]:
            lines.append("")
            lines.append("## Outputs")
            for name, expr in info["outputs"].items():
                lines.append(f"- **{name}**: `{expr}`")

        return "\n".join(lines)

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
    # Schema can be generated from EXECUTOR_REGISTRY without context
    from .engine import EXECUTOR_REGISTRY

    # Use registry's schema generation method
    schema = EXECUTOR_REGISTRY.generate_workflow_schema()
    return schema


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def validate_workflow_yaml(
    yaml_content: str,
) -> dict[str, Any]:
    """Validate workflow YAML against schema before execution.

    Performs comprehensive validation including:
    - YAML syntax validation
    - Schema compliance (structure, required fields)
    - Block type validation (registered executors)
    - Input schema validation (per block type)

    Args:
        yaml_content: YAML workflow definition as string

    Returns:
        Validation result with errors (if any)
        {
            "valid": bool,
            "errors": list[str],
            "warnings": list[str],
            "block_types_used": list[str]
        }
    """
    # Validation works without context

    # Parse workflow YAML
    load_result = load_workflow_from_yaml(yaml_content, source="<validation>")

    if not load_result.is_success:
        return {
            "valid": False,
            "errors": [f"YAML parsing error: {load_result.error}"],
            "warnings": [],
            "block_types_used": [],
        }

    workflow_def = load_result.value
    if workflow_def is None:
        return {
            "valid": False,
            "errors": ["Workflow definition parsing returned None"],
            "warnings": [],
            "block_types_used": [],
        }

    # Extract block types used
    block_types_used = list({block["type"] for block in workflow_def.blocks})

    # Validate block types against executor registry
    from .engine import EXECUTOR_REGISTRY

    errors: list[str] = []
    warnings: list[str] = []

    registered_types = EXECUTOR_REGISTRY.list_types()

    for block in workflow_def.blocks:
        block_type = block["type"]
        if block_type not in registered_types:
            errors.append(f"Unknown block type '{block_type}' in block '{block['id']}'")

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
    checkpoint_id: str,
    llm_response: str = "",
    response_format: Literal["minimal", "detailed"] = "minimal",
    *,
    ctx: AppContextType,
) -> WorkflowResponse:
    """Resume a paused or checkpointed workflow.

    Use this to continue a workflow that was paused for interactive input,
    or to restart a workflow from a crash recovery checkpoint.

    Args:
        checkpoint_id: Checkpoint token from pause or list_checkpoints
        llm_response: Your response to the pause prompt (required for paused workflows)
        response_format: Control output verbosity
            - "minimal": Returns only status, outputs, and errors (saves tokens)
            - "detailed": Includes full block execution details and metadata
        ctx: Server context for accessing shared resources

    Returns:
        WorkflowResponse with structure controlled by response_format:
        {"status": "success", "outputs": {...}, "blocks": {...}, "metadata": {...}}
        - blocks/metadata are empty dicts when response_format="minimal"
        - blocks/metadata are fully populated when response_format="detailed"

    Example:
        # Resume paused workflow with confirmation
        resume_workflow(
            checkpoint_id="pause_abc123",
            llm_response="yes"
        )
    """
    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor

    # Resume workflow - pass response_format to executor
    response = await executor.resume_workflow(
        checkpoint_id, llm_response, response_format=response_format
    )
    return response


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def list_checkpoints(
    workflow_name: str = "",
    format: Literal["json", "markdown"] = "json",
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

    filter_name = workflow_name if workflow_name else None
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

    if format == "markdown":
        if not checkpoints:
            filter_msg = f" for workflow: {workflow_name}" if workflow_name else ""
            return f"No checkpoints found{filter_msg}"

        lines = [f"## Available Checkpoints ({len(checkpoints)})"]
        if workflow_name:
            lines.append(f"**Filtered by workflow**: {workflow_name}")
        lines.append("")

        for cp in checkpoint_data:
            checkpoint_type = str(cp["type"]).capitalize()
            # created_at is guaranteed to be float from checkpoint_data construction
            created_at_value = cp["created_at"]
            if isinstance(created_at_value, (int, float)):
                created_at_ts = float(created_at_value)
            else:
                created_at_ts = 0.0
            created_dt = datetime.fromtimestamp(created_at_ts).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"### {cp['checkpoint_id']}")
            lines.append(f"- **Workflow**: {cp['workflow']}")
            lines.append(f"- **Type**: {checkpoint_type}")
            lines.append(f"- **Created**: {created_dt}")
            if cp["is_paused"] and cp["pause_prompt"]:
                lines.append(f"- **Pause Prompt**: {cp['pause_prompt']}")
            lines.append("")

        return "\n".join(lines)
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
    checkpoint_id: str,
    format: Literal["json", "markdown"] = "json",
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

    state = await executor.checkpoint_store.load_checkpoint(checkpoint_id)
    if state is None:
        if format == "markdown":
            return f"**Error**: Checkpoint `{checkpoint_id}` not found or expired"
        else:
            return {
                "found": False,
                "error": f"Checkpoint {checkpoint_id} not found or expired",
            }

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

    if format == "markdown":
        created_dt = datetime.fromtimestamp(state.created_at).strftime("%Y-%m-%d %H:%M:%S")
        checkpoint_type = "Pause" if state.paused_block_id else "Automatic"

        lines = [
            f"# Checkpoint: {state.checkpoint_id}",
            "",
            f"**Workflow**: {state.workflow_name}",
            f"**Type**: {checkpoint_type}",
            f"**Created**: {created_dt}",
            "",
            "## Progress",
            f"- **Current Wave**: {state.current_wave_index} / {len(state.execution_waves)}",
            (
                f"- **Completed Blocks**: {len(state.completed_blocks)} / {total_blocks} "
                f"({round(progress_percentage, 1)}%)"
            ),
        ]

        if state.paused_block_id:
            lines.append("")
            lines.append("## Pause Information")
            lines.append(f"- **Paused Block ID**: {state.paused_block_id}")
            if state.pause_prompt:
                lines.append(f"- **Prompt**: {state.pause_prompt}")

        if state.completed_blocks:
            lines.append("")
            lines.append("## Completed Blocks")
            for block_id in state.completed_blocks:
                lines.append(f"- {block_id}")

        return "\n".join(lines)

    return info


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,  # Deletes checkpoint
        idempotentHint=True,  # Same result if called multiple times
    )
)
async def delete_checkpoint(
    checkpoint_id: str,
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

    deleted = await executor.checkpoint_store.delete_checkpoint(checkpoint_id)

    return {
        "deleted": deleted,
        "checkpoint_id": checkpoint_id,
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
