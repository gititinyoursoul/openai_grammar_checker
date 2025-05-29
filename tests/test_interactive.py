import pytest
from unittest.mock import patch, MagicMock
from interactive import main, get_cli_input
from grammar_checker.config import DEFAULT_MODEL


def test_main_exits_on_empty_input(caplog):
    mongo_handler = MagicMock()

    with patch("interactive.get_cli_input", return_value=""):
        main(mongo_handler)

    # check for logger.warning
    assert "No sentence provided. Exiting program." in caplog.text
    # Nothing should be saved to the DB
    mongo_handler.save_record.assert_not_called()


def test_main_saves_record_to_db(monkeypatch):
    # Arrange
    test_sentence = "This is a test sentence."
    test_response = "This is a corrected sentence."

    mock_mongo_handler = MagicMock()
    mock_prompt_builder = MagicMock()
    mock_client = MagicMock()

    mock_checker = MagicMock()
    mock_checker.check_grammar.return_value = test_response
    mock_grammar_checker_cls = MagicMock(return_value=mock_checker)

    # Patch GrammarChecker class to return the mock instance
    monkeypatch.setattr("interactive.GrammarChecker", mock_grammar_checker_cls)
    # Patch get_cli_input to return the test sentence
    monkeypatch.setattr(
        "interactive.get_cli_input", lambda prompt, logger: test_sentence
    )
    
    # Act
    main(mock_mongo_handler, mock_prompt_builder, mock_client, DEFAULT_MODEL)

    #  Assert the GrammarChecker was created with the correct arguments
    mock_grammar_checker_cls.assert_called_once_with(
        mock_prompt_builder, test_sentence, DEFAULT_MODEL, mock_client
    )
    # Assert the grammar check was performed
    mock_checker.check_grammar.assert_called_once()
    # Assert the record was saved to MongoDB
    mock_mongo_handler.save_record.assert_called_once()
    saved_request = mock_mongo_handler.save_record.call_args[1]["request"]
    assert saved_request["sentence"] == test_sentence


@pytest.mark.parametrize("error_type", [EOFError, KeyboardInterrupt])
def test_get_cli_input_handles_errors(error_type):
    mock_logger = MagicMock()
    test_sentence = "This is a test sentence."

    with patch("builtins.input", side_effect=error_type):
        result = get_cli_input(test_sentence, mock_logger)
        assert result == ""
        mock_logger.error_type.called
