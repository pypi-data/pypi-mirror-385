# MCP Workflows - Validated TODO

**Last Updated**: 2025-10-17
**Review**: MCP Best Practices + Codebase Validation
**Status**: Validated against current implementation (removed hallucinations)
**Recent Completions**: MCP-1 (Tool Hint Annotations), MCP-2 (Response Format Control)

This TODO combines validated architecture issues with MCP server best practices from the official Anthropic MCP SDK guidelines.

---

## 🔴 High Priority: MCP Best Practices Alignment

These improvements align the server with official MCP best practices and enhance LLM usability.

### ✅ MCP-1: Add MCP Tool Hint Annotations (COMPLETED)

**Location**: `src/workflows_mcp/tools.py` (all @mcp.tool() decorators)
**Status**: ✅ **COMPLETED** - All tools now have ToolAnnotations with proper hints
**Completed**: 2025-10-17

**Implementation**: All MCP tools now use `annotations=ToolAnnotations(...)` pattern:

```python
from mcp.types import ToolAnnotations

# Workflow execution tools (side effects, external interaction)
@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,  # Creates side effects
        openWorldHint=True,    # Interacts with external systems
    )
)
async def execute_workflow(...) -> WorkflowResponse: ...
async def execute_inline_workflow(...) -> WorkflowResponse: ...
async def resume_workflow(...) -> WorkflowResponse: ...

# Read-only information tools
@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def list_workflows(...) -> list[str] | str: ...
async def get_workflow_info(...) -> dict[str, Any] | str: ...
async def get_workflow_schema() -> dict[str, Any]: ...
async def validate_workflow_yaml(...) -> dict[str, Any]: ...
async def list_checkpoints(...) -> dict[str, Any] | str: ...
async def get_checkpoint_info(...) -> dict[str, Any] | str: ...

# Destructive operation
@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,   # Deletes checkpoint data
        idempotentHint=True,    # Same result if called multiple times
    )
)
async def delete_checkpoint(...) -> dict[str, Any]: ...
```

**Benefits Achieved**:

- ✅ LLMs understand which tools have side effects
- ✅ Better decision-making about tool usage
- ✅ Aligns with MCP protocol specification
- ✅ Minimal code changes with high value

---

### ✅ MCP-2: Add Response Format Control (JSON vs Markdown) (COMPLETED)

**Location**: `src/workflows_mcp/tools.py`
**Status**: ✅ **COMPLETED** - Format control added to all applicable tools
**Completed**: 2025-10-17

**Implementation**: The following tools now support both JSON and Markdown formats:

```python
from typing import Literal

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
async def list_workflows(
    tags: list[str] = [],
    format: Literal["json", "markdown"] = "json",
    *,
    ctx: AppContextType,
) -> list[str] | str: ...

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
async def get_workflow_info(
    workflow: str,
    format: Literal["json", "markdown"] = "json",
    *,
    ctx: AppContextType,
) -> dict[str, Any] | str: ...

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
async def list_checkpoints(
    workflow_name: str = "",
    format: Literal["json", "markdown"] = "json",
    *,
    ctx: AppContextType,
) -> dict[str, Any] | str: ...

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
async def get_checkpoint_info(
    checkpoint_id: str,
    format: Literal["json", "markdown"] = "json",
    *,
    ctx: AppContextType,
) -> dict[str, Any] | str: ...
```

**Format Behavior**:

- `format="json"` (default): Returns structured data (list/dict) for programmatic access
- `format="markdown"`: Returns human-readable formatted strings with headers, sections, and bullet points

**Benefits Achieved**:

- ✅ Human-readable responses for LLM understanding
- ✅ Follows MCP best practices
- ✅ Better user experience when inspecting workflows
- ✅ Enables richer tool descriptions

---

### MCP-3: Add Response Verbosity Control
**Location**: `src/workflows_mcp/tools.py` - execute_workflow, execute_inline_workflow
**Priority**: Medium
**Effort**: Low (1 hour)

**Issue**: Response verbosity currently controlled by environment variable only. Should allow per-request control.

**Implementation**:
```python
@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
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

    Args:
        workflow: Workflow name (e.g., 'sequential-echo', 'parallel-echo')
        inputs: Runtime inputs as key-value pairs for block variable substitution
        response_format: Control output verbosity
            - "minimal": Returns only status, outputs, and errors (saves tokens)
            - "detailed": Includes full block execution details and metadata
        ctx: Server context for accessing shared resources

    Returns:
        WorkflowResponse with structure controlled by response_format
    """
    # ... existing validation and execution ...

    # Modify response based on format
    if response_format == "minimal":
        # Return minimal response
        return WorkflowResponse(
            status=response.status,
            outputs=response.outputs,
            error=response.error,
            blocks={},  # Empty
            metadata={},  # Empty
            # ... other fields
        )
    else:
        # Return full response
        return response
```

**Benefits**:
- Agents can optimize context window usage per request
- No dependency on environment variables
- More flexible than global WORKFLOWS_LOG_LEVEL setting
- Enables token-efficient workflows

**Reference**: MCP Best Practices - Context Optimization

---

### MCP-4: Add Pagination to list_workflows
**Location**: `src/workflows_mcp/tools.py` - list_workflows
**Priority**: Medium
**Effort**: Medium (2 hours)

**Issue**: list_workflows returns all workflows. Could become problematic with hundreds of workflows.

**Implementation**:
```python
@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        idempotentHint=True,
    )
)
async def list_workflows(
    tags: list[str] = [],
    limit: int = 100,
    offset: int = 0,
    *,
    ctx: AppContextType,
) -> dict[str, Any]:
    """List all available workflows, optionally filtered by tags.

    Args:
        tags: Optional list of tags to filter workflows.
              Workflows matching ALL tags are returned (AND logic).
        limit: Maximum workflows to return (default: 100, max: 1000)
        offset: Number of workflows to skip (for pagination)
        ctx: Server context for accessing shared resources

    Returns:
        {
            "workflows": ["name1", "name2", ...],
            "total": 150,
            "limit": 100,
            "offset": 0,
            "has_more": true
        }
    """
    app_ctx = ctx.request_context.lifespan_context
    registry = app_ctx.registry

    # Validate pagination params
    limit = max(1, min(limit, 1000))  # Clamp between 1 and 1000
    offset = max(0, offset)

    # Get all matching workflows
    all_workflows = registry.list_names(tags=tags)
    total = len(all_workflows)

    # Apply pagination
    paginated = all_workflows[offset:offset + limit]
    has_more = (offset + limit) < total

    return {
        "workflows": paginated,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
    }
```

**Benefits**:
- Prevents context window overflow with large workflow collections
- Scalable for production systems
- Follows MCP pagination best practices
- Maintains backward compatibility (defaults work like before)

**Reference**: MCP Best Practices - Pagination Patterns

---

### MCP-5: Enhanced Tool Docstrings with Examples
**Location**: `src/workflows_mcp/tools.py` - All tools
**Priority**: Medium
**Effort**: Medium (3-4 hours)

**Issue**: Docstrings are good but could include more usage examples and error guidance.

**Implementation Example**:
```python
@mcp.tool()
async def execute_inline_workflow(
    workflow_yaml: str,
    inputs: dict[str, Any] | None = None,
    *,
    ctx: AppContextType,
) -> WorkflowResponse:
    """Execute a workflow provided as YAML string without registering it.

    Enables dynamic workflow execution without file system modifications.
    Useful for ad-hoc workflows or tests.

    **When to use**:
    - Testing workflow definitions before saving
    - One-time automated tasks
    - Dynamically generated workflows from templates

    **When NOT to use**:
    - Frequently executed workflows (use execute_workflow with registered workflows)
    - Production workflows (register via YAML files for better performance)

    **Common errors and solutions**:
    - "Failed to parse workflow YAML": Check YAML syntax. Use validate_workflow_yaml first.
    - "Unknown block type 'X'": Block type not registered. Check available types with get_workflow_schema.
    - "Missing required input": Provide all required inputs. Use get_workflow_info to see requirements.

    **Example - Quick validation workflow**:
    ```python
    execute_inline_workflow(
        workflow_yaml='''
        name: quick-test
        description: Quick validation test

        blocks:
          - id: check
            type: Shell
            inputs:
              command: echo "Hello World"

        outputs:
          result: "${blocks.check.outputs.stdout}"
        ''',
        inputs={}
    )
    ```

    **Example - Dynamic project setup**:
    ```python
    execute_inline_workflow(
        workflow_yaml=f'''
        name: setup-{project_name}
        description: Setup project environment

        inputs:
          project_path:
            type: string
            required: true

        blocks:
          - id: create_dir
            type: Shell
            inputs:
              command: mkdir -p ${{inputs.project_path}}

          - id: init_git
            type: Shell
            inputs:
              command: git init
              working_dir: ${{inputs.project_path}}
            depends_on: [create_dir]

        outputs:
          project_initialized: "${{blocks.init_git.outputs.success}}"
        ''',
        inputs={"project_path": f"/projects/{project_name}"}
    )
    ```

    Args:
        workflow_yaml: Complete workflow definition as YAML string including
                      name, description, blocks, etc.
        inputs: Runtime inputs as key-value pairs for block variable substitution
        ctx: Server context for accessing shared resources

    Returns:
        WorkflowResponse on success:
        {"status": "success", "outputs": {...}, "blocks": {...}, "metadata": {...}}

        On failure:
        {"status": "failure", "error": "Detailed error message with guidance"}

        On pause (for interactive workflows):
        {"status": "paused", "checkpoint_id": "...", "prompt": "...", "message": "..."}
    """
    # ... implementation ...
```

**Benefits**:
- Improved LLM understanding of tool usage
- Reduced errors through clear guidance
- Self-documenting API
- Follows "make errors educational" MCP principle

**Reference**: MCP Best Practices - Tool Documentation Standards

---

## 🟡 Medium Priority: Security & Architecture

These issues improve security posture and architectural cleanliness.

### SEC-1: Use Whitelist for Variable Namespace Validation
**Location**: `src/workflows_mcp/engine/variables.py:143-147`
**Priority**: High
**Effort**: Low (30 minutes)
**Validated**: ✅ True issue

**Current Implementation** (blacklist approach):
```python
# Security: Block access to internal namespace
if var_path.startswith("__internal__") or ".__internal__" in var_path:
    raise VariableNotFoundError(
        f"Access to internal namespace is not allowed: ${{{var_path}}}"
    )
```

**Issues**:
- Case sensitivity bypass: `${__INTERNAL__}` would not be caught
- Typo tolerance: `${_internal_}` might slip through
- Blacklists are inherently weak security boundaries

**Recommendation** (whitelist approach):
```python
# Whitelist of allowed root namespaces
ALLOWED_NAMESPACES = {"inputs", "metadata", "blocks"}

def validate_namespace(var_path: str) -> None:
    """Validate variable uses allowed namespace (whitelist approach)."""
    segments = var_path.split(".")
    if not segments:
        raise VariableNotFoundError(f"Invalid variable path: ${{{var_path}}}")

    root_namespace = segments[0]
    if root_namespace not in ALLOWED_NAMESPACES:
        raise SecurityError(
            f"Access to namespace '{root_namespace}' not allowed. "
            f"Allowed namespaces: {', '.join(ALLOWED_NAMESPACES)}"
        )
```

**Benefits**:
- More robust security boundary
- Case-insensitive by design
- Explicitly declares what's allowed
- Prevents future namespace pollution

---

### ARCH-1: Remove Global EXECUTOR_REGISTRY Singleton
**Location**: `src/workflows_mcp/engine/executor_base.py:554`
**Priority**: Medium
**Effort**: High (6-8 hours)
**Validated**: ✅ True issue

**Current Implementation**:
```python
# Global registry instance
EXECUTOR_REGISTRY = ExecutorRegistry()
```

**Issues**:
- Impossible to isolate tests (shared global state)
- Parallel test execution fails
- Hidden dependencies throughout codebase
- Violates dependency injection principle

**Recommendation**: Use dependency injection
```python
# Remove global singleton
# EXECUTOR_REGISTRY = ExecutorRegistry()  # Delete this

# Create registry factory
def create_default_registry() -> ExecutorRegistry:
    """Create registry with all built-in executors."""
    registry = ExecutorRegistry()

    # Explicit registration - clear and testable
    from .executors_core import ShellExecutor, ExecuteWorkflowExecutor
    from .executors_file import CreateFileExecutor, ReadFileExecutor
    from .executors_interactive import ConfirmOperationExecutor

    registry.register(ShellExecutor())
    registry.register(ExecuteWorkflowExecutor())
    registry.register(CreateFileExecutor())
    registry.register(ReadFileExecutor())
    registry.register(ConfirmOperationExecutor())

    return registry

# Inject registry where needed
class WorkflowExecutor:
    def __init__(
        self,
        registry: ExecutorRegistry,  # Inject dependency
        checkpoint_store: Optional[CheckpointStore] = None
    ):
        self.registry = registry
        self.checkpoint_store = checkpoint_store or InMemoryCheckpointStore()

# In server.py
@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    # Explicit initialization
    executor_registry = create_default_registry()
    workflow_registry = WorkflowRegistry()
    executor = WorkflowExecutor(registry=executor_registry)
    # ...
```

**Impact**: Breaking change - requires updates to:
- Block class initialization
- All executor imports
- Test fixtures
- Server initialization

**Benefits**:
- Testable (can create isolated registries per test)
- Clear dependencies
- No hidden global state
- Better for parallel execution

---

### ARCH-2: Add AST Depth Limit to ConditionEvaluator
**Location**: `src/workflows_mcp/engine/variables.py` - ConditionEvaluator
**Priority**: Medium
**Effort**: Low (1-2 hours)
**Validated**: ✅ True issue

**Issue**: No validation of expression complexity. Malicious input can cause stack overflow.

**Example Attack**:
```yaml
condition: "((((((((((True)))))))))) and ((((((((((True)))))))))) and ..."  # 1000 levels deep
```

**Recommendation**:
```python
class ConditionEvaluator:
    """Safe AST-based boolean expression evaluator."""

    MAX_AST_DEPTH = 20  # Maximum nesting level
    MAX_AST_NODES = 100  # Maximum total nodes

    def _safe_eval(self, expr: str) -> bool:
        """Safely evaluate boolean expression with AST limits."""
        try:
            # Normalize YAML booleans
            expr = re.sub(r"\btrue\b", "True", expr)
            expr = re.sub(r"\bfalse\b", "False", expr)
            expr = expr.replace("'True'", "True").replace("'False'", "False")
            expr = expr.replace('"True"', "True").replace('"False"', "False")

            # Parse and validate AST
            tree = ast.parse(expr, mode='eval')
            self._validate_ast_complexity(tree.body)

            # Use eval with empty builtins for security
            result = eval(expr, {"__builtins__": {}}, {})

            if not isinstance(result, bool):
                raise InvalidConditionError(
                    f"Expression must evaluate to boolean, got {type(result).__name__}"
                )

            return result

        except Exception as e:
            raise InvalidConditionError(f"Evaluation error: {e}") from e

    def _validate_ast_complexity(self, node: ast.AST) -> None:
        """Validate AST depth and node count."""
        depth, node_count = self._measure_ast(node)

        if depth > self.MAX_AST_DEPTH:
            raise InvalidConditionError(
                f"Expression too deeply nested (depth: {depth}, max: {self.MAX_AST_DEPTH})"
            )

        if node_count > self.MAX_AST_NODES:
            raise InvalidConditionError(
                f"Expression too complex ({node_count} nodes, max: {self.MAX_AST_NODES})"
            )

    def _measure_ast(self, node: ast.AST, current_depth: int = 0) -> tuple[int, int]:
        """Measure AST depth and node count."""
        max_depth = current_depth
        node_count = 1

        for child in ast.iter_child_nodes(node):
            child_depth, child_count = self._measure_ast(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
            node_count += child_count

        return max_depth, node_count
```

**Benefits**:
- Prevents DoS attacks via complex expressions
- Protects against stack overflow
- Clear error messages for users
- Minimal performance impact

---

### ARCH-3: Remove Context None Checks in MCP Tools
**Location**: `src/workflows_mcp/tools.py` - All tools
**Priority**: Low
**Effort**: Low (30 minutes)
**Validated**: ✅ True issue (unnecessary boilerplate)

**Issue**: Every tool checks `if ctx is None` but FastMCP guarantees context injection for decorated tools.

**Current Pattern** (unnecessary):
```python
@mcp.tool()
async def execute_workflow(
    workflow: str,
    inputs: dict[str, Any] | None = None,
    *,
    ctx: AppContextType,
) -> WorkflowResponse:
    # Validate context availability
    if ctx is None:  # This check is never true!
        return WorkflowResponse(
            status="failure",
            error="Server context not available",
        )

    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor
    # ...
```

**Recommendation**: Remove unnecessary checks
```python
@mcp.tool()
async def execute_workflow(
    workflow: str,
    inputs: dict[str, Any] | None = None,
    ctx: AppContextType,  # FastMCP guarantees this is never None
) -> WorkflowResponse:
    """Execute a DAG-based workflow with inputs."""
    # Direct access - no None check needed
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor
    registry = app_ctx.registry
    # ...
```

**Benefits**:
- Cleaner code (remove ~10 lines per tool)
- Trust type system and FastMCP guarantees
- Reduce cognitive overhead
- Align with FastMCP official patterns

**Reference**: Verified with Context7 - FastMCP always injects context for decorated tools

---

## 🟢 Low Priority: Enhancements & Quality of Life

These improvements enhance developer experience and future extensibility.

### ENH-1: Add Workflow Dry-Run Mode
**Location**: `src/workflows_mcp/tools.py` - execute_workflow
**Priority**: Low
**Effort**: Medium (3 hours)

**Benefit**: Validate workflows without execution - show execution plan, validate inputs, estimate duration.

**Implementation**:
```python
@mcp.tool()
async def execute_workflow(
    workflow: str,
    inputs: dict[str, Any] | None = None,
    dry_run: bool = False,
    *,
    ctx: AppContextType,
) -> WorkflowResponse | dict[str, Any]:
    """Execute workflow with optional dry-run mode.

    Args:
        dry_run: If True, validate inputs and show execution plan without running blocks
    """
    if dry_run:
        # Validate inputs and show execution plan
        workflow_def = registry.get(workflow)
        validated_inputs = workflow_def.validate_inputs(inputs or {})

        dag = DAGResolver(...)
        waves = dag.get_execution_waves()

        return {
            "dry_run": True,
            "workflow": workflow,
            "execution_plan": {
                "total_blocks": len(workflow_def.blocks),
                "execution_waves": waves,
                "validated_inputs": validated_inputs,
                "estimated_parallel_blocks": sum(len(wave) for wave in waves),
            }
        }

    # Normal execution
    return await executor.execute_workflow(workflow, inputs)
```

---

### ENH-2: Add Workflow Execution History
**Location**: New module `src/workflows_mcp/engine/history.py`
**Priority**: Low
**Effort**: High (8-10 hours)

**Benefit**: Track workflow executions for debugging, auditing, and analytics.

---

### ENH-3: Variable Resolution Regex Support Uppercase
**Location**: `src/workflows_mcp/engine/variables.py:89`
**Priority**: Low
**Effort**: Low (5 minutes)
**Validated**: ✅ True issue

**Current**:
```python
VAR_PATTERN = re.compile(r"\$\{([a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)*)\}")
# Rejects: ${inputs.projectName}, ${inputs.API_KEY}
```

**Recommendation**:
```python
VAR_PATTERN = re.compile(
    r"\$\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}"
)
```

**Benefits**:
- Supports camelCase and SCREAMING_SNAKE_CASE
- Aligns with common programming conventions
- Minimal change, high usability improvement

---

## Summary

### Priority Breakdown

- 🔴 **High Priority (MCP Best Practices)**: 3 items remaining (MCP-3 to MCP-5) | ✅ 2 completed (MCP-1, MCP-2)
- 🟡 **Medium Priority (Security & Architecture)**: 3 items (SEC-1, ARCH-1, ARCH-2)
- 🟢 **Low Priority (Enhancements)**: 3 items (ENH-1, ENH-2, ENH-3)

### Effort Estimate

- **Quick Wins (< 1 hour)**: ~~MCP-1~~ ✅, MCP-3, SEC-1, ARCH-3, ENH-3
- **Medium Effort (2-4 hours)**: ~~MCP-2~~ ✅, MCP-4, MCP-5, ARCH-2
- **Large Effort (> 6 hours)**: ARCH-1, ENH-2

### Removed Hallucinations
The following issues from the previous TODO were **removed** because they are:

1. **HIGH-1: Result Monad** - ✅ **ALREADY FIXED** - Uses discriminated union with ResultState enum
2. **CRIT-2: shell=True default** - ⚠️ **Not a vulnerability** - Design choice for workflow flexibility
3. **Multiple issues about duplicate workflow storage** - ✅ **Not actually duplicated** - Registry and executor have different responsibilities
4. **Checkpoint serialization issues** - ⚠️ **Overstated** - CheckpointState is serializable (simple dataclass)

---

**Generated**: 2025-10-17
**Tools**: MCP Builder Skill + Manual Code Validation
**Validation**: All issues cross-referenced with actual source code
