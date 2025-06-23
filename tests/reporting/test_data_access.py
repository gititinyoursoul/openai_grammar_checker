import mongomock
import pytest
from reporting.data_access import query_benchmark_data


@pytest.fixture()
def mock_mongo(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["test_db"]
    mock_collection = mock_db["test_collection"]

    # insert test data
    mock_collection.insert_many(
        [
            {
                "request": "Question A",
                "response": "Answer A",
                "benchmark_eval": {"run_id": "run_1"},
                "timestamp": "2024-01-01T00:00:00Z",
                "_id": "should_be_excluded",
            },
            {
                "request": "Question B",
                "response": "Answer B",
                "benchmark_eval": {"run_id": "run_2"},
                "timestamp": "2024-01-02T00:00:00Z",
            },
        ]
    )

    # Monkeypatch the config values used in your query function
    monkeypatch.setattr("reporting.data_access.MONGO_URI", "mongodb://localhost:27017")  # still needed but unused
    monkeypatch.setattr("reporting.data_access.MONGO_DB", "test_db")
    monkeypatch.setattr("reporting.data_access.MONGO_COLLECTION", "test_collection")

    monkeypatch.setattr("reporting.data_access.MongoClient", lambda *args, **kwargs: mock_client)

    return mock_collection


def test_single_run_id_returns_data(mock_mongo):
    result = query_benchmark_data(["run_1"])

    assert len(result) == 1
    doc = result[0]
    assert doc["benchmark_eval"]["run_id"] == "run_1"


def test_multiple_run_ids_return_data(mock_mongo):
    result = query_benchmark_data(["run_1", "run_2"])

    assert len(result) == 2
    doc = result[0]
    assert doc["benchmark_eval"]["run_id"] == "run_1"
    doc = result[1]
    assert doc["benchmark_eval"]["run_id"] == "run_2"


def test_returned_dicts_only_have_expected_keys(mock_mongo):
    result = query_benchmark_data(["run_1"])

    doc = result[0]
    assert "request" in doc
    assert "response" in doc
    assert "timestamp" in doc
    assert "_id" not in doc


def test_empty_run_ids_return_empty_list(mock_mongo):
    result = query_benchmark_data([])
    assert len(result) == 0


def test_no_matching_run_ids_return_empty_list(mock_mongo):
    result = query_benchmark_data(["missing_run"])
    assert len(result) == 0
