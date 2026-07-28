"""
Answer enrichment for Perplexity responses.

Perplexity streams the assembled answer alongside rich side data — web
citations, inline images, and related queries — that the plain-text pipeline
drops. This module recovers those structures from the raw SSE events and
renders them as a markdown appendix so the OpenAI-compatible output can
surface sources and images.

Extraction is deliberately snapshot-based (not JSON-Patch replay): the single
``step_type == "FINAL"`` event carries the fully-assembled ``web_results``, and
inline media arrives as whole-value ``replace`` blocks. Both are stable to read
directly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Citation:
    """A web source cited in the answer."""

    title: str
    url: str
    snippet: str = ""


@dataclass
class MediaItem:
    """An inline image/diagram attached to the answer."""

    url: str  # direct image URL
    title: str = ""
    source_url: str = ""  # page the image came from


@dataclass
class Enrichment:
    """Side data recovered from a Perplexity response."""

    citations: list[Citation] = field(default_factory=list)
    media: list[MediaItem] = field(default_factory=list)
    related: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.citations or self.media or self.related)


def _safe_json(value: Any) -> Optional[Any]:
    """json.loads that never raises; returns None on non-string/invalid input."""
    if not isinstance(value, str) or not value:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return None


def _citations_from_final(event: dict[str, Any]) -> list[Citation]:
    """
    Extract assembled citations from a ``step_type == "FINAL"`` event.

    Prefers the inner ``FINAL`` step's ``answer.web_results`` (fully assembled);
    falls back to ``SEARCH_RESULTS`` steps when the answer carries none.
    """
    steps = _safe_json(event.get("text", "")) or []
    if not isinstance(steps, list):
        return []

    final_cites: list[Citation] = []
    search_cites: list[Citation] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        content = step.get("content") or {}
        step_type = step.get("step_type")
        if step_type == "FINAL":
            answer = _safe_json(content.get("answer", "")) or {}
            for wr in answer.get("web_results", []) or []:
                if wr.get("url") and wr.get("name"):
                    final_cites.append(
                        Citation(wr["name"], wr["url"], wr.get("snippet", "") or "")
                    )
        elif step_type == "SEARCH_RESULTS":
            for wr in content.get("web_results", []) or []:
                if wr.get("url") and wr.get("name"):
                    search_cites.append(
                        Citation(wr["name"], wr["url"], wr.get("snippet", "") or "")
                    )
    return final_cites or search_cites


def _media_from_block(block: dict[str, Any]) -> list[MediaItem]:
    """Extract media items from an inline-entity / media block (whole-value)."""
    candidates: list[list[Any]] = []

    inline = block.get("inline_entity_block") or {}
    media_block = inline.get("media_block") or {}
    if isinstance(media_block.get("media_items"), list):
        candidates.append(media_block["media_items"])

    # Media may also arrive inside a diff patch value (replace at path "").
    diff = block.get("diff_block") or {}
    for patch in diff.get("patches", []) or []:
        value = patch.get("value")
        if isinstance(value, dict):
            items = (value.get("media_block") or {}).get("media_items")
            if isinstance(items, list):
                candidates.append(items)

    out: list[MediaItem] = []
    for items in candidates:
        for m in items:
            if not isinstance(m, dict):
                continue
            img = m.get("image")
            if img:
                out.append(
                    MediaItem(
                        url=img,
                        title=m.get("name", "") or "",
                        source_url=m.get("url", "") or "",
                    )
                )
    return out


def extract_enrichment(events: Any) -> Enrichment:
    """
    Recover citations, inline images, and related queries from raw SSE events.

    Args:
        events: An iterable of raw event dicts (as yielded by ask_stream or
            accumulated in PerplexityResponse.raw_events). Non-list input
            yields an empty Enrichment so callers can pass mocks safely.
    """
    enr = Enrichment()
    if not isinstance(events, (list, tuple)):
        return enr

    seen_cite: set[str] = set()
    seen_media: set[str] = set()
    for event in events:
        if not isinstance(event, dict):
            continue

        if event.get("step_type") == "FINAL":
            for c in _citations_from_final(event):
                if c.url not in seen_cite:
                    seen_cite.add(c.url)
                    enr.citations.append(c)
            for q in event.get("related_queries") or []:
                if isinstance(q, str) and q and q not in enr.related:
                    enr.related.append(q)

        for block in event.get("blocks", []) or []:
            if not isinstance(block, dict):
                continue
            iu = block.get("intended_usage", "")
            if (
                iu.endswith("_images")
                or iu == "answer_media_items"
                or block.get("inline_entity_block")
            ):
                for m in _media_from_block(block):
                    if m.url not in seen_media:
                        seen_media.add(m.url)
                        enr.media.append(m)

    return enr


def format_enrichment_markdown(enr: Enrichment, max_related: int = 5) -> str:
    """
    Render an Enrichment as a markdown appendix, or "" when empty.

    The appendix is separated from the answer by a horizontal rule so it reads
    cleanly in any OpenAI client.
    """
    if enr.is_empty():
        return ""

    parts: list[str] = ["\n\n---\n"]
    if enr.citations:
        parts.append("\n**Sources:**\n")
        for i, c in enumerate(enr.citations, 1):
            parts.append(f"{i}. [{c.title}]({c.url})\n")
    if enr.media:
        parts.append("\n**Images:**\n")
        for m in enr.media:
            alt = m.title or "image"
            parts.append(f"- ![{alt}]({m.url})\n")
    if enr.related:
        parts.append("\n**Related:**\n")
        for q in enr.related[:max_related]:
            parts.append(f"- {q}\n")
    return "".join(parts)
