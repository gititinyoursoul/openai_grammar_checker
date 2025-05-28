import os
from grammar_checker.logger import get_logger
from grammar_checker.config import PROMPTS_DIR

logger = get_logger(__name__)


class PromptBuilder:
    """A class for building prompts by loading a template from a file and replacing placeholders with a given sentence.

    Attributes:
        prompt_template_path (str): The file path to the prompt template.
        template (str): The loaded prompt template content.
    Methods:
        __init__(prompt_template_path: str, sentence: str):
            Initializes the `PromptBuilder` with the template file path and the sentence to be used.
        _load_template():
            Loads the prompt template from the specified file path, handling errors appropriately.
        build_prompt():
            Constructs a prompt by replacing the placeholder in the template with the provided sentence.
    """

    def __init__(self, prompt_template: str, prompt_dir: str = PROMPTS_DIR):
        self.template_path = os.path.join(prompt_dir, prompt_template) 
        self.template = self._load_template()

    def _load_template(self):
        """
        Loads the prompt template from the file specified by `self.prompt_template_path`.

        Returns:
            str: The content of the prompt template file as a stripped string.

        Raises:
            FileNotFoundError: If the file specified by `self.prompt_template_path` does not exist.
            Exception: If any other error occurs while reading the file.
        """
        try:
            with open(self.template_path, "r", encoding="utf-8") as file:
                template = file.read().strip()
            logger.info(f"Loaded prompt template from '{self.template_path}'")
            return template
        except FileNotFoundError:
            logger.error(f"Prompt template file not found: '{self.template_path}'")
            raise
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            raise

    def build_prompt(self, sentence: str):
        """
        Builds a prompt by replacing the placeholder in the template with the provided sentence.

        Returns:
            str: The constructed prompt with the sentence inserted into the template.
        Raises:
            ValueError: If `sentence` is empty.
        """
        if not sentence:
            logger.error("Empty sentence provided for prompt building")
            raise ValueError("Sentence cannot be empty")
        prompt = self.template.replace("{sentence}", sentence)

        truncated_sentence = sentence[:20] + "..." if len(sentence) > 20 else sentence
        logger.info(
            f"Building prompt using template '{self.template_path}' with sentence: '{truncated_sentence}'"
        )

        return prompt
