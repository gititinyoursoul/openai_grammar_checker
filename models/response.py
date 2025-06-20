from pydantic import BaseModel, Field
from typing import List, Literal

# Represents one individual mistake entry in the response
# class Mistake(BaseModel):
#     type: Literal[
#         "PunctuationMistake",
#         "WordOrderMistake",
#         "WrongArticleMistake",
#         "VerbTenseMistake",
#         "ComparativeFormMistake",
#         "SpellingMistake",
#         "CapitalizationMistake",
#         "OtherMistake"
#     ]
#     original: str
#     corrected: str
    
# Base schema used by API and interactive responses
class GrammarResponse(BaseModel):
    input: str = Field(..., min_length=1)
    mistakes: List[dict]
    corrected_sentence: str =  Field(..., min_length=1)
