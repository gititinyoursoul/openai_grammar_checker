import pytest
from unittest.mock import patch
from reporting.mistakes_report import score_string_similarity, compare_dicts_keys, evaluate_mistakes


# score_string_similarity
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


# compare_dicts_keys
@pytest.mark.parametrize(
    "source_index, source_item, target_index, target_item, threshold, similarity_score, expected",
    [
        # --- key in both, score > threshold ---
        (0, {"name": "Alice"}, 1, {"name": "Alicia"}, 0.7, 0.9, [(0, 1, "name", "Alice", "Alicia", 0.9, True)]),
        # --- key in both, score == threshold ---
        (0, {"name": "Alice"}, 1, {"name": "Alicia"}, 0.8, 0.8, [(0, 1, "name", "Alice", "Alicia", 0.8, True)]),
        # --- key in both, score < threshold ---
        (0, {"name": "Alice"}, 1, {"name": "Bob"}, 0.8, 0.3, [(0, 1, "name", "Alice", "Bob", 0.3, False)]),
        # --- key only in source ---
        (0, {"city": "Berlin"}, 1, {}, 0.5, None, [(0, 1, "city", "Berlin", None, 0.0, False)]),
        # --- key only in target ---
        (0, {}, 1, {"country": "Germany"}, 0.5, None, [(0, 1, "country", None, "Germany", 0.0, False)]),
    ],
    ids=[
        "match_above_threshold",
        "match_equal_threshold",
        "match_below_threshold",
        "only_in_source",
        "only_in_target",
    ],
)
@patch("reporting.mistakes_report.score_string_similarity")
def test_compare_dicts_keys_success(
    mock_score, source_index, source_item, target_index, target_item, threshold, similarity_score, expected
):
    if similarity_score is not None:
        mock_score.return_value = similarity_score
    result = compare_dicts_keys(source_index, source_item, target_index, target_item, threshold)
    assert result == expected


def test_compare_dicts_keys_empty_dicts():
    result = compare_dicts_keys(0, {}, 1, {}, 0.5)
    assert result == []


# evaluate_mistakes
@patch("reporting.mistakes_report.compare_dicts_keys")
def test_evaluate_mistakes_sucess(mock_compare):
    test_actual = [{"key1": "val1"}, {"key2": "val2"}]
    test_expected = [{"key1": "val1"}, {"key2": "val3"}]

    mock_compare.side_effect = [[(True,)], [(False,)], [(False,)], [(False,)]]

    result = evaluate_mistakes(test_actual, test_expected, 0.8)

    assert result == [(True,), (False,), (False,), (False,)]
    assert mock_compare.call_count == 4


@pytest.mark.parametrize(
    "test_actual,test_expected",
    [([{"key1": "val1"}, {"key2": "val2"}], []), ([], [{"key1": "val1"}, {"key2": "val2"}]), ([], [])],
)
def test_evaluate_mistakes_empty_list_inputs(test_actual, test_expected):

    result = evaluate_mistakes(test_actual, test_expected, 0.8)

    assert result == []


@pytest.mark.parametrize(
    "test_actual,test_expected",
    [
        ("no_list", [{"key": "value"}]),
        ([{"key": "value"}], "no_list"),
    ],
)
@patch("reporting.mistakes_report.compare_dicts_keys")
def test_evaluate_mistakes_invalid_inputs_raises_error(mock_compare, test_actual, test_expected):
    with pytest.raises(ValueError):
        evaluate_mistakes(test_actual, test_expected, 0.8)

    assert mock_compare.call_count == 0
