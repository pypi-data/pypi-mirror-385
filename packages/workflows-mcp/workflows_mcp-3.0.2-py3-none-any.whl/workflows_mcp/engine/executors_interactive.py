"""Interactive workflow executor with pause/resume - Simplified to single Prompt type.

This module provides a single, simple interactive executor that pauses workflow
execution and waits for LLM input. All interaction patterns (confirmation, choice,
free-form input) are handled through prompt wording and response interpretation.

Philosophy: YAGNI (You Aren't Gonna Need It)
- Single executor type instead of three specialized types
- No built-in validation or choice parsing
- Workflows handle response interpretation using conditions and Shell blocks
- Maximum simplicity and flexibility
"""

from typing import Any, ClassVar

from pydantic import Field

from .block import BlockInput, BlockOutput
from .block_utils import ExecutionTimer
from .checkpoint import PauseData
from .executor_base import (
    BlockExecutor,
    ExecutorCapabilities,
    ExecutorSecurityLevel,
)
from .result import Result

# ============================================================================
# Prompt Executor - Single Interactive Type
# ============================================================================


class PromptInput(BlockInput):
    """Input for Prompt executor.

    Simple design: single prompt field for maximum flexibility.
    """

    prompt: str = Field(
        description="Prompt/question to display to LLM. The LLM will provide a response."
    )


class PromptOutput(BlockOutput):
    """Output for Prompt executor.

    Simple design: single response field containing raw LLM response.
    """

    response: str = Field(description="Raw LLM response to the prompt")


class PromptExecutor(BlockExecutor):
    """Interactive prompt executor - pauses workflow for LLM input.

    This is the ONLY interactive executor type. All interaction patterns
    (yes/no confirmation, multiple choice, free-form input) are handled
    through prompt wording and conditional logic in workflows.

    Design Philosophy:
    - KISS (Keep It Simple, Stupid): Single input, single output
    - YAGNI (You Aren't Gonna Need It): No validation, no parsing, no special cases
    - DRY (Don't Repeat Yourself): One executor handles all interactive patterns

    Example YAML - Yes/No Confirmation:
        - id: confirm_deploy
          type: Prompt
          inputs:
            prompt: |
              Deploy to production?

              Respond with 'yes' or 'no'

        # Parse response with condition
        - id: deploy
          type: Shell
          inputs:
            command: "./deploy.sh"
          condition: ${blocks.confirm_deploy.outputs.response} == 'yes'
          depends_on: [confirm_deploy]

    Example YAML - Multiple Choice:
        - id: select_env
          type: Prompt
          inputs:
            prompt: |
              Select deployment environment:

              1. development
              2. staging
              3. production

              Respond with the number of your choice.

        # Parse response with conditions
        - id: deploy_dev
          type: Shell
          inputs:
            command: "./deploy.sh dev"
          condition: ${blocks.select_env.outputs.response} == '1'
          depends_on: [select_env]

        - id: deploy_staging
          type: Shell
          inputs:
            command: "./deploy.sh staging"
          condition: ${blocks.select_env.outputs.response} == '2'
          depends_on: [select_env]

    Example YAML - Free-form Input:
        - id: get_commit_msg
          type: Prompt
          inputs:
            prompt: |
              Generate a semantic commit message following Conventional Commits.

              Format: type(scope): description

              Respond with ONLY the commit message.

        # Use response directly
        - id: create_commit
          type: Shell
          inputs:
            command: git commit -m "${blocks.get_commit_msg.outputs.response}"
          depends_on: [get_commit_msg]

    Benefits of Simplified Design:
    - No complex validation logic to maintain
    - No choice parsing edge cases
    - Workflows have full control over response interpretation
    - Easy to understand and extend
    - Follows YAGNI principle
    """

    type_name: ClassVar[str] = "Prompt"
    input_type: ClassVar[type[BlockInput]] = PromptInput
    output_type: ClassVar[type[BlockOutput]] = PromptOutput

    security_level: ClassVar[ExecutorSecurityLevel] = ExecutorSecurityLevel.SAFE
    capabilities: ClassVar[ExecutorCapabilities] = ExecutorCapabilities()

    async def execute(self, inputs: BlockInput, context: dict[str, Any]) -> Result[BlockOutput]:
        """Execute prompt - always pauses for LLM input.

        Args:
            inputs: Validated PromptInput
            context: Workflow context (unused by this executor)

        Returns:
            Result.pause() with prompt for LLM
        """
        assert isinstance(inputs, PromptInput)

        # Create pause data
        pause_data = PauseData(
            prompt=inputs.prompt,
            checkpoint_id="",  # Will be filled by workflow executor
            pause_metadata={
                "type": "prompt",
            },
        )

        return Result.pause(
            prompt=pause_data.prompt,
            checkpoint_id=pause_data.checkpoint_id,
            **pause_data.pause_metadata,
        )

    async def resume(
        self,
        inputs: BlockInput,
        context: dict[str, Any],
        llm_response: str,
        pause_metadata: dict[str, Any],
    ) -> Result[BlockOutput]:
        """Resume with LLM response.

        Args:
            inputs: Original PromptInput
            context: Workflow context
            llm_response: LLM's response to the prompt
            pause_metadata: Metadata from the pause

        Returns:
            Result with PromptOutput containing raw response
        """
        assert isinstance(inputs, PromptInput)
        timer = ExecutionTimer()

        # Simply return the raw response - no validation, no parsing
        output = PromptOutput(response=llm_response)

        return Result.success(output, metadata={"execution_time_ms": timer.elapsed_ms()})


# ============================================================================
# Registration
# ============================================================================

# Executor is registered via create_default_registry() in executor_base.py
# This enables dependency injection and test isolation
