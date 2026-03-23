import time
import subprocess
import base64
import mimetypes
import logging
from pathlib import Path
import replicate
from platformdirs import user_log_path, user_data_path
import importlib.resources


def get_asset_path(filename: str) -> Path:
    # Use importlib.resources to access assets within the package
    # In Python 3.12+, .files() returns a Traversable, which can be cast to Path if needed
    # for open(), but it usually works directly.
    return Path(str(importlib.resources.files("mfman.assets").joinpath(filename)))


def setup_logging():
    log_dir = user_log_path("mfman")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "mfman.log"

    logging.basicConfig(
        filename=str(log_file),
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return log_file


def file_to_data_uri(filepath: Path | str) -> str:
    logging.debug(f"Converting {filepath} to Data URI")
    mime_type, _ = mimetypes.guess_type(str(filepath))
    if not mime_type:
        mime_type = "application/octet-stream"

    with open(filepath, "rb") as f:
        data = f.read()
        base64_encoded = base64.b64encode(data).decode("utf-8")

    return f"data:{mime_type};base64,{base64_encoded}"


def generate_prompt() -> str:
    logging.info("Generating new prompt from examples")
    examples_path = get_asset_path("prompt_examples.txt")
    with open(examples_path, "r", encoding="utf-8") as f:
        examples = f.read()

    prompt_instruction = (
        "Generate a single new encouraging statement for Morgan Freeman to say to a vibe-coder "
        "or hacker. Be creative. You can be crass or unsavoury. Use the same style, tone and "
        "vocabulary as these examples. Do not include any introductory text or explanations, "
        "just output the generated prompt.\n\n"
        f"Examples:\n{examples}"
    )

    output = replicate.run(
        "meta/meta-llama-3-8b-instruct", input={"prompt": prompt_instruction}
    )

    generated_text = "".join(output).strip()
    logging.info(f"Generated prompt: {generated_text}")
    return generated_text


def clone_voice(prompt: str) -> str:
    logging.info(f"Cloning voice for prompt: {prompt}")

    transcription_path = get_asset_path("transcription.txt")
    with open(transcription_path, "r", encoding="utf-8") as f:
        reference_text = f.read().strip()

    reference_audio_path = get_asset_path("reference.wav")
    reference_audio_uri = file_to_data_uri(reference_audio_path)

    output = replicate.run(
        "qwen/qwen3-tts",
        input={
            "mode": "voice_clone",
            "text": prompt,
            "reference_text": reference_text,
            "reference_audio": reference_audio_uri,
        },
    )

    output_dir = user_data_path("mfman") / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{time.time()}.wav"
    filepath = output_dir / filename

    with open(filepath, "wb") as file:
        file.write(output.read())  # type: ignore

    logging.info(f"Saved audio to {filepath}")
    return str(filepath)


def main() -> None:
    log_file = setup_logging()
    logging.info(f"Starting main execution. Logging to {log_file}")
    try:
        new_prompt = generate_prompt()
        time.sleep(
            10
        )  # Sleep to avoid rate limiting between API calls for low-credit accounts
        audio_filepath = clone_voice(new_prompt)

        logging.info(f"Playing audio: {audio_filepath}")
        subprocess.Popen(
            ["mpv", audio_filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        logging.error(f"Error during execution: {e}", exc_info=True)
        raise
