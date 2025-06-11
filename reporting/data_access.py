from pymongo import MongoClient
from grammar_checker.logger import get_logger
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

logger = get_logger(__name__)


def query_benchmark_data(run_ids: list[str]) -> dict:
    """
    Query the database for a specific run ID.

    Args:
        run_id (str): The run ID to query.

    Returns:
        dict: The document corresponding to the run ID.
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    query = {"benchmark_eval.run_id": {"$in": run_ids}}
    projection = {"_id": 0, "request": 1, "response": 1, "benchmark_eval": 1, "timestamp": 1}

    raw_data = collection.find(query, projection)

    return raw_data
