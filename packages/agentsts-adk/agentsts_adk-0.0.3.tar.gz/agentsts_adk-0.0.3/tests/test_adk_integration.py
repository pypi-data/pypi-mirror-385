"""Tests for ADK integration classes."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from google.adk.tools.mcp_tool import MCPTool

from agentsts.adk import (
    SUBJECT_TOKEN_KEY,
    ADKRunner,
    ADKTokenPropagationPlugin,
)
from agentsts.adk._base import _extract_jwt_from_headers as extract_jwt_from_headers


class TestADKTokenPropagationPlugin:
    """Test cases for ADKTokenPropagationPlugin."""

    def test_init(self):
        """Test plugin initialization."""
        mock_sts_integration = Mock()
        plugin = ADKTokenPropagationPlugin(mock_sts_integration)

        assert plugin.name == "ADKTokenPropagationPlugin"
        assert plugin.sts_integration == mock_sts_integration

    @pytest.mark.asyncio
    async def test_before_tool_callback_with_mcp_tool(self):
        """Test before_tool_callback with MCPTool."""
        mock_sts_integration = Mock()
        mock_credential = Mock()
        mock_sts_integration.get_auth_credential = AsyncMock(return_value=mock_credential)

        plugin = ADKTokenPropagationPlugin(mock_sts_integration)

        # Create mock MCPTool
        mock_tool = Mock(spec=MCPTool)
        mock_tool.name = "test-mcp-tool"
        mock_tool._run_async_impl = AsyncMock(return_value="tool_result")

        # Create mock tool context with session state
        mock_tool_context = Mock()
        mock_tool_context._invocation_context.session.state = {SUBJECT_TOKEN_KEY: "subject-token-123"}

        tool_args = {"arg1": "value1"}

        result = await plugin.before_tool_callback(tool=mock_tool, tool_args=tool_args, tool_context=mock_tool_context)

        mock_sts_integration.get_auth_credential.assert_called_once_with(subject_token="subject-token-123")
        mock_tool._run_async_impl.assert_called_once_with(
            args=tool_args, tool_context=mock_tool_context, credential=mock_credential
        )
        assert result == "tool_result"

    @pytest.mark.asyncio
    async def test_before_tool_callback_with_non_mcp_tool(self):
        """Test before_tool_callback with non-MCPTool."""
        mock_sts_integration = Mock()
        plugin = ADKTokenPropagationPlugin(mock_sts_integration)

        # Create mock non-MCPTool
        mock_tool = Mock()
        mock_tool.name = "test-tool"

        mock_tool_context = Mock()
        tool_args = {"arg1": "value1"}

        result = await plugin.before_tool_callback(tool=mock_tool, tool_args=tool_args, tool_context=mock_tool_context)

        mock_sts_integration.get_auth_credential.assert_not_called()
        assert result is None

    @pytest.mark.asyncio
    async def test_before_tool_callback_no_subject_token(self):
        """Test before_tool_callback when no subject token in session state."""
        mock_sts_integration = Mock()
        mock_sts_integration.get_auth_credential = AsyncMock(return_value=None)

        plugin = ADKTokenPropagationPlugin(mock_sts_integration)

        mock_tool = Mock(spec=MCPTool)
        mock_tool.name = "test-mcp-tool"
        mock_tool._run_async_impl = AsyncMock()

        mock_tool_context = Mock()
        mock_tool_context._invocation_context.session.state = {}  # No subject token

        tool_args = {"arg1": "value1"}

        with patch("agentsts.adk._base.logger") as mock_logger:
            result = await plugin.before_tool_callback(
                tool=mock_tool, tool_args=tool_args, tool_context=mock_tool_context
            )

            mock_logger.warning.assert_called_once_with("No access token available for ADK tool: %s", "test-mcp-tool")
            assert result is None


class TestADKRunner:
    """Test cases for ADKRunner."""

    def test_init(self):
        """Test ADKRunner initialization."""
        with patch("agentsts.adk._base.ADKSessionService") as mock_session_service:
            mock_agent = Mock()
            runner = ADKRunner(session_service=mock_session_service, app_name="test-app", agent=mock_agent)

            assert runner.session_service == mock_session_service

    @pytest.mark.asyncio
    async def test_run_async_with_jwt(self):
        """Test run_async with JWT in headers."""
        headers = {"Authorization": "Bearer jwt-token-123"}

        with patch("agentsts.adk._base.ADKSessionService") as mock_session_service:
            mock_session_service_instance = Mock()
            mock_session_service_instance._store_subject_token = Mock(return_value=None)
            mock_session_service.return_value = mock_session_service_instance
            with patch("agentsts.adk._base.extract_jwt_from_headers") as mock_extract:
                # Mock the async generator
                async def mock_async_gen():
                    yield "event1"
                    yield "event2"

                with patch("agentsts.adk._base.Runner.run_async", return_value=mock_async_gen()) as mock_super_run:
                    mock_extract.return_value = "jwt-token-123"
                    mock_agent = Mock()

                    runner = ADKRunner(
                        session_service=mock_session_service_instance, app_name="test-app", agent=mock_agent
                    )

                    # Collect all events from the async generator
                    events = []
                    async for event in runner.run_async("arg1", "arg2", headers=headers, kwarg1="value1"):
                        events.append(event)

                    mock_extract.assert_called_once_with(headers)
                    mock_session_service_instance._store_subject_token.assert_called_once_with("jwt-token-123")
                    mock_super_run.assert_called_once_with("arg1", "arg2", kwarg1="value1")
                    assert events == ["event1", "event2"]

    @pytest.mark.asyncio
    async def test_run_async_without_jwt(self):
        """Test run_async without JWT in headers."""
        headers = {"Other-Header": "value"}

        with patch("agentsts.adk._base.ADKSessionService") as mock_session_service:
            with patch("agentsts.adk._base.extract_jwt_from_headers") as mock_extract:
                # Mock the async generator
                async def mock_async_gen():
                    yield "event1"
                    yield "event2"

                with patch("agentsts.adk._base.Runner.run_async", return_value=mock_async_gen()) as mock_super_run:
                    mock_extract.return_value = None
                    mock_agent = Mock()

                    runner = ADKRunner(session_service=mock_session_service, app_name="test-app", agent=mock_agent)

                    # Collect all events from the async generator
                    events = []
                    async for event in runner.run_async("arg1", "arg2", headers=headers):
                        events.append(event)

                    mock_extract.assert_called_once_with(headers)
                    mock_super_run.assert_called_once_with("arg1", "arg2")
                    assert events == ["event1", "event2"]

    def test_extract_jwt_from_headers_success(self):
        """Test successful JWT extraction from headers."""
        headers = {"Authorization": "Bearer jwt-token-123"}

        with patch("agentsts.adk._base.logger") as mock_logger:
            result = extract_jwt_from_headers(headers)

            assert result == "jwt-token-123"
            mock_logger.debug.assert_called_once()

    def test_extract_jwt_from_headers_no_headers(self):
        """Test JWT extraction with no headers."""
        with patch("agentsts.adk._base.logger") as mock_logger:
            result = extract_jwt_from_headers({})

            assert result is None
            mock_logger.warning.assert_called_once_with("No headers provided for JWT extraction")

    def test_extract_jwt_from_headers_no_auth_header(self):
        """Test JWT extraction with no Authorization header."""
        headers = {"Other-Header": "value"}

        with patch("agentsts.adk._base.logger") as mock_logger:
            result = extract_jwt_from_headers(headers)

            assert result is None
            mock_logger.warning.assert_called_once_with("No Authorization header found in request")

    def test_extract_jwt_from_headers_invalid_bearer(self):
        """Test JWT extraction with invalid Bearer format."""
        headers = {"Authorization": "Basic jwt-token-123"}

        with patch("agentsts.adk._base.logger") as mock_logger:
            result = extract_jwt_from_headers(headers)

            assert result is None
            mock_logger.warning.assert_called_once_with("Authorization header must start with Bearer")

    def test_extract_jwt_from_headers_empty_token(self):
        """Test JWT extraction with empty token."""
        headers = {"Authorization": "Bearer "}

        with patch("agentsts.adk._base.logger") as mock_logger:
            result = extract_jwt_from_headers(headers)

            assert result is None
            mock_logger.warning.assert_called_once_with("Empty JWT token found in Authorization header")

    def test_extract_jwt_from_headers_whitespace_token(self):
        """Test JWT extraction with whitespace-only token."""
        headers = {"Authorization": "Bearer   \n\t  "}

        with patch("agentsts.adk._base.logger") as mock_logger:
            result = extract_jwt_from_headers(headers)

            assert result is None
            mock_logger.warning.assert_called_once_with("Empty JWT token found in Authorization header")

    def test_extract_jwt_from_headers_stripped_token(self):
        """Test JWT extraction with token that has whitespace."""
        headers = {"Authorization": "Bearer  jwt-token-123  \n"}

        with patch("agentsts.adk._base.logger") as mock_logger:
            result = extract_jwt_from_headers(headers)

            assert result == "jwt-token-123"
            mock_logger.debug.assert_called_once()
