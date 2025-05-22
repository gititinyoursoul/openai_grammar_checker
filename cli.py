import typer
import subprocess
import os
import uvicorn
from typing import List
from grammar_checker.logger import get_logger
from grammar_checker.db import MongoDBHandler
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from interactive import main as interactive_main
from runner import main as benchmarks_main
from grammar_checker.config import (
    MODELS,
    TEST_CASES_FILE_DEV,
    PROMPT_TEMPLATE,
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
def benchmarks(
    test_cases_file: str = TEST_CASES_FILE_DEV,
    models: List[str] = typer.Option(MODELS, help="List of OpenAI model names"),
    prompt_template: str = PROMPT_TEMPLATE,
    output_destination: str = "save_to_db",
):
    logger.info("Starting benchmark mode...")
    mongo_handler = MongoDBHandler(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    benchmarks_main(
        test_cases_file,
        models,
        output_destination,
        prompt_template,
        mongo_handler
    )


if __name__ == "__main__":
    app()
