import pytest
import mongomock
from unittest.mock import MagicMock
import logging
from bson import ObjectId
from grammar_checker.db import MongoDBHandler
from models.request import GrammarRequest
from models.response import GrammarResponse


@pytest.fixture
def mock_mongo_handler(monkeypatch):
    # Create a mongomock client and patch MongoClient
    mock_client = mongomock.MongoClient()
    monkeypatch.setattr("grammar_checker.db.MongoClient", lambda uri: mock_client)

    # Create handler using mock
    handler = MongoDBHandler("mock_uri", "test_db", "test_collection")
    return handler


def test_connect(mock_mongo_handler):
    mock_mongo_handler.connect()

    assert isinstance(mock_mongo_handler.client, mongomock.MongoClient)
    assert mock_mongo_handler.db == mock_mongo_handler.client["test_db"]
    assert mock_mongo_handler.collection == mock_mongo_handler.db["test_collection"]


def test_disconnect(mock_mongo_handler):
    mock_mongo_handler.connect()
    mock_mongo_handler.disconnect()

    assert mock_mongo_handler.client is None
    assert mock_mongo_handler.database is None
    assert mock_mongo_handler.collection is None


def test_mongo_handler_context_manager(mock_mongo_handler):
    with mock_mongo_handler:
        assert isinstance(mock_mongo_handler.client, mongomock.MongoClient)
        assert mock_mongo_handler.db == mock_mongo_handler.client["test_db"]
        assert mock_mongo_handler.collection == mock_mongo_handler.db["test_collection"]

    assert mock_mongo_handler.client is None
    assert mock_mongo_handler.database is None
    assert mock_mongo_handler.collection is None


def test_save_record_success(mock_mongo_handler):

    request = GrammarRequest(
        sentence="He go to school.",
        prompt_version="v1_original.txt",
        model="gpt-3.5-turbo",
        mode="interactive"
    )

    response = GrammarResponse(
        input="He go to school.",
        mistakes=[{"error": "subject-verb agreement"}],  # Optional or []
        corrected_sentence="He goes to school."
    )

    with mock_mongo_handler as db:
        # Save record
        record_id = db.save_record(request, response)
        assert record_id is not None

        # Check if the record is saved correctly
        record = db.collection.find_one({"_id": record_id})
        assert record["request"] == request.model_dump()
        assert record["response"] == response.model_dump()
        assert "timestamp" in record


def test_save_record_with_benchmark_eval(mock_mongo_handler):
    request = GrammarRequest(
        sentence="They is playing.",
        prompt_version="v1_original.txt",
        model="gpt-3.5-turbo",
        mode="interactive"
    )

    response = GrammarResponse(
        input="They is playing.",
        mistakes=[],
        corrected_sentence="They are playing."
    )
    benchmark_eval = {"accuracy": 0.95, "feedback": "Good correction"}

    with mock_mongo_handler as db:
        record_id = db.save_record(request, response, benchmark_eval=benchmark_eval)
        record = db.collection.find_one({"_id": record_id})

        assert "benchmark_eval" in record
        assert record["benchmark_eval"]["accuracy"] == 0.95
        assert record["benchmark_eval"]["feedback"] == "Good correction"


def test_save_record_failure(monkeypatch, caplog, mock_mongo_handler):
    def mock_insert_one_fail(*args, **kwargs):
        raise Exception("DB error")

    mock_request = MagicMock(spec=GrammarRequest)
    mock_request.model_dump.return_value = {"sentence": "x", "prompt_version": "y", "model": "z", "mode": "interactive"}

    mock_response = MagicMock(spec=GrammarResponse)
    mock_response.model_dump.return_value = {"input": "x", "mistakes": [], "corrected_sentence": "y"}

    with mock_mongo_handler as db:
        # Apply monkeypatch to simulate failure in insert_one
        monkeypatch.setattr(db.collection, "insert_one", mock_insert_one_fail)

        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception) as excinfo:
                db.save_record(mock_request, mock_response)

        assert "DB error" in str(excinfo.value)
        assert "Failed to save record" in caplog.text


def test_delete_record_success(mock_mongo_handler):
    request = GrammarRequest(
        sentence="test_input",
        prompt_version="v1_original.txt",
        model="gpt-3.5-turbo",
        mode="interactive"
    )

    response = GrammarResponse(
        input="test_input",
        mistakes=[],
        corrected_sentence="test_response"
    )
    
    with mock_mongo_handler:
        # insert a dummy record to delete
        inserted_id = mock_mongo_handler.save_record(request, response)
        # delete the record
        mock_mongo_handler.delete_record(inserted_id)
        # check if the record is deleted
        deleted_record = mock_mongo_handler.collection.find_one({"_id": inserted_id})

        assert deleted_record is None


# caplog is a pytest fixture that captures log messages
def test_delete_record_not_found(mock_mongo_handler, caplog):
    fake_id = ObjectId()  # generates a unique MongoDB-style ID

    # check if the log contains the warning
    with mock_mongo_handler:
        with caplog.at_level(logging.WARNING):
            mock_mongo_handler.delete_record(fake_id)
        assert "No record found" in caplog.text


def test_delete_record_failure(monkeypatch, caplog, mock_mongo_handler):
    # Simulate a failure in delete_one using monkeypatch
    def mock_delete_one_fail(*args, **kwargs):
        raise Exception("Delete error")

    with mock_mongo_handler:
        # Apply monkeypatch to simulate failure
        monkeypatch.setattr(mock_mongo_handler.collection, "delete_one", mock_delete_one_fail)

        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception) as excinfo:
                mock_mongo_handler.delete_record(ObjectId())

        assert "Delete error" in str(excinfo.value)
        assert "Failed to delete record" in caplog.text
