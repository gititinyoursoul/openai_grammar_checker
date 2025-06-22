import json
import pytest
from pydantic import BaseModel
from unittest.mock import patch, mock_open, MagicMock
from grammar_checker.utils import transform_results, save_to_file
from grammar_checker.utils import load_test_cases, save_test_results


class MockModel(BaseModel):
    value: str


def test_transform_results_valid():
    results = [
        {
            "request": MockModel(value="request1"),
            "response": MockModel(value="response1"),
            "benchmark_eval": {"score": 0.95},
        },
        {
            "request": MockModel(value="request2"),
            "response": MockModel(value="response2"),
            "benchmark_eval": {"score": 0.85},
        },
    ]

    output = transform_results(results)
    assert len(output) == 2
    assert output[0]["request"] == {"value": "request1"}
    assert output[1]["response"] == {"value": "response2"}


def test_transform_results_missing_key():
    results = [{"response": MockModel(value="response1"), "benchmark_eval": {"score": 0.95}}]

    with pytest.raises(KeyError):
        transform_results(results)


def test_transform_results_invalid_model():
    results = [
        {
            "request": {"value": "not a model"},
            "response": MockModel(value="response1"),
            "benchmark_eval": {"score": 0.95},
        }
    ]

    with pytest.raises(AttributeError):
        transform_results(results)


def test_transform_results_empty():
    results = []
    output = transform_results(results)
    assert output == []


def test_load_test_cases_valid_json(tmp_path):
    # Arrange
    test_data = [{"input": "This is a test.", "benchmark_eval": "This is a test."}]
    file_path = tmp_path / "test_cases.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f)
    # Act
    result = load_test_cases(str(file_path))
    # Assert
    assert result == test_data


def test_load_test_cases_file_not_found():
    # Arrange
    fake_path = "non_existent_file.json"
    # Act & Assert
    with pytest.raises(FileNotFoundError) as excinfo:
        load_test_cases(fake_path)
    assert "Test cases file not found" in str(excinfo.value)


def test_load_test_cases_invalid_json(tmp_path):
    # Arrange
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("{invalid json}")
    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        load_test_cases(str(file_path))
    assert "Invalid JSON format" in str(excinfo.value)


def test_save_to_file_success():
    mock_writer = MagicMock()
    mock_open_obj = mock_open()

    with patch("builtins.open", mock_open_obj):
        save_to_file("dummy.json", {"foo": "bar"}, writer=mock_writer)

    mock_writer.assert_called_once()
    mock_open_obj.assert_called_once_with("dummy.json", "w", encoding="utf-8")


def test_save_to_file_writer_exception(caplog):
    def failing_writer(data, file_obj, indent):
        raise ValueError("Mocked writer failure")

    with patch("builtins.open", mock_open()), caplog.at_level("ERROR"):
        with pytest.raises(ValueError, match="Mocked writer failure"):
            save_to_file("dummy.json", {"foo": "bar"}, writer=failing_writer)

    assert "Error saving test results" in caplog.text


def test_save_to_file_open_exception(caplog):
    with patch("builtins.open", side_effect=PermissionError("Permission denied")), caplog.at_level("ERROR"):
        with pytest.raises(PermissionError):
            save_to_file("dummy.json", {"foo": "bar"})

    assert "Error saving test results" in caplog.text
    assert "Permission denied" in caplog.text


def test_save_test_results_success():
    dummy_results = [{"some": "data"}]
    transformed_data = [{"transformed": "yes"}]

    with (
        patch("grammar_checker.utils.transform_results", return_value=transformed_data) as mock_transform,
        patch("grammar_checker.utils.save_to_file") as mock_save,
    ):

        save_test_results("dummy.json", dummy_results)

        mock_transform.assert_called_once_with(dummy_results)
        mock_save.assert_called_once_with("dummy.json", transformed_data)


def test_save_test_results_transform_raises():
    dummy_results = [{"bad": "data"}]

    with (
        patch("grammar_checker.utils.transform_results", side_effect=ValueError("bad input")),
        patch("grammar_checker.utils.save_to_file") as mock_save,
    ):

        with pytest.raises(ValueError, match="bad input"):
            save_test_results("file.json", dummy_results)

        mock_save.assert_not_called()


def test_save_test_results_save_raises():
    dummy_results = [{"some": "data"}]
    transformed_data = [{"transformed": "yes"}]

    with (
        patch("grammar_checker.utils.transform_results", return_value=transformed_data),
        patch("grammar_checker.utils.save_to_file", side_effect=IOError("disk full")),
    ):

        with pytest.raises(IOError, match="disk full"):
            save_test_results("file.json", dummy_results)


def test_save_test_results_integration(tmp_path):
    # Arrange
    results = [
        {
            "request": MockModel(value="test_request"),
            "response": MockModel(value="test_response"),
            "benchmark_eval": "eval",
        }
    ]
    expected_output = [
        {"request": {"value": "test_request"}, "response": {"value": "test_response"}, "benchmark_eval": "eval"}
    ]
    file_path = tmp_path / "results.json"
    # Act
    save_test_results(str(file_path), results)
    # Assert
    assert file_path.exists()
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == expected_output
