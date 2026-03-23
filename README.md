# mfman

`mfman` is a CLI tool that uses AI to clone Morgan Freeman's voice and encourages you to "vibecode" harder. It automatically generates a new, uncensored prompt based on examples, clones the voice of Morgan Freeman to read it, and plays the resulting audio.

## Prerequisites

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv)
- [mpv](https://mpv.io/) (for audio playback)
- A [Replicate](https://replicate.com/) account and API token.

## Setup

1.  **Clone the repository.**
2.  **Set your Replicate API token:**
    ```bash
    export REPLICATE_API_TOKEN='your_api_token_here'
    ```
    Alternatively, you can create a `.env` file (which is ignored by git) and add it there:
    ```
    REPLICATE_API_TOKEN=your_api_token_here
    ```

## Usage

Run the following command to generate a new prompt and hear the encouragement from Morgan Freeman:

```bash
uv run mfman
```

## Configuration

`mfman` supports user configuration via a `config.toml` file.

- **Linux:** `~/.config/mfman/config.toml`
- **macOS:** `~/Library/Application Support/mfman/config.toml`
- **Windows:** `%AppData%\mfman\config.toml`

See [config.toml.example](config.toml.example) for available options, including:
- `prompt_model`: Change the LLM used for prompt generation.
- `tts_model`: Change the TTS model used for voice cloning.
- `playback_command`: Change the command used to play audio (e.g., `["ffplay", "-nodisp", "-autoexit"]`).
- `sleep_interval`: Adjust the delay between API calls.

### Overriding Assets

You can override the default assets by placing your own files in the `assets` directory within your configuration folder (e.g., `~/.config/mfman/assets/`).

Supported overrides:
- `prompt_examples.txt`: Custom examples for the prompt generator.
- `reference.wav`: A different reference voice for cloning.
- `transcription.txt`: The transcription of your custom `reference.wav`.

## How It Works

1.  **Prompt Generation:** Uses an LLM (default: `meta-llama-3-8b-instruct`) on Replicate to create a new, uncensored "vibecoding" encouragement prompt based on examples in `prompt_examples.txt`.
2.  **Voice Cloning:** Uses a TTS model (default: `qwen/qwen3-tts`) to clone the voice from `reference.wav` and read the generated prompt.
3.  **Playback:** Saves the generated audio in the user data directory and plays it in the background (default command: `mpv`).

## Development

- **Formatting:** `uv run ruff format`
- **Linting:** `uv run ruff check`
- **Type Checking:** `uv run ty check`
- **Testing:** `uv run pytest` (uses mocks to avoid API costs)
