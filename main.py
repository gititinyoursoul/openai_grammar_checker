import os
import argparse
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import uvicorn
from runner import main as run_tests
from interactive import main as start_interactive_mode
from grammar_checker.logger import get_logger
from grammar_checker.db import MongoDBHandler
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from grammar_checker.config import (
    MODELS,
    TEST_CASES_FILE_REF,
    PROMPT_TEMPLATE,
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run Grammar Checker.")

    parser.add_argument(
        "--mode",
        choices=["interactive", "api", "run_tests"],
        default="interactive",
        help="Choose mode: 'interactive' for user input, 'api' to start the FastAPI server or 'run_tests' to run test cases",
    )

    parser.add_argument(
        "--output",
        choices=["save_to_db", "save_to_file"],
        default="save_to_db",
        help="Specify where to save the test results: 'save_to_db' for database or 'save_to_file' for a JSON file (default: 'save_to_db').",
    )

    # arguments for FastAPI server
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key (default: from environment variable).",
    )
    parser.add_argument("--api-host", default="127.0.0.1")

    parser.add_argument("--api-port", type=int, default=8000)

    parser.add_argument(
        "--models",
        nargs="+",
        default=MODELS,
        help="List of models to evaluate (default: from config).",
    )

    parser.add_argument(
        "--prompt-template",
        default=PROMPT_TEMPLATE,
        help="Path to the prompt template file (default: from config).",
    )

    parser.add_argument(
        "--test-cases",
        default=TEST_CASES_FILE_REF,
        help="Path to the test cases JSON file (default: from config).",
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
    logger.info("Logging configuration set up successfully.")

    args = parse_arguments()
    logger.info(f"Command-line arguments parsed successfully: {args}")

    db_handler = MongoDBHandler(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    logger.info("MongoDB handler initialized successfully.")

    if args.mode == "run_tests":
        run_tests(
            test_cases_file=args.test_cases,
            models=args.models,
            output_destination=args.output,
            prompt_template=args.prompt_template,
            db_handler=db_handler,
        )
        logger.info("run_tests executed successfully.")
    elif args.mode == "api":
        logger.info(f"Starting FastAPI server at {args.api_host}:{args.api_port}")
        uvicorn.run("api:app", host=args.api_host, port=args.api_port, reload=True)
    elif args.mode == "interactive":
        start_interactive_mode(db_handler)
        logger.info("Interactive mode started successfully.")
    else:
        logger.error("Invalid mode selected. Please choose 'interactive', 'api', or 'run_tests'.")
        raise ValueError("Invalid mode selected. Please choose 'interactive', 'api', or 'run_tests'.")


if __name__ == "__main__":
    main()
