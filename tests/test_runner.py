from unittest.mock import patch, MagicMock
import pytest
from runner import validate_main_inputs, run_tests, summary_results, main


class TestValidateMainInputs:
    # test cases for validate_main_inputs
    def test_valid_inputs_file(self):
        # Should not raise anything
        validate_main_inputs(
            test_cases_file="cases.json",
            models=["gpt-3"],
            output_destination="save_to_file",
            prompt_template="Prompt",
            db_handler=None,
        )

    def test_invalid_inputs_db(self):
        validate_main_inputs(
            test_cases_file="cases.json",
            models=["gpt-3"],
            output_destination="save_to_db",
            prompt_template="Prompt",
            db_handler=MagicMock(),
        )

    @pytest.mark.parametrize("invalid_file", ["", "   ", None])
    def test_invalid_test_cases_file(self, invalid_file):
        with pytest.raises(
            ValueError, match="test_cases_file must be a non-empty string"
        ):
            validate_main_inputs(
                test_cases_file=invalid_file,
                models=["gpt-3"],
                output_destination="save_to_file",
                prompt_template="Prompt",
                db_handler=None,
            )

    @pytest.mark.parametrize("invalid_models", [[], None, "gpt-3"])
    def test_invalid_models(self, invalid_models):
        with pytest.raises(ValueError, match="models must be a non-empty list"):
            validate_main_inputs(
                test_cases_file="cases.json",
                models=invalid_models,
                output_destination="save_to_file",
                prompt_template="Prompt",
                db_handler=None,
            )

    @pytest.mark.parametrize("invalid_output", ["", "  ", None])
    def test_invalid_output_destination(self, invalid_output):
        with pytest.raises(
            ValueError, match="output_destination must be non-empty string."
        ):
            validate_main_inputs(
                test_cases_file="cases.json",
                models=["gpt-3"],
                output_destination=invalid_output,
                prompt_template="Prompt",
                db_handler=None,
            )

    @pytest.mark.parametrize("invalid_prompt", ["", "   ", None])
    def test_invalid_prompt_template(self, invalid_prompt):
        with pytest.raises(
            ValueError, match="prompt_template must be a non-empty string"
        ):
            validate_main_inputs(
                test_cases_file="cases.json",
                models=["gpt-3"],
                output_destination="save_to_file",
                prompt_template=invalid_prompt,
                db_handler=None,
            )

    def test_db_handler_required_for_db(self):
        with pytest.raises(ValueError, match="db_handler is required"):
            validate_main_inputs(
                test_cases_file="cases.json",
                models=["gpt-3"],
                output_destination="save_to_db",
                prompt_template="Prompt",
                db_handler=None,
            )


# test cases for main function
@pytest.fixture
def mock_prompt_builder():
    return MagicMock()


@pytest.fixture
def mock_client():
    return MagicMock()


# test cases for run_tests
def test_run_tests_multiple_models_and_cases(
    monkeypatch, mock_prompt_builder, mock_client
):
    test_cases = [{"input": "This is a test."}, {"input": "Another one."}]
    models = ["gpt-3", "gpt-4"]

    # monkeypatch evaluate_response() to always return True
    monkeypatch.setattr("runner.evaluate_response", lambda *args, **kwargs: True)

    with patch("runner.GrammarChecker") as mock_grammar_checker:
        mock_instance = mock_grammar_checker()
        mock_instance.check_grammar.return_value = "mocked_response"

        results = run_tests(test_cases, models, mock_prompt_builder, mock_client)

        assert len(results) == len(models) * len(test_cases)
        for result in results:
            assert result["model"] in models
            assert result["input"] in [tc["input"] for tc in test_cases]
            assert result["output"] == "mocked_response"
            assert isinstance(result["match"], bool)


def test_run_tests_handles_exception(
    monkeypatch, mock_prompt_builder, mock_client, caplog
):
    test_cases = [{"input": "Bad sentence"}]
    monkeypatch.setattr(
        "runner.GrammarChecker", MagicMock(side_effect=Exception("error"))
    )
    monkeypatch.setattr("runner.logger", MagicMock())

    with pytest.raises(Exception):
        run_tests(test_cases, ["gpt-3"], mock_prompt_builder, mock_client)
        assert "Unexpected error: error" in caplog.text


# unittest summary_results
def test_summary_results_multiple_models():
    results = [
        {"model": "gpt-2", "input": "Another one.", "match": False},
        {"model": "gpt-3", "input": "This is a test.", "match": True},
        {"model": "gpt-3", "input": "Another one.", "match": False},
        {"model": "gpt-4", "input": "This is a test.", "match": True},
    ]

    summary = summary_results(results)

    assert summary["gpt-2"]["total"] == 1
    assert summary["gpt-2"]["passed"] == 0
    assert summary["gpt-3"]["total"] == 2
    assert summary["gpt-3"]["passed"] == 1
    assert summary["gpt-4"]["total"] == 1
    assert summary["gpt-4"]["passed"] == 1


def test_summary_results_empty():
    assert summary_results([]) == {}


# integration test main function
@pytest.mark.parametrize(
    "output_destination, expect_db_call, expect_file_call, expected_log_msg",
    [
        ("save_to_db", True, False, "Saving test results to MongoDB"),
        ("save_to_file", False, True, "Saving test results to dummy_results.json"),
        (
            "invalid_option",
            False,
            False,
            "Invalid output option. Please refer to the help documentation for valid options.",
        ),
    ],
)
def test_main(output_destination, expect_db_call, expect_file_call, expected_log_msg):
    test_cases_file = "dummy_cases.json"
    models = ["gpt-3"]
    prompt_template = "template"
    mock_db_handler = MagicMock()

    dummy_test_cases = [{"input": "This is a test."}]
    dummy_results = [
        {
            "model": "gpt-3",
            "input": "This is a test.",
            "output": "output",
            "expected": {"input": "This is a test."},
            "match": True,
        }
    ]

    with (
        patch("runner.PromptBuilder") as mock_prompt_builder,
        patch("runner.OpenAIClient") as mock_client,
        patch(
            "runner.load_test_cases", return_value=dummy_test_cases
        ) as mock_load_test_cases,
        patch("runner.run_tests", return_value=dummy_results) as mock_run_tests,
        patch("runner.summary_results") as mock_summary,
        patch("runner.save_test_results") as mock_save_test_results,
        patch("runner.TEST_RESULTS_FILE", "dummy_results.json"),
        patch("runner.logger") as mock_logger,
    ):
        main(
            test_cases_file,
            models,
            output_destination,
            prompt_template,
            mock_db_handler,
        )

        # --- Control Flow ---
        mock_prompt_builder.assert_called_once_with(prompt_template)
        mock_client.assert_called_once()
        mock_load_test_cases.assert_called_once_with(test_cases_file)
        mock_run_tests.assert_called_once_with(
            dummy_test_cases,
            models,
            mock_prompt_builder.return_value,
            mock_client.return_value,
        )
        mock_summary.assert_called_once_with(dummy_results)

        # --- Output / Side Effects ---
        if expect_db_call:
            mock_db_handler.save_record.assert_called_once()
            mock_save_test_results.assert_not_called()
            mock_logger.info.assert_any_call(expected_log_msg)
        if expect_file_call:
            mock_save_test_results.assert_called_once()
            mock_db_handler.save_record.assert_not_called()
            mock_logger.info.assert_any_call(expected_log_msg)
        if not expect_db_call and not expect_file_call:
            mock_db_handler.save_record.assert_not_called()
            mock_save_test_results.assert_not_called()
            mock_logger.error.assert_any_call(expected_log_msg)
