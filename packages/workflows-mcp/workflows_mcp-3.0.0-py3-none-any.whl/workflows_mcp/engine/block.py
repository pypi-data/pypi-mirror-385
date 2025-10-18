"""
Block system for workflow execution using the executor pattern.

This module provides the foundation for workflow blocks that delegate
execution to specialized executor implementations.

Architecture:
- Block: Configuration and coordination (lightweight wrapper)
- BlockExecutor: Logic implementation (stateless executors)
- BlockInput/BlockOutput: Pydantic models for type-safe I/O

Key Benefits:
- Separation of concerns (config vs logic)
- Reusable executors (singleton pattern)
- Type safety (Pydantic v2 validation)
- Plugin extensibility (executor discovery)
- Security model (per-executor capabilities)
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from .result import Result

if TYPE_CHECKING:
    from .executor_base import ExecutorRegistry


class BlockInput(BaseModel):
    """Base class for block input validation using Pydantic v2."""

    model_config = {"extra": "forbid"}  # Pydantic v2 config - reject unknown fields


class BlockOutput(BaseModel):
    """Base class for block output validation using Pydantic v2.

    Allows extra fields to support dynamic outputs from custom block configurations
    and child workflow outputs in ExecuteWorkflow blocks.
    """

    model_config = {"extra": "allow"}


class Block:
    """Universal block class that delegates execution to executors.

    This is the new architecture - blocks coordinate execution via executors.
    Blocks are lightweight coordination objects that:
    - Hold block-specific configuration (id, type, inputs, dependencies)
    - Delegate execution to stateless executor instances
    - Validate inputs using executor's input model
    - Return typed outputs via Result monad

    This design separates concerns:
    - Block: Configuration and coordination (this class)
    - Executor: Logic implementation (BlockExecutor subclasses)

    Example:
        # Create block using new architecture
        block = Block(
            id="shell1",
            type="Shell",
            inputs={"command": "echo hello"},
            depends_on=["setup"]
        )

        # Execute via executor
        result = await block.execute(context)
    """

    def __init__(
        self,
        id: str,
        type: str,
        inputs: dict[str, Any],
        registry: "ExecutorRegistry",
        depends_on: list[str] | None = None,
        outputs: dict[str, Any] | None = None,
    ):
        """Initialize block with executor-based architecture.

        Args:
            id: Unique block identifier
            type: Block type (executor name, e.g., "Shell", "CreateFile")
            inputs: Raw input parameters (will be validated)
            registry: ExecutorRegistry instance for looking up block executors
            depends_on: List of block IDs this block depends on
            outputs: Optional output schema (for blocks like Shell with custom outputs)

        Raises:
            ValueError: If block type not registered or input validation fails
        """
        self.id = id
        self.type = type
        self.depends_on = depends_on or []
        self._raw_inputs = inputs
        self._outputs_schema = outputs

        # Get executor for this block type
        self.executor = registry.get(type)

        # Validate inputs using executor's input model
        self._validated_inputs = self._validate_inputs()

    def _validate_inputs(self) -> BlockInput:
        """Validate inputs against executor's input model.

        Returns:
            Validated input model instance

        Raises:
            ValueError: If inputs don't match executor's schema
        """
        try:
            input_model_class = self.executor.input_type
            return input_model_class(**self._raw_inputs)
        except Exception as e:
            raise ValueError(f"Block '{self.id}' input validation failed: {e}")

    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        """Execute block by delegating to executor.

        Args:
            context: Shared workflow context (four namespaces)

        Returns:
            Result with block output or error

        Example:
            context = {
                "inputs": {"project_name": "my-app"},
                "blocks": {},
                "metadata": {"workflow_name": "setup"}
            }
            result = await block.execute(context)
        """
        try:
            result = await self.executor.execute(self._validated_inputs, context)
            return result
        except Exception as e:
            from .result import Result

            return Result.failure(f"Block execution exception: {e}")

    async def resume(
        self,
        context: dict[str, Any],
        llm_response: str,
        pause_metadata: dict[str, Any],
    ) -> Result[BlockOutput]:
        """Resume block execution after pause (for interactive blocks).

        This delegates to the executor's resume method. Only interactive
        executors implement this - others will raise NotImplementedError.

        Args:
            context: Shared workflow context
            llm_response: Response from LLM to the pause prompt
            pause_metadata: Metadata stored when the block paused

        Returns:
            Result with block output or error

        Raises:
            NotImplementedError: If executor doesn't support resume
        """
        try:
            result = await self.executor.resume(
                self._validated_inputs, context, llm_response, pause_metadata
            )
            return result
        except Exception as e:
            from .result import Result

            return Result.failure(f"Block resume exception: {e}")

    def supports_resume(self) -> bool:
        """Check if this block's executor supports resume functionality.

        Returns:
            True if executor implements resume, False otherwise
        """
        # Check if executor has overridden the resume method
        # by checking if it's the base class method
        from .executor_base import BlockExecutor

        return self.executor.resume != BlockExecutor.resume

    def get_capabilities(self) -> dict[str, Any]:
        """Get executor capabilities for security audit.

        Returns:
            Dictionary with executor type, security level, and capabilities
        """
        return self.executor.get_capabilities()
