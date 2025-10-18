"""Test helper executors and utilities.

This module contains test-specific block executors that are not part of
the production codebase but are needed for testing the workflow engine.
"""

from typing import Any

from pydantic import Field

from workflows_mcp.engine.block import BlockInput, BlockOutput
from workflows_mcp.engine.executor_base import BlockExecutor
from workflows_mcp.engine.result import Result


class EchoBlockInput(BlockInput):
    """Input for EchoBlock test executor."""

    message: str = Field(description="Message to echo")


class EchoBlockOutput(BlockOutput):
    """Output for EchoBlock test executor."""

    echoed: str = Field(description="Echoed message")
    success: bool = Field(default=True, description="Always succeeds")


class EchoBlockExecutor(BlockExecutor):
    """Simple echo executor for testing workflows.

    This executor is used in tests to verify workflow execution,
    variable resolution, and DAG ordering without complex I/O operations.
    """

    type_name = "EchoBlock"
    input_type = EchoBlockInput
    output_type = EchoBlockOutput

    async def execute(self, inputs: BlockInput, context: dict[str, Any]) -> Result[BlockOutput]:
        """Echo the input message back as output with "Echo: " prefix.

        Args:
            inputs: Validated EchoBlockInput
            context: Workflow execution context (unused)

        Returns:
            Result with EchoBlockOutput containing the echoed message with prefix
        """
        assert isinstance(inputs, EchoBlockInput)
        return Result.success(EchoBlockOutput(echoed=f"Echo: {inputs.message}", success=True))


# EchoBlock executor registration moved to test fixtures
# Each test creates an isolated ExecutorRegistry via create_default_registry()
# and registers EchoBlock into it as needed (see conftest.py)
