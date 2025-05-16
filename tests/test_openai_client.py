import os
import pytest
import json
from unittest.mock import patch, MagicMock
from grammar_checker.openai_client import OpenAIClient

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

def test_init_sets_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "abc123")
    with patch("grammar_checker.openai_client.OpenAI") as mock_openai:
        client = OpenAIClient()
        assert client.api_key == "abc123"
        mock_openai.assert_called_once_with(api_key="abc123")

def test_init_raises_if_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        OpenAIClient()

def test_get_model_response_returns_json(monkeypatch):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({"result": "ok"})
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("grammar_checker.openai_client.OpenAI") as mock_openai:
        mock_openai.return_value = mock_client
        client = OpenAIClient()
        result = client.get_model_response("gpt-3", "test prompt", "template.txt", "sentence")
        assert result == {"result": "ok"}
        mock_client.chat.completions.create.assert_called_once()

def test_get_model_response_invalid_json(monkeypatch):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "not a json"
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("grammar_checker.openai_client.OpenAI") as mock_openai:
        mock_openai.return_value = mock_client
        client = OpenAIClient()
        with pytest.raises(json.JSONDecodeError):
            client.get_model_response("gpt-3", "test prompt", "template.txt", "sentence")

def test_get_model_response_raises(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("fail")

    with patch("grammar_checker.openai_client.OpenAI") as mock_openai:
        mock_openai.return_value = mock_client
        client = OpenAIClient()
        with pytest.raises(Exception):
            client.get_model_response("gpt-3", "test prompt", "template.txt", "sentence")