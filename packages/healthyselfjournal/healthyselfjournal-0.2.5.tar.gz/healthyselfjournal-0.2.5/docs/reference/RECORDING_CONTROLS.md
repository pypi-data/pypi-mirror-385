# Recording Controls (shared CLI/Web)

## Overview

Keyboard controls for voice recording and session management.

## See also

- `CLI_RECORDING_INTERFACE.md` - CLI flags and display modes
- `WEB_RECORDING_INTERFACE.md` - Web run instructions
- `DIALOGUE_FLOW.md` - Session flow after recording
- `FILE_FORMATS_ORGANISATION.md` - What gets saved when

## Recording Flow

1. Recording starts immediately on command launch
2. Visual volume meter shows recording active
3. Press SPACE to pause/resume; press any other key to stop recording (when paused, the volume meter is hidden and a "Paused" label is shown)
4. If the captured answer is extremely short and low‑voiced, it is discarded automatically (no files saved, no transcription)
5. Otherwise, Whisper transcribes to text
6. LLM generates response question

## Session Controls

- **SPACE**: Pause/resume the recording (paused audio is not saved; meter hidden while paused)
- **Q**: Quit after this response
  - If pressed early (duration < 5s by default): the take is auto‑discarded and the session ends cleanly
  - If pressed after a normal answer: the take is saved/transcribed, then the session ends
  - Threshold is configurable via `CONFIG.quit_discard_duration_seconds`

### Known Issue

- On some terminals, the ESC key may require a second press to cancel reliably and can be interpreted as a generic stop on the first press. As a result, the in-app hints omit the ESC instruction for now. Cancellation still works but may be inconsistent across environments. Tracking for a more robust fix.

## Error Prevention

- Short accidental takes are auto‑discarded
- Audio saved to .wav; optional .mp3 conversion queued when available
- Transcript saved after each transcription
- Summary updated after each exchange