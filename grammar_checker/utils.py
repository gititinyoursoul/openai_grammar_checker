import json
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

# save test results to a json file
def save_test_results(file_path, results):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=4)  
        logger.info(f"Test results saved to '{file_path}'")
    except Exception as e:
        logger.error(f"Error saving test results to file '{file_path}': {e}")
        raise 
    
