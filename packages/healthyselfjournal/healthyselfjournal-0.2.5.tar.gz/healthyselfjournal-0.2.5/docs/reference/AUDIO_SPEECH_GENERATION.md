## Introduction

Optional speech output speaks the assistant’s questions out loud during the journaling loop. It uses OpenAI TTS by default and local playback via `afplay` on macOS (with `ffplay` as a fallback). Only assistant questions are spoken; summaries and status remain text.

This document covers design principles, configuration, architecture, how‑tos, troubleshooting, limitations, and planned work.

## See also

- `CLI_RECORDING_INTERFACE.md` – CLI flags (`--voice-mode`, `--tts-voice`, `--tts-model`, `--tts-format`) and environment requirements.
- `DIALOGUE_FLOW.md` – Where the assistant question is generated within the session loop.
- `AUDIO_VOICE_RECOGNITION_WHISPER.md` – STT capture/processing; ensures we don’t record while TTS is playing.
- `BACKGROUND_PROCESSING.md` – Summary regeneration is scheduled in the background; TTS runs in the foreground just before the next capture.
- `FILE_FORMATS_ORGANISATION.md` – Session files; TTS audio is not persisted (temporary only).
- Code: `healthyselfjournal/cli.py` (flags and orchestration), `healthyselfjournal/tts.py` (synthesis + playback), `healthyselfjournal/config.py` (defaults and user preference), `healthyselfjournal/session.py` (loop), `healthyselfjournal/events.py` (metadata logging).

## Principles and key decisions

- Speak only the assistant’s question. Avoids long-form narration and keeps pacing tight.
- Default to OpenAI TTS for quality; add privacy-first/backends later (e.g., `macos-say`).
- Keep the microphone closed during playback to prevent echo/feedback.
- If speech is enabled, disable streaming text display for clarity (still print the full question non‑streaming).
- Fail soft: if TTS fails, continue with text-only without breaking the session.
- Do not persist TTS audio to disk; use temp files only. Log metadata, never content.

## Architecture

### Flow

1. Capture response and transcribe.
2. Generate next question (LLM; when asked "give me a question", model selects from embedded examples).
3. If `--voice-mode` is enabled:
   - Synthesize speech via OpenAI TTS.
   - Write bytes to a temp file; play via `afplay` (macOS) or `ffplay`.
   - Return to the loop and begin the next recording.

The microphone is not active during playback; recording starts after playback completes.

### Components

- `healthyselfjournal/config.py`
  - `speak_llm: bool` – feature toggle.
  - `tts_model`, `tts_voice`, `tts_format`, `tts_backend` – user preferences and defaults.
- `healthyselfjournal/cli.py`
  - CLI options: `--voice-mode`, `--tts-model`, `--tts-voice`, `--tts-format`.
  - Requires `OPENAI_API_KEY` when speech is enabled (OpenAI backend).
  - Auto-disables `--stream-llm` when speaking.
- `healthyselfjournal/tts.py`
  - `speak_text(text, TTSOptions)` – orchestrates synthesis and playback.
  - OpenAI synthesis (non-streaming, with streaming fallback) → temp file → `afplay`/`ffplay`.
  - During playback, pressing ENTER skips the spoken question immediately.
- `healthyselfjournal/session.py`
  - Prints the question and then records user audio; TTS is invoked from the CLI loop just before recording starts.
- `healthyselfjournal/events.py`
  - Logs `tts.request`, `tts.response`, `tts.error` with metadata (no content).

## How to use

- Enable speech:
```bash
uv run --active healthyselfjournal journal cli --voice-mode
```

- Environment:
  - `ANTHROPIC_API_KEY` – required when the journaling loop uses `anthropic:*` models (default cloud mode).
  - `OPENAI_API_KEY` – required when `--voice-mode` is enabled (OpenAI TTS) and when `--stt-backend cloud-openai`.

- Format selection:
  - `--tts-format wav` (default) is recommended for reliable playback across players.

## Troubleshooting

- “attempted relative import with no known parent package” when launching:
  - Prefer running via `uvx`: `uvx healthyselfjournal -- journal cli ...`.
  - Or, inside an active virtualenv, use: `uv run --active healthyselfjournal journal cli ...`.

- “No audio player found (tried afplay, ffplay)”:
  - On macOS, `afplay` should exist; otherwise install `ffmpeg` to get `ffplay` on PATH.

- TTS fails intermittently or returns silence:
  - Check `OPENAI_API_KEY` and network; review `sessions/events.log` for `tts.error` entries.
  - Long prompts may increase latency; keep assistant questions concise.

- Echo/feedback in recordings:
  - Ensure external speakers aren’t overly loud; consider headphones.
  - Confirm that recording starts only after playback completes (expected behavior).

## Gotchas and limitations

- Only assistant questions are spoken; summaries and status remain text.
- Streaming text display is auto-disabled when speech is enabled.
- OpenAI is the only synthesis backend at present; audio is not persisted.
- Playback relies on `afplay` (macOS) or `ffplay` if available; other platforms pending.

## Planned enhancements

- Privacy-first local synthesis (e.g., `macos-say`) selectable via `tts_backend`.
- Streaming TTS for lower perceived latency and barge‑in style playback.
- SSML support and richer prosody controls.
- Caching repeated utterances to reduce latency.
- Wider cross‑platform playback and backend options.

## Appendix

### Events

- `tts.request`: `{ backend, model, voice, format }`
- `tts.response`: `{ backend, model, voice, format, bytes, mode? }`
- `tts.error`: `{ backend, model, voice, format, error_type, error }`

### Configuration keys and defaults

- `speak_llm = False` (enabled indirectly by `--voice-mode`)
- `tts_backend = "openai"`
- `tts_model = "gpt-4o-mini-tts"`
- `tts_voice = "shimmer"`
- `tts_format = "wav"`

