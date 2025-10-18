"""Tests for schema generation and validation."""

import json

import pytest

from workflows_mcp.engine.executor_base import create_default_registry


@pytest.fixture
def executor_registry():
    """Create isolated ExecutorRegistry with all built-in executors for each test."""
    return create_default_registry()


def test_schema_generation(executor_registry):
    """Test schema generation from registry."""
    schema = executor_registry.generate_workflow_schema()

    # Verify schema structure
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert "properties" in schema
    assert "blocks" in schema["properties"]
    assert "definitions" in schema

    # Verify core executors are included
    block_types = schema["properties"]["blocks"]["items"]["properties"]["type"]["enum"]
    registered_types = executor_registry.list_types()

    # Schema should include all registered executor types
    assert len(block_types) > 0, "Schema should include at least one block type"
    assert set(block_types) == set(registered_types), (
        "Schema block types should match registered executors"
    )

    # Core executors that should be present when all modules are loaded
    expected_core_executors = {
        "Shell",
        "CreateFile",
        "ReadFile",
        "PopulateTemplate",
        "ExecuteWorkflow",
        "ReadJSONState",
        "WriteJSONState",
        "MergeJSONState",
        "ConfirmOperation",
        "AskChoice",
        "GetInput",
    }

    # Check if we have the expected core executors
    # (They should all be there since create_default_registry loads all executors)
    missing_core = expected_core_executors - set(block_types)
    assert not missing_core, f"Missing core executors in schema: {missing_core}"


def test_schema_has_all_executor_definitions(executor_registry):
    """Test that schema includes input definitions for all executors."""
    schema = executor_registry.generate_workflow_schema()

    # All executor types should have input definitions
    block_types = schema["properties"]["blocks"]["items"]["properties"]["type"]["enum"]

    for block_type in block_types:
        definition_key = f"{block_type}Input"
        assert definition_key in schema["definitions"], f"Missing definition for {block_type}"


def test_schema_json_serializable(executor_registry):
    """Test that schema is JSON serializable."""
    schema = executor_registry.generate_workflow_schema()

    # Should serialize to JSON without errors
    json_str = json.dumps(schema, indent=2)
    assert len(json_str) > 0

    # Should deserialize back
    parsed = json.loads(json_str)
    assert parsed == schema


def test_validate_valid_workflow(executor_registry):
    """Test validation of valid workflow."""
    from jsonschema import validate

    schema = executor_registry.generate_workflow_schema()

    workflow = {
        "name": "test-workflow",
        "blocks": [{"id": "test", "type": "Shell", "inputs": {"command": "echo test"}}],
    }

    # Should not raise
    validate(instance=workflow, schema=schema)


def test_validate_invalid_workflow_missing_name(executor_registry):
    """Test validation catches missing required field."""
    from jsonschema import ValidationError, validate

    schema = executor_registry.generate_workflow_schema()

    workflow = {
        # Missing "name" (required)
        "blocks": []
    }

    with pytest.raises(ValidationError):
        validate(instance=workflow, schema=schema)


def test_validate_invalid_workflow_unknown_type(executor_registry):
    """Test validation catches unknown block type."""
    from jsonschema import ValidationError, validate

    schema = executor_registry.generate_workflow_schema()

    workflow = {
        "name": "test",
        "blocks": [
            {
                "id": "test",
                "type": "NonExistentBlock",  # Unknown type
                "inputs": {},
            }
        ],
    }

    with pytest.raises(ValidationError):
        validate(instance=workflow, schema=schema)
