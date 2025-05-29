from pydantic import BaseModel, Field
from typing import Literal
from grammar_checker.config import (
    DEFAULT_MODEL,
    DEFAULT_PROMPT_TEMPLATE,
)

class GrammarRequest(BaseModel):
    sentence: str = Field(..., min_length=1)
    prompt_version: str = DEFAULT_PROMPT_TEMPLATE
    model: str = DEFAULT_MODEL
    mode: Literal["api", "benchmark", "interactive"] = Field("api", description="The mode of operation, e.g., 'benchmark', 'interactive', 'api'.")
