import os
import tempfile
import pytest
from grammar_checker.prompt_builder import PromptBuilder


class DummyLogger:
    def __init__(self):
        self.messages = []

    def info(self, msg):
        self.messages.append(("info", msg))

    def error(self, msg):
        self.messages.append(("error", msg))


def test_load_template_success(monkeypatch):
    # Create a temporary template file
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp.write("Correct this: {sentence}")
        tmp_path = tmp.name

    # Patch logger to avoid side effects
    monkeypatch.setattr("grammar_checker.prompt_builder.logger", DummyLogger())

    builder = PromptBuilder(tmp_path)
    assert builder.template == "Correct this: {sentence}"

    os.remove(tmp_path)


def test_load_template_file_not_found(monkeypatch):
    monkeypatch.setattr("grammar_checker.prompt_builder.logger", DummyLogger())
    with pytest.raises(FileNotFoundError):
        PromptBuilder("nonexistent_template.txt")


def test_load_template_other_exception(monkeypatch):
    # Simulate open() raising an unexpected exception
    monkeypatch.setattr("grammar_checker.prompt_builder.logger", DummyLogger())

    def bad_open(*a, **kw):
        raise OSError("fail")

    monkeypatch.setattr("builtins.open", bad_open)
    with pytest.raises(OSError):
        PromptBuilder("irrelevant.txt")


def test_build_prompt_success(monkeypatch):
    # Patch logger to avoid side effects
    monkeypatch.setattr("grammar_checker.prompt_builder.logger", DummyLogger())
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp.write("Check: {sentence}")
        tmp_path = tmp.name

    builder = PromptBuilder(tmp_path)
    prompt = builder.build_prompt("This is a test.")
    assert prompt == "Check: This is a test."

    os.remove(tmp_path)


def test_build_prompt_empty_sentence(monkeypatch):
    monkeypatch.setattr("grammar_checker.prompt_builder.logger", DummyLogger())
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp.write("Prompt: {sentence}")
        tmp_path = tmp.name

    builder = PromptBuilder(tmp_path)
    with pytest.raises(ValueError):
        builder.build_prompt("")

    os.remove(tmp_path)


def test_build_prompt_long_sentence_truncation(monkeypatch):
    # Patch logger to capture info
    logger = DummyLogger()
    monkeypatch.setattr("grammar_checker.prompt_builder.logger", logger)
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp.write("Prompt: {sentence}")
        tmp_path = tmp.name

    builder = PromptBuilder(tmp_path)
    long_sentence = "a" * 50
    builder.build_prompt(long_sentence)
    # Check that the logger.info call contains the truncated sentence
    found = any(
        "aaaaaaaaaaaaaaaaaaaa..." in msg
        for level, msg in logger.messages
        if level == "info"
    )
    assert found

    os.remove(tmp_path)
