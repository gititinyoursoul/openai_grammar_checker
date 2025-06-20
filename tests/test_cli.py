# tests/test_cli.py
from cli import app
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
import logging
from pathlib import Path
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from grammar_checker.config import TEST_CASES_FILE, DEFAULT_MODEL, DEFAULT_PROMPT_TEMPLATE
from reporting.factory import ReporterType, ReportType

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


## Benchmark Command ##
@patch("cli.benchmark_main")
@patch("cli.MongoDBHandler")
def test_benchmark_default_inputs(mock_db_handler_class, mock_main):
    mock_handler = MagicMock()
    mock_db_handler_class.return_value = mock_handler

    result = runner.invoke(
        app,
        [
            "benchmark",
        ],
    )

    assert result.exit_code == 0
    mock_db_handler_class.assert_called_once()
    mock_main.assert_called_once_with(
        TEST_CASES_FILE, [DEFAULT_MODEL], "save_to_db", [DEFAULT_PROMPT_TEMPLATE], mock_handler
    )


@patch("cli.benchmark_main")
@patch("cli.MongoDBHandler")
def test_benchmark_list_inputs(mock_db_handler_class, mock_main):
    mock_handler = MagicMock()
    mock_db_handler_class.return_value = mock_handler

    result = runner.invoke(
        app,
        [
            "benchmark",
            "--test-cases",
            "my_test_cases.json",
            "--models=gpt-4",
            "--models=gpt-3.5-turbo",
            "--prompt-version=Prompt V1: {test_sentence}",
            "--prompt-version=Prompt V2: {test_sentence}",
            "--save-to",
            "print",
        ],
    )

    assert result.exit_code == 0
    mock_db_handler_class.assert_called_once()
    mock_main.assert_called_once_with(
        Path("my_test_cases.json"), ["gpt-4", "gpt-3.5-turbo"], "print", ["Prompt V1: {test_sentence}", "Prompt V2: {test_sentence}"], mock_handler
    )


## Report Command ##
@patch("cli.run_reports")
def test_report_valid_single_input(mock_run_reports):
    result = runner.invoke(app, ["report", "test_uuid", "--reports", "sentences", "--reporter", "csv"])

    assert result.exit_code == 0
    mock_run_reports.assert_called_once_with(["test_uuid"], [ReportType.SENTENCES], ReporterType.CSV)


@patch("cli.run_reports")
def test_report_list_inputs(mock_run_reports):
    result = runner.invoke(
        app, ["report", "uuid-1", "uuid-2", "--reports", "sentences", "--reports", "mistakes", "--reporter", "csv"]
    )

    assert result.exit_code == 0
    mock_run_reports.assert_called_once_with(
        ["uuid-1", "uuid-2"], [ReportType.SENTENCES, ReportType.MISTAKES], ReporterType.CSV
    )


@patch("cli.run_reports")
def test_report_debug_logging(mock_run_reports, caplog):
    with caplog.at_level(logging.DEBUG):
        runner.invoke(app, ["report", "uuid-1234", "--reports", "sentences", "--reporter", "csv"])
        assert "Arguments received:" in caplog.text
        assert "uuid-1234" in caplog.text


def test_report_missing_run_ids():
    result = runner.invoke(app, ["report", "--reports", "sentences", "--reporter", "csv"])

    assert result.exit_code == 2  # Usage error
    assert "Error" in result.output
    assert "RUN_IDS" in result.output


@patch("cli.run_reports")
def test_report_default_reports_used(mock_run_reports):
    result = runner.invoke(app, ["report", "uuid-1234", "--reporter", "csv"])
    assert result.exit_code == 0
    args = mock_run_reports.call_args[0]
    run_ids, reports, reporter_type = args
    assert run_ids == ["uuid-1234"]
    assert isinstance(reports, list)
    assert len(reports) == len(ReportType.__members__)
    assert all([isinstance(report, ReportType) for report in reports])
