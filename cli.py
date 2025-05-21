import typer
import subprocess
import os
import uvicorn
from grammar_checker.logger import get_logger
from grammar_checker.db import MongoDBHandler
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from interactive import main as interactive_main


app = typer.Typer(help="CLI for managing MongoDB and running the grammar checker.")

logger = get_logger(__name__)


@app.command()
def interactive():
    """Run the interactive mode."""
    logger.info("Starting interactive mode...")
    mongo_handler = MongoDBHandler(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    interactive_main(mongo_handler=mongo_handler)


if __name__ == "__main__":
    app()
