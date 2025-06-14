import typer
import uvicorn
from dotenv import load_dotenv
load_dotenv()
from typing import List
from grammar_checker.logger import get_logger
from grammar_checker.db import MongoDBHandler
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from interactive import main as interactive_main
from benchmark import main as benchmark_main
from grammar_checker.config import (
    VALID_MODELS,
    TEST_CASES_FILE,
    TEST_CASES_FILE_DEV,
    DEFAULT_PROMPT_TEMPLATE,
)


app = typer.Typer(help="CLI for managing MongoDB and running the grammar checker.")

logger = get_logger(__name__)


@app.command()
def run_api(host: str = "127.0.0.1", port: int = 8000):
    """Run the FastAPI server."""
    logger.info(f"Starting FastAPI server at {host}:{port}")
    uvicorn.run("api:app", host=host, port=port, reload=True)


@app.command()
def interactive():
    """Run the interactive mode."""
    logger.info("Starting interactive mode...")
    mongo_handler = MongoDBHandler(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    interactive_main(mongo_handler=mongo_handler)


@app.command()
def benchmark(
    test_cases_file: str = typer.Option(TEST_CASES_FILE, help="Path to the test cases JSON file"),
    models: List[str] = typer.Option(VALID_MODELS, help="List of OpenAI model names"),
    prompt_templates: List[str] = typer.Option([DEFAULT_PROMPT_TEMPLATE], help="List of prompt template files"),
    output_destination: str = typer.Option("save_to_db"),
):
    """
    Run grammar benchmarks on selected OpenAI models using test cases and a prompt template.

    Args:
        --test-cases-file: Path to test case file (default: dev test cases).
        --models: One or more OpenAI model names to benchmark.
        --prompt-template: Prompt template to use.
        --output-destination: Where to send results ("save_to_db", "print", etc.).

    Benchmarks are logged and may be saved to MongoDB.
    """
    logger.info("Starting benchmark mode...")
    logger.debug(f"Arguments received: {test_cases_file=}, {models=}, {prompt_templates=}, {output_destination=}")
    mongo_handler = MongoDBHandler(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    benchmark_main(test_cases_file, models, output_destination, prompt_templates, mongo_handler)


if __name__ == "__main__":
    app()
