# This script runs the grammar checker tests using the OpenAI API.
import os
import argparse
from dotenv import load_dotenv

from grammar_checker.logger import get_logger
from grammar_checker.prompt_builder import PromptBuilder
from grammar_checker.openai_client import OpenAIClient
from grammar_checker.grammar_checker import GrammarChecker
from grammar_checker.evaluator import evaluate_response
from grammar_checker.config import MODELS, TEST_RESULTS_FILE, TEST_CASES_FILE_REF, PROMPT_TEMPLATE
from grammar_checker.utils import load_test_cases, save_test_results


# initialize logger
logger = get_logger(__name__)
logger.info("Logging configuration set up successfully.")


def setup_environment():
    """Load environment variables."""
    load_dotenv()
    logger.info("Environment variables loaded successfully.")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run Grammar Checker Tests.")
    parser.add_argument(
        "--models",
        nargs="+",
        default=MODELS,
        help="List of models to evaluate (default: from config).",
    )
    parser.add_argument(
        "--test-cases",
        default=TEST_CASES_FILE_REF,
        help="Path to the test cases JSON file (default: from config).",
    )
    parser.add_argument(
        "--output",
        default=TEST_RESULTS_FILE,
        help="Path to save the test results JSON file (default: from config).",
    )
    parser.add_argument(
        "--prompt-template",
        default=PROMPT_TEMPLATE,
        help="Path to the prompt template file (default: from config).",
    )
    parser.add_argument(
        "--debug",
        default=os.getenv("DEBUG", "False").lower() == "true",
        help="Enable debug mode (default: value from .env, 'False' if not set).",
    )
    return parser.parse_args()


# test cases
def run_tests(test_cases, prompt_builder: PromptBuilder, client: OpenAIClient):
    results = []
    for model in MODELS:
        for test_case in test_cases:
            logger.info(f"Begin grammar check of model: '{model}' and sentence: '{test_case['input']}'")
            sentence = test_case["input"]
            try:
                grammar_checker = GrammarChecker(prompt_builder, sentence, model, client)
                response = grammar_checker.check_grammar()
                is_match = evaluate_response(test_case, response)
                results.append(
                    {
                        "model": model,
                        "input": test_case["input"],
                        "output": response,
                        "expected": test_case,
                        "match": is_match,
                    }
                )
                logger.info(f"Sentence: {test_case['input']} => {'PASS' if is_match else 'FAIL'}")
            except Exception as e:
                logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
                raise
    return results


def summary_results(results):
    # summarize the results

    summary = {}
    for result in results:
        model = result["model"]
        if model not in summary:
            summary[model] = {"total": 0, "passed": 0}
        summary[model]["total"] += 1
        if result["match"]:
            summary[model]["passed"] += 1
    logger.info(f"Model Matches: {summary}")
    return summary


def main():
    # args = parse_arguments()

    logger.info("Starting Grammar Checker Runner...")
    # logger.debug("Debug Test")
    # load environment variables
    setup_environment()

    # set up the OpenAI client and prompt builder
    prompt_builder = PromptBuilder(PROMPT_TEMPLATE)
    client = OpenAIClient()

    # run the tests
    test_cases = load_test_cases(TEST_CASES_FILE_REF)
    results = run_tests(test_cases, prompt_builder, client)

    summary_results(results)

    # write the results to a file
    save_test_results(TEST_RESULTS_FILE, results)
    logger.info("Test results saved successfully.")


if __name__ == "__main__":
    main()
