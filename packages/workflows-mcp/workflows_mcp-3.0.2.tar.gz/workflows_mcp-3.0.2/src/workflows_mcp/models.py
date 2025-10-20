"""Pydantic input models for MCP tool validation.

This module defines input validation models for all MCP tools using Pydantic v2.
Following MCP Python SDK best practices:
- ConfigDict for model configuration (Pydantic v2 pattern)
- Field() with descriptions and constraints
- Explicit type hints for all fields
- field_validator for custom validation logic
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# =============================================================================
# Workflow Execution Input Models
# =============================================================================


class ExecuteWorkflowInput(BaseModel):
    """Input model for execute_workflow tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    workflow: str = Field(
        ...,
        description=(
            "Workflow name to execute (e.g., 'python-ci-pipeline', 'sequential-echo', "
            "'git-create-feature-branch'). Use list_workflows() to see all available workflows."
        ),
        min_length=1,
        max_length=200,
    )
    inputs: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Runtime inputs as key-value pairs for block variable substitution. "
            "Example: {'project_name': 'my-app', 'branch_name': 'feature/new-ui'}. "
            "Use get_workflow_info(workflow) to see required inputs for a workflow."
        ),
    )
    response_format: Literal["minimal", "detailed"] = Field(
        default="minimal",
        description=(
            "Output verbosity control:\n"
            "- 'minimal': Returns only status, outputs, and errors (saves tokens)\n"
            "- 'detailed': Includes full block execution details and metadata"
        ),
    )

    @field_validator("workflow")
    @classmethod
    def validate_workflow_name(cls, v: str) -> str:
        """Validate workflow name is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Workflow name cannot be empty or whitespace only")
        return v.strip()


class ExecuteInlineWorkflowInput(BaseModel):
    """Input model for execute_inline_workflow tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    workflow_yaml: str = Field(
        ...,
        description=(
            "Complete workflow definition as YAML string including name, description, blocks, etc. "
            "Must be valid YAML syntax following the workflow schema. "
            "Use validate_workflow_yaml() to check YAML before execution."
        ),
        min_length=10,
        max_length=100000,
    )
    inputs: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Runtime inputs as key-value pairs for block variable substitution. "
            "Example: {'source_path': 'src/', 'output_dir': 'dist/'}."
        ),
    )
    response_format: Literal["minimal", "detailed"] = Field(
        default="minimal",
        description=(
            "Output verbosity control:\n"
            "- 'minimal': Returns only status, outputs, and errors (saves tokens)\n"
            "- 'detailed': Includes full block execution details and metadata"
        ),
    )

    @field_validator("workflow_yaml")
    @classmethod
    def validate_yaml_not_empty(cls, v: str) -> str:
        """Validate YAML content is not empty."""
        if not v.strip():
            raise ValueError("Workflow YAML cannot be empty or whitespace only")
        return v


class ResumeWorkflowInput(BaseModel):
    """Input model for resume_workflow tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    checkpoint_id: str = Field(
        ...,
        description=(
            "Checkpoint token from pause or list_checkpoints "
            "(e.g., 'pause_abc123', 'auto_def456'). "
            "Use list_checkpoints() to see all available checkpoints."
        ),
        min_length=1,
        max_length=100,
    )
    llm_response: str = Field(
        default="",
        description=(
            "Your response to the pause prompt (required for paused workflows). "
            "For Prompt blocks, provide appropriate text based on the prompt. "
            "The workflow will interpret your response using conditions or subsequent blocks."
        ),
        max_length=10000,
    )
    response_format: Literal["minimal", "detailed"] = Field(
        default="minimal",
        description=(
            "Output verbosity control:\n"
            "- 'minimal': Returns only status, outputs, and errors (saves tokens)\n"
            "- 'detailed': Includes full block execution details and metadata"
        ),
    )

    @field_validator("checkpoint_id")
    @classmethod
    def validate_checkpoint_id(cls, v: str) -> str:
        """Validate checkpoint ID is not empty."""
        if not v.strip():
            raise ValueError("Checkpoint ID cannot be empty or whitespace only")
        return v.strip()


# =============================================================================
# Workflow Query Input Models
# =============================================================================


class ListWorkflowsInput(BaseModel):
    """Input model for list_workflows tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    tags: list[str] = Field(
        default_factory=list,
        description=(
            "Optional list of tags to filter workflows (e.g., ['python', 'ci'], ['git']). "
            "Workflows matching ALL tags are returned (AND logic). "
            "Empty list returns all workflows."
        ),
        max_length=20,
    )
    format: Literal["json", "markdown"] = Field(
        default="json",
        description=(
            "Response format:\n"
            "- 'json': List of workflow names for programmatic access\n"
            "- 'markdown': Human-readable formatted list with headers"
        ),
    )


class GetWorkflowInfoInput(BaseModel):
    """Input model for get_workflow_info tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    workflow: str = Field(
        ...,
        description=(
            "Workflow name to retrieve information about (e.g., 'python-ci-pipeline'). "
            "Use list_workflows() to see all available workflows."
        ),
        min_length=1,
        max_length=200,
    )
    format: Literal["json", "markdown"] = Field(
        default="json",
        description=(
            "Response format:\n"
            "- 'json': Structured data with workflow metadata, blocks, inputs, outputs\n"
            "- 'markdown': Human-readable formatted description with sections"
        ),
    )

    @field_validator("workflow")
    @classmethod
    def validate_workflow_name(cls, v: str) -> str:
        """Validate workflow name is not empty."""
        if not v.strip():
            raise ValueError("Workflow name cannot be empty or whitespace only")
        return v.strip()


class ValidateWorkflowYamlInput(BaseModel):
    """Input model for validate_workflow_yaml tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    yaml_content: str = Field(
        ...,
        description=(
            "YAML workflow definition to validate. Must be complete workflow YAML "
            "including name, description, and blocks sections."
        ),
        min_length=10,
        max_length=100000,
    )

    @field_validator("yaml_content")
    @classmethod
    def validate_yaml_not_empty(cls, v: str) -> str:
        """Validate YAML content is not empty."""
        if not v.strip():
            raise ValueError("YAML content cannot be empty or whitespace only")
        return v


# =============================================================================
# Checkpoint Management Input Models
# =============================================================================


class ListCheckpointsInput(BaseModel):
    """Input model for list_checkpoints tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    workflow_name: str = Field(
        default="",
        description=(
            "Filter checkpoints by workflow name (e.g., 'python-ci-pipeline'). "
            "Empty string returns checkpoints for all workflows."
        ),
        max_length=200,
    )
    format: Literal["json", "markdown"] = Field(
        default="json",
        description=(
            "Response format:\n"
            "- 'json': Structured data with checkpoints list and metadata\n"
            "- 'markdown': Human-readable formatted list with checkpoint details"
        ),
    )


class GetCheckpointInfoInput(BaseModel):
    """Input model for get_checkpoint_info tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    checkpoint_id: str = Field(
        ...,
        description=(
            "Checkpoint token to retrieve information about (e.g., 'pause_abc123'). "
            "Use list_checkpoints() to see all available checkpoints."
        ),
        min_length=1,
        max_length=100,
    )
    format: Literal["json", "markdown"] = Field(
        default="json",
        description=(
            "Response format:\n"
            "- 'json': Structured data with detailed checkpoint information\n"
            "- 'markdown': Human-readable formatted details with progress sections"
        ),
    )

    @field_validator("checkpoint_id")
    @classmethod
    def validate_checkpoint_id(cls, v: str) -> str:
        """Validate checkpoint ID is not empty."""
        if not v.strip():
            raise ValueError("Checkpoint ID cannot be empty or whitespace only")
        return v.strip()


class DeleteCheckpointInput(BaseModel):
    """Input model for delete_checkpoint tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    checkpoint_id: str = Field(
        ...,
        description=(
            "Checkpoint token to delete (e.g., 'pause_abc123'). "
            "Use list_checkpoints() to see all available checkpoints. "
            "Useful for cleaning up paused workflows that are no longer needed."
        ),
        min_length=1,
        max_length=100,
    )

    @field_validator("checkpoint_id")
    @classmethod
    def validate_checkpoint_id(cls, v: str) -> str:
        """Validate checkpoint ID is not empty."""
        if not v.strip():
            raise ValueError("Checkpoint ID cannot be empty or whitespace only")
        return v.strip()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Workflow execution models
    "ExecuteWorkflowInput",
    "ExecuteInlineWorkflowInput",
    "ResumeWorkflowInput",
    # Workflow query models
    "ListWorkflowsInput",
    "GetWorkflowInfoInput",
    "ValidateWorkflowYamlInput",
    # Checkpoint management models
    "ListCheckpointsInput",
    "GetCheckpointInfoInput",
    "DeleteCheckpointInput",
]
