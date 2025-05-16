import json
import tempfile
import pytest
from grammar_checker.utils import load_test_cases
from grammar_checker.utils import save_test_results


def test_load_test_cases_valid_json(tmp_path):
    # Arrange
    test_data = [{"input": "This is a test.", "expected": "This is a test."}]
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


def test_save_test_results_creates_file_and_writes_json(tmp_path):
    # Arrange
    results = [{"input": "Hello", "output": "Hello"}]
    file_path = tmp_path / "results.json"
    # Act
    save_test_results(str(file_path), results)
    # Assert
    assert file_path.exists()
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == results


def test_save_test_results_overwrites_existing_file(tmp_path):
    # Arrange
    initial_data = [{"input": "A", "output": "A"}]
    new_data = [{"input": "B", "output": "B"}]
    file_path = tmp_path / "results.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(initial_data, f)
    # Act
    save_test_results(str(file_path), new_data)
    # Assert
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == new_data


def test_save_test_results_raises_on_invalid_path(tmp_path):
    # Arrange
    results = [{"input": "X", "output": "Y"}]
    # Use an invalid path (directory as file)
    dir_path = tmp_path / "adir"
    dir_path.mkdir()
    file_path = dir_path  # Intentionally passing a directory
    # Act & Assert
    with pytest.raises(Exception):
        save_test_results(str(file_path), results)
