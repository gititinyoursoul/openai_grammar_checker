# This script runs the grammar checker tests using the OpenAI API.
from dotenv import load_dotenv
from grammar_checker.logger import get_logger
from grammar_checker.prompt_builder import PromptBuilder
from grammar_checker.openai_client import OpenAIClient
from grammar_checker.grammar_checker import GrammarChecker
from grammar_checker.evaluator import evaluate_response
from grammar_checker.utils import load_test_cases, save_test_results
from grammar_checker.db import MongoDBHandler
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from grammar_checker.config import TEST_RESULTS_FILE


# initialize logger
logger = get_logger(__name__)

def setup_environment():
    """Load environment variables."""
    load_dotenv()
    logger.info("Environment variables loaded successfully.")


# test cases
def run_tests(test_cases, models, prompt_builder: PromptBuilder, client: OpenAIClient):
    results = []
    for model in models:
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


def main(test_cases_file: str,
         models: list,
         output_destination: str,
         prompt_template: str,
         db_handler: MongoDBHandler):
    logger.info("Starting Grammar Checker Tests.")

    # load environment variables
    setup_environment()

    # set up the OpenAI client and prompt builder
    prompt_builder = PromptBuilder(prompt_template)
    client = OpenAIClient()

    # run the tests
    test_cases = load_test_cases(test_cases_file)
    results = run_tests(test_cases, models, prompt_builder, client)

    summary_results(results)

    # save results
    if output_destination == "save_to_db":
        logger.info("Saving test results to MongoDB")
        for result in results:
            db_handler.save_record(
                input_data=result["input"],
                model_response=result["output"],
                test_eval={
                    "match": result["match"],
                    "expected": result["expected"]
                    },
                metadata={
                    "mode": "test_runner.py",
                    "model": result["model"]
                    }
            ) 
    elif output_destination == "save_to_file":
        logger.info(f"Saving test results to {TEST_RESULTS_FILE}")
        save_test_results(TEST_RESULTS_FILE, results)
    else:
        logger.error("Invalid output option. Please refer to the help documentation for valid options.")


if __name__ == "__main__":
    main()
