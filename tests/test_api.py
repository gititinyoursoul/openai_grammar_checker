from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from api import app, get_mongo_handler


# Test Fast API client setup
@asynccontextmanager
async def mock_lifespan(app: FastAPI):
    print("mock_lifespan")
    yield  # do nothing


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# @patch("api.logger")
@patch("api.PromptBuilder")
@patch("api.OpenAIClient")
@patch("api.GrammarChecker")
def test_check_grammar_success(
    #    mock_logger,
    mock_checker_class,
    mock_client_class,
    mock_prompt_builder_class,
):
    # Arrange
    test_sentence = "This are bad grammar."
    test_response = {"corrected": "This is bad grammar."}
    test_prompt_template = "This i a test template"

    mock_checker = MagicMock()
    mock_checker.check_grammar.return_value = test_response
    mock_checker_class.return_value = mock_checker

    # Mock Mongo handler
    mock_handler = MagicMock()
    app.dependency_overrides[get_mongo_handler] = lambda: mock_handler

    # Act
    response = client.post(
        "/check-grammar/",
        json={
            "sentence": test_sentence,
            "prompt_template": test_prompt_template,
            "model": "gpt-3.5-turbo",
        },
    )

    assert response.status_code == 200
    assert response.json() == test_response
    mock_prompt_builder_class.assert_called_once_with(test_prompt_template)
    mock_client_class.assert_called_once()
    mock_checker.check_grammar.assert_called_once()
    mock_handler.save_record.assert_called_once()

    app.dependency_overrides = {}


@patch("api.GrammarChecker", side_effect=Exception("Something went wrong"))
def test_check_grammar_failure(mock_checker):
    response = client.post("/check-grammar/", json={"sentence": "Hello world"})
    assert response.status_code == 500
    assert "Something went wrong" in response.text
