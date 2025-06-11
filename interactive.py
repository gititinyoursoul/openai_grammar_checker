from grammar_checker.logger import get_logger
from grammar_checker.prompt_builder import PromptBuilder
from grammar_checker.openai_client import OpenAIClient
from grammar_checker.grammar_checker import GrammarChecker
from grammar_checker.db import MongoDBHandler
from grammar_checker.config import DEFAULT_PROMPT_TEMPLATE, DEFAULT_MODEL
from models.request import GrammarRequest


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


def main(
    mongo_handler: MongoDBHandler,
    prompt_builder: PromptBuilder = None,
    client: OpenAIClient = None,
    model: str = DEFAULT_MODEL,
):
    logger = get_logger(__name__)
    logger.info("Starting Grammar Checker CLI...")

    sentence = get_cli_input("Enter a sentence to check grammar: ", logger)
    if not sentence:
        logger.warning("No sentence provided. Exiting program.")
        return

    prompt_builder = prompt_builder or PromptBuilder(DEFAULT_PROMPT_TEMPLATE)
    client = client or OpenAIClient()

    grammar_checker = GrammarChecker(prompt_builder, sentence, model, client)
    response = grammar_checker.check_grammar()

    request = GrammarRequest(
        sentence=sentence, 
        prompt_version=prompt_builder.prompt_template, 
        model=model, 
        mode="interactive"
    )

    with mongo_handler:
        mongo_handler.save_record(request=request, response=response)


if __name__ == "__main__":
    main()
