import pytest
from reporting.mistakes_report import score_string_similarity


@pytest.mark.parametrize(
    "val1,val2,condition",
    [
        ("we match fully", "we match fully", lambda score: score == 1),
        ("we match almost", "we match mostly", lambda score: score > 0.8),
        ("we match almost", "we almost match", lambda score: score < 0.8),
        ("we are anagrams", "aware managers", lambda score: score < 0.8),
        ("we do", "not match", lambda score: score < 0.2),
    ],
)
def test_score_string_similarity_success(val1, val2, condition):

    score = score_string_similarity(val1, val2)
    assert condition(score), f"Score {score} did not satisfy condition for input: {val1!r} vs {val2!r}"


@pytest.mark.parametrize(
    "val1, val2",
    [
        (None, "foo"),
        ("bar", None),
        (123, "123"),
        ([1], "1"),
        (True, False),
    ],
)
def test_score_string_similarity_non_strings(val1, val2):
    score = score_string_similarity(val1, val2)
    assert score == 0.0, f"Score {score} did not satisfy condition for input: {val1!r} vs {val2!r}"
