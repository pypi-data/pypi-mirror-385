"""Tests for executor base architecture."""

import pytest
from pydantic import Field

from workflows_mcp.engine.block import Block, BlockInput, BlockOutput
from workflows_mcp.engine.executor_base import (
    BlockExecutor,
    ExecutorCapabilities,
    ExecutorRegistry,
    ExecutorSecurityLevel,
)
from workflows_mcp.engine.result import Result


@pytest.fixture
def executor_registry():
    """Create isolated ExecutorRegistry for each test.

    This fixture provides a fresh ExecutorRegistry instance for test isolation.
    Tests that need executors should register them explicitly.
    """
    return ExecutorRegistry()


# Test executor implementation
class DemoInput(BlockInput):
    """Demo input model for testing."""

    message: str = Field(description="Test message")


class DemoOutput(BlockOutput):
    """Demo output model for testing."""

    result: str = Field(description="Test result")


class DemoExecutor(BlockExecutor):
    """Demo executor for testing purposes."""

    type_name = "Demo"
    input_type = DemoInput
    output_type = DemoOutput
    security_level = ExecutorSecurityLevel.SAFE

    async def execute(self, inputs: BlockInput, context: dict) -> Result[BlockOutput]:
        """Execute demo logic."""
        demo_inputs = inputs  # Already validated as DemoInput
        output = DemoOutput(result=f"Processed: {demo_inputs.message}")
        return Result.success(output)


def test_executor_registration(executor_registry):
    """Test executor registration."""
    executor = DemoExecutor()

    executor_registry.register(executor)

    assert executor_registry.has_type("Demo")
    assert executor_registry.get("Demo") == executor
    assert "Demo" in executor_registry.list_types()


def test_executor_duplicate_registration(executor_registry):
    """Test that duplicate registration fails."""
    executor = DemoExecutor()

    executor_registry.register(executor)

    with pytest.raises(ValueError, match="already registered"):
        executor_registry.register(executor)


def test_executor_unknown_type(executor_registry):
    """Test that unknown type raises error."""
    with pytest.raises(ValueError, match="Unknown block type"):
        executor_registry.get("NonExistent")


@pytest.mark.asyncio
async def test_block_execution(executor_registry):
    """Test block execution via executor."""
    executor = DemoExecutor()
    executor_registry.register(executor)

    # Create block with injected registry
    block = Block(id="test1", type="Demo", inputs={"message": "hello"}, registry=executor_registry)

    # Execute
    result = await block.execute(context={})

    assert result.is_success
    assert result.value.result == "Processed: hello"


def test_schema_generation(executor_registry):
    """Test JSON Schema generation."""
    executor = DemoExecutor()
    executor_registry.register(executor)

    schema = executor_registry.generate_workflow_schema()

    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert "Demo" in schema["properties"]["blocks"]["items"]["properties"]["type"]["enum"]
    assert "DemoInput" in schema["definitions"]


def test_executor_input_schema(executor_registry):
    """Test executor input schema generation."""
    executor = DemoExecutor()

    schema = executor.get_input_schema()

    assert "properties" in schema
    assert "message" in schema["properties"]
    assert schema["properties"]["message"]["description"] == "Test message"


def test_executor_output_schema(executor_registry):
    """Test executor output schema generation."""
    executor = DemoExecutor()

    schema = executor.get_output_schema()

    assert "properties" in schema
    assert "result" in schema["properties"]


def test_executor_capabilities(executor_registry):
    """Test executor capabilities retrieval."""
    executor = DemoExecutor()

    capabilities = executor.get_capabilities()

    assert capabilities["type"] == "Demo"
    assert capabilities["security_level"] == "safe"
    assert "capabilities" in capabilities


def test_executor_security_level(executor_registry):
    """Test executor security level attributes."""
    executor = DemoExecutor()

    assert executor.security_level == ExecutorSecurityLevel.SAFE


def test_executor_capabilities_model(executor_registry):
    """Test ExecutorCapabilities model."""
    caps = ExecutorCapabilities(can_read_files=True, can_write_files=True)

    assert caps.can_read_files is True
    assert caps.can_write_files is True
    assert caps.can_execute_commands is False
    assert caps.can_network is False


def test_registry_list_types(executor_registry):
    """Test listing registered types."""
    # Should be empty initially
    assert executor_registry.list_types() == []

    # Register executor
    executor = DemoExecutor()
    executor_registry.register(executor)

    # Should contain Demo
    assert executor_registry.list_types() == ["Demo"]


def test_registry_has_type(executor_registry):
    """Test checking if type exists."""
    executor = DemoExecutor()
    executor_registry.register(executor)

    assert executor_registry.has_type("Demo") is True
    assert executor_registry.has_type("NonExistent") is False


@pytest.mark.asyncio
async def test_block_invalid_inputs(executor_registry):
    """Test block creation with invalid inputs."""
    executor = DemoExecutor()
    executor_registry.register(executor)

    # Missing required field 'message'
    with pytest.raises(ValueError, match="input validation failed"):
        Block(id="test1", type="Demo", inputs={}, registry=executor_registry)


@pytest.mark.asyncio
async def test_block_unknown_type(executor_registry):
    """Test block creation with unknown type."""
    # Type not registered - empty registry
    with pytest.raises(ValueError, match="Unknown block type"):
        Block(
            id="test1",
            type="NonExistent",
            inputs={"message": "hello"},
            registry=executor_registry,
        )


def test_executor_missing_type_name(executor_registry):
    """Test executor registration without type_name."""

    class BadExecutor(BlockExecutor):
        # Missing type_name
        input_type = DemoInput
        output_type = DemoOutput

        async def execute(self, inputs, context):
            pass

    executor = BadExecutor()

    with pytest.raises(ValueError, match="missing type_name"):
        executor_registry.register(executor)


def test_workflow_schema_structure(executor_registry):
    """Test complete workflow schema structure."""
    executor = DemoExecutor()
    executor_registry.register(executor)

    schema = executor_registry.generate_workflow_schema()

    # Check top-level structure
    assert "properties" in schema
    assert "name" in schema["properties"]
    assert "blocks" in schema["properties"]
    assert "inputs" in schema["properties"]
    assert "outputs" in schema["properties"]

    # Check required fields
    assert "name" in schema["required"]
    assert "blocks" in schema["required"]

    # Check blocks schema
    blocks_schema = schema["properties"]["blocks"]
    assert blocks_schema["type"] == "array"
    assert "items" in blocks_schema

    # Check block item schema
    block_item = blocks_schema["items"]
    assert block_item["type"] == "object"
    assert "id" in block_item["required"]
    assert "type" in block_item["required"]
    assert "inputs" in block_item["required"]


@pytest.mark.asyncio
async def test_block_with_dependencies(executor_registry):
    """Test block creation with dependencies."""
    executor = DemoExecutor()
    executor_registry.register(executor)

    block = Block(
        id="test1",
        type="Demo",
        inputs={"message": "hello"},
        depends_on=["setup", "config"],
        registry=executor_registry,
    )

    assert block.depends_on == ["setup", "config"]


@pytest.mark.asyncio
async def test_block_capabilities(executor_registry):
    """Test block capabilities retrieval."""
    executor = DemoExecutor()
    executor_registry.register(executor)

    block = Block(
        id="test1",
        type="Demo",
        inputs={"message": "hello"},
        registry=executor_registry,
    )

    capabilities = block.get_capabilities()

    assert capabilities["type"] == "Demo"
    assert capabilities["security_level"] == "safe"
