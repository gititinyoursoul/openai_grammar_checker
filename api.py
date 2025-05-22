# api.py
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
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

# Create a global MongoDB handler
mongo_handler = MongoDBHandler(MONGO_URI, MONGO_DB, MONGO_COLLECTION)


def get_mongo_handler() -> MongoDBHandler:
    return mongo_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    mongo_handler.connect()

    yield  # ← This is where the app runs

    # Shutdown logic
    mongo_handler.disconnect()


# Create the app with lifespan handler
app = FastAPI(lifespan=lifespan, title="Grammar Checker API")


class GrammarRequest(BaseModel):
    sentence: str = Field(..., min_length=1)
    prompt_template: str = PROMPT_TEMPLATE
    model: str = DEFAULT_MODEL


@app.post("/check-grammar/")
def check_grammar(request: GrammarRequest, mongo_handler: MongoDBHandler = Depends(get_mongo_handler)):
    logger.info(f"Received input: {request.sentence} | Model: {request.model}")
    try:
        prompt_builder = PromptBuilder(request.prompt_template)
        client = OpenAIClient()
        grammar_checker = GrammarChecker(prompt_builder, request.sentence, request.model, client)
        response = grammar_checker.check_grammar()

        mongo_handler.save_record(
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
