import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("api.PromptBuilder")
@patch("api.OpenAIClient")
@patch("api.GrammarChecker")
@patch("api.db")  # Patch the MongoDBHandler instance directly
def test_check_grammar_success(mock_db, mock_checker_class, mock_client_class, mock_prompt_builder_class):
    # Arrange
    test_sentence = "This are bad grammar."
    test_response = {"corrected": "This is bad grammar."}

    mock_checker = MagicMock()
    mock_checker.check_grammar.return_value = test_response
    mock_checker_class.return_value = mock_checker

    # Act
    response = client.post(
        "/check-grammar/",
        json={
            "sentence": test_sentence,
            "prompt_template": "Correct the grammar of the following sentence: {test_sentence}",
            "model": "gpt-3.5-turbo",
        },
    )
    assert response.status_code == 200
    assert response.json() == test_response
    mock_checker.check_grammar.assert_called_once()
    mock_db.save_record.assert_called_once()


@patch("api.GrammarChecker", side_effect=Exception("Something went wrong"))
def test_check_grammar_failure(mock_checker):
    response = client.post("/check-grammar/", json={"sentence": "Hello world"})
    assert response.status_code == 500
    assert "Something went wrong" in response.text
