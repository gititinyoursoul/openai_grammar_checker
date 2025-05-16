import pytest
import mongomock
import logging
from bson import ObjectId
from grammar_checker.db import MongoDBHandler


@pytest.fixture
def mock_mongo_handler(monkeypatch):
    # Create a mongomock client and patch MongoClient
    mock_client = mongomock.MongoClient()
    monkeypatch.setattr("grammar_checker.db.MongoClient", lambda uri: mock_client)

    # Create handler using mock
    handler = MongoDBHandler("mock://localhost", "test_db", "test_collection")
    return handler


def test_save_record_success(mock_mongo_handler):
    input_data = "He go to school."
    model_response = {"corrected_sentence": "He goes to school."}

    record_id = mock_mongo_handler.save_record(input_data, model_response)
    assert record_id is not None

    record = mock_mongo_handler.collection.find_one({"_id": record_id})
    assert record["input"] == input_data
    assert record["response"] == model_response
    assert "timestamp" in record


def test_save_record_with_metadata(mock_mongo_handler):
    input_data = "She don't like apples."
    model_response = {"corrected_sentence": "She doesn't like apples."}
    metadata = {"model": "gpt-4", "mode": "test"}

    record_id = mock_mongo_handler.save_record(input_data, model_response, metadata=metadata)
    record = mock_mongo_handler.collection.find_one({"_id": record_id})

    assert "metadata" in record
    assert record["metadata"]["model"] == "gpt-4"


def test_save_record_failure(monkeypatch, caplog, mock_mongo_handler):
    def mock_insert_one_fail(*args, **kwargs):
        raise Exception("DB error")
    
    #mock_mongo_handler.collection.insert_one.side_effect = Exception("DB error")
    monkeypatch.setattr(mock_mongo_handler, "save_record", mock_insert_one_fail)
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception) as excinfo:
            mock_mongo_handler.save_record("input", "response")
    
    assert "DB error" in str(excinfo.value)
    assert "Failed to save record" in caplog.text


def test_delete_record_success(mock_mongo_handler):
    # insert a dummy record to delete
    inserted_id = mock_mongo_handler.save_record("test_input", "test_response")
    # delete the record
    mock_mongo_handler.delete_record(inserted_id)
    # check if the record is deleted
    deleted_record = mock_mongo_handler.collection.find_one({"_id": inserted_id})
    assert deleted_record is None


# caplog is a pytest fixture that captures log messages
def test_delete_record_not_found(mock_mongo_handler, caplog):
    fake_id = ObjectId()  # generates a unique MongoDB-style ID
    # check if the log contains the warning
    with caplog.at_level(logging.WARNING):
        mock_mongo_handler.delete_record(fake_id)
    assert "No record found" in caplog.text


def test_delete_record_failure(monkeypatch, caplog, mock_mongo_handler):
    # Simulate a failure in delete_one using monkeypatch
    def mock_delete_one_fail(*args, **kwargs):
        raise Exception("Delete error")
    
    # Apply monkeypatch to simulate failure
    monkeypatch.setattr(mock_mongo_handler.collection, "delete_one", mock_delete_one_fail)
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception) as excinfo:
            mock_mongo_handler.delete_record(ObjectId())
    
    assert "Delete error" in str(excinfo.value)
    assert "Failed to delete record" in caplog.text
