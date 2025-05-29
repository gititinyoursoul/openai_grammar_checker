"""
Configuration file for the grammar checker tool.
Attributes:
    MODELS (list): A list of model names available for use in the grammar checker.
        Uncomment the desired model to activate it.
    TEST_CASES_FILE (str): The relative file path to the JSON file containing test cases.
    TEST_RESULTS_FILE (str): The relative file path to the JSON file where test results
        will be stored.
"""

import os


# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# Models
VALID_MODELS = [
    "gpt-3.5-turbo",
    # "gpt-4",
    # "gpt-4.1"
]
DEFAULT_MODEL = "gpt-3.5-turbo"  # default model to use if none is specified

# prompt template configuration
PROMPTS_DIR = "prompts"
DEFAULT_PROMPT_TEMPLATE = "v1_original.txt"

# Test Cases configuration
TEST_CASES_FILE = "tests/test_cases.json"
TEST_CASES_FILE_DEV = "tests/test_cases_DEV.json"

# test results configuration
TEST_RESULTS_FILE = "tests/test_results.json"

# logging configuration
LOG_FILE = "grammar_checker.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3
