import pytest
from argparse import Namespace
from unittest.mock import patch
from main import main


def make_fake_args(mode="run_tests"):
    return Namespace(
        mode=mode,
        output="save_to_db",
        api_host="127.0.0.1",
        api_port=8000,
        models=["gpt-3"],
        prompt_template="template",
        test_cases="cases.json",
        debug=False,
    )


@pytest.mark.parametrize(
    "test_mode, expected_func",
    [
        ("run_tests", "main.run_tests"),
        ("interactive", "main.start_interactive_mode"),
        ("api", "main.uvicorn.run"),
        ("invalid_mode", None),  # This should raise an exception
    ],
)
def test_main_control_flow_by_mode(test_mode, expected_func):
    fake_args = make_fake_args(mode=test_mode)

    with (
        patch("main.get_logger") as mock_get_logger,
        patch("main.parse_arguments", return_value=fake_args) as mock_parse_args,
        patch("main.MONGO_URI", "dummy_uri"),  # <-- patch constants to what you expect
        patch("main.MONGO_DB", "dummy_db"),
        patch("main.MONGO_COLLECTION", "dummy_results"),
        patch("main.MongoDBHandler") as mock_db_handler,
        patch("main.run_tests") as mock_run_tests,
        patch("main.uvicorn.run") as mock_uvicorn,
        patch("main.start_interactive_mode") as mock_interactive,
    ):
        if test_mode == "invalid_mode":
            with pytest.raises(ValueError, match="Invalid mode selected.*"):
                main()
        else:
            main()

        # Check that the correct function was called based on the mode
        mock_get_logger.assert_called_once()
        mock_parse_args.assert_called_once()
        mock_db_handler.assert_called_once_with(
            "dummy_uri",
            "dummy_db",
            "dummy_results",
        )

        if test_mode == "run_tests":
            mock_run_tests.assert_called_once()
        elif test_mode == "interactive":
            mock_interactive.assert_called_once()
        elif test_mode == "api":
            mock_uvicorn.assert_called_once_with(
                "api:app", host=fake_args.api_host, port=fake_args.api_port, reload=True
            )
