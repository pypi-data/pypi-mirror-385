"""Result type for workflow error handling."""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from workflows_mcp.engine.checkpoint import PauseData

T = TypeVar("T")


class ResultState(str, Enum):
    """Enumeration of possible result states.

    Using a discriminated union pattern ensures type safety by preventing
    invalid state combinations (e.g., success=True and paused=True).
    """

    SUCCESS = "success"
    FAILURE = "failure"
    PAUSED = "paused"


@dataclass
class Result(Generic[T]):  # noqa: UP046
    """
    Result type for success/failure handling without exceptions.

    Uses a discriminated union pattern with ResultState enum to ensure
    type-safe state management and prevent invalid state combinations.

    Usage:
        result = some_operation()
        if result.is_success:
            print(result.value)
        else:
            print(result.error)
    """

    state: ResultState
    value: T | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    pause_data: "PauseData | None" = None

    def __post_init__(self) -> None:
        """Validate state consistency after initialization.

        Ensures that the result data matches the declared state:
        - SUCCESS results must have a value
        - FAILURE results must have an error message
        - PAUSED results must have pause_data
        """
        if self.state == ResultState.SUCCESS and self.value is None:
            raise ValueError("Success result must have a value")
        if self.state == ResultState.FAILURE and not self.error:
            raise ValueError("Failure result must have an error message")
        if self.state == ResultState.PAUSED and not self.pause_data:
            raise ValueError("Paused result must have pause_data")

    @property
    def is_success(self) -> bool:
        """Check if result is successful."""
        return self.state == ResultState.SUCCESS

    @property
    def is_failure(self) -> bool:
        """Check if result is failed."""
        return self.state == ResultState.FAILURE

    @property
    def is_paused(self) -> bool:
        """Check if result is paused."""
        return self.state == ResultState.PAUSED

    @classmethod
    def success(cls, value: T, metadata: dict[str, Any] | None = None) -> "Result[T]":
        """Create a successful result.

        Args:
            value: The success value
            metadata: Optional metadata dictionary (defaults to empty dict)

        Returns:
            Result with SUCCESS state and the provided value
        """
        return cls(
            state=ResultState.SUCCESS,
            value=value,
            metadata=metadata or {},
        )

    @classmethod
    def failure(cls, error: str, metadata: dict[str, Any] | None = None) -> "Result[T]":
        """Create a failed result.

        Args:
            error: Error message describing the failure
            metadata: Optional metadata dictionary (defaults to empty dict)

        Returns:
            Result with FAILURE state and the error message
        """
        return cls(
            state=ResultState.FAILURE,
            error=error,
            metadata=metadata or {},
        )

    @classmethod
    def pause(cls, prompt: str, checkpoint_id: str, **pause_metadata: Any) -> "Result[T]":
        """Create a paused result with checkpoint information.

        Args:
            prompt: Human-readable message explaining why workflow is paused
            checkpoint_id: Reference to checkpoint for resumption
            **pause_metadata: Additional metadata about the pause

        Returns:
            Result with PAUSED state and associated pause data
        """
        from workflows_mcp.engine.checkpoint import PauseData

        pause_data = PauseData(
            prompt=prompt, checkpoint_id=checkpoint_id, pause_metadata=pause_metadata
        )

        return cls(state=ResultState.PAUSED, pause_data=pause_data, metadata={})

    def __bool__(self) -> bool:
        """Allow using result in if statements."""
        return self.is_success

    def unwrap(self) -> T:
        """Get value or raise exception if failed."""
        if not self.is_success:
            raise ValueError(f"Cannot unwrap failed result: {self.error}")
        if self.value is None:
            raise ValueError("Cannot unwrap result: value is None")
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get value or return default if failed."""
        if self.is_success and self.value is not None:
            return self.value
        return default
