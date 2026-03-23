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

## How It Works

1.  **Prompt Generation:** Uses `meta-llama-3-8b-instruct` on Replicate to create a new, uncensored "vibecoding" encouragement prompt based on examples in `input/prompt_examples.txt`.
2.  **Voice Cloning:** Uses `qwen/qwen3-tts` to clone the voice from `input/reference.wav` and read the generated prompt.
3.  **Playback:** Saves the generated audio in the `output/` directory and plays it in the background using `mpv`.

## Development

- **Formatting:** `uv run ruff format`
- **Linting:** `uv run ruff check`
- **Type Checking:** `uv run ty check`
- **Testing:** `uv run pytest` (uses mocks to avoid API costs)
