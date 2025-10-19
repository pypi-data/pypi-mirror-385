from __future__ import annotations

"""Markdown persistence and frontmatter utilities."""

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, MutableMapping

import yaml

_LOGGER = logging.getLogger(__name__)

from .utils.pending import placeholder_block, placeholder_comment


FRONTMATTER_KEYS = {
    "created_at",
    "audio_file",
    "transcript_file",
    "duration_seconds",
    "summary",
    "recent_summary_refs",
    "model_llm",
    "model_stt",
    "app_version",
}


@dataclass
class Frontmatter:
    data: MutableMapping[str, Any]

    def ensure_keys(self) -> None:
        for key in FRONTMATTER_KEYS:
            if key == "audio_file":
                self.data.setdefault(key, [])
            elif key == "recent_summary_refs":
                self.data.setdefault(key, [])
            elif key == "duration_seconds":
                self.data.setdefault(key, 0.0)
            else:
                self.data.setdefault(key, None)


@dataclass
class TranscriptDocument:
    frontmatter: Frontmatter
    body: str


def load_transcript(markdown_path: Path) -> TranscriptDocument:
    if not markdown_path.exists():
        fm = Frontmatter(data={})
        fm.ensure_keys()
        return TranscriptDocument(frontmatter=fm, body="")

    raw = markdown_path.read_text(encoding="utf-8")
    fm_data, body = _parse_frontmatter(raw)
    fm = Frontmatter(data=fm_data)
    fm.ensure_keys()
    return TranscriptDocument(frontmatter=fm, body=body)


def write_transcript(markdown_path: Path, document: TranscriptDocument) -> None:
    document.frontmatter.ensure_keys()
    if not document.frontmatter.data.get("transcript_file"):
        document.frontmatter.data["transcript_file"] = markdown_path.name
    # Ensure summary is a single-line scalar for YAML output
    try:
        summary_value = document.frontmatter.data.get("summary")
        if isinstance(summary_value, str):
            # Collapse all whitespace (including newlines) to single spaces
            single_line_summary = " ".join(summary_value.split())
            document.frontmatter.data["summary"] = single_line_summary
    except Exception:
        # Defensive: never let summary formatting break persistence
        pass
    fm_text = yaml.safe_dump(
        document.frontmatter.data,
        sort_keys=False,
        allow_unicode=False,
        width=100000,
    ).strip()

    body_text = document.body.rstrip()

    lines: list[str] = ["---", fm_text, "---"]
    if body_text:
        lines.append("")
        lines.append(body_text)
        lines.append("")

    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write: write to a temp file then replace
    tmp_path = markdown_path.with_name("." + markdown_path.name + ".tmp")
    tmp_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        tmp_path.replace(markdown_path)
    except Exception:
        # Fallback to direct write if replace fails (e.g., cross-filesystem)
        markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


def append_exchange_body(
    markdown_path: Path,
    question: str,
    transcript_text: str,
) -> None:
    doc = load_transcript(markdown_path)
    # New format: Heading followed by fenced llm-question block
    heading = "## AI Q"
    response = transcript_text.strip()

    blocks: list[str] = []
    if doc.body.strip():
        blocks.append(doc.body.rstrip())
        # Add a double linebreak before each new AI Q heading
        blocks.append("")
        blocks.append("")
    blocks.append(heading)
    blocks.append("")
    blocks.append("```llm-question")
    blocks.append(question.strip())
    blocks.append("```")
    blocks.append("")
    blocks.append(response)

    doc.body = "\n".join(blocks).rstrip() + "\n\n"
    write_transcript(markdown_path, doc)


def append_pending_exchange(
    markdown_path: Path,
    question: str,
    segment_label: str,
) -> None:
    """Append a placeholder exchange for a failed transcription attempt."""

    append_exchange_body(
        markdown_path,
        question,
        placeholder_block(segment_label),
    )


def replace_pending_exchange(
    markdown_path: Path,
    segment_label: str,
    transcript_text: str,
) -> bool:
    """Replace a placeholder entry with the supplied transcript text."""

    doc = load_transcript(markdown_path)
    block = placeholder_block(segment_label)
    replacement = transcript_text.strip()

    if block in doc.body:
        doc.body = doc.body.replace(block, replacement, 1)
    else:
        marker = placeholder_comment(segment_label)
        if marker not in doc.body:
            return False
        lines = doc.body.splitlines()
        for idx, line in enumerate(lines):
            if line.strip() == marker:
                start_idx = max(idx - 1, 0)
                lines[start_idx] = replacement
                lines.pop(idx)
                doc.body = "\n".join(lines)
                break
        else:
            return False

    doc.body = doc.body.rstrip() + "\n\n"
    write_transcript(markdown_path, doc)
    return True


def clear_pending_flag(markdown_path: Path, segment_label: str) -> bool:
    """Remove pending metadata markers for the given audio segment."""

    doc = load_transcript(markdown_path)
    audio_entries = list(doc.frontmatter.data.get("audio_file") or [])
    changed = False

    for entry in audio_entries:
        if str(entry.get("wav")) == segment_label:
            if entry.pop("pending", None) is not None:
                changed = True
            if entry.pop("pending_reason", None) is not None:
                changed = True

    if changed:
        doc.frontmatter.data["audio_file"] = audio_entries
        write_transcript(markdown_path, doc)

    return changed


def _parse_frontmatter(raw: str) -> tuple[MutableMapping[str, Any], str]:
    if not raw.startswith("---"):
        return {}, raw

    lines = raw.splitlines()
    if not lines:
        return {}, ""

    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            fm_lines = lines[1:idx]
            body_lines = lines[idx + 1 :]
            fm_text = "\n".join(fm_lines)
            try:
                parsed = yaml.safe_load(fm_text) or {}
                if not isinstance(parsed, dict):
                    raise TypeError("Frontmatter must be a mapping")
            except Exception as exc:  # pragma: no cover - defensive logging
                _LOGGER.warning("Failed to parse frontmatter: %s", exc)
                parsed = {}
            body = "\n".join(body_lines).lstrip("\n")
            return dict(parsed), body

    return {}, raw
