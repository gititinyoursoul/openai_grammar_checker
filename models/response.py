from pydantic import BaseModel, Field, constr
from typing import List, Literal, Optional

# Represents one individual mistake entry in the response
class Mistake(BaseModel):
    type: Literal[
        "PunctuationMistake",
        "WordOrderMistake",
        "WrongArticleMistake",
        "VerbTenseMistake",
        "ComparativeFormMistake",
        "SpellingMistake",
        "CapitalizationMistake",
        "OtherMistake"
    ]
    original: str
    corrected: str
    
# Base schema used by API and interactive responses
class GrammarResponse(BaseModel):
    input: constr(min_length=1)
    mistakes: List[Mistake]
    corrected_sentence: constr(min_length=1)
