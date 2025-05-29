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


@patch("api.PromptBuilder")
@patch("api.OpenAIClient")
@patch("api.GrammarChecker")
def test_check_grammar_success(
    mock_checker_class,
    mock_client_class,
    mock_prompt_builder_class,
):
    # Arrange
    test_request = MagicMock()
    test_request.sentence = "This are bad grammar."
    test_request.prompt_version = "This is a test template"
    test_request.model = "gpt-3.5-turbo"
    test_request.mode = "api"

    test_response = {"corrected": "This is bad grammar."}
    

    mock_checker = MagicMock()
    mock_checker.check_grammar.return_value = test_response
    mock_checker_class.return_value = mock_checker

    # Mock Mongo handler
    mock_handler = MagicMock()
    app.dependency_overrides[get_mongo_handler] = lambda: mock_handler

    print(test_request)

    # Act
    response = client.post(
        "/check-grammar/",
        json={
            "sentence": test_request.sentence,
            "prompt_version": test_request.prompt_version,
            "model": test_request.model,
            "mode": test_request.mode
        },
    )

    assert response.status_code == 200
    assert response.json() == test_response
    mock_prompt_builder_class.assert_called_once_with(test_request.prompt_version)
    mock_client_class.assert_called_once()
    mock_checker.check_grammar.assert_called_once()
    mock_handler.save_record.assert_called_once()

    app.dependency_overrides = {}


@patch("api.GrammarChecker", side_effect=Exception("Something went wrong"))
def test_check_grammar_failure(mock_checker):
    response = client.post("/check-grammar/", json={"sentence": "Hello world"})
    assert response.status_code == 500
    assert "Something went wrong" in response.text
