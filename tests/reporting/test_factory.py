import pytest
from unittest.mock import patch, MagicMock
from reporting.factory import ReportType, ReporterType
from reporting.csv_reporter import CSVReporter


@pytest.mark.parametrize(
    "report_type,report_fn,return_value",
    [
        ("sentences", "generate_sentence_report", "sentences_report"),
        ("mistakes", "generate_mistakes_report", "mistakes_report"),
    ],
)
def test_run_report(report_type, report_fn, return_value):
    test_data = {"test_id": "data"}
    mock_reporter = MagicMock()

    with patch(f"reporting.factory.{report_fn}", return_value=return_value) as mock_report:
        report = ReportType(report_type)
        result = report.run(test_data, mock_reporter)

        mock_report.assert_called_once_with(test_data, mock_reporter)
        assert result == return_value


def test_instantiate_invalid_report():
    with pytest.raises(ValueError, match="'invalid_report' is not a valid ReportType"):
        ReportType("invalid_report")


def test_build_reporter():
    reporter_type = ReporterType("csv")
    reporter = reporter_type.build()

    assert reporter_type == ReporterType.CSV
    assert isinstance(reporter, CSVReporter)


def test_instantiate_invalid_reporter():
    with pytest.raises(ValueError, match="'invalid_reporter' is not a valid ReporterType"):
        ReporterType("invalid_reporter")
