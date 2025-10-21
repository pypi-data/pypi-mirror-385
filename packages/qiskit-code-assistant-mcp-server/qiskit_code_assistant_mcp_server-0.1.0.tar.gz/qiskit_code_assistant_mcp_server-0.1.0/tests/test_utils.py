# This code is part of Qiskit.
#
# (C) Copyright IBM 2025.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Unit tests for utility functions."""

import pytest
from unittest.mock import patch, Mock
import httpx
import respx
import os

from qiskit_code_assistant_mcp_server.utils import (
    make_qca_request,
    get_error_message,
    get_http_client,
    close_http_client,
)


class TestGetTokenFromSystem:
    """Test token retrieval from system."""

    def test_get_token_from_env(self, mock_env_vars):
        """Test token retrieval from environment variable."""
        with patch.dict("os.environ", {"QISKIT_IBM_TOKEN": "env_token_123"}):
            # Need to reload the module to get the updated token
            from qiskit_code_assistant_mcp_server.utils import _get_token_from_system

            token = _get_token_from_system()
            assert token == "env_token_123"

    def test_get_token_from_file(self, mock_qiskit_credentials):
        """Test token retrieval from credentials file."""
        with patch.dict("os.environ", {}, clear=True):
            # Remove QISKIT_IBM_TOKEN from env
            if "QISKIT_IBM_TOKEN" in os.environ:
                del os.environ["QISKIT_IBM_TOKEN"]

            from qiskit_code_assistant_mcp_server.utils import _get_token_from_system

            token = _get_token_from_system()
            assert token == "test_token_from_file"

    def test_get_token_no_env_no_file(self):
        """Test exception when no token is available."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                from qiskit_code_assistant_mcp_server.utils import (
                    _get_token_from_system,
                )

                with pytest.raises(Exception) as exc_info:
                    _get_token_from_system()

                assert "does not exist" in str(exc_info.value)

    def test_get_token_file_missing_default(self, mock_qiskit_credentials):
        """Test exception when credentials file exists but missing default entry."""
        import json

        # Create file without default-ibm-quantum-platform entry
        with open(mock_qiskit_credentials, "w") as f:
            json.dump({"other-account": {"token": "other_token"}}, f)

        with patch.dict("os.environ", {}, clear=True):
            from qiskit_code_assistant_mcp_server.utils import _get_token_from_system

            with pytest.raises(Exception) as exc_info:
                _get_token_from_system()

            assert "default-ibm-quantum-platform not found" in str(exc_info.value)


class TestGetErrorMessage:
    """Test error message extraction from HTTP responses."""

    def test_get_error_message_success_response(self):
        """Test error message for successful response."""
        response = Mock(spec=httpx.Response)
        response.is_success = True

        message = get_error_message(response)
        assert "Unable to fetch Qiskit Code Assistant" in message

    def test_get_error_message_json_detail(self):
        """Test error message extraction from JSON response."""
        response = Mock(spec=httpx.Response)
        response.is_success = False
        response.status_code = 401
        response.json.return_value = {"detail": "Invalid token"}
        response.text = "Raw error text"

        message = get_error_message(response)
        assert "Qiskit Code Assistant API Token is not authorized" in message
        assert "Invalid token" in message

    def test_get_error_message_json_exception(self):
        """Test error message when JSON parsing fails."""
        response = Mock(spec=httpx.Response)
        response.is_success = False
        response.status_code = 500
        response.json.side_effect = Exception("JSON decode error")
        response.text = "Internal server error"

        message = get_error_message(response)
        assert message == "Internal server error"

    def test_get_error_message_403_forbidden(self):
        """Test error message for 403 Forbidden."""
        response = Mock(spec=httpx.Response)
        response.is_success = False
        response.status_code = 403
        response.json.return_value = {"detail": "Access denied"}
        response.text = "Forbidden"

        message = get_error_message(response)
        assert "Qiskit Code Assistant API Token is not authorized" in message
        assert "Access denied" in message


class TestHTTPClient:
    """Test HTTP client management."""

    @pytest.mark.asyncio
    async def test_get_http_client_creation(self, mock_env_vars):
        """Test HTTP client creation."""
        client = get_http_client()
        assert isinstance(client, httpx.AsyncClient)
        assert not client.is_closed

        # Clean up
        await close_http_client()

    @pytest.mark.asyncio
    async def test_get_http_client_reuse(self, mock_env_vars):
        """Test HTTP client reuse."""
        client1 = get_http_client()
        client2 = get_http_client()

        assert client1 is client2  # Same instance

        # Clean up
        await close_http_client()

    @pytest.mark.asyncio
    async def test_close_http_client(self, mock_env_vars):
        """Test HTTP client closure."""
        client = get_http_client()
        assert not client.is_closed

        await close_http_client()
        assert client.is_closed

    @pytest.mark.asyncio
    async def test_get_client_after_close(self, mock_env_vars):
        """Test getting client after closure creates new instance."""
        client1 = get_http_client()
        await close_http_client()

        client2 = get_http_client()
        assert client1 is not client2
        assert client1.is_closed
        assert not client2.is_closed

        # Clean up
        await close_http_client()


class TestMakeQCARequest:
    """Test QCA API request function."""

    @pytest.mark.asyncio
    async def test_make_request_success(self, mock_env_vars):
        """Test successful API request."""
        with respx.mock() as respx_mock:
            respx_mock.get("https://test-api.example.com/test").mock(
                return_value=httpx.Response(200, json={"result": "success"})
            )

            result = await make_qca_request("https://test-api.example.com/test", "GET")

            assert result == {"result": "success"}

            # Clean up
            await close_http_client()

    @pytest.mark.asyncio
    async def test_make_request_with_params(self, mock_env_vars):
        """Test API request with parameters."""
        with respx.mock() as respx_mock:
            respx_mock.get("https://test-api.example.com/test").mock(
                return_value=httpx.Response(200, json={"result": "success"})
            )

            result = await make_qca_request(
                "https://test-api.example.com/test", "GET", params={"q": "test"}
            )

            assert result == {"result": "success"}

            # Clean up
            await close_http_client()

    @pytest.mark.asyncio
    async def test_make_request_with_body(self, mock_env_vars):
        """Test API request with JSON body."""
        with respx.mock() as respx_mock:
            respx_mock.post("https://test-api.example.com/test").mock(
                return_value=httpx.Response(200, json={"result": "created"})
            )

            result = await make_qca_request(
                "https://test-api.example.com/test", "POST", body={"data": "test"}
            )

            assert result == {"result": "created"}

            # Clean up
            await close_http_client()

    @pytest.mark.asyncio
    async def test_make_request_http_error(self, mock_env_vars):
        """Test API request with HTTP error."""
        with respx.mock() as respx_mock:
            respx_mock.get("https://test-api.example.com/test").mock(
                return_value=httpx.Response(404, json={"detail": "Not found"})
            )

            result = await make_qca_request("https://test-api.example.com/test", "GET")

            assert "error" in result
            assert (
                "Not found" in result["error"] or "Unable to fetch" in result["error"]
            )

            # Clean up
            await close_http_client()

    @pytest.mark.asyncio
    async def test_make_request_timeout_retry(self, mock_env_vars):
        """Test API request with timeout and retry."""
        with respx.mock() as respx_mock:
            # First two calls timeout, third succeeds
            respx_mock.get("https://test-api.example.com/test").mock(
                side_effect=[
                    httpx.TimeoutException("Request timeout"),
                    httpx.TimeoutException("Request timeout"),
                    httpx.Response(200, json={"result": "success"}),
                ]
            )

            result = await make_qca_request(
                "https://test-api.example.com/test", "GET", max_retries=3
            )

            assert result == {"result": "success"}

            # Clean up
            await close_http_client()

    @pytest.mark.asyncio
    async def test_make_request_connection_error_retry(self, mock_env_vars):
        """Test API request with connection error and retry."""
        with respx.mock() as respx_mock:
            # First call fails, second succeeds
            respx_mock.get("https://test-api.example.com/test").mock(
                side_effect=[
                    httpx.ConnectError("Connection failed"),
                    httpx.Response(200, json={"result": "success"}),
                ]
            )

            result = await make_qca_request(
                "https://test-api.example.com/test", "GET", max_retries=2
            )

            assert result == {"result": "success"}

            # Clean up
            await close_http_client()

    @pytest.mark.asyncio
    async def test_make_request_max_retries_exceeded(self, mock_env_vars):
        """Test API request when max retries exceeded."""
        with respx.mock() as respx_mock:
            respx_mock.get("https://test-api.example.com/test").mock(
                side_effect=httpx.TimeoutException("Request timeout")
            )

            result = await make_qca_request(
                "https://test-api.example.com/test", "GET", max_retries=2
            )

            assert "error" in result
            assert "Request failed after 2 attempts" in result["error"]

            # Clean up
            await close_http_client()

    @pytest.mark.asyncio
    async def test_make_request_unexpected_exception(self, mock_env_vars):
        """Test API request with unexpected exception."""
        with respx.mock() as respx_mock:
            respx_mock.get("https://test-api.example.com/test").mock(
                side_effect=ValueError("Unexpected error")
            )

            result = await make_qca_request("https://test-api.example.com/test", "GET")

            assert "error" in result
            assert "Request failed after" in result["error"]

            # Clean up
            await close_http_client()


# Assisted by watsonx Code Assistant
