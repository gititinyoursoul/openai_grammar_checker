# This script runs the grammar checker tests using the OpenAI API.
import os
import uuid
from typing import List
from grammar_checker.logger import get_logger
from grammar_checker.prompt_builder import PromptBuilder
from grammar_checker.openai_client import OpenAIClient
from grammar_checker.grammar_checker import GrammarChecker
from grammar_checker.evaluator import evaluate_response
from grammar_checker.utils import load_test_cases, save_test_results
from grammar_checker.db import MongoDBHandler
from grammar_checker.config import TEST_RESULTS_FILE, VALID_MODELS, PROMPTS_DIR
from models.request import GrammarRequest


# initialize logger
logger = get_logger(__name__)


def validate_main_inputs(
    test_cases_file: str,
    models: List[str],
    output_destination: str,
    prompt_templates: List[str],
    db_handler: MongoDBHandler,
):
    if not isinstance(test_cases_file, str) or not test_cases_file.strip():
        raise ValueError("test_cases_file must be a non-empty string path.")

    if not isinstance(models, list) or not models:
        raise ValueError("models must be a non-empty list of model names.")
    for model in models:
        if not isinstance(model, str) or model.strip() not in VALID_MODELS:
            raise ValueError(f"Model '{model}' is not a valid model name.")

    if not isinstance(output_destination, str) or not output_destination.strip():
        raise ValueError("output_destination must be non-empty string.")

    if not isinstance(prompt_templates, list) or not prompt_templates:
        raise ValueError("prompt_template must be a non-empty list of prompt templates.")
    for template in prompt_templates:
        if not isinstance(template, str) or not template.strip():
            raise ValueError("Each prompt template must be a string.")
        template_path = f"{PROMPTS_DIR}/{template}"
        if not os.path.isfile(template_path):
            raise ValueError(f"Prompt template '{template}' does not exist.")

    if output_destination == "save_to_db" and db_handler is None:
        raise ValueError("db_handler is required when output_destination is 'save_to_db'.")


def get_run_id():
    """Generate a unique ID for this test run."""
    return str(uuid.uuid4())


# test cases
def run_tests(test_cases: List[str], models: List[str], prompt_templates: List[str], client: OpenAIClient):
    run_id = get_run_id()
    logger.info(f"Starting benchmark tests {run_id}.")
    results = []
    for model in models:
        for template in prompt_templates:
            for test_case in test_cases:
                logger.debug(f"test_id {test_case['test_id']} | model: '{model}' | prompt_version: '{template}'")
                sentence = test_case["input"]
                try:
                    prompt_builder = PromptBuilder(template)
                    grammar_checker = GrammarChecker(prompt_builder, sentence, model, client)
                    response = grammar_checker.check_grammar()

                    is_match = evaluate_response(test_case, response)
                    test_case["match"] = is_match
                    test_case["run_id"] = run_id

                    # build GrammarRequest
                    request = GrammarRequest(
                        sentence=sentence,
                        prompt_version=template,
                        model=model,
                        mode="benchmark",
                    )

                    results.append(
                        {
                            "request": request,
                            "response": response,
                            "benchmark_eval": test_case,
                        }
                    )
                except Exception as e:
                    logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
                    raise
    logger.info(f"Benchmark tests for {run_id} completed.")
    return results


def summary_results(results: list):
    # summarize the results

    summary = {}
    for result in results:
        prompt_version = result["request"].prompt_version
        if prompt_version not in summary:
            summary[prompt_version] = {}
        model = result["request"].model
        if model not in summary[prompt_version]:
            summary[prompt_version][model] = {"total": 0, "passed": 0}

        summary[prompt_version][model]["total"] += 1
        if result["benchmark_eval"]["match"]:
            summary[prompt_version][model]["passed"] += 1
    logger.info(f"Model Matches: {summary}")
    return summary


def main(
    test_cases_file: str,
    models: List[str],
    output_destination: str,
    prompt_templates: List[str],
    mongo_handler: MongoDBHandler,
):
    logger.info("Starting Grammar Checker Tests.")

    # validate inputs
    validate_main_inputs(test_cases_file, models, output_destination, prompt_templates, mongo_handler)
    logger.info("Input validation passed.")

    # set up the OpenAI client and prompt builder
    client = OpenAIClient()

    # run the tests
    test_cases = load_test_cases(test_cases_file)
    results = run_tests(test_cases, models, prompt_templates, client)

    summary_results(results)

    # save results
    if output_destination == "save_to_db":
        logger.info("Saving test results to MongoDB")
        with mongo_handler as db:
            for result in results:
                db.save_record(
                    request=result["request"],
                    response=result["response"],
                    benchmark_eval=result["benchmark_eval"],
                )
    # elif output_destination == "save_to_file":
    #     logger.info(f"Saving test results to {TEST_RESULTS_FILE}")
    #     save_test_results(TEST_RESULTS_FILE, results)
    else:
        logger.error("Invalid output option. Please refer to the help documentation for valid options.")


if __name__ == "__main__":
    main()
