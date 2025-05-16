import pytest
from unittest.mock import MagicMock, patch
from grammar_checker.grammar_checker import GrammarChecker

@pytest.fixture
def mock_prompt_builder():
    mock = MagicMock()
    mock.build_prompt.return_value = "Correct this sentence: test"
    mock.template_path = "template.txt"
    return mock

@pytest.fixture
def mock_client():
    return MagicMock()

def test_grammar_checker_initialization(mock_prompt_builder, mock_client):
    checker = GrammarChecker(mock_prompt_builder, "test", "gpt-3", mock_client)
    assert checker.prompt_builder == mock_prompt_builder
    assert checker.sentence == "test"
    assert checker.model == "gpt-3"
    assert checker.client == mock_client

def test_check_grammar_success(mock_prompt_builder, mock_client):
    mock_client.get_model_response.return_value = "Corrected sentence."
    checker = GrammarChecker(mock_prompt_builder, "test", "gpt-3", mock_client)
    result = checker.check_grammar()
    mock_prompt_builder.build_prompt.assert_called_once_with("test")
    mock_client.get_model_response.assert_called_once_with(
        "gpt-3", "Correct this sentence: test", "template.txt", "test"
    )
    assert result == "Corrected sentence."

def test_check_grammar_empty_response_raises(mock_prompt_builder, mock_client):
    mock_client.get_model_response.return_value = ""
    checker = GrammarChecker(mock_prompt_builder, "test", "gpt-3", mock_client)
    with pytest.raises(ValueError):
        checker.check_grammar()

def test_check_grammar_exception_propagates(mock_prompt_builder, mock_client):
    mock_client.get_model_response.side_effect = Exception("API error")
    checker = GrammarChecker(mock_prompt_builder, "test", "gpt-3", mock_client)
    with pytest.raises(Exception) as excinfo:
        checker.check_grammar()
    assert "API error" in str(excinfo.value)