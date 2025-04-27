import os
import logging
import json
from openai import OpenAI
from grammar_checker.logger import get_logger

logger = get_logger(__name__)

# get the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in environment variables!")

client = OpenAI(api_key=api_key)

def get_model_response(model, prompt, client=client):
    logger.info(f"Sending request to model: {model} with prompt: {prompt}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": f"Sentence: {prompt}"}
            ],
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
