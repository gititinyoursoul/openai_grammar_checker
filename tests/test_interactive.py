import pytest
from unittest.mock import patch, MagicMock
from interactive import main, get_cli_input


def test_main_exits_on_empty_input(caplog):
    mongo_handler = MagicMock()

    with patch("interactive.get_cli_input", return_value=""):
        main(mongo_handler)

    # check for logger.warning
    assert "No sentence provided. Exiting program." in caplog.text
    # Nothing should be saved to the DB
    mongo_handler.save_record.assert_not_called()
    

def test_main_saves_record_to_db(caplog):
    mongo_handler = MagicMock()
    test_sentence = "This is a test sentence."
    test_response = "This is a corrected sentence."

    with patch("interactive.get_cli_input", return_value=test_sentence), \
         patch("interactive.PromptBuilder") as MockPromptBuilder, \
         patch("interactive.OpenAIClient") as MockClient, \
         patch("interactive.GrammarChecker") as MockChecker:
            
            mock_checker = MockChecker.return_value
            mock_checker.check_grammar.return_value = test_response      
            
            main(mongo_handler)
           
            # control flow
            MockPromptBuilder.assert_called_once()
            MockClient.assert_called_once()
            MockChecker.assert_called_once_with(
                MockPromptBuilder.return_value,
                test_sentence,
                "gpt-3.5-turbo",
                MockClient.return_value
            )
            mock_checker.check_grammar.assert_called_once()
            mongo_handler.save_record.assert_called_once_with(
                input_data=test_sentence,
                model_response=test_response,
                metadata={"model": "gpt-3.5-turbo", "mode": "interactive.py"}
            )


@pytest.mark.parametrize("error_type", [EOFError, KeyboardInterrupt]) 
def test_get_cli_input_handles_errors(error_type):
    mock_logger = MagicMock()
    test_sentence = "This is a test sentence."

    with patch("builtins.input", side_effect=error_type):
        result = get_cli_input(test_sentence, mock_logger)
        assert result == ""
        mock_logger.error_type.called
