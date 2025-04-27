# This script runs the grammar checker tests using the OpenAI API.
from grammar_checker.logger import get_logger
from grammar_checker.prompt_builder import build_prompt
from grammar_checker.openai_client import get_model_response
from grammar_checker.evaluator import evaluate_result
from grammar_checker.config import MODELS, TEST_RESULTS_FILE, TEST_CASES_FILE_REF
from grammar_checker.utils import load_test_cases, save_test_results
from dotenv import load_dotenv

# initialize logger
logger = get_logger(__name__)
logger.info("Logging configuration set up successfully.")

# load environment variables
load_dotenv()
logger.info("Environment variables loaded successfully.")

    
# test cases
def run_tests(test_cases):
    results = []
    for model in MODELS:
        print(f"\nEvaluating model: {model}")
        for test_case in test_cases:
            prompt = build_prompt(test_case["input"])
            try:
                response = get_model_response(model, prompt)
                match = evaluate_result(test_case, response)
                results.append(
                    {
                        "model": model,
                        "input": test_case["input"],
                        "output": response,
                        "expected": test_case,
                        "match": match,
                    }
                )
                print(f"- {test_case['input']} => {'✓ PASS' if match else '✗ FAIL'}")
            except Exception as e:
                print(f"- {test_case['input']} => ERROR: {str(e)}")
    return results


if __name__ == "__main__" :
    # load test cases
    TEST_CASES = load_test_cases(TEST_CASES_FILE_REF)
    
    results = run_tests(TEST_CASES)
    
    # from the output i want to count matches per model
    model_matches = {ele["model"]: 0 for ele in results}
    for result in results:
        if result["match"]:
            model_matches[result["model"]] += 1
    logger.info(f"Model Matches: {model_matches}\n")    
        
    # write the results to a file
    save_test_results(TEST_RESULTS_FILE, results)