# tests/test_cli.py

from typer.testing import CliRunner
from cli import app
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from unittest.mock import patch, MagicMock

runner = CliRunner()


@patch("cli.uvicorn.run")
def test_run_api_calls_uvicorn(mock_uvicorn):
    result = runner.invoke(app, ["run-api", "--host", "0.0.0.0", "--port", "8080"])
    
    assert result.exit_code == 0
    mock_uvicorn.assert_called_once_with("api:app", host="0.0.0.0", port=8080, reload=True)
    
    
@patch("cli.interactive_main")
@patch("cli.MongoDBHandler")
def test_interactive_command(mock_db_handler_class, mock_main):
    mock_handler = MagicMock()
    mock_db_handler_class.return_value = mock_handler

    result = runner.invoke(app, ["interactive"])

    assert result.exit_code == 0
    mock_db_handler_class.assert_called_once_with(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    mock_main.assert_called_once_with(mongo_handler=mock_handler)
    
    
@patch("cli.benchmarks_main")
@patch("cli.MongoDBHandler")
def test_benchmarks_command(mock_db_handler_class, mock_main):
    mock_handler = MagicMock()
    mock_db_handler_class.return_value = mock_handler

    result = runner.invoke(app, [
        "benchmarks",
        "--test-cases-file", "my_test_cases.json",
        "--models=gpt-4", "--models=gpt-3.5-turbo", 
        "--prompt-template", "Correct: {test_sentence}",
        "--output-destination", "print"
    ])

    assert result.exit_code == 0
    mock_db_handler_class.assert_called_once()
    mock_main.assert_called_once_with(
        "my_test_cases.json",
        ["gpt-4", "gpt-3.5-turbo"],
        "print",
        "Correct: {test_sentence}",
        mock_handler
    )
