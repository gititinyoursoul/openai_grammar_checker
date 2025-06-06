from grammar_checker.logger import get_logger
from grammar_checker.prompt_builder import PromptBuilder
from grammar_checker.openai_client import OpenAIClient
from models.response import GrammarResponse

logger = get_logger(__name__)


class GrammarChecker:
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        sentence: str,
        model: str,
        client: OpenAIClient,
    ):
        self.prompt_builder = prompt_builder
        self.sentence = sentence
        self.model = model
        self.client = client

        logger.info(f"GrammarChecker initialized with model: {self.model}, sentence: {self.sentence}")

    def check_grammar(self) -> GrammarResponse:
        prompt = self.prompt_builder.build_prompt(self.sentence)
        try:
            response = self.client.get_model_response(self.model, prompt)
            logger.debug(
                f"GrammarChecker request: '{self.model}' with template '{self.prompt_builder.prompt_template}' and sentence '{self.sentence}'"
            )
            if response:
                return GrammarResponse(**response)
            else:
                logger.error("Received empty response from the model.")
                raise ValueError
        except Exception as e:
            logger.error(f"An error occurred while checking grammar: {e}")
            raise
