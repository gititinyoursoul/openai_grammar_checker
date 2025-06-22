import pytest
from unittest.mock import MagicMock
from grammar_checker.grammar_checker import GrammarChecker
from models.response import GrammarResponse


@pytest.fixture
def mock_prompt_builder():
    mock_prompt_builder = MagicMock()
    test_sentence = "This is an test sentence."
    mock_prompt_builder.build_prompt.return_value = f"Correct this sentence: {test_sentence}"
    mock_prompt_builder.template_path = "template.txt"
    return mock_prompt_builder


@pytest.fixture
def mock_client():
    mock_client = MagicMock()
    mock_client.get_model_response.return_value = {
        "input": "This is an test sentence.",
        "mistakes": [{"type": "OtherMistake", "original": "an", "corrected": "a"}],
        "corrected_sentence": "This is a test sentence.",
    }
    return mock_client


def test_grammar_checker_initialization(mock_prompt_builder, mock_client):
    checker = GrammarChecker(mock_prompt_builder, "test_sentence", "gpt-3", mock_client)
    
    assert checker.prompt_builder == mock_prompt_builder
    assert checker.sentence == "test_sentence"
    assert checker.model == "gpt-3"
    assert checker.client == mock_client


def test_check_grammar_success(mock_prompt_builder, mock_client):
    test_sentence = "This is an test sentence."
    test_checker = GrammarChecker(mock_prompt_builder, test_sentence, "gpt-3", mock_client)

    response = test_checker.check_grammar()

    mock_prompt_builder.build_prompt.assert_called_once_with(test_sentence)
    mock_client.get_model_response.assert_called_once_with("gpt-3", f"Correct this sentence: {test_sentence}")
    assert isinstance(response, GrammarResponse)


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
