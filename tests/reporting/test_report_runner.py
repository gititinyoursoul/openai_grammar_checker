from pathlib import Path
import pytest
from unittest.mock import patch
from reporting.report_runner import run_reports
from reporting.csv_reporter import CSVReporter
from reporting.factory import ReportType, ReporterType


test_data = [
    {
        "request": {"input": "What is AI?", "model": "gpt-4", "prompt_version": "v1.2"},
        "response": {
            "mistakes": [{"type": "MockMistake", "original": "test_orginial", "corrected": "test_corrected"}],
            "corrected_sentence": "AI is the simulation of human intelligence in machines.",
        },
        "benchmark_eval": {
            "run_id": "run_1",
            "test_id": "test_001",
            "mistakes": [{"type": "MockMistake", "original": "test_orginial", "corrected": "test_corrected"}],
            "corrected_sentence": "AI simulates human intelligence in machines.",
        },
        "timestamp": "2024-01-01T00:00:00Z",
    },
    {
        "request": {"input": "Explain quantum computing.", "model": "gpt-4", "prompt_version": "v1.2"},
        "response": {
            "mistakes": [{"type": "MockMistake", "original": "test_orginial", "corrected": "test_corrected"}],
            "corrected_sentence": "Quantum computing uses qubits to perform complex calculations.",
        },
        "benchmark_eval": {
            "run_id": "run_2",
            "test_id": "test_002",
            "mistakes": [{"type": "MockMistake", "original": "test_orginial", "corrected": "test_corrected"}],
            "corrected_sentence": "Quantum computing is a form of computation using quantum-mechanical phenomena.",
        },
        "timestamp": "2024-01-02T00:00:00Z",
    },
]


@pytest.mark.parametrize("run_ids", [["run_1"], ["run_1", "run_2"]], ids=["single_run", "multi_run"])
@pytest.mark.parametrize("reports", [[ReportType["SENTENCES"]], list(ReportType)], ids=["single_report", "all_reports"])
def test_run_reports_CSVReporter_integration(
    run_ids: list[str], reports: list[ReportType], tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    reporter_type = ReporterType.CSV

    with (
        patch("reporting.report_runner.query_benchmark_data", return_value=test_data),
        patch.object(reporter_type, "build", return_value=CSVReporter(tmp_path)),
    ):

        run_reports(run_ids, reports, reporter_type)

        # Check that CSV file(s) were written in tmp_path
        csv_files = list(tmp_path.glob("*.csv"))
        assert csv_files, "No CSV files were written"
        for report in reports:
            assert any([f"{report.value}_details" in file.name for file in csv_files])
            assert any([f"{report.value}_summary" in file.name for file in csv_files])


@pytest.mark.parametrize("run_ids", [["run_1"]], ids=["single_run"])
@pytest.mark.parametrize("reports", [list(ReportType)], ids=["all_reports"])
@pytest.mark.parametrize("empty_data", [[]], ids=["empty_list"] )
def test_run_reports_empty_data(
    run_ids: list[str], reports: list[ReportType], empty_data: list, tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    reporter_type = ReporterType.CSV

    with (
        patch("reporting.report_runner.query_benchmark_data", return_value=empty_data),
        patch.object(reporter_type, "build", return_value=CSVReporter(tmp_path)),
    ):

        run_reports(run_ids, reports, reporter_type)

        # Check that CSV file(s) were written in tmp_path
        csv_files = list(tmp_path.glob("*.csv"))
        assert not csv_files, "CSV files were written"
        assert "No benchmark data found" in caplog.text
