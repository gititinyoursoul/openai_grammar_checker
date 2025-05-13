import os
import argparse
from grammar_checker.config import (
    MODELS,
    TEST_CASES_FILE_REF,
    PROMPT_TEMPLATE,
)
from runner import main as run_tests
from interactive import main as start_interactive_mode
from grammar_checker.logger import get_logger


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run Grammar Checker.")

    parser.add_argument(
        "--mode",
        choices=["interactive", "run_tests"],
        default="interactive",
        help="Choose mode: 'interactive' for user input, 'run_tests' for test cases",
    )
    
    parser.add_argument(
        "--output",
        choices=["save_to_db", "save_to_file"],
        default="save_to_db",
        help="Specify where to save the test results: 'save_to_db' for database or 'save_to_file' for a JSON file (default: 'save_to_db').",
    )

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
        "--prompt-template",
        default=PROMPT_TEMPLATE,
        help="Path to the prompt template file (default: from config).",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("DEBUG", "False").lower() == "true",
        help="Enable debug mode (default: from .env)",
    )

    return parser.parse_args()


def main():
    logger = get_logger(__name__)
    logger.info("Logging configuration set up successfully. main.py")
    
    args = parse_arguments()

    if args.mode == "run_tests":
        logger.info("run_tests executed successfully.")
        run_tests(
            test_cases_file=args.test_cases,
            models=args.models,
            output_destination=args.output,
            prompt_template=args.prompt_template,
        )
        
    else:
        logger.info("start_interactive_mode started successfully.")
        start_interactive_mode(debug=args.debug)
        

if __name__ == "__main__":
    main()
