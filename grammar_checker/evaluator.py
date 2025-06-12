from models.response import GrammarResponse

# Simple evaluator
def evaluate_response(expected: dict, actual: GrammarResponse):
    def normalize(s):
        return s.strip().lower()

    correct_sentence = normalize(expected["corrected_sentence"])
    actual_sentence = normalize(actual.corrected_sentence)

    # Compare full sentence
    sentence_match = correct_sentence == actual_sentence

    # Compare mistakes (loosely – for demo purposes)
    mistake_types_match = all(
        any(m["type"] == e["type"] for m in actual.mistakes)
        for e in expected["mistakes"]
    )

    return sentence_match and mistake_types_match
