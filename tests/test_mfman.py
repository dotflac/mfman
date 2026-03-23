from pathlib import Path
from unittest.mock import MagicMock
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

    original_path = Path

    def mock_path(*args, **kwargs):
        if args and str(args[0]) == "output":
            return tmp_path / "output"
        return original_path(*args, **kwargs)

    mocker.patch("mfman.Path", side_effect=mock_path)

    mocker.patch("mfman.file_to_data_uri", return_value="data:audio/wav;base64,dummy")

    # We also mock the transcription read just to make it fast and isolated
    # Let's just use the real file since it exists in the workspace.
    # but we need to let open work for writing the binary file
    # Let's just create a dummy input/transcription.txt if it doesn't exist, but it DOES exist.
    # So we don't need to mock open, we can just use the real file.

    filepath = clone_voice("test prompt")

    assert "output" in filepath
    assert filepath.endswith(".wav")
    assert Path(filepath).exists()
    assert Path(filepath).read_bytes() == b"dummy audio data"

    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == "qwen/qwen3-tts"
    assert kwargs["input"]["text"] == "test prompt"
