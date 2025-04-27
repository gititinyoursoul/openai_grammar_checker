from grammar_checker.logger import get_logger
from grammar_checker.prompt_builder import PromptBuilder
from grammar_checker.openai_client import OpenAIClient
from grammar_checker.evaluator import evaluate_result

logger = get_logger(__name__)

class GrammarChecker:
    def __init__(self, prompt_template :str, sentence: str, model: str, prompt_builder: PromptBuilder, client: OpenAIClient):
        self.prompt_template = prompt_template
        self.sentence = sentence
        self.model = model
        self.prompt_builder = prompt_builder
        self.client = client
        
        logger.info(f"GrammarChecker initialized with model: {model}, sentence: {sentence}")

    def check_grammar(self):
        prompt = self.prompt_builder.build_prompt(self.sentence)
        try:
            response = self.client.get_model_response(self.model, prompt, self.prompt_template, self.sentence)
            if response:
                return response
            else:
                logger.error("Received empty response from the model.")
                raise ValueError
        except Exception as e:
            logger.error(f"An error occurred while checking grammar: {e}")
            raise
