import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch
from api import app, get_mongo_handler
from models.response import GrammarResponse


# Test Fast API client setup
@asynccontextmanager
async def mock_lifespan(app: FastAPI):
    print("mock_lifespan")
    yield  # do nothing


client = TestClient(app)


@pytest.fixture
def valid_grammar_response():
    return GrammarResponse(
        input="This are bad grammar.",
        mistakes=[{"type": "OtherMistake", "original": "are", "corrected": "is"}],
        corrected_sentence="This is bad grammar.",
    )


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("api.PromptBuilder")
@patch("api.OpenAIClient")
@patch("api.GrammarChecker")
def test_check_grammar_success(
    mock_checker_class, mock_client_class, mock_prompt_builder_class, valid_grammar_response
):
    # Arrange
    mock_checker = MagicMock()
    mock_checker.check_grammar.return_value = valid_grammar_response
    mock_checker_class.return_value = mock_checker

    # Mock Mongo handler
    mock_handler = MagicMock()
    app.dependency_overrides[get_mongo_handler] = lambda: mock_handler

    # Act
    response = client.post(
        "/check-grammar/",
        json={
            "sentence": "This is a test sentence.",
            "prompt_version": "default_prompt",
            "model": "gpt-3.5-turbo",
            "mode": "api",
        },
    )

    # Assert
    assert response.status_code == 200
    mock_prompt_builder_class.assert_called_once_with("default_prompt")
    mock_client_class.assert_called_once()
    mock_checker.check_grammar.assert_called_once()
    mock_handler.save_record.assert_called_once()

    app.dependency_overrides = {}


def test_check_grammar_validation_error_from_request_sentence():
    # Invalid: 'sentence' is too short (min_length=1)
    response = client.post("/check-grammar/", json={"sentence": ""})
    assert response.status_code == 422
    assert "string_too_short" in response.text


def test_check_grammar_validation_error_from_request_mode():
    # Invalid: 'mode' is not one of the allowed values
    response = client.post("/check-grammar/", json={"sentence": "Hello world", "mode": "invalid_mode"})
    assert response.status_code == 422
    assert "literal_error" in response.text


@patch("api.GrammarChecker", side_effect=Exception("Something went wrong"))
def test_check_grammar_failure(mock_checker):
    response = client.post("/check-grammar/", json={"sentence": "Hello world"})
    assert response.status_code == 500
    assert "Something went wrong" in response.text


@patch("api.PromptBuilder")
@patch("api.OpenAIClient")
@patch("api.GrammarChecker")
def test_check_grammar_response_success(
    mock_checker_class, mock_client_class, mock_prompt_builder_class, valid_grammar_response
):

    mock_checker = MagicMock()
    mock_checker.check_grammar.return_value = valid_grammar_response
    mock_checker_class.return_value = mock_checker

    # Mock Mongo handler
    mock_handler = MagicMock()
    app.dependency_overrides[get_mongo_handler] = lambda: mock_handler

    response = client.post(
        "/check-grammar/",
        json={
            "sentence": "This is a test sentence.",
            "prompt_version": "default_prompt",
            "model": "gpt-3.5-turbo",
            "mode": "api",
        },
    )

    assert response.status_code == 200
    assert "input" in response.json()
    assert "mistakes" in response.json()
    assert "corrected_sentence" in response.json()
