from grammar_checker.logger import get_logger
from grammar_checker.prompt_builder import PromptBuilder
from grammar_checker.openai_client import OpenAIClient
from grammar_checker.grammar_checker import GrammarChecker
from grammar_checker.db import MongoDBHandler
from grammar_checker.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from grammar_checker.config import PROMPT_TEMPLATE, DEFAULT_MODEL


def get_cli_input(prompt: str, logger) -> str:
    """Get input from the command line."""
    try:
        return input(prompt)
    except EOFError:
        logger.error("EOFError: No input received.")
        return ""
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt: Input interrupted.")
        return ""


def main(mongo_handler: MongoDBHandler, model: str = DEFAULT_MODEL):
    # initialize logger
    logger = get_logger(__name__)
    logger.info("Logging configuration set up successfully.")

    logger.info("Starting Grammar Checker CLI...")
    logger.debug(f"Model selected: {model}")

    sentence = get_cli_input("Enter a sentence to check grammar: ", logger)
    if not sentence:
        logger.warning("No sentence provided. Exiting program.")
        return

    logger.debug(f"Input sentence: {sentence}")

    prompt_builder = PromptBuilder(PROMPT_TEMPLATE)
    logger.debug("PromptBuilder initialized.")

    client = OpenAIClient()
    logger.debug("OpenAIClient initialized.")

    grammar_checker = GrammarChecker(prompt_builder, sentence, model, client)
    logger.debug("GrammarChecker initialized.")

    response = grammar_checker.check_grammar()
    logger.debug("Grammar check completed.")

    mongo_handler.save_record(
        input_data=sentence, model_response=response, metadata={"model": model, "mode": "interactive.py"}
    )
    logger.info("Record saved to MongoDB successfully.")


if __name__ == "__main__":
    main()
