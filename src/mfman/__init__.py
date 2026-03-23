import time
import subprocess
import base64
import mimetypes
import logging
import tomllib
from pathlib import Path
import replicate
from platformdirs import user_log_path, user_data_path, user_config_path
import importlib.resources


class Config:
    def __init__(self):
        self.config_dir = user_config_path("mfman")
        self.config_file = self.config_dir / "config.toml"

        # Default settings
        self.prompt_model = "meta/meta-llama-3-8b-instruct"
        self.tts_model = "qwen/qwen3-tts"
        self.playback_command = ["mpv"]
        self.sleep_interval = 10

        self._load_config()

    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "rb") as f:
                    data = tomllib.load(f)
                    self.prompt_model = data.get("prompt_model", self.prompt_model)
                    self.tts_model = data.get("tts_model", self.tts_model)
                    self.playback_command = data.get(
                        "playback_command", self.playback_command
                    )
                    self.sleep_interval = data.get("sleep_interval", self.sleep_interval)
            except Exception as e:
                logging.error(f"Failed to load config from {self.config_file}: {e}")

    def get_asset_path(self, filename: str) -> Path:
        user_asset = self.config_dir / "assets" / filename
        if user_asset.exists():
            logging.debug(f"Using user asset: {user_asset}")
            return user_asset

        # Fallback to package assets
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


def generate_prompt(config: Config) -> str:
    logging.info("Generating new prompt from examples")
    examples_path = config.get_asset_path("prompt_examples.txt")
    with open(examples_path, "r", encoding="utf-8") as f:
        examples = f.read()

    prompt_instruction = (
        "Generate a single new encouraging statement for Morgan Freeman to say to a vibe-coder "
        "or hacker. Be creative. You can be crass or unsavoury. Use the same style, tone and "
        "vocabulary as these examples. Do not include any introductory text or explanations, "
        "just output the generated prompt.\n\n"
        f"Examples:\n{examples}"
    )

    output = replicate.run(config.prompt_model, input={"prompt": prompt_instruction})

    generated_text = "".join(output).strip()
    logging.info(f"Generated prompt: {generated_text}")
    return generated_text


def clone_voice(prompt: str, config: Config) -> str:
    logging.info(f"Cloning voice for prompt: {prompt}")

    transcription_path = config.get_asset_path("transcription.txt")
    with open(transcription_path, "r", encoding="utf-8") as f:
        reference_text = f.read().strip()

    reference_audio_path = config.get_asset_path("reference.wav")
    reference_audio_uri = file_to_data_uri(reference_audio_path)

    output = replicate.run(
        config.tts_model,
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
    config = Config()
    try:
        new_prompt = generate_prompt(config)
        time.sleep(
            config.sleep_interval
        )  # Sleep to avoid rate limiting between API calls for low-credit accounts
        audio_filepath = clone_voice(new_prompt, config)

        logging.info(f"Playing audio: {audio_filepath}")
        subprocess.Popen(
            [*config.playback_command, audio_filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        logging.error(f"Error during execution: {e}", exc_info=True)
        raise
