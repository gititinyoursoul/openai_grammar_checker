from typing import List, Dict
from pymongo import MongoClient
from grammar_checker.logger import get_logger
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

logger = get_logger(__name__)


def query_benchmark_data(run_ids: List[str]) -> List[Dict]:
    """
    Queries the database for documents matching the provided list of run IDs.
    
    Args:
        run_ids (List[str]): A list of run IDs to query in the database.
    Returns:
        List[Dict]: A list of documents containing the fields for each matching run ID.
    """
    query = {"benchmark_eval.run_id": {"$in": run_ids}}
    projection = {"_id": 0, "request": 1, "response": 1, "benchmark_eval": 1, "timestamp": 1}
    
    with MongoClient(MONGO_URI) as client:
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        raw_data = list(collection.find(query, projection))

    return raw_data
