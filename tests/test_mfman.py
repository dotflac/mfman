from pathlib import Path
from unittest.mock import MagicMock
import pytest
from mfman import file_to_data_uri, generate_prompt, clone_voice


def test_file_to_data_uri(tmp_path):
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("hello world")
    uri = file_to_data_uri(str(dummy_file))
    assert uri.startswith("data:text/plain;base64,")
    assert uri.endswith("aGVsbG8gd29ybGQ=")


def test_generate_prompt(mocker, tmp_path):
    mock_run = mocker.patch("mfman.replicate.run")
    mock_run.return_value = ["This is a ", "mocked prompt."]

    # Mock get_asset_path to return a temporary file
    dummy_examples = tmp_path / "prompt_examples.txt"
    dummy_examples.write_text("Example 1\nExample 2")
    mocker.patch("mfman.get_asset_path", return_value=dummy_examples)

    prompt = generate_prompt()

    assert prompt == "This is a mocked prompt."
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == "meta/meta-llama-3-8b-instruct"


def test_clone_voice(mocker, tmp_path):
    mock_output = MagicMock()
    mock_output.read.return_value = b"dummy audio data"

    mock_run = mocker.patch("mfman.replicate.run")
    mock_run.return_value = mock_output

    # Mock get_asset_path to return temporary files
    dummy_transcription = tmp_path / "transcription.txt"
    dummy_transcription.write_text("dummy transcription")
    dummy_wav = tmp_path / "reference.wav"
    dummy_wav.write_bytes(b"dummy wav data")

    def mock_get_asset_path(filename):
        if filename == "transcription.txt":
            return dummy_transcription
        if filename == "reference.wav":
            return dummy_wav
        return Path(filename)

    mocker.patch("mfman.get_asset_path", side_effect=mock_get_asset_path)

    # Mock user_data_path to return a temporary directory
    mock_user_data_path = tmp_path / "user_data"
    mocker.patch("mfman.user_data_path", return_value=mock_user_data_path)

    mocker.patch("mfman.file_to_data_uri", return_value="data:audio/wav;base64,dummy")

    filepath = clone_voice("test prompt")

    assert "output" in filepath
    assert filepath.endswith(".wav")
    assert Path(filepath).exists()
    assert Path(filepath).read_bytes() == b"dummy audio data"
    assert str(mock_user_data_path) in filepath

    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == "qwen/qwen3-tts"
    assert kwargs["input"]["text"] == "test prompt"
