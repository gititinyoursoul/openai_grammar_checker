import logging
from datetime import datetime
import pandas as pd
import pytest
from unittest.mock import patch
from reporting.csv_reporter import CSVReporter


@patch("reporting.base_reporter.dt")
def test_extension_override(mock_dt, tmp_path):
    mock_dt.now.return_value = datetime(2024, 1, 1, 12, 30, 45)

    reporter = CSVReporter(output_dir=tmp_path)
    file_path = reporter._make_file_path("test_file")

    assert reporter.extension == "csv"
    assert file_path.name.endswith(".csv")


@patch("reporting.base_reporter.dt")
def test_report_data_is_df(mock_dt, tmp_path):
    mock_dt.now.return_value = datetime(2024, 1, 1, 12, 30, 45)
    test_df = pd.DataFrame(data={"col1": [1, 2], "col2": ["a", "b"]})
    report_dir = tmp_path / "reports"

    reporter = CSVReporter(report_dir)
    reporter.report("test_file", test_df)

    # Verify file exsists
    expected_file_path = report_dir / f"20240101123045_test_file.csv"
    assert expected_file_path.exists()

    # Read file and verify contents match
    written_df = pd.read_csv(expected_file_path)
    pd.testing.assert_frame_equal(written_df, test_df)


def test_report_data_not_df(tmp_path, caplog):
    test_data = "not_df"
    expected_error_msg = "cannot handle data"
    report_dir = tmp_path / "reports"
    reporter = CSVReporter(report_dir)

    with (
        pytest.raises(TypeError, match=expected_error_msg),
        caplog.at_level(logging.ERROR),
    ):
        reporter.report("test_file", test_data)
        # Log message should be present
        assert expected_error_msg in caplog.text

    # No CSV file should be created
    assert not any(report_dir.glob("*.csv"))
