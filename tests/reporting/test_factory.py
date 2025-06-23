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


def test_run_invalid_report(caplog):
    test_data = {"test_id": "data"}
    mock_reporter = MagicMock()

    class FakeReportType(str):
        def run(self, data, reporter):
            return ReportType.__dict__["run"](self, data, reporter)

    fake_report = FakeReportType("invalid_report")

    with pytest.raises(ValueError, match="Unknown report type: invalid_report"):
        fake_report.run(test_data, mock_reporter)

    assert "Unknown report type" in caplog.text


def test_build_reporter():
    reporter_type = ReporterType("csv")
    reporter = reporter_type.build()

    assert reporter_type == ReporterType.CSV
    assert isinstance(reporter, CSVReporter)


def test_build_invalid_reporter(caplog):

    class FakeReporterType(str):
        def build(self):
            return ReporterType.__dict__["build"](self)

    fake_reporter = FakeReporterType("invalid_reporter")

    with pytest.raises(ValueError, match="Unknown reporter type"):
        fake_reporter.build()

    assert "Unknown reporter type" in caplog.text
