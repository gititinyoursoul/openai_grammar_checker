import json
from typing import List, Dict, Any, Callable
from grammar_checker.logger import get_logger

logger = get_logger(__name__)


# load test cases from a json file
def load_test_cases(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            logger.info(f"Loading test cases from '{file_path}'")
            return json.load(file)
    except FileNotFoundError as e:
        logger.error(f"Test cases file not found: '{file_path}': {e}")
        raise FileNotFoundError(f"Test cases file not found: '{file_path}'") from e
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file '{file_path}': {e}")
        raise ValueError(f"Invalid JSON format in file '{file_path}'") from e


def transform_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    transformed = []

    for result in results:
        try:
            request = result["request"].model_dump()
            response = result["response"].model_dump()
            benchmark_eval = result["benchmark_eval"]
        except (KeyError, AttributeError) as e:
            logger.error(f"Invalid result structure {result}: {e}")
            raise

        transformed.append({"request": request, "response": response, "benchmark_eval": benchmark_eval})
    return transformed


def save_to_file(file_path: str, data: Any, writer: Callable = json.dump) -> None:
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            writer(data, f, indent=4)
        logger.info(f"Test results saved to '{file_path}'")
    except Exception as e:
        logger.error(f"Error saving test results to file '{file_path}': {e}")
        raise


def save_test_results(file_path: str, results: List[Dict[str, Any]]) -> None:
    transformed = transform_results(results)
    save_to_file(file_path, transformed)
