from pymongo import MongoClient
from datetime import datetime
from grammar_checker.logger import get_logger

logger = get_logger(__name__)


class MongoDBHandler:
    def __init__(self, uri, database_name, collection_name):
        self.client = MongoClient(uri)
        self.database = self.client[database_name]
        self.collection = self.database[collection_name]
        logger.info(f"Connected to MongoDB: {database_name}/{collection_name}")

    def save_record(self, input_data, model_response, test_eval=None, metadata=None):
        record = {"input": input_data, "response": model_response, "timestamp": datetime.utcnow()}
        if metadata:
            record["metadata"] = metadata
        if test_eval:
            record["test_eval"] = test_eval
        try:
            result = self.collection.insert_one(record)
            logger.debug(f"Record inserted with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to save record: {e}")
            raise

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
