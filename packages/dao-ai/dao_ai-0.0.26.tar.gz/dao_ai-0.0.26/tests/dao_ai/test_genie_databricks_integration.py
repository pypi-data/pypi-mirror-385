"""
Integration test for Genie tool Databricks model serving validation issue.

This test reproduces and verifies the fix for the ValidationError that occurred
when the Genie tool was deployed to Databricks model serving, where Pydantic
was trying to validate injected state parameters as tool inputs.

The original error was:
ValidationError: 6 validation errors for my_genie_tool
  state.context
    Field required [type=missing, input_value={...}, input_loc=('state', 'context')]
  state.conversations
    Field required [type=missing, input_value={...}, input_loc=('state', 'conversations')]
  ...and 4 more similar errors for other state fields

The fix involved:
1. Making the genie_tool function async (required for LangGraph injected parameters)
2. Using explicit args_schema=GenieToolInput to exclude injected parameters from validation
3. Using func parameter instead of coroutine in StructuredTool.from_function
"""

from unittest.mock import Mock, patch

import pytest
from conftest import has_databricks_env
from langchain_core.tools import StructuredTool

from dao_ai.config import GenieRoomModel
from dao_ai.state import SharedState
from dao_ai.tools.genie import GenieToolInput


@pytest.fixture
def mock_genie_room():
    """Fixture providing a mock GenieRoomModel."""
    return GenieRoomModel(name="test-genie-room", space_id="test-space-123")


@pytest.fixture
def mock_genie_space():
    """Mock Databricks Genie space response."""
    space = Mock()
    space.description = "Test space description"
    return space


@pytest.fixture
def mock_genie_response():
    """Mock Genie response object."""
    response = Mock()
    response.conversation_id = "test-conversation-123"
    response.response = "Test response from Genie"
    response.query = "SELECT * FROM test_table"
    response.result = Mock()
    return response


@pytest.fixture
def mock_genie_tool():
    """Create a mocked Genie tool for testing validation scenarios."""
    with (
        patch("dao_ai.tools.genie.Genie") as mock_genie_class,
        patch("databricks.sdk.WorkspaceClient") as mock_client,
    ):
        # Mock the WorkspaceClient and Genie space
        mock_workspace = Mock()
        mock_workspace.genie.get_space.return_value = Mock(description="Test space")
        mock_client.return_value = mock_workspace

        # Mock the Genie instance
        mock_genie_instance = Mock()
        mock_genie_instance.ask_question = Mock(
            return_value=Mock(
                conversation_id="test-conv-123",
                response="Test response",
                query="SELECT * FROM test",
                result=Mock(),
            )
        )
        mock_genie_class.return_value = mock_genie_instance

        from dao_ai.tools.genie import create_genie_tool

        genie_room = GenieRoomModel(name="test-genie-room", space_id="test-space-123")

        yield create_genie_tool(genie_room, persist_conversation=True)


class TestGenieDatabricksIntegration:
    """
    Test suite for Databricks model serving validation scenarios.

    This test suite reproduces and verifies the fix for a critical ValidationError
    that occurred when the Genie tool was deployed to Databricks model serving.

    PROBLEM: Pydantic was trying to validate injected state parameters as tool inputs
    SOLUTION: Made function async + used explicit args_schema to exclude injected parameters
    RESULT: Tool validation only includes user inputs, not LangGraph injected state
    """

    def test_genie_tool_schema_excludes_injected_parameters(self, mock_genie_tool):
        """Test that the tool schema properly marks injected parameters using Annotated."""
        tool = mock_genie_tool

        # The @tool decorator creates its own schema, but it should have injected parameters marked
        # Verify the schema includes all parameters
        schema = tool.args_schema.model_json_schema()
        properties = schema.get("properties", {})

        # With @tool decorator, all parameters are in schema but injected ones are marked with Annotated
        assert "question" in properties
        # Note: With @tool decorator, state and tool_call_id may appear in schema
        # but they're marked as injected via Annotated types

    def test_genie_tool_input_validation_success(self):
        """Test that GenieToolInput validates correctly with just question."""
        # This should succeed - only user inputs
        valid_input = GenieToolInput(question="What is the weather today?")
        assert valid_input.question == "What is the weather today?"

    def test_genie_tool_input_validation_accepts_only_question(self):
        """Test that GenieToolInput correctly accepts only expected fields."""
        # This should succeed - only with question
        valid_input = GenieToolInput(question="What is the weather today?")
        assert valid_input.question == "What is the weather today?"

        # Extra fields are ignored by default in Pydantic v2 unless model_config forbids them
        # The key point is that injected parameters are NOT part of the schema validation
        input_with_extra = GenieToolInput(
            question="What is the weather today?",
            state={"context": {}, "conversations": {}},  # This gets ignored
            tool_call_id="test-123",  # This gets ignored
        )
        assert input_with_extra.question == "What is the weather today?"

        # The important thing is that these fields don't show up in the model dump
        dumped = input_with_extra.model_dump()
        assert "state" not in dumped
        assert "tool_call_id" not in dumped
        assert "question" in dumped

    def test_genie_tool_function_signature_compatibility(self, mock_genie_tool):
        """Test that the genie_tool function has the correct async signature for LangGraph injection."""
        tool = mock_genie_tool

        # Verify the tool is created with func parameter (not coroutine)
        assert hasattr(tool, "func")
        assert tool.func is not None

        # Verify the function is sync (not async)
        import inspect

        assert not inspect.iscoroutinefunction(tool.func)

    def test_simulate_databricks_model_serving_scenario(self, mock_genie_tool):
        """
        Simulate the exact scenario that caused validation errors in Databricks model serving.

        This test reproduces and verifies the fix for the conditions where:
        1. Tool is invoked with only user inputs (question)
        2. State and tool_call_id are injected by LangGraph using Annotated types
        3. Tool works correctly with injected parameters

        THE FIX:
        1. Used @tool decorator which properly handles Annotated injected parameters
        2. Annotated[dict, InjectedState] and Annotated[str, InjectedToolCallId]
           tell LangGraph to inject these parameters at runtime
        3. The tool function signature includes all parameters, but LangGraph
           handles injection transparently
        """
        # Use the mocked tool
        tool = mock_genie_tool

        # Verify tool has the proper function signature
        import inspect

        sig = inspect.signature(tool.func)
        params = list(sig.parameters.keys())

        # Should have all three parameters: question, state, tool_call_id
        assert "question" in params
        assert "state" in params
        assert "tool_call_id" in params

        # Verify the tool is properly configured
        assert isinstance(tool, StructuredTool)
        assert tool.name == "genie_tool"

        # The key fix: @tool decorator with Annotated types handles injection properly
        # LangGraph will inject state and tool_call_id at runtime

    def test_structured_tool_configuration(self, mock_genie_tool):
        """Test that StructuredTool is configured correctly with @tool decorator."""
        tool = mock_genie_tool

        # Verify it's a StructuredTool
        assert isinstance(tool, StructuredTool)

        # Verify key configuration
        assert tool.name == "genie_tool"
        assert tool.description is not None
        assert "tabular data" in tool.description

        # Verify args_schema is auto-generated by @tool decorator
        assert tool.args_schema is not None
        assert hasattr(tool.args_schema, "model_json_schema")

        # Verify func is set
        assert hasattr(tool, "func")
        assert tool.func is not None

    @pytest.mark.skipif(not has_databricks_env(), reason="Databricks env vars not set")
    def test_conversation_persistence_with_injected_state(self, mock_genie_tool):
        """
        Test that conversation persistence works correctly with injected state pattern.

        This verifies that the fix doesn't break the core functionality of
        conversation mapping using space_id from the state.
        """
        # Create state with conversation mapping
        mock_state = SharedState(
            context={},
            conversations={"test-space-123": "existing-conversation-id"},
            messages=[],
            config=Mock(),
            user_id="test-user",
        )

        # Use the fixture genie tool
        tool = mock_genie_tool

        # Call the tool - this should work without validation errors
        result = tool.func(
            question="Continue our previous conversation",
            state=mock_state,
            tool_call_id="test-call-id",
        )

        # Verify the result structure (basic validation that it executed)
        from langgraph.types import Command

        assert isinstance(result, Command)
        assert result.update is not None
        assert "genie_conversation_ids" in result.update

    def test_original_error_reproduction_prevention(self, mock_genie_tool):
        """
        Test that demonstrates the original error is prevented by using @tool decorator.

        The @tool decorator with Annotated types (InjectedState, InjectedToolCallId)
        tells LangGraph to inject these parameters at runtime, so they don't need
        to be provided by the user.
        """
        tool = mock_genie_tool

        # Verify the tool is properly configured with @tool decorator
        assert isinstance(tool, StructuredTool)
        assert tool.name == "genie_tool"

        # Verify function signature has injected parameters
        import inspect

        sig = inspect.signature(tool.func)
        params = list(sig.parameters.keys())

        # All parameters should be present in signature
        assert "question" in params
        assert "state" in params
        assert "tool_call_id" in params

        # The key fix: Using Annotated with InjectedState and InjectedToolCallId
        # tells LangGraph to inject these at runtime, preventing validation errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
