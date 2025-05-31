from pymongo import MongoClient
from datetime import datetime, UTC
from grammar_checker.logger import get_logger

logger = get_logger(__name__)


class MongoDBHandler:
    def __init__(self, uri, database_name, collection_name):
        self.client = None
        self.database = None
        self.collection = None
        self.uri = uri
        self.database_name = database_name
        self.collection_name = collection_name

    def connect(self):
        if not self.client:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            logger.debug(f"Connected to MongoDB: {self.database_name}/{self.collection_name}")

    def disconnect(self):
        if self.client:
            self.client.close()
            logger.debug(f"Disconnected from MongoDB: {self.database_name}/{self.collection_name}.")
            self.client = None
            self.database = None
            self.collection = None
        else:
            logger.debug(f"No active MongoDB connection to close: {self.database_name}/{self.collection_name}")

    def save_record(self, request, response, benchmark_eval=None):
        record = {
            "request": request,
            "response": response,
            "timestamp": datetime.now(UTC),
        }
        if benchmark_eval:
            record["benchmark_eval"] = benchmark_eval
        try:
            result = self.collection.insert_one(record)
            logger.debug(f"Record inserted with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to save record: {e}")
            raise e

    # delete record
    def delete_record(self, record_id):
        try:
            result = self.collection.delete_one({"_id": record_id})
            if result.deleted_count > 0:
                logger.debug(f"Record with ID {record_id} deleted successfully.")
            else:
                logger.warning(f"No record found with ID {record_id}.")
        except Exception as e:
            logger.error(f"Failed to delete record: {e}")
            raise

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
