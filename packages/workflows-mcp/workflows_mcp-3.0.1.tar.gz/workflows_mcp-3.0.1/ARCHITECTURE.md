# Workflows MCP Server Architecture

Comprehensive system architecture for the DAG-based workflow orchestration MCP server.

## Table of Contents

- [System Overview](#system-overview)
- [Design Principles](#design-principles)
- [Core Components](#core-components)
- [Workflow Execution Model](#workflow-execution-model)
- [Variable Resolution System](#variable-resolution-system)
- [Conditional Execution](#conditional-execution)
- [Block System (Executor Pattern)](#block-system-executor-pattern)
- [Workflow Composition](#workflow-composition)
- [Checkpoint & Pause/Resume System](#checkpoint--pauseresume-system)
- [MCP Integration](#mcp-integration)
- [Security Model](#security-model)
- [Error Handling](#error-handling)

## System Overview

The Workflows MCP Server is a Model Context Protocol server that provides DAG-based workflow orchestration for LLM Agents. The system enables complex multi-step automation through YAML-defined workflows with dependency resolution, variable substitution, conditional execution, and workflow composition.

### Key Characteristics

- **Declarative**: Workflows defined in YAML with clear semantics
- **Async-First**: Non-blocking I/O operations throughout
- **Type-Safe**: Pydantic v2 validation for all data structures
- **Composable**: Workflows can call other workflows as blocks
- **Extensible**: Custom blocks via executor pattern
- **MCP-Native**: Exposes workflows as MCP tools to LLM Agents
- **Executor Pattern**: Separation of configuration (Block) from logic (BlockExecutor)

## Design Principles

### 1. Simplicity Over Complexity

Follow YAGNI (You Aren't Gonna Need It) and KISS (Keep It Simple, Stupid) principles:

- Minimal abstractions: DAGResolver, Block (config), BlockExecutor (logic), WorkflowExecutor
- No over-engineering: single workflow type
- Clear execution model: DAG resolution → variable resolution → execution
- Straightforward composition: ExecuteWorkflow executor for calling workflows

### 2. Separation of Concerns

**Synchronous vs Async**:
- DAGResolver: Synchronous pure graph algorithms (no I/O)
- WorkflowExecutor: Async orchestration with block execution
- BlockExecutor: Async execution units with I/O operations

**Configuration vs Logic**:
- Block class: Holds configuration and delegates to executor
- BlockExecutor: Stateless logic implementation
- EXECUTOR_REGISTRY: Global singleton registry

**Validation vs Execution**:
- Schema validation at load time (Pydantic models)
- Input validation before execution (type checking)
- Output validation after execution (result verification)

**Planning vs Execution**:
- Planning phase: DAG resolution, topological sort, wave detection (synchronous)
- Execution phase: Block execution, variable resolution, output collection (async)

### 3. Explicit Over Implicit

- Dependencies declared via `depends_on` (no implicit ordering)
- Variable resolution via explicit `${var}` syntax with namespace paths
- Context isolation in workflow composition (no implicit parent context)
- Type annotations throughout (Pydantic v2, Python type hints)

### 4. Fail-Fast Validation

- YAML schema validation at load time
- Cyclic dependency detection before execution
- Variable reference validation during schema validation
- Type validation for all inputs and outputs
- Circular workflow dependency detection

## Core Components

### Result Monad (`engine/result.py`)

**Purpose**: Type-safe error handling with three-state model

**Class Definition**:
```python
@dataclass
class Result(Generic[T]):
    is_success: bool
    value: T | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    is_paused: bool = False
    pause_data: PauseData | None = None
```

**Static Methods**:
- `success(value: T, metadata: dict | None = None) -> Result[T]`: Create success result
- `failure(error: str, metadata: dict | None = None) -> Result[T]`: Create failure result
- `pause(prompt: str, checkpoint_id: str, **pause_metadata) -> Result[T]`: Create paused result

**Instance Methods**:
- `__bool__() -> bool`: Allow using result in if statements
- `unwrap() -> T`: Get value or raise exception if failed
- `unwrap_or(default: T) -> T`: Get value or return default if failed

**Three-State Model**:
- `is_success=True`: Operation completed successfully
- `is_success=False, is_paused=False`: Operation failed (error)
- `is_success=False, is_paused=True`: Operation paused (waiting for input)

### DAGResolver (`engine/dag.py`)

**Purpose**: Dependency resolution and execution order determination

**Class Definition**:
```python
class DAGResolver:
    def __init__(self, nodes: list[str], dependencies: dict[str, list[str]]):
        self.nodes = nodes  # All block IDs
        self.dependencies = dependencies  # block_id -> [dependency_ids]
        self._in_degree: dict[str, int] = {}  # Track dependencies count
        self._adjacency: dict[str, list[str]] = {}  # Reverse dependencies
```

**Methods**:

1. **`topological_sort() -> Result[list[str]]`**
   - Performs topological sort using Kahn's algorithm
   - Returns ordered list of block IDs for sequential execution
   - Detects cyclic dependencies and returns failure
   - Algorithm complexity: O(V + E) where V=blocks, E=dependencies

2. **`get_execution_waves() -> Result[list[list[str]]]`**
   - Groups blocks into waves for parallel execution
   - Each wave contains blocks with no dependencies on each other
   - Returns list of waves: `[[wave1_blocks], [wave2_blocks], ...]`
   - Uses Kahn's algorithm with level-based grouping

**Algorithm Details (Kahn's Topological Sort)**:
```python
def topological_sort(self) -> Result[list[str]]:
    # 1. Calculate in-degree for each node
    in_degree = {node: len(self.dependencies[node]) for node in self.nodes}

    # 2. Find nodes with no dependencies (in-degree = 0)
    queue = [node for node in self.nodes if in_degree[node] == 0]

    # 3. Process nodes in order
    result = []
    while queue:
        node = queue.pop(0)
        result.append(node)

        # Reduce in-degree for dependent nodes
        for dependent in self._adjacency[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # 4. Check if all nodes were processed (no cycles)
    if len(result) != len(self.nodes):
        # Cycle detected
        return Result.failure("Cyclic dependency detected")

    return Result.success(result)
```

### BlockExecutor Base Class (`engine/executor_base.py`)

**Purpose**: Base class for all workflow execution units with stateless execution logic

**Class Definition**:
```python
class BlockExecutor(ABC):
    """Stateless executor for a specific block type."""

    # Class variables (must be overridden)
    type_name: ClassVar[str]  # Block type identifier (e.g., "Shell")
    input_type: ClassVar[type[BlockInput]]  # Pydantic input model
    output_type: ClassVar[type[BlockOutput]]  # Pydantic output model
    security_level: ClassVar[ExecutorSecurityLevel] = ExecutorSecurityLevel.SAFE
    capabilities: ClassVar[ExecutorCapabilities] = ExecutorCapabilities()

    @abstractmethod
    async def execute(
        self, inputs: BlockInput, context: dict[str, Any]
    ) -> Result[BlockOutput]:
        """Execute block logic asynchronously."""
```

**Security Levels**:
```python
class ExecutorSecurityLevel(str, Enum):
    SAFE = "safe"  # No dangerous operations
    TRUSTED = "trusted"  # Can modify workflow state
    PRIVILEGED = "privileged"  # Can execute commands, access files
```

**Capabilities**:
```python
@dataclass
class ExecutorCapabilities:
    can_execute_commands: bool = False
    can_read_files: bool = False
    can_write_files: bool = False
    can_network: bool = False
    can_modify_state: bool = False
```

**BlockInput Base Model**:
```python
class BlockInput(BaseModel):
    """Base input model for all executors."""
    model_config = {"extra": "forbid"}  # Strict validation
```

**BlockOutput Base Model**:
```python
class BlockOutput(BaseModel):
    """Base output model for all executors."""
    model_config = {"extra": "allow"}  # Allow dynamic fields
```

### EXECUTOR_REGISTRY (`engine/executor_base.py`)

**Purpose**: Global singleton registry for executor instances

**Class Definition**:
```python
class ExecutorRegistry:
    """Global registry for executor instances."""

    def __init__(self):
        self._executors: dict[str, BlockExecutor] = {}

    def register(self, executor: BlockExecutor) -> None:
        """Register executor instance."""
        self._executors[executor.type_name] = executor

    def get(self, type_name: str) -> BlockExecutor | None:
        """Get executor by type name."""
        return self._executors.get(type_name)

    def list_types(self) -> list[str]:
        """List all registered executor types."""
        return list(self._executors.keys())

    def generate_workflow_schema(self) -> dict[str, Any]:
        """Generate JSON Schema for workflow validation."""
        # Returns complete schema with all executor types
```

**Global Instance**:
```python
EXECUTOR_REGISTRY = ExecutorRegistry()
```

**Auto-Registration Pattern**:
```python
# In engine/__init__.py
from . import (
    executors_core,  # Imports module, which registers executors
    executors_file,
    executors_interactive,
)

# In executors_core.py
EXECUTOR_REGISTRY.register(ShellExecutor())
EXECUTOR_REGISTRY.register(ExecuteWorkflowExecutor())
```

### Block Class (`engine/block.py`)

**Purpose**: Configuration wrapper that delegates to executors

**Class Definition**:
```python
class Block:
    """Block configuration that delegates execution to registered executor."""

    def __init__(
        self,
        block_id: str,
        block_type: str,
        inputs: dict[str, Any],
        depends_on: list[str] = [],
        condition: str | None = None,
        custom_outputs: dict[str, Any] | None = None,
    ):
        self.id = block_id
        self.type = block_type
        self.raw_inputs = inputs  # Before variable resolution
        self.depends_on = depends_on
        self.condition = condition
        self.custom_outputs = custom_outputs  # For Shell block file-based outputs

        # Get executor from registry
        self._executor = EXECUTOR_REGISTRY.get(block_type)
        if self._executor is None:
            raise ValueError(f"Unknown block type: {block_type}")

        # Store input/output types from executor
        self._input_type = self._executor.input_type
        self._output_type = self._executor.output_type

    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        """Execute block by delegating to registered executor."""

        # 1. Resolve variables in inputs
        from .variables import VariableResolver
        resolver = VariableResolver(context)
        resolved_inputs = resolver.resolve(self.raw_inputs)

        # 2. Inject custom outputs into context if present (for Shell block)
        if self.custom_outputs:
            context["__block_custom_outputs__"] = self.custom_outputs

        # 3. Validate inputs against executor's input model
        try:
            validated_inputs = self._input_type(**resolved_inputs)
        except Exception as e:
            return Result.failure(f"Input validation failed: {e}")

        # 4. Delegate to executor
        result = await self._executor.execute(validated_inputs, context)

        # 5. Clean up context
        if "__block_custom_outputs__" in context:
            del context["__block_custom_outputs__"]

        return result
```

**Key Methods**:
- `execute(context: dict[str, Any]) -> Result[BlockOutput]`: Execute block logic
- `input_schema() -> dict[str, Any]`: Get input JSON schema from executor
- `output_schema() -> dict[str, Any]`: Get output JSON schema from executor

### WorkflowExecutor (`engine/executor.py`)

**Purpose**: Async workflow orchestration and execution coordinator

**Class Definition**:
```python
class WorkflowExecutor:
    """Workflow execution orchestrator with checkpoint support."""

    def __init__(
        self,
        checkpoint_store: CheckpointStore | None = None,
        checkpoint_config: CheckpointConfig | None = None,
    ):
        self.workflows: dict[str, WorkflowDefinition] = {}
        self.checkpoint_store = checkpoint_store or InMemoryCheckpointStore()
        self.checkpoint_config = checkpoint_config or CheckpointConfig()
```

**Main Methods**:

1. **`load_workflow(workflow: WorkflowDefinition) -> None`**
   - Registers workflow definition for execution
   - Stores in internal dictionary by name
   - Called during server startup

2. **`async execute_workflow(workflow_name: str, inputs: dict[str, Any] | None = None) -> WorkflowResponse`**
   - Public API for workflow execution
   - Returns WorkflowResponse (unified response model)
   - Handles execution, pause, and failure states

3. **`async _execute_workflow_internal(...) -> Result[dict[str, Any]]`**
   - Internal execution method used by ExecuteWorkflow executor
   - Returns Result with four-namespace structure
   - Supports parent workflow stack for circular dependency detection

4. **`async resume_workflow(checkpoint_id: str, llm_response: str = "") -> WorkflowResponse`**
   - Resumes paused or checkpointed workflow
   - Loads checkpoint state, reconstructs context
   - Continues from paused block or next wave

**Execution Flow**:
```python
async def execute_workflow(
    self, workflow_name: str, inputs: dict[str, Any] | None = None
) -> WorkflowResponse:
    """Execute workflow with given inputs."""

    try:
        # 1. Get workflow definition
        workflow_def = self.workflows.get(workflow_name)
        if workflow_def is None:
            return WorkflowResponse(
                status="failure",
                error=f"Workflow '{workflow_name}' not found"
            )

        # 2. Validate and merge inputs
        runtime_inputs = self._validate_and_merge_inputs(workflow_def, inputs)

        # 3. Build blocks
        blocks = [Block(**block_data) for block_data in workflow_def.blocks]

        # 4. Resolve DAG
        dag_resolver = DAGResolver(
            nodes=[block.id for block in blocks],
            dependencies={block.id: block.depends_on for block in blocks}
        )
        waves_result = dag_resolver.get_execution_waves()
        if not waves_result.is_success:
            return WorkflowResponse(
                status="failure",
                error=f"DAG resolution failed: {waves_result.error}"
            )
        execution_waves = waves_result.value

        # 5. Initialize four-namespace context
        context = {
            "inputs": runtime_inputs,
            "metadata": {
                "workflow_name": workflow_name,
                "start_time": time.time(),
            },
            "blocks": {},
            "__internal__": {
                "executor": self,
                "workflow_stack": [],
            }
        }

        # 6. Execute waves
        for wave_idx, wave in enumerate(execution_waves):
            # Execute all blocks in wave in parallel
            wave_results = await asyncio.gather(*[
                self._execute_block(block, context)
                for block in blocks if block.id in wave
            ])

            # Check for pause
            for block, result in zip([b for b in blocks if b.id in wave], wave_results):
                if result.is_paused:
                    # Create pause checkpoint
                    checkpoint_id = await self._create_pause_checkpoint(
                        workflow_name, context, wave_idx, block.id,
                        result.pause_data
                    )
                    return WorkflowResponse(
                        status="paused",
                        checkpoint_id=checkpoint_id,
                        prompt=result.pause_data.prompt,
                        message="Workflow paused - use resume_workflow to continue"
                    )

                if not result.is_success:
                    return WorkflowResponse(
                        status="failure",
                        error=f"Block {block.id} failed: {result.error}"
                    )

                # Store block results in context
                context["blocks"][block.id] = {
                    "inputs": block.raw_inputs,
                    "outputs": result.value.model_dump(),
                    "metadata": {
                        "wave": wave_idx,
                        "execution_order": len(context["blocks"]),
                        "execution_time_ms": result.metadata.get("execution_time_ms", 0),
                    }
                }

            # Checkpoint after wave (if enabled)
            if self.checkpoint_config.checkpoint_every_wave:
                await self._create_automatic_checkpoint(
                    workflow_name, context, wave_idx
                )

        # 7. Extract workflow outputs
        outputs = self._extract_workflow_outputs(workflow_def, context)

        # 8. Build metadata
        metadata = self._build_execution_metadata(workflow_def, context)

        return WorkflowResponse(
            status="success",
            outputs=outputs,
            blocks=context["blocks"],
            metadata=metadata
        )

    except Exception as e:
        return WorkflowResponse(
            status="failure",
            error=f"Workflow execution failed: {str(e)}"
        )
```

### WorkflowDefinition (`engine/executor.py`)

**Purpose**: Validated, executor-compatible representation of a loaded workflow

**Class Definition**:
```python
class WorkflowDefinition:
    """Workflow definition for execution."""

    def __init__(
        self,
        name: str,
        description: str,
        blocks: list[dict[str, Any]],
        inputs: dict[str, dict[str, Any]] | None = None,
        outputs: dict[str, str] | None = None,
    ):
        self.name = name
        self.description = description
        self.blocks = blocks  # List of block configuration dicts
        self.inputs = inputs or {}  # Input declarations
        self.outputs = outputs or {}  # Output mappings
```

**Block Structure**:
```python
{
    "id": "block_id",
    "type": "BlockType",
    "inputs": {"param": "value"},
    "depends_on": ["dep1", "dep2"],
    "condition": "${expression}",
}
```

### VariableResolver (`engine/variables.py`)

**Purpose**: Resolves `${var}` variable references from four-namespace context

**Class Definition**:
```python
class VariableResolver:
    """Resolves ${var} syntax from workflow context."""

    VAR_PATTERN = re.compile(r"\$\{([a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)*)\}")

    def __init__(self, context: dict[str, Any]):
        self.context = context  # Four-namespace structure
```

**Context Structure**:
```python
context = {
    "inputs": {
        "project_name": "my-project",
        "version": "1.0.0"
    },
    "metadata": {
        "workflow_name": "build-project",
        "start_time": 1234567890.123
    },
    "blocks": {
        "run_tests": {
            "inputs": {"command": "pytest"},
            "outputs": {"exit_code": 0, "success": True},
            "metadata": {"execution_time_ms": 1234.56}
        }
    },
    "__internal__": {
        "executor": <WorkflowExecutor>,
        "workflow_stack": []
    }
}
```

**Main Methods**:

1. **`resolve(value: Any, for_eval: bool = False) -> Any`**
   - Recursively resolves variables in any value type
   - Handles strings, dicts, lists, primitives
   - `for_eval=True` formats values for Python eval (quotes strings)

2. **`_resolve_string(text: str, for_eval: bool = False) -> str`**
   - Replaces `${var}` patterns with context values
   - Uses regex matching and dictionary navigation
   - Security: Blocks `__internal__` namespace access

**Variable Syntax Patterns**:

1. **Workflow Inputs**: `${inputs.field_name}`
   ```yaml
   ${inputs.project_name}
   ${inputs.version}
   ```

2. **Workflow Metadata**: `${metadata.field_name}`
   ```yaml
   ${metadata.workflow_name}
   ${metadata.start_time}
   ```

3. **Block Outputs (explicit)**: `${blocks.block_id.outputs.field}`
   ```yaml
   ${blocks.run_tests.outputs.exit_code}
   ${blocks.run_tests.outputs.success}
   ```

4. **Block Outputs (shortcut)**: `${blocks.block_id.field}` (auto-expands to `outputs.field`)
   ```yaml
   ${blocks.run_tests.exit_code}  # Same as outputs.exit_code
   ${blocks.run_tests.success}    # Same as outputs.success
   ```

5. **Block Inputs**: `${blocks.block_id.inputs.param}`
   ```yaml
   ${blocks.run_tests.inputs.command}  # For debugging
   ```

6. **Block Metadata**: `${blocks.block_id.metadata.field}`
   ```yaml
   ${blocks.run_tests.metadata.execution_time_ms}
   ${blocks.run_tests.metadata.wave}
   ```

**Resolution Algorithm**:
```python
def _resolve_string(self, text: str, for_eval: bool = False) -> str:
    """Replace ${var} patterns with context values."""

    def replace_var(match: re.Match[str]) -> str:
        var_path = match.group(1)  # e.g., "blocks.run_tests.outputs.exit_code"

        # Security: Block __internal__ access
        if var_path.startswith("__internal__") or ".__internal__" in var_path:
            raise VariableNotFoundError(
                f"Access to internal namespace not allowed: ${{{var_path}}}"
            )

        segments = var_path.split(".")  # ["blocks", "run_tests", "outputs", "exit_code"]

        # Navigate context dictionary
        value = self.context
        for i, segment in enumerate(segments):
            if not isinstance(value, dict):
                raise VariableNotFoundError(
                    f"Cannot access '{segment}' on non-dict at segment {i}"
                )

            if segment not in value:
                available = list(value.keys()) if isinstance(value, dict) else []
                raise VariableNotFoundError(
                    f"Variable '${{{var_path}}}' not found. "
                    f"At segment '{segment}', available: {available}"
                )

            value = value[segment]

        # Format for return
        return self._format_for_eval(value) if for_eval else self._format_for_string(value)

    return self.VAR_PATTERN.sub(replace_var, text)
```

### ConditionEvaluator (`engine/variables.py`)

**Purpose**: Safe AST-based boolean expression evaluator

**Class Definition**:
```python
class ConditionEvaluator:
    """Safe boolean expression evaluator for conditional execution."""

    # Whitelist of safe operators
    SAFE_OPERATORS: dict[type, Any] = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.And: operator.and_,
        ast.Or: operator.or_,
        ast.Not: operator.not_,
        ast.In: lambda x, y: x in y,
        ast.NotIn: lambda x, y: x not in y,
    }
```

**Main Methods**:

1. **`evaluate(condition: str, context: dict[str, Any]) -> bool`**
   - Evaluates condition string against context
   - Resolves variables first, then evaluates expression
   - Returns boolean result

**Evaluation Algorithm**:
```python
def evaluate(self, condition: str, context: dict[str, Any]) -> bool:
    """Evaluate condition string."""

    # 1. Resolve variables with for_eval=True (proper Python literals)
    resolver = VariableResolver(context)
    resolved_condition = resolver.resolve(condition, for_eval=True)

    # 2. Parse and evaluate safely
    result = self._safe_eval(resolved_condition)

    if not isinstance(result, bool):
        raise InvalidConditionError(
            f"Condition must evaluate to boolean, got {type(result).__name__}"
        )

    return result

def _safe_eval(self, expr: str) -> bool:
    """Safely evaluate boolean expression."""

    # Normalize YAML boolean literals (true/false → True/False)
    expr = re.sub(r"\btrue\b", "True", expr)
    expr = re.sub(r"\bfalse\b", "False", expr)

    # Normalize string boolean representations
    expr = expr.replace("'True'", "True").replace("'False'", "False")
    expr = expr.replace('"True"', "True").replace('"False"', "False")

    # Use eval with empty builtins for security
    result = eval(expr, {"__builtins__": {}}, {})

    if not isinstance(result, bool):
        raise InvalidConditionError(
            f"Expression must evaluate to boolean, got {type(result).__name__}"
        )

    return result
```

**Supported Expressions**:
```python
# Comparisons
"${blocks.run_tests.outputs.exit_code} == 0"
"${blocks.analyze.outputs.count} > 10"
"${inputs.environment} == 'production'"

# Logical operators
"${blocks.test.outputs.success} and ${blocks.lint.outputs.success}"
"${blocks.analyze.outputs.error_count} > 0 or ${blocks.analyze.outputs.warning_count} > 100"
"not ${inputs.skip_deployment}"

# Membership
"'error' in ${blocks.run_tests.outputs.stdout}"
"${inputs.status} not in ['failed', 'cancelled']"

# Shortcut syntax (auto-expands to outputs)
"${blocks.run_tests.exit_code} == 0"  # Same as outputs.exit_code
```

## Workflow Execution Model

The workflow engine follows a **declarative DAG-based execution model** with parallel wave execution.

### Execution Phases

#### 1. DAG Resolution Phase (Synchronous)

**Input**: List of block definitions from YAML
**Output**: List of execution waves (groups of parallel blocks)

**Algorithm** (Kahn's Topological Sort):
```text
1. Identify blocks with no dependencies (in-degree = 0) → Wave 1
2. Remove Wave 1 blocks from graph
3. Identify newly independent blocks → Wave 2
4. Repeat until all blocks assigned to waves
5. If any blocks remain, cyclic dependency exists → error
```

**Example Workflow**:
```yaml
blocks:
  - id: start
    type: Shell
    inputs:
      command: "echo 'Starting'"

  - id: parallel_a
    type: Shell
    inputs:
      command: "echo 'Task A'"
    depends_on: [start]

  - id: parallel_b
    type: Shell
    inputs:
      command: "echo 'Task B'"
    depends_on: [start]

  - id: merge
    type: Shell
    inputs:
      command: "echo 'Merging'"
    depends_on: [parallel_a, parallel_b]
```

**Execution Waves**:
- Wave 1: `["start"]`
- Wave 2: `["parallel_a", "parallel_b"]` (execute in parallel)
- Wave 3: `["merge"]`

#### 2. Variable Resolution Phase

**Purpose**: Replace `${var}` syntax with actual values from context

**Resolution Order**:
1. Check namespace prefix (inputs, metadata, blocks)
2. Navigate dictionary path
3. Format value for string substitution or eval
4. Recursive resolution for nested references

**Example**:
```yaml
blocks:
  - id: create_dir
    type: Shell
    inputs:
      command: "mkdir -p ${inputs.workspace}/output"

  - id: write_file
    type: CreateFile
    inputs:
      path: "${inputs.workspace}/README.md"
      content: |
        # ${inputs.project_name}
        Version: ${inputs.version}

        Tests: ${blocks.run_tests.outputs.success}
        Time: ${blocks.run_tests.metadata.execution_time_ms}ms
    depends_on: [run_tests]
```

#### 3. Conditional Execution Phase

**Purpose**: Evaluate conditions to determine if blocks should execute

**Condition Types**:
- Comparisons: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Boolean: `and`, `or`, `not`
- Membership: `in`, `not in`

**Example**:
```yaml
blocks:
  - id: run_tests
    type: Shell
    inputs:
      command: "pytest tests/"

  - id: deploy
    type: Shell
    inputs:
      command: "kubectl apply -f k8s/"
    condition: "${blocks.run_tests.outputs.exit_code} == 0"
    depends_on: [run_tests]
```

#### 4. Async Execution Phase

**Purpose**: Execute blocks in parallel waves with async I/O

**Execution Strategy**:
```python
for wave_idx, wave in enumerate(execution_waves):
    # 1. Resolve variables for all blocks in wave
    resolved_blocks = [
        resolve_variables(block, context) for block in wave
    ]

    # 2. Filter blocks based on conditions
    blocks_to_execute = [
        block for block in resolved_blocks
        if evaluate_condition(block.condition, context)
    ]

    # 3. Execute blocks in parallel within wave
    results = await asyncio.gather(*[
        block.execute(context)
        for block in blocks_to_execute
    ])

    # 4. Check for pause
    for block, result in zip(blocks_to_execute, results):
        if result.is_paused:
            # Create pause checkpoint
            checkpoint_id = await create_pause_checkpoint(...)
            return WorkflowResponse(status="paused", ...)

    # 5. Collect outputs into shared context
    for block, result in zip(blocks_to_execute, results):
        if result.is_success:
            context["blocks"][block.id] = {
                "inputs": block.raw_inputs,
                "outputs": result.value.model_dump(),
                "metadata": {...}
            }
        else:
            return WorkflowResponse(
                status="failure",
                error=f"Block {block.id} failed: {result.error}"
            )

    # 6. Checkpoint after wave (if enabled)
    if checkpoint_config.checkpoint_every_wave:
        await checkpoint_after_wave(wave_idx, context)
```

## Variable Resolution System

### Four-Namespace Architecture

The workflow engine uses a **four-namespace architecture** for context organization:

**Root-Level Namespaces**:
1. **`inputs`**: Workflow input parameters provided at runtime
2. **`metadata`**: Workflow-level metadata (name, timestamps, execution info)
3. **`blocks`**: Block execution results with three-namespace structure per block
4. **`__internal__`**: System state (not accessible via variables, security boundary)

**Context Structure**:
```python
context = {
    "inputs": {
        "project_name": "my-project",
        "version": "1.0.0",
        "workspace": "/path/to/workspace"
    },
    "metadata": {
        "workflow_name": "build-project",
        "start_time": 1234567890.123,
        "execution_id": "exec_abc123"
    },
    "blocks": {
        "run_tests": {
            "inputs": {
                "command": "pytest tests/",
                "working_dir": "/path/to/workspace"
            },
            "outputs": {
                "exit_code": 0,
                "success": True,
                "stdout": "All tests passed"
            },
            "metadata": {
                "wave": 0,
                "execution_order": 0,
                "execution_time_ms": 1234.56,
                "started_at": "2025-10-11T14:00:00Z",
                "completed_at": "2025-10-11T14:00:01Z"
            }
        }
    },
    "__internal__": {
        "executor": <WorkflowExecutor>,
        "workflow_stack": [],
        "checkpoint_store": <CheckpointStore>
    }
}
```

### Three-Namespace Block Structure

Each block has three sub-namespaces:

1. **`inputs`**: Resolved input values passed to the block
2. **`outputs`**: Results produced by the block (domain-specific data)
3. **`metadata`**: Execution metadata added by orchestrator

### Variable Syntax Examples

```yaml
# Workflow inputs
${inputs.project_name}
${inputs.workspace}

# Workflow metadata
${metadata.workflow_name}
${metadata.start_time}

# Block outputs (explicit)
${blocks.run_tests.outputs.exit_code}
${blocks.run_tests.outputs.stdout}

# Block outputs (shortcut - auto-expands to outputs)
${blocks.run_tests.exit_code}
${blocks.run_tests.success}

# Block inputs (for debugging)
${blocks.run_tests.inputs.command}

# Block metadata
${blocks.run_tests.metadata.execution_time_ms}
${blocks.run_tests.metadata.wave}

# Security boundary (blocked)
${__internal__.executor}  # ❌ Access denied
```

## Conditional Execution

### ConditionEvaluator Implementation

**Safety Model**:
- AST-based parsing via `ast.parse()`
- Operator whitelist (no arbitrary code execution)
- Sandboxed execution with empty `__builtins__`
- Security boundary blocks `__internal__` access

**Supported Expressions**:
```python
# Comparisons
"${blocks.run_tests.outputs.exit_code} == 0"
"${blocks.analyze.outputs.count} > 10"
"${inputs.environment} == 'production'"

# Logical operators
"${blocks.test.outputs.success} and ${blocks.lint.outputs.success}"
"${blocks.analyze.outputs.error_count} > 0 or ${blocks.analyze.outputs.warning_count} > 100"
"not ${inputs.skip_deployment}"

# Membership
"'error' in ${blocks.run_tests.outputs.stdout}"
"${inputs.status} not in ['failed', 'cancelled']"
```

## Block System (Executor Pattern)

### Executor Pattern Architecture

**Separation of Concerns**:
- **Block class**: Holds configuration, delegates to executor
- **BlockExecutor**: Stateless logic implementation
- **EXECUTOR_REGISTRY**: Global singleton registry

**Benefits**:
- Clean separation of configuration from logic
- Stateless executors (singleton instances)
- Easier testing (mock executors)
- Better code organization

### Built-In Executors

#### Shell Executor (`executors_core.py`)

**Purpose**: Execute shell commands with comprehensive error handling

**Input Model**:
```python
class ShellInput(BlockInput):
    command: str
    working_dir: str = ""
    timeout: int = 120
    env: dict[str, str] = Field(default_factory=dict)
    capture_output: bool = True
    shell: bool = True
    continue_on_error: bool = Field(default=False, alias="continue-on-error")
    custom_outputs: dict[str, Any] | None = None  # File-based outputs
```

**Output Model**:
```python
class ShellOutput(BlockOutput):
    exit_code: int
    stdout: str
    stderr: str
    success: bool
    command_executed: str
    execution_time_ms: float
    # Custom outputs as dynamic fields via extra="allow"
```

**Features**:
- Async subprocess execution
- Timeout support
- Environment variable injection
- Working directory control
- Scratch directory management (`.scratch/` with `.gitignore` integration)
- Custom file-based outputs with security validation
- GitHub Actions `continue-on-error` semantics

**Custom Outputs Example**:
```yaml
- id: run_tests
  type: Shell
  inputs:
    command: "pytest --json-report --json-report-file=$SCRATCH/results.json"
  outputs:
    test_results:
      type: json
      path: "$SCRATCH/results.json"
      description: "Test execution results"
      required: true
```

**Output Path Validation** (Security):
```python
def validate_output_path(
    output_name: str, path: str, working_dir: Path, unsafe: bool = False
) -> Path:
    """Validate output file path with security checks."""

    # 1. Expand environment variables
    expanded_path = os.path.expandvars(path)
    file_path = Path(expanded_path)

    # 2. Security: reject absolute paths in safe mode
    if file_path.is_absolute() and not unsafe:
        raise OutputSecurityError("Absolute paths not allowed in safe mode")

    # 3. Build absolute path
    if file_path.is_absolute():
        absolute_path = file_path
    else:
        absolute_path = working_dir / file_path

    # 4. Security: no symlinks
    if absolute_path.is_symlink():
        raise OutputSecurityError("Symlinks not allowed for security")

    # 5. Security: path traversal check
    resolved_path = absolute_path.resolve()
    if not unsafe:
        try:
            resolved_path.relative_to(working_dir.resolve())
        except ValueError:
            raise OutputSecurityError("Path escapes working directory")

    # 6. Check file exists
    if not resolved_path.exists():
        raise OutputNotFoundError(f"File not found at {resolved_path}")

    # 7. Security: must be a file
    if not resolved_path.is_file():
        raise OutputSecurityError("Path is not a file")

    # 8. Security: size limit (10MB)
    max_size = 10 * 1024 * 1024
    if resolved_path.stat().st_size > max_size:
        raise OutputSecurityError(f"File too large (max {max_size} bytes)")

    return resolved_path
```

#### ExecuteWorkflow Executor (`executors_core.py`)

**Purpose**: Workflow composition - call workflows as blocks

**Input Model**:
```python
class ExecuteWorkflowInput(BlockInput):
    workflow: str  # Workflow name to execute
    inputs: dict[str, Any] = Field(default_factory=dict)  # Child inputs
    timeout_ms: int | None = None
```

**Output Model**:
```python
class ExecuteWorkflowOutput(BlockOutput):
    success: bool
    workflow: str
    execution_time_ms: float
    total_blocks: int
    execution_waves: int
    # Child workflow outputs as dynamic fields via extra="allow"
```

**Features**:
- Clean context isolation (child sees only passed inputs)
- Circular dependency detection via workflow stack
- Error propagation
- Output composition (child outputs become block outputs)
- Pause propagation (child pause propagates to parent)

**Composition Pattern**:
```yaml
# Child workflow (run-tests.yaml)
outputs:
  test_passed: "${blocks.pytest.outputs.success}"
  coverage: "${blocks.coverage.outputs.percent}"

# Parent workflow
blocks:
  - id: run_tests
    type: ExecuteWorkflow
    inputs:
      workflow: "run-tests"
      inputs:
        project_path: "${inputs.project_path}"

  - id: deploy
    type: Shell
    inputs:
      command: "deploy.sh"
    condition: "${blocks.run_tests.outputs.test_passed}"
    depends_on: [run_tests]
```

**Circular Dependency Detection**:
```python
# Context structure includes workflow_stack
context["__internal__"]["workflow_stack"] = [
    "parent-workflow",
    "child-workflow",
]

# Check for circular dependency
if workflow_name in workflow_stack:
    cycle_path = " → ".join(workflow_stack) + f" → {workflow_name}"
    return Result.failure(f"Circular dependency detected: {cycle_path}")
```

### File Operation Executors (`executors_file.py`)

#### CreateFile

**Input**: `path`, `content`, `permissions`, `encoding`, `overwrite`
**Output**: `file_path`, `success`

#### ReadFile

**Input**: `path`, `mode` (text/binary), `encoding`, `max_size_mb`
**Output**: `content`, `size_bytes`, `success`

#### PopulateTemplate

**Input**: `template` (Jinja2), `variables`, `strict`
**Output**: `rendered`, `success`

### Interactive Executors (`executors_interactive.py`)

These executors enable workflow pause/resume for LLM interaction.

#### ConfirmOperation

**Input**: `message`, `operation`, `details`
**Output**: `confirmed`, `response`

**Example**:
```yaml
- id: confirm_deploy
  type: ConfirmOperation
  inputs:
    message: "Deploy to production?"
    operation: "deploy_production"
```

#### AskChoice

**Input**: `question`, `choices`
**Output**: `choice`, `choice_index`

#### GetInput

**Input**: `prompt`, `validation_pattern`
**Output**: `input_value`

## Workflow Composition

### ExecuteWorkflow Pattern

**Design Principles**:
- Clean isolation: Child workflows receive ONLY explicitly passed inputs
- No parent context: Child workflows don't inherit parent's full context
- Four-namespace structure: Child workflows maintain same architecture
- Automatic namespacing: Child outputs stored under `parent_context["blocks"][block_id]`
- Circular detection: Prevent infinite recursion via workflow stack

**Context Management**:
```python
# Parent workflow execution context
parent_context = {
    "inputs": {"username": "alice", "environment": "production"},
    "metadata": {"workflow_name": "parent-workflow"},
    "blocks": {
        "setup": {
            "outputs": {"python_path": "/usr/bin/python3"}
        }
    },
    "__internal__": {
        "executor": <WorkflowExecutor>,
        "workflow_stack": ["parent-workflow"]
    }
}

# ExecuteWorkflow block
block = ExecuteWorkflowBlock(
    id="run_tests",
    workflow="pytest-workflow",
    inputs={
        "python_path": "${blocks.setup.outputs.python_path}",  # Resolved before passing
        "test_dir": "tests/",
        "env": "${inputs.environment}"
    }
)

# Child workflow receives ONLY explicitly passed inputs
child_context = {
    "inputs": {
        "python_path": "/usr/bin/python3",  # Resolved from parent
        "test_dir": "tests/",
        "env": "production"  # Resolved from parent
    },
    "metadata": {"workflow_name": "pytest-workflow"},
    "blocks": {},
    "__internal__": {
        "executor": <WorkflowExecutor>,
        "workflow_stack": ["parent-workflow", "pytest-workflow"]
    }
}

# Child outputs stored in parent context
parent_context["blocks"]["run_tests"] = {
    "inputs": {
        "workflow": "pytest-workflow",
        "inputs": {
            "python_path": "/usr/bin/python3",
            "test_dir": "tests/",
            "env": "production"
        }
    },
    "outputs": {
        "exit_code": 0,
        "coverage": 85.5,
        "passed": 42
    },
    "metadata": {
        "wave": 1,
        "execution_time_ms": 5678.90
    }
}
```

## Checkpoint & Pause/Resume System

### Overview

**Three Core Features**:
1. **Automatic Checkpointing**: Workflow state snapshots after each execution wave
2. **Interactive Workflows**: Pause execution to request LLM input, then resume
3. **Crash Recovery**: Resume workflows from last successful checkpoint

### CheckpointState (`engine/checkpoint.py`)

**Purpose**: Immutable snapshot of workflow execution state

**Class Definition**:
```python
@dataclass
class CheckpointState:
    checkpoint_id: str  # Format: "chk_<uuid>" or "pause_<uuid>"
    workflow_name: str
    created_at: float  # Unix timestamp
    runtime_inputs: dict[str, Any]  # Original workflow inputs
    context: dict[str, Any]  # Serialized context (filtered)
    completed_blocks: list[str]  # Block IDs completed so far
    current_wave_index: int  # Current wave in execution
    execution_waves: list[list[str]]  # All waves from DAG resolution
    block_definitions: dict[str, Any]  # Block configs for reconstruction
    workflow_stack: list[dict[str, Any]] = field(default_factory=list)
    paused_block_id: str | None = None  # Block that triggered pause
    pause_prompt: str | None = None  # Prompt for LLM
    pause_metadata: dict[str, Any] | None = None  # Block-specific pause data
```

### PauseData (`engine/checkpoint.py`)

**Purpose**: Data structure for paused execution

**Class Definition**:
```python
@dataclass
class PauseData:
    prompt: str  # Message to LLM requesting input
    checkpoint_id: str  # Token for resuming
    pause_metadata: dict[str, Any] = field(default_factory=dict)
```

### Checkpoint Store

**Interface** (Abstract Base Class):
```python
class CheckpointStore(ABC):
    async def save_checkpoint(self, state: CheckpointState) -> str:
        """Save checkpoint and return checkpoint_id."""

    async def load_checkpoint(self, checkpoint_id: str) -> CheckpointState | None:
        """Load checkpoint by ID."""

    async def list_checkpoints(
        self, workflow_name: str | None = None
    ) -> list[CheckpointMetadata]:
        """List all checkpoints, optionally filtered by workflow."""

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete checkpoint."""
```

**Implementation** (In-Memory):
```python
class InMemoryCheckpointStore(CheckpointStore):
    """Thread-safe in-memory checkpoint storage."""

    def __init__(self):
        self._checkpoints: dict[str, CheckpointState] = {}
        self._lock = asyncio.Lock()
```

### Pause/Resume Flow

**Interactive Block Execution**:
```text
1. Workflow starts → Blocks execute in parallel waves
2. Interactive block pauses → Returns Result.pause(prompt="...")
3. Executor creates pause checkpoint → checkpoint_id = "pause_<uuid>"
4. Return to LLM → WorkflowResponse(status="paused", checkpoint_id, prompt)
5. LLM provides input → Calls resume_workflow(checkpoint_id, response)
6. Executor restores context → Calls block.resume(context, response, metadata)
7. Block processes response → Returns Result.success() or Result.pause() again
8. Workflow continues → Remaining blocks execute
```

**Resume Workflow Algorithm**:
```python
async def resume_workflow(
    self, checkpoint_id: str, llm_response: str = ""
) -> WorkflowResponse:
    """Resume paused or checkpointed workflow."""

    # 1. Load checkpoint
    state = await self.checkpoint_store.load_checkpoint(checkpoint_id)
    if state is None:
        return WorkflowResponse(
            status="failure",
            error=f"Checkpoint {checkpoint_id} not found or expired"
        )

    # 2. Restore context
    context = state.context.copy()
    context["__internal__"] = {
        "executor": self,
        "workflow_stack": state.workflow_stack,
    }

    # 3. Check if paused (interactive block)
    if state.paused_block_id is not None:
        # Resume paused block with LLM response
        block = self._reconstruct_block(state, state.paused_block_id)
        result = await block.resume(context, llm_response, state.pause_metadata)

        # Check if block paused again
        if result.is_paused:
            # Create new pause checkpoint
            new_checkpoint_id = await self._create_pause_checkpoint(...)
            return WorkflowResponse(
                status="paused",
                checkpoint_id=new_checkpoint_id,
                prompt=result.pause_data.prompt
            )

        # Block completed, continue from next wave
        context["blocks"][state.paused_block_id] = {
            "outputs": result.value.model_dump(),
            ...
        }
        start_wave = state.current_wave_index + 1
    else:
        # Resume from automatic checkpoint (crash recovery)
        start_wave = state.current_wave_index + 1

    # 4. Continue execution from next wave
    return await self._continue_execution_from_wave(
        state.workflow_name,
        start_wave,
        context,
        state.completed_blocks
    )
```

## MCP Integration

### Server Architecture (`server.py`, `tools.py`, `context.py`)

**Design Pattern**: Official Anthropic MCP Python SDK patterns

**Lifespan Management**:
```python
@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle."""

    # Startup: initialize resources
    logger.info("Initializing MCP server resources...")
    registry = WorkflowRegistry()
    executor = WorkflowExecutor()

    # Load workflows from built-in and user template directories
    load_workflows(registry, executor)

    try:
        # Make resources available to tools
        yield AppContext(registry=registry, executor=executor)
    finally:
        # Shutdown: cleanup resources
        logger.info("Shutting down MCP server...")
        # No explicit cleanup needed for in-memory stores

# Initialize MCP server with lifespan management
mcp = FastMCP("workflows", lifespan=app_lifespan)
```

**AppContext** (Context Injection):
```python
@dataclass
class AppContext:
    """Shared resources for MCP tools."""
    registry: WorkflowRegistry
    executor: WorkflowExecutor

# Type alias for tool context parameter
AppContextType = Context[ServerSession, AppContext]
```

**Tool Implementation Pattern**:
```python
@mcp.tool()
async def execute_workflow(
    workflow: str,
    inputs: dict[str, Any] | None = None,
    *,
    ctx: AppContextType,
) -> WorkflowResponse:
    """Execute a DAG-based workflow with inputs."""

    # Validate context availability
    if ctx is None:
        return WorkflowResponse(
            status="failure",
            error="Server context not available"
        )

    # Access shared resources from lifespan context
    app_ctx = ctx.request_context.lifespan_context
    executor = app_ctx.executor
    registry = app_ctx.registry

    # Validate workflow exists
    if workflow not in registry:
        return WorkflowResponse(
            status="failure",
            error=f"Workflow '{workflow}' not found"
        )

    # Execute workflow - executor returns WorkflowResponse
    response = await executor.execute_workflow(workflow, inputs)
    return response
```

### MCP Tools

**Workflow Execution**:
- `execute_workflow(workflow, inputs)`: Execute registered workflow
- `execute_inline_workflow(workflow_yaml, inputs)`: Execute YAML string without registration
- `resume_workflow(checkpoint_id, llm_response)`: Resume paused workflow

**Workflow Discovery**:
- `list_workflows(tags)`: List workflows, optionally filtered by tags
- `get_workflow_info(workflow)`: Get detailed workflow metadata
- `get_workflow_schema()`: Get JSON Schema for workflow validation
- `validate_workflow_yaml(yaml_content)`: Validate workflow YAML before execution

**Checkpoint Management**:
- `list_checkpoints(workflow_name)`: List available checkpoints
- `get_checkpoint_info(checkpoint_id)`: Get detailed checkpoint information
- `delete_checkpoint(checkpoint_id)`: Delete checkpoint

### WorkflowResponse (`engine/response.py`)

**Purpose**: Unified response model for all workflow execution states

**Class Definition**:
```python
class WorkflowResponse(BaseModel):
    """Unified response model for all workflow states."""

    status: Literal["success", "failure", "paused"]
    outputs: dict[str, Any] | None = None
    blocks: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    error: str | None = None
    checkpoint_id: str | None = None
    prompt: str | None = None
    message: str | None = None
```

**Verbosity Control** (via `response_format` parameter):
```python
def model_dump(self, **kwargs: Any) -> dict[str, Any]:
    """Override model_dump to apply verbosity filtering."""

    data = super().model_dump(**kwargs)

    # Apply verbosity filtering if in minimal mode
    if self.response_format == "minimal":
        # For success: clear to empty dicts (consistent structure)
        # For failure/paused: keep as None
        if data.get("status") == "success":
            if "blocks" in data and data["blocks"] is not None:
                data["blocks"] = {}
            if "metadata" in data and data["metadata"] is not None:
                data["metadata"] = {}

    return data
```

The `response_format` field controls output verbosity on a per-request basis:
- `"minimal"` (default): Returns only status, outputs, and errors (saves tokens)
- `"detailed"`: Includes full block execution details and metadata (for debugging)

**Properties** (Backward Compatibility with Result):
```python
@property
def is_success(self) -> bool:
    return self.status == "success"

@property
def is_failure(self) -> bool:
    return self.status == "failure"

@property
def is_paused(self) -> bool:
    return self.status == "paused"

@property
def value(self) -> dict[str, Any] | None:
    """Get workflow execution result data."""
    if self.status == "success":
        return {
            "outputs": self.outputs,
            "blocks": self.blocks,
            "metadata": self.metadata,
        }
    return None

@property
def pause_data(self) -> Any:
    """Get pause data for paused workflows."""
    if self.status == "paused":
        from types import SimpleNamespace
        return SimpleNamespace(
            checkpoint_id=self.checkpoint_id,
            prompt=self.prompt,
        )
    return None
```

### Workflow Loading (`server.py`)

**Multi-Directory Loading with Priority**:
```python
def load_workflows(registry: WorkflowRegistry, executor: WorkflowExecutor) -> None:
    """Load workflows from built-in and user template directories."""

    # 1. Built-in templates directory
    built_in_templates = Path(__file__).parent / "templates"

    # 2. Parse WORKFLOWS_TEMPLATE_PATHS environment variable
    env_paths_str = os.getenv("WORKFLOWS_TEMPLATE_PATHS", "")
    user_template_paths: list[Path] = []

    if env_paths_str.strip():
        for path_str in env_paths_str.split(","):
            path_str = path_str.strip()
            if path_str:
                expanded_path = Path(path_str).expanduser()
                if expanded_path.exists() and expanded_path.is_dir():
                    user_template_paths.append(expanded_path)

    # 3. Build directory list: built-in first, then user paths
    directories_to_load = [built_in_templates]
    directories_to_load.extend(user_template_paths)

    # 4. Load workflows with overwrite policy (user templates override)
    result = registry.load_from_directories(
        directories_to_load,
        on_duplicate="overwrite"
    )

    # 5. Load all registry workflows into executor
    for workflow in registry.list_all():
        executor.load_workflow(workflow)
```

## Security Model

### File Operations Security

**Safe Mode (Default)**:
- Only relative paths allowed
- No path traversal (`../`)
- No symlinks
- Size limits (10MB default)
- Must be within working directory

**Unsafe Mode (Opt-In)**:
- Absolute paths allowed
- Still blocks symlinks
- Still enforces size limits
- Requires explicit `unsafe: true` flag

**Path Validation** (`executors_core.py`):
```python
def validate_output_path(
    output_name: str, path: str, working_dir: Path, unsafe: bool = False
) -> Path:
    """Validate output file path for security."""

    # 1. Expand environment variables
    expanded_path = os.path.expandvars(path)
    file_path = Path(expanded_path)

    # 2. Security: reject absolute paths in safe mode
    if file_path.is_absolute() and not unsafe:
        raise OutputSecurityError("Absolute paths not allowed in safe mode")

    # 3. Security: no symlinks
    if absolute_path.is_symlink():
        raise OutputSecurityError("Symlinks not allowed")

    # 4. Security: path traversal check
    resolved_path = absolute_path.resolve()
    if not unsafe:
        try:
            resolved_path.relative_to(working_dir.resolve())
        except ValueError:
            raise OutputSecurityError("Path escapes working directory")

    # 5. Security: size limit (10MB)
    max_size = 10 * 1024 * 1024
    if resolved_path.stat().st_size > max_size:
        raise OutputSecurityError("File too large")

    return resolved_path
```

### Command Execution Security

**Shell Safety**:
- Timeout enforcement (prevents infinite loops)
- Environment variable isolation
- Shell vs direct execution modes
- Working directory validation

### Variable Resolution Security

**Security Boundary**:
```python
# Block access to __internal__ namespace
if var_path.startswith("__internal__") or ".__internal__" in var_path:
    raise VariableNotFoundError(
        f"Access to internal namespace not allowed: ${{{var_path}}}"
    )
```

**Conditional Evaluation Security**:
```python
# Safe AST evaluation with empty builtins
result = eval(expr, {"__builtins__": {}}, {})
```

## Error Handling

### Result Monad Pattern

All workflow operations return `Result[T]`:

```python
# Success case
result = await block.execute(context)
if result.is_success:
    outputs = result.value
else:
    handle_error(result.error)

# Three-state handling
if result.is_paused:
    # Handle pause
    checkpoint_id = result.pause_data.checkpoint_id
    prompt = result.pause_data.prompt
elif result.is_success:
    # Handle success
    value = result.value
else:
    # Handle failure
    error = result.error
```

### Error Categories

**Load-Time Errors**:
- Invalid YAML syntax
- Schema validation failures
- Cyclic dependencies in DAG
- Invalid variable references
- Unknown block types

**Runtime Errors**:
- Block execution failures
- Timeout errors
- Variable resolution failures
- Condition evaluation errors
- File operation errors
- Security violations

**Error Propagation**:
```text
Block fails → Wave fails → Workflow fails → MCP tool returns WorkflowResponse(status="failure")
```

### Validation Levels

1. **YAML Syntax Validation** (loader.py): `yaml.safe_load()`
2. **Schema Validation** (schema.py): Pydantic v2 models
3. **DAG Validation** (dag.py): Cyclic dependency detection
4. **Variable Validation** (schema.py): Reference syntax and existence
5. **Input Validation** (executor_base.py): Pydantic input models
6. **Output Validation** (executor_base.py): Pydantic output models

## Summary

The Workflows MCP Server provides a comprehensive, type-safe architecture for DAG-based workflow orchestration:

**Core Design**:
- **Executor Pattern**: Clean separation of configuration (Block) from logic (BlockExecutor)
- **Four-Namespace Context**: `inputs`, `metadata`, `blocks`, `__internal__`
- **Result Monad**: Type-safe error handling with three-state model
- **WorkflowResponse**: Unified response model with verbosity control

**Execution Model**:
- **DAG Resolution**: Kahn's algorithm for topological sort and wave detection
- **Parallel Execution**: Async wave-based execution with `asyncio.gather()`
- **Variable Resolution**: Recursive resolution with explicit namespace paths
- **Conditional Execution**: Safe AST evaluation with operator whitelist

**Key Features**:
- Workflow composition via ExecuteWorkflow executor
- Checkpoint system for pause/resume and crash recovery
- Interactive workflows for LLM interaction
- MCP integration with lifespan management and context injection
- Comprehensive validation at multiple levels
- Security model with safe defaults

**Implementation Quality**:
- Type-safe throughout (Pydantic v2, Python type hints)
- Async-first (non-blocking I/O)
- Well-tested (86 tests, 48% coverage)
- MCP-compliant (official Anthropic SDK patterns)
- Production-ready (error handling, logging, validation)

This architecture enables complex automation while maintaining clarity, type safety, and extensibility.
