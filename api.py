# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from grammar_checker.logger import get_logger
from grammar_checker.prompt_builder import PromptBuilder
from grammar_checker.openai_client import OpenAIClient
from grammar_checker.grammar_checker import GrammarChecker
from grammar_checker.db import MongoDBHandler
from grammar_checker.config import (
    MONGO_URI,
    MONGO_DB,
    MONGO_COLLECTION,
    DEFAULT_MODEL,
    PROMPT_TEMPLATE,
)

logger = get_logger(__name__)

app = FastAPI(title="Grammar Checker API")

# MongoDB handler instance
db = MongoDBHandler(MONGO_URI, MONGO_DB, MONGO_COLLECTION)


class GrammarRequest(BaseModel):
    sentence: str = Field(..., min_length=1)
    prompt_template: str = PROMPT_TEMPLATE
    model: str = DEFAULT_MODEL


@app.post("/check-grammar/")
def check_grammar(request: GrammarRequest):
    logger.info(f"Received input: {request.sentence} | Model: {request.model}")
    try:
        prompt_builder = PromptBuilder(request.prompt_template)
        client = OpenAIClient()
        grammar_checker = GrammarChecker(
            prompt_builder, request.sentence, request.model, client
        )
        response = grammar_checker.check_grammar()
        db.save_record(
            input_data=request.sentence,
            model_response=response,
            metadata={"model": request.model, "mode": "api.py"},
        )
        return response
    except Exception as e:
        logger.exception("Error during grammar check processing")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "ok"}
