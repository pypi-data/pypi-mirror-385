"""Workflow engine core components using executor pattern.

This package contains the modern workflow execution engine based on the executor pattern.
Key components:

- Result: Type-safe Result monad for error handling
- DAGResolver: Dependency resolution via Kahn's algorithm
- Block: Universal block class that delegates to executors
- BlockExecutor: Base class for executor implementations
- BlockInput/BlockOutput: Pydantic v2 base classes for validation
- create_default_registry: Factory function to create ExecutorRegistry with built-in executors
- WorkflowExecutor: Async workflow orchestrator
- WorkflowDefinition: Workflow definition container
- WorkflowRegistry: Registry for managing workflow definitions
- WorkflowSchema: Pydantic v2 schema for YAML validation

Architecture:
- Executor Pattern: Blocks delegate to stateless executors
- Dependency Injection: ExecutorRegistry injected via constructor
- Plugin System: Executors can be discovered via entry points
- Security Model: Per-executor capabilities and security levels
- Type Safety: Pydantic models ensure correct I/O
"""

# Import executors (they auto-register in create_default_registry)
from . import (  # noqa: F401
    executors_core,  # Shell and ExecuteWorkflow executors
    executors_file,  # File operation executors
    executors_interactive,  # Interactive executors
    executors_state,  # JSON state executors
)
from .block import Block, BlockInput, BlockOutput
from .dag import DAGResolver
from .executor import WorkflowDefinition, WorkflowExecutor
from .executor_base import create_default_registry
from .executors_core import (
    ExecuteWorkflowExecutor,
    ExecuteWorkflowInput,
    ExecuteWorkflowOutput,
    ShellExecutor,
    ShellInput,
    ShellOutput,
)
from .executors_file import (
    CreateFileExecutor,
    CreateFileInput,
    CreateFileOutput,
    PopulateTemplateExecutor,
    PopulateTemplateInput,
    PopulateTemplateOutput,
    ReadFileExecutor,
    ReadFileInput,
    ReadFileOutput,
)
from .executors_interactive import (
    AskChoiceExecutor,
    AskChoiceInput,
    AskChoiceOutput,
    ConfirmOperationExecutor,
    ConfirmOperationInput,
    ConfirmOperationOutput,
    GetInputExecutor,
    GetInputInput,
    GetInputOutput,
)
from .executors_state import (
    MergeJSONStateExecutor,
    MergeJSONStateInput,
    MergeJSONStateOutput,
    ReadJSONStateExecutor,
    ReadJSONStateInput,
    ReadJSONStateOutput,
    WriteJSONStateExecutor,
    WriteJSONStateInput,
    WriteJSONStateOutput,
)
from .loader import load_workflow_from_yaml
from .registry import WorkflowRegistry
from .response import WorkflowResponse
from .result import Result
from .schema import WorkflowSchema

__all__ = [
    # Core types
    "Result",
    "DAGResolver",
    "Block",
    "BlockInput",
    "BlockOutput",
    "create_default_registry",
    "WorkflowExecutor",
    "WorkflowDefinition",
    "WorkflowRegistry",
    "WorkflowResponse",
    "WorkflowSchema",
    "load_workflow_from_yaml",
    # Core Executors
    "ShellExecutor",
    "ShellInput",
    "ShellOutput",
    "ExecuteWorkflowExecutor",
    "ExecuteWorkflowInput",
    "ExecuteWorkflowOutput",
    # File Executors
    "CreateFileExecutor",
    "CreateFileInput",
    "CreateFileOutput",
    "ReadFileExecutor",
    "ReadFileInput",
    "ReadFileOutput",
    "PopulateTemplateExecutor",
    "PopulateTemplateInput",
    "PopulateTemplateOutput",
    # Interactive Executors
    "ConfirmOperationExecutor",
    "ConfirmOperationInput",
    "ConfirmOperationOutput",
    "AskChoiceExecutor",
    "AskChoiceInput",
    "AskChoiceOutput",
    "GetInputExecutor",
    "GetInputInput",
    "GetInputOutput",
    # State Executors
    "ReadJSONStateExecutor",
    "ReadJSONStateInput",
    "ReadJSONStateOutput",
    "WriteJSONStateExecutor",
    "WriteJSONStateInput",
    "WriteJSONStateOutput",
    "MergeJSONStateExecutor",
    "MergeJSONStateInput",
    "MergeJSONStateOutput",
]
