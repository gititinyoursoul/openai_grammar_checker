import tempfile
from typing import Any
from unittest.mock import patch
from pathlib import Path
from datetime import datetime
from reporting.base_reporter import BenchmarkReporter


class DummyReporter(BenchmarkReporter):
    def report(self, file_name: str, data: Any):
        return f"Reported {file_name} with {data}"


def test_output_dir_is_created():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "test_reports"
        assert not output_path.exists()

        DummyReporter(output_dir=output_path)
        assert output_path.exists()
        assert output_path.is_dir()


@patch("reporting.base_reporter.dt")
def test_make_file_path_format(mock_dt):
    with tempfile.TemporaryDirectory() as tmp_dir:
        mock_dt.now.return_value = datetime(2024, 1, 1, 12, 30, 45)
        output_path = Path(tmp_dir) / "test_reports"
        reporter_instance = DummyReporter(output_dir=output_path)

        file_path = reporter_instance._make_file_path(file_name="test_file")

        expected_prefix = "20240101123045_test_file.txt"

        assert file_path.name == expected_prefix
        assert file_path.parent == output_path


@patch("reporting.base_reporter.dt")
def test_default_extension_is_txt(mock_dt):
    with tempfile.TemporaryDirectory() as tmp_dir:
        mock_dt.now.return_value = datetime(2024, 1, 1, 12, 30, 45)
        reporter = DummyReporter(Path(tmp_dir))
        file_path = reporter._make_file_path("test")

        assert file_path.name.endswith(".txt")
