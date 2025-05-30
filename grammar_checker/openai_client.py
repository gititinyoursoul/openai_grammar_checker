import os
import json
from openai import OpenAI
from grammar_checker.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    def __init__(self):
        self.api_key = self._get_api_key()
        self.client = OpenAI(api_key=self.api_key)
        logger.info("OpenAI client initialized successfully.")

    def _get_api_key(self):
        # get the OpenAI API key from environment variables
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables.")
            raise RuntimeError("Missing OPENAI_API_KEY in environment variables!")

        return api_key

    # get model reponse / error handling
    def get_model_response(self, model: str, prompt: str) -> dict:

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": f"Sentence: {prompt}"}],
                temperature=0,
            )
            logger.info("Received response from the model.")
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error("Response content is not valid JSON.")
                raise
        except Exception as e:
            logger.error(f"An error occurred while getting the model response: {e}")
            raise
