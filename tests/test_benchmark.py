import pytest
from unittest.mock import patch, MagicMock
import mongomock
import json
from types import SimpleNamespace
from grammar_checker.db import MongoDBHandler
from models.response import GrammarResponse
from benchmark import validate_main_inputs, run_tests, summary_results, main
from grammar_checker.config import VALID_MODELS, DEFAULT_PROMPT_TEMPLATE


class TestValidateMainInputs:
    valid_test_cases_file = "cases.json"
    valid_models = VALID_MODELS
    valid_prompt_templates = [DEFAULT_PROMPT_TEMPLATE]

    # test cases for validate_main_inputs
    def test_valid_inputs_file(self):
        # Should not raise anything
        validate_main_inputs(
            test_cases_file=self.valid_test_cases_file,
            models=self.valid_models,
            output_destination="save_to_file",
            prompt_templates=self.valid_prompt_templates,
            db_handler=None,
        )

    def test_invalid_inputs_db(self):
        validate_main_inputs(
            test_cases_file=self.valid_test_cases_file,
            models=self.valid_models,
            output_destination="save_to_db",
            prompt_templates=self.valid_prompt_templates,
            db_handler=MagicMock(),
        )

    @pytest.mark.parametrize("invalid_file", ["", "   ", None])
    def test_invalid_test_cases_file(self, invalid_file):
        with pytest.raises(ValueError, match="test_cases_file must be a non-empty string"):
            validate_main_inputs(
                test_cases_file=invalid_file,
                models=self.valid_models,
                output_destination="save_to_file",
                prompt_templates=self.valid_prompt_templates,
                db_handler=None,
            )

    @pytest.mark.parametrize("invalid_models", [[], None, "gpt-3"])
    def test_invalid_models(self, invalid_models):
        with pytest.raises(ValueError, match="models must be a non-empty list"):
            validate_main_inputs(
                test_cases_file=self.valid_test_cases_file,
                models=invalid_models,
                output_destination="save_to_file",
                prompt_templates=self.valid_prompt_templates,
                db_handler=None,
            )

    @pytest.mark.parametrize("invalid_output", ["", "  ", None])
    def test_invalid_output_destination(self, invalid_output):
        with pytest.raises(ValueError, match="output_destination must be non-empty string."):
            validate_main_inputs(
                test_cases_file=self.valid_test_cases_file,
                models=self.valid_models,
                output_destination=invalid_output,
                prompt_templates=self.valid_prompt_templates,
                db_handler=None,
            )

    @pytest.mark.parametrize(
        "invalid_prompt, expected_msg",
        [
            ([], "prompt_template must be a non-empty list of prompt templates"),
            ("invalid_prompt.txt", "prompt_template must be a non-empty list of prompt templates"),
            (None, "prompt_template must be a non-empty list of prompt templates"),
            ([""], "Each prompt template must be a string"),
            (["   "], "Each prompt template must be a string"),
            (["invalid_prompt.txt"], "Prompt template 'invalid_prompt.txt' does not exist."),
        ],
    )
    def test_invalid_prompt_template(self, invalid_prompt, expected_msg):
        with pytest.raises(ValueError, match=expected_msg):
            validate_main_inputs(
                test_cases_file=self.valid_test_cases_file,
                models=self.valid_models,
                output_destination="save_to_file",
                prompt_templates=invalid_prompt,
                db_handler=None,
            )

    def test_db_handler_required_for_db(self):
        with pytest.raises(ValueError, match="db_handler is required"):
            validate_main_inputs(
                test_cases_file=self.valid_test_cases_file,
                models=self.valid_models,
                output_destination="save_to_db",
                prompt_templates=self.valid_prompt_templates,
                db_handler=None,
            )


# test cases for main function
@pytest.fixture
def mock_prompt_builder():
    return MagicMock()


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def mock_mongo_handler():
    # Use mongomock directly, no URI needed
    client = mongomock.MongoClient()
    db = client["test_db"]
    collection = db["test_collection"]

    handler = MongoDBHandler(uri="mock_uri", database_name="test_db", collection_name="test_collection")
    handler.client = client
    handler.database = db
    handler.collection = collection
    
    # Mock the connect method to assign the mock client, db, and collection
    def mock_connect():
        handler.client = client
        handler.database = db
        handler.collection = collection
        return handler

    # Mock the disconnect method
    handler.disconnect = MagicMock()

    # Patch connect to mock behavior
    handler.connect = mock_connect

    # Simulate context manager behavior
    handler.__enter__ = lambda self=handler: handler.connect()
    handler.__exit__ = lambda self, exc_type, exc_val, exc_tb: handler.disconnect()

    yield handler


def fake_grammar_request(prompt_version, model, sentence):
    return SimpleNamespace(prompt_version=prompt_version, model=model, sentence=sentence)


# test cases for run_tests
def test_run_tests_multiple_combinations(monkeypatch, mock_prompt_builder, mock_client):
    models = ["gpt-3", "gpt-4"]
    templates = ["template1.txt", "template2.txt"]
    test_cases = [{"test_id": 1, "input": "This is a test."}, {"test_id": 2, "input": "Another one."}]

    # monkeypatch evaluate_response() to always return True
    monkeypatch.setattr("benchmark.evaluate_response", lambda *args, **kwargs: True)

    with (
        patch("benchmark.GrammarChecker") as mock_grammar_checker,
        patch("benchmark.PromptBuilder", return_value=mock_prompt_builder),
    ):
        mock_instance = mock_grammar_checker()
        mock_instance.check_grammar.return_value = GrammarResponse(
            input="This is a test.",
            mistakes=[],
            corrected_sentence="This is a test.",
        )

        test_response_json = mock_instance.check_grammar.return_value
        results = run_tests(test_cases, models, templates, mock_client)

        assert len(results) == len(models) * len(templates) * len(test_cases)
        for result in results:
            assert result["request"].model in models
            assert result["request"].prompt_version in templates
            assert result["request"].sentence in [tc["input"] for tc in test_cases]
            assert result["response"] == test_response_json
            assert isinstance(result["benchmark_eval"]["match"], bool)


def test_run_tests_handles_exception(monkeypatch, mock_prompt_builder, mock_client, caplog):
    test_cases = [{"input": "Bad sentence"}]
    monkeypatch.setattr("benchmark.GrammarChecker", MagicMock(side_effect=Exception("error")))
    monkeypatch.setattr("benchmark.logger", MagicMock())

    with pytest.raises(Exception):
        run_tests(test_cases, ["gpt-3"], mock_prompt_builder, mock_client)
        assert "Unexpected error: error" in caplog.text


# unittest summary_results
def test_summary_results_multiple_models():
    results = [
        {"request": fake_grammar_request("v1_test", "gpt-2", "Another one."), "benchmark_eval": {"match": False}},
        {"request": fake_grammar_request("v1_test", "gpt-3", "This is a test."), "benchmark_eval": {"match": True}},
        {"request": fake_grammar_request("v1_test", "gpt-3", "Another one."), "benchmark_eval": {"match": False}},
        {"request": fake_grammar_request("v1_test", "gpt-4", "This is a test."), "benchmark_eval": {"match": True}},
        {"request": fake_grammar_request("v2_test", "gpt-3", "Another one."), "benchmark_eval": {"match": False}},
        {"request": fake_grammar_request("v2_test", "gpt-4", "This is a test."), "benchmark_eval": {"match": True}},
    ]

    summary = summary_results(results)

    assert summary["v1_test"]["gpt-2"]["total"] == 1
    assert summary["v1_test"]["gpt-2"]["passed"] == 0
    assert summary["v1_test"]["gpt-3"]["total"] == 2
    assert summary["v1_test"]["gpt-3"]["passed"] == 1
    assert summary["v1_test"]["gpt-4"]["total"] == 1
    assert summary["v1_test"]["gpt-4"]["passed"] == 1
    assert summary["v2_test"]["gpt-3"]["total"] == 1
    assert summary["v2_test"]["gpt-3"]["passed"] == 0
    assert len(summary["v2_test"]) == 2


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
    prompt_templates = ["template"]
    mock_db_handler = MagicMock()
    mock_db_handler.__enter__.return_value = mock_db_handler  # return value of context manager

    dummy_test_cases = [{"input": "This is a test."}]
    dummy_results = [
        {
            "request": {"sentence": "This is a test.", "prompt_version": prompt_templates[0], "model": models[0]},
            "response": "mock_response",
            "benchmark_eval": {"match": True, "benchmark_eval": {"input": "This is a test."}},
        }
    ]

    with (
        patch("benchmark.validate_main_inputs"),
        patch("benchmark.OpenAIClient") as mock_client,
        patch("benchmark.load_test_cases", return_value=dummy_test_cases) as mock_load_test_cases,
        patch("benchmark.run_tests", return_value=dummy_results) as mock_run_tests,
        patch("benchmark.summary_results") as mock_summary,
        patch("benchmark.save_test_results") as mock_save_test_results,
        patch("benchmark.TEST_RESULTS_FILE", "dummy_results.json"),
        patch("benchmark.logger") as mock_logger,
    ):
        main(
            test_cases_file,
            models,
            output_destination,
            prompt_templates,
            mock_db_handler,
        )

        # --- Control Flow ---
        mock_client.assert_called_once()
        mock_load_test_cases.assert_called_once_with(test_cases_file)
        mock_run_tests.assert_called_once_with(
            dummy_test_cases,
            models,
            prompt_templates,
            mock_client.return_value,
        )
        mock_summary.assert_called_once_with(dummy_results)

        # --- Output / Side Effects ---
        if expect_db_call:
            mock_db_handler.save_record.assert_called_once()
            mock_save_test_results.assert_not_called()
            mock_logger.info.assert_any_call(expected_log_msg)
        # if expect_file_call:
        #     mock_save_test_results.assert_called_once()
        #     mock_db_handler.save_record.assert_not_called()
        #     mock_logger.info.assert_any_call(expected_log_msg)
        if not expect_db_call and not expect_file_call:
            mock_db_handler.save_record.assert_not_called()
            mock_save_test_results.assert_not_called()
            mock_logger.error.assert_any_call(expected_log_msg)


@pytest.mark.parametrize(
    "output_destination, expect_db_call, expect_file_call, expected_log_msg",
    [
        ("save_to_db", True, False, "Saving test results to MongoDB"),
        # ("save_to_file", False, True, "Saving test results to dummy_results.json"),
        (
            "invalid_option",
            False,
            False,
            "Invalid output option. Please refer to the help documentation for valid options.",
        ),
    ],
)
def test_main_integration(
    output_destination, expect_db_call, expect_file_call, expected_log_msg, tmp_path, mock_mongo_handler
):
    # Setup: write dummy test case file
    test_cases = [
        {
            "test_id": "test_001",
            "input": "This is a test.",
            "mistakes": [],
            "corrected_sentence": "This is a test.",
        }
    ]
    test_cases_file = tmp_path / "dummy_cases.json"
    test_cases_file.write_text(json.dumps(test_cases, indent=2))

    models = ["gpt-4"]
    prompt_templates = ["v1_original.txt"]

    with (
        patch("benchmark.OpenAIClient") as MockClientClass,
        patch("benchmark.MongoDBHandler", return_value=mock_mongo_handler),
        patch("benchmark.logger") as mock_logger,
        patch("benchmark.TEST_RESULTS_FILE", str(tmp_path / "dummy_results.json")),
    ):
        # Return a dummy client with mocked .check() if needed
        test_response = {
            "input": "test_input", 
            "mistakes": [{"type": "test_mistake"}], 
            "corrected_sentence": "test_corr"}
        mock_client = MagicMock()
        MockClientClass.return_value = mock_client
        mock_client.get_model_response.return_value = test_response

        main(
            str(test_cases_file),
            models,
            output_destination,
            prompt_templates,
            mock_mongo_handler,
        )

        # Assertions
        if expect_db_call:
            assert mock_mongo_handler.collection is not None
            saved_docs = list(mock_mongo_handler.collection.find({}))
            assert len(saved_docs) == 1
            assert saved_docs[0]["request"]["sentence"] == "This is a test."
            mock_logger.info.assert_any_call(expected_log_msg)

        # elif expect_file_call:
        #     result_file = tmp_path / "dummy_results.json"
        #     assert result_file.exists()
        #     assert "This is a test." in result_file.read_text()
        #     mock_logger.info.assert_any_call(expected_log_msg)

        else:
            mock_logger.error.assert_any_call(expected_log_msg)
