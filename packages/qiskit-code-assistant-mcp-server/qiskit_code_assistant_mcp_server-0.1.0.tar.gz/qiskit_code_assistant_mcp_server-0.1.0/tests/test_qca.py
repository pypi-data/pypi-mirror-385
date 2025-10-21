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

"""Unit tests for QCA functions."""

import pytest
from unittest.mock import patch

from qiskit_code_assistant_mcp_server.qca import (
    qca_list_models,
    qca_get_model,
    qca_accept_model_disclaimer,
    qca_get_completion,
    qca_get_rag_completion,
    qca_accept_completion,
    qca_get_service_status,
)


class TestQCAListModels:
    """Test qca_list_models function."""

    @pytest.mark.asyncio
    async def test_list_models_success(self, mock_env_vars, mock_http_responses):
        """Test successful models listing."""
        result = await qca_list_models()

        assert result["status"] == "success"
        assert "models" in result
        assert len(result["models"]) == 2
        assert result["models"][0]["id"] == "granite-3.3-8b-qiskit"

    @pytest.mark.asyncio
    async def test_list_models_empty_response(self, mock_env_vars):
        """Test handling of empty models response."""
        with patch(
            "qiskit_code_assistant_mcp_server.qca.make_qca_request"
        ) as mock_request:
            mock_request.return_value = {"data": []}

            result = await qca_list_models()

            assert result["status"] == "error"
            assert "No models retrieved" in result["message"]

    @pytest.mark.asyncio
    async def test_list_models_api_error(self, mock_env_vars):
        """Test handling of API error."""
        with patch(
            "qiskit_code_assistant_mcp_server.qca.make_qca_request"
        ) as mock_request:
            mock_request.return_value = {"error": "Authentication failed"}

            result = await qca_list_models()

            assert result["status"] == "error"
            assert result["message"] == "Authentication failed"

    @pytest.mark.asyncio
    async def test_list_models_exception(self, mock_env_vars):
        """Test handling of unexpected exceptions."""
        with patch(
            "qiskit_code_assistant_mcp_server.qca.make_qca_request"
        ) as mock_request:
            mock_request.side_effect = Exception("Network error")

            result = await qca_list_models()

            assert result["status"] == "error"
            assert "Failed to list models" in result["message"]


class TestQCAGetModel:
    """Test qca_get_model function."""

    @pytest.mark.asyncio
    async def test_get_model_success(self, mock_env_vars, mock_http_responses):
        """Test successful model retrieval."""
        result = await qca_get_model("granite-3.3-8b-qiskit")

        assert result["status"] == "success"
        assert "model" in result
        assert result["model"]["id"] == "granite-3.3-8b-qiskit"

    @pytest.mark.asyncio
    async def test_get_model_empty_id(self, mock_env_vars):
        """Test validation of empty model ID."""
        result = await qca_get_model("")

        assert result["status"] == "error"
        assert "model_id is required" in result["message"]

    @pytest.mark.asyncio
    async def test_get_model_whitespace_id(self, mock_env_vars):
        """Test validation of whitespace-only model ID."""
        result = await qca_get_model("   ")

        assert result["status"] == "error"
        assert "model_id is required" in result["message"]

    @pytest.mark.asyncio
    async def test_get_model_not_found(self, mock_env_vars):
        """Test handling of model not found."""
        with patch(
            "qiskit_code_assistant_mcp_server.qca.make_qca_request"
        ) as mock_request:
            mock_request.return_value = {"name": "Model X"}  # Missing 'id' field

            result = await qca_get_model("nonexistent-model")

            assert result["status"] == "error"
            assert "Model not retrieved" in result["message"]


class TestQCAGetCompletion:
    """Test qca_get_completion function."""

    @pytest.mark.asyncio
    async def test_get_completion_success(self, mock_env_vars, mock_http_responses):
        """Test successful completion generation."""
        prompt = "Create a quantum circuit with 2 qubits"
        result = await qca_get_completion(prompt)

        assert result["status"] == "success"
        assert "completion_id" in result
        assert "choices" in result
        assert len(result["choices"]) == 1
        assert "quantum circuit" in result["choices"][0]["text"].lower()

    @pytest.mark.asyncio
    async def test_get_completion_empty_prompt(self, mock_env_vars):
        """Test validation of empty prompt."""
        result = await qca_get_completion("")

        assert result["status"] == "error"
        assert "prompt is required" in result["message"]

    @pytest.mark.asyncio
    async def test_get_completion_whitespace_prompt(self, mock_env_vars):
        """Test validation of whitespace-only prompt."""
        result = await qca_get_completion("   ")

        assert result["status"] == "error"
        assert "prompt is required" in result["message"]

    @pytest.mark.asyncio
    async def test_get_completion_too_long_prompt(self, mock_env_vars):
        """Test validation of overly long prompt."""
        long_prompt = "x" * 10001  # Exceeds 10000 char limit
        result = await qca_get_completion(long_prompt)

        assert result["status"] == "error"
        assert "prompt is too long" in result["message"]

    @pytest.mark.asyncio
    async def test_get_completion_no_choices(self, mock_env_vars):
        """Test handling of response with no choices."""
        with patch(
            "qiskit_code_assistant_mcp_server.qca.make_qca_request"
        ) as mock_request:
            mock_request.return_value = {"id": "completion_123", "choices": []}

            result = await qca_get_completion("test prompt")

            assert result["status"] == "error"
            assert "No choices for this prompt" in result["message"]


class TestQCAGetRAGCompletion:
    """Test qca_get_rag_completion function."""

    @pytest.mark.asyncio
    async def test_get_rag_completion_success(self, mock_env_vars, mock_http_responses):
        """Test successful RAG completion generation."""
        prompt = "What is quantum entanglement?"
        result = await qca_get_rag_completion(prompt)

        assert result["status"] == "success"
        assert "completion_id" in result
        assert "choices" in result


class TestQCAAcceptModelDisclaimer:
    """Test qca_accept_model_disclaimer function."""

    @pytest.mark.asyncio
    async def test_accept_disclaimer_success(self, mock_env_vars, mock_http_responses):
        """Test successful disclaimer acceptance."""
        result = await qca_accept_model_disclaimer(
            "granite-3.3-8b-qiskit", "disclaimer_123"
        )

        assert result["status"] == "success"
        assert "result" in result

    @pytest.mark.asyncio
    async def test_accept_disclaimer_no_success_field(self, mock_env_vars):
        """Test handling of response without success field."""
        with patch(
            "qiskit_code_assistant_mcp_server.qca.make_qca_request"
        ) as mock_request:
            mock_request.return_value = {
                "acknowledged": True
            }  # Missing 'success' field

            result = await qca_accept_model_disclaimer(
                "granite-3.3-8b-qiskit", "disclaimer_123"
            )

            assert result["status"] == "error"
            assert "acceptance result" in result["message"]


class TestQCAAcceptCompletion:
    """Test qca_accept_completion function."""

    @pytest.mark.asyncio
    async def test_accept_completion_success(self, mock_env_vars, mock_http_responses):
        """Test successful completion acceptance."""
        result = await qca_accept_completion("completion_456")

        assert result["status"] == "success"
        assert "result" in result

    @pytest.mark.asyncio
    async def test_accept_completion_no_result(self, mock_env_vars):
        """Test handling of response without result field."""
        with patch(
            "qiskit_code_assistant_mcp_server.qca.make_qca_request"
        ) as mock_request:
            mock_request.return_value = {"status": "ok"}  # Missing 'result' field

            result = await qca_accept_completion("completion_456")

            assert result["status"] == "error"
            assert "No result for this completion acceptance" in result["message"]


class TestQCAServiceStatus:
    """Test qca_get_service_status function."""

    @pytest.mark.asyncio
    async def test_service_status_connected(self, mock_env_vars, mock_http_responses):
        """Test service status when connected."""
        result = await qca_get_service_status()

        assert "Qiskit Code Assistant Service Status" in result
        assert "connected" in result.lower()

    @pytest.mark.asyncio
    async def test_service_status_disconnected(self, mock_env_vars):
        """Test service status when disconnected."""
        with patch("qiskit_code_assistant_mcp_server.qca.qca_list_models") as mock_list:
            mock_list.return_value = {"status": "error", "message": "Connection failed"}

            result = await qca_get_service_status()

            assert "Qiskit Code Assistant Service Status" in result
            assert "connected" in result.lower()

    @pytest.mark.asyncio
    async def test_service_status_exception(self, mock_env_vars):
        """Test service status with exception."""
        with patch("qiskit_code_assistant_mcp_server.qca.qca_list_models") as mock_list:
            mock_list.side_effect = Exception("Network error")

            result = await qca_get_service_status()

            assert "Error" in result


# Assisted by watsonx Code Assistant
