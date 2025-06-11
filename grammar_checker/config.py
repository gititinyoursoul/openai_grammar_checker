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
from pathlib import Path

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# Models
VALID_MODELS = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4.1"
]
DEFAULT_MODEL = "gpt-3.5-turbo"  # default model to use if none is specified

# Path config
PROJECT_ROOT = Path(__file__).resolve().parent.parent # resolve converts into an absolute path

# Prompt version config
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DEFAULT_PROMPT_TEMPLATE = "v1_original.txt"

# Benchmark Cases config
BENCHMARKS_DIR = PROJECT_ROOT / "benchmarks"
TEST_CASES_FILE = BENCHMARKS_DIR / "test_cases_2.json"
TEST_CASES_FILE_DEV = BENCHMARKS_DIR / "test_cases_DEV_2.json"

# Benchmark Results config
REPORTS_DIR = PROJECT_ROOT / "outputs" #/ "reports"
TEST_RESULTS_FILE = REPORTS_DIR / "test_results.json"

# logging configuration
LOG_DIR = PROJECT_ROOT / "outputs" #/ "logs"
LOG_FILE = LOG_DIR / "grammar_checker.log"

MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3
