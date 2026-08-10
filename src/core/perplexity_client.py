"""
Perplexity API Client

A Python wrapper for the Perplexity AI web interface API.
Uses curl_cffi to bypass Cloudflare protection.
"""

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Generator, Optional

from curl_cffi import requests as cffi_requests
from curl_cffi.const import CurlOpt
from curl_cffi.requests.exceptions import Timeout as CurlTimeout
from dotenv import load_dotenv

from src.services.sse_parser import PerplexitySSEParser

logger = logging.getLogger(__name__)
DEFAULT_REQUEST_TIMEOUT_SECONDS = 1800.0


@dataclass
class PerplexityResponse:
    """Structured response from Perplexity API."""

    text: str = ""
    citations: list[dict] = field(default_factory=list)
    media_items: list[dict] = field(default_factory=list)
    related_queries: list[str] = field(default_factory=list)
    raw_events: list[dict] = field(default_factory=list)
    partial: bool = False
    warning: Optional[str] = None


def _add_citations(
    response: PerplexityResponse,
    web_results: Any,
    seen_urls: set[str],
) -> None:
    """Append valid web citations once, keyed by URL."""
    if not isinstance(web_results, list):
        return

    for web_result in web_results:
        if not isinstance(web_result, dict):
            continue
        title = web_result.get("name", "")
        url = web_result.get("url", "")
        if not title or not url or url in seen_urls:
            continue
        seen_urls.add(url)
        response.citations.append(
            {
                "title": title,
                "url": url,
                "snippet": web_result.get("snippet", ""),
            }
        )


def _process_legacy_final(
    event: dict,
    response: PerplexityResponse,
    seen_urls: set[str],
) -> None:
    """Parse the legacy nested FINAL event format."""
    response.related_queries = event.get("related_queries", [])
    text_json = event.get("text", "")
    if not text_json:
        return

    try:
        steps = json.loads(text_json)
    except (json.JSONDecodeError, TypeError):
        return
    if not isinstance(steps, list):
        return

    for step in steps:
        if not isinstance(step, dict):
            continue
        content = step.get("content", {})
        if not isinstance(content, dict):
            continue

        if step.get("step_type") == "SEARCH_RESULTS":
            _add_citations(response, content.get("web_results", []), seen_urls)

        if step.get("step_type") == "FINAL":
            answer_value = content.get("answer", "")
            if isinstance(answer_value, str) and answer_value:
                try:
                    answer_data = json.loads(answer_value)
                except json.JSONDecodeError:
                    response.text = answer_value
                else:
                    if isinstance(answer_data, dict):
                        if isinstance(answer_data.get("answer"), str):
                            response.text = answer_data["answer"]
                        _add_citations(
                            response,
                            answer_data.get("web_results", []),
                            seen_urls,
                        )
                        for item in answer_data.get("structured_answer", []):
                            if (
                                isinstance(item, dict)
                                and item.get("type") == "markdown"
                                and isinstance(item.get("text"), str)
                            ):
                                response.text = item["text"]

        for item in content.get("structured_answer", []):
            if (
                isinstance(item, dict)
                and item.get("type") == "markdown"
                and isinstance(item.get("text"), str)
            ):
                response.text = item["text"]


def _set_chunk(chunks: list[str], index: int, value: Any) -> None:
    """Set a streamed chunk by index, extending sparse snapshots safely."""
    while len(chunks) <= index:
        chunks.append("")
    chunks[index] = str(value) if value is not None else ""


def _process_answer_block(
    block: dict,
    chunk_state: dict[str, list[str]],
    answer_state: dict[str, str],
) -> bool:
    """Apply a current or legacy answer block and report completion."""
    intended_usage = block.get("intended_usage", "")
    if not PerplexitySSEParser.is_markdown_block(intended_usage):
        return False

    complete = False
    has_direct_answer = False
    markdown = block.get("markdown_block")
    if isinstance(markdown, dict):
        answer = markdown.get("answer")
        chunks = markdown.get("chunks")
        if isinstance(answer, str) and answer:
            answer_state[intended_usage] = answer
            has_direct_answer = True
        elif isinstance(chunks, list):
            chunk_state[intended_usage] = [str(chunk) for chunk in chunks]
        complete = markdown.get("progress") == "DONE"

    diff_block = block.get("diff_block")
    if not isinstance(diff_block, dict):
        return complete and intended_usage in ("ask_text", "ask_text_markdown")

    for patch in diff_block.get("patches", []):
        if not isinstance(patch, dict):
            continue
        path = patch.get("path", "")
        value = patch.get("value")
        op = patch.get("op")

        if path == "" and isinstance(value, dict):
            complete = complete or value.get("progress") == "DONE"
            if has_direct_answer:
                continue
            answer = value.get("answer")
            chunks = value.get("chunks")
            if isinstance(answer, str) and answer:
                answer_state[intended_usage] = answer
            elif isinstance(chunks, list):
                chunk_state[intended_usage] = [str(chunk) for chunk in chunks]
        elif path == "/progress":
            complete = complete or value == "DONE"
        elif (
            not has_direct_answer
            and path == "/answer"
            and isinstance(value, str)
            and value
        ):
            answer_state[intended_usage] = value
        elif (
            not has_direct_answer
            and path.startswith("/chunks/")
            and op in ("add", "replace")
        ):
            try:
                index = int(path.rsplit("/", 1)[-1])
            except ValueError:
                continue
            chunks = chunk_state.setdefault(intended_usage, [])
            _set_chunk(chunks, index, value)

    return complete and intended_usage in ("ask_text", "ask_text_markdown")


def _current_answer_text(
    chunk_state: dict[str, list[str]],
    answer_state: dict[str, str],
) -> str:
    """Choose the combined answer, falling back to ordered section blocks."""

    def block_text(intended_usage: str) -> str:
        return answer_state.get(intended_usage) or "".join(
            chunk_state.get(intended_usage, [])
        )

    for combined_usage in ("ask_text", "ask_text_markdown"):
        text = block_text(combined_usage)
        if text:
            return text

    def section_sort_key(intended_usage: str) -> tuple[int, int, str]:
        section = intended_usage.removeprefix("ask_text_").removesuffix("_markdown")
        try:
            return (0, int(section), intended_usage)
        except ValueError:
            return (1, 0, intended_usage)

    section_usages = sorted(
        (
            usage
            for usage in set(chunk_state) | set(answer_state)
            if usage.startswith("ask_text_") and usage.endswith("_markdown")
        ),
        key=section_sort_key,
    )
    return "".join(block_text(usage) for usage in section_usages)


def _process_current_blocks(
    event: dict,
    response: PerplexityResponse,
    chunk_state: dict[str, list[str]],
    answer_state: dict[str, str],
    seen_urls: set[str],
) -> bool:
    """Parse current block-only events and report terminal answer progress."""
    complete = False
    for block in event.get("blocks", []) or []:
        if not isinstance(block, dict):
            continue
        intended_usage = block.get("intended_usage", "")

        if intended_usage == "web_results":
            direct_results = block.get("web_results")
            _add_citations(response, direct_results, seen_urls)
            direct_block = block.get("web_result_block")
            if isinstance(direct_block, dict):
                _add_citations(
                    response,
                    direct_block.get("web_results", []),
                    seen_urls,
                )
            diff_block = block.get("diff_block")
            if isinstance(diff_block, dict):
                for patch in diff_block.get("patches", []):
                    if not isinstance(patch, dict):
                        continue
                    value = patch.get("value")
                    if isinstance(value, dict):
                        _add_citations(
                            response,
                            value.get("web_results", []),
                            seen_urls,
                        )
                        if patch.get("path", "").startswith("/web_results/"):
                            _add_citations(response, [value], seen_urls)
                    elif isinstance(value, list):
                        _add_citations(response, value, seen_urls)

        complete = _process_answer_block(block, chunk_state, answer_state) or complete

    current_text = _current_answer_text(chunk_state, answer_state)
    if current_text:
        response.text = current_text
    return complete


class PerplexityClient:
    """Client for interacting with Perplexity AI web API."""

    BASE_URL = "https://www.perplexity.ai"
    SSE_ENDPOINT = "/rest/sse/perplexity_ask"

    def __init__(self, env_path: Optional[str] = None):
        """
        Initialize the Perplexity client.

        Args:
            env_path: Optional path to .env file. Defaults to current directory.
        """
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        self.session_token = os.getenv("PERPLEXITY_SESSION_TOKEN")
        self.cf_bm = os.getenv("PERPLEXITY_CF_BM")
        self.cf_clearance = os.getenv("PERPLEXITY_CF_CLEARANCE")
        self.visitor_id = os.getenv("PERPLEXITY_VISITOR_ID")
        self.session_id = os.getenv("PERPLEXITY_SESSION_ID")

        if not self.session_token:
            raise ValueError(
                "Missing required environment variable. "
                "Please set PERPLEXITY_SESSION_TOKEN in your .env file."
            )

    def _build_cookies(self) -> dict:
        """Build cookies dict for requests."""
        cookies = {
            "pplx.visitor-id": self.visitor_id,
            "__Secure-next-auth.session-token": self.session_token,
            "cf_clearance": self.cf_clearance,
            "pplx.session-id": self.session_id,
        }

        if self.cf_bm:
            cookies["__cf_bm"] = self.cf_bm

        return {k: v for k, v in cookies.items() if v}

    def _build_headers(self, request_id: str) -> dict[str, str]:
        """Build request headers."""
        return {
            "accept": "text/event-stream",
            "accept-language": "en-US,en;q=0.9,id;q=0.8,nb;q=0.7",
            "content-type": "application/json",
            "origin": self.BASE_URL,
            "referer": f"{self.BASE_URL}/",
            "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Microsoft Edge";v="146"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
            "x-perplexity-request-endpoint": f"{self.BASE_URL}{self.SSE_ENDPOINT}",
            "x-perplexity-request-reason": "perplexity-query-state-provider",
            "x-perplexity-request-try-number": "1",
            "x-request-id": request_id,
        }

    def _build_payload(
        self,
        query: str,
        mode: str = "copilot",
        model_preference: str = "gpt56_terra_thinking",
        search_focus: str = "internet",
        sources: Optional[list[str]] = None,
        language: str = "en-US",
        timezone: str = "Asia/Bangkok",
        is_incognito: bool = False,
    ) -> dict[str, Any]:
        """Build request payload.

        Args:
            query: The search query
            mode: Search mode (copilot, search, etc.)
            model_preference: AI model to use
            search_focus: Search focus (internet, academic, etc.)
            sources: List of sources to search
            language: Language code
            timezone: Timezone string
            is_incognito: If True, query won't appear in Perplexity dashboard
        """
        frontend_uuid = str(uuid.uuid4())
        context_uuid = str(uuid.uuid4())

        return {
            "params": {
                "attachments": [],
                "language": language,
                "timezone": timezone,
                "search_focus": search_focus,
                "sources": sources or ["web", "scholar"],
                "frontend_uuid": frontend_uuid,
                "mode": mode,
                "model_preference": model_preference,
                "is_related_query": False,
                "is_sponsored": False,
                "frontend_context_uuid": context_uuid,
                "prompt_source": "user",
                "query_source": "home",
                "is_incognito": is_incognito,
                "time_from_first_type": 4395.6,
                "local_search_enabled": False,
                "use_schematized_api": True,
                "send_back_text_in_streaming_api": False,
                "supported_block_use_cases": [
                    "answer_modes",
                    "media_items",
                    "knowledge_cards",
                    "inline_entity_cards",
                    "place_widgets",
                    "finance_widgets",
                    "prediction_market_widgets",
                    "sports_widgets",
                    "flight_status_widgets",
                    "news_widgets",
                    "shopping_widgets",
                    "jobs_widgets",
                    "search_result_widgets",
                    "inline_images",
                    "inline_assets",
                    "placeholder_cards",
                    "diff_blocks",
                    "inline_knowledge_cards",
                    "entity_group_v2",
                    "refinement_filters",
                    "canvas_mode",
                    "maps_preview",
                    "answer_tabs",
                    "price_comparison_widgets",
                    "preserve_latex",
                    "generic_onboarding_widgets",
                    "in_context_suggestions",
                    "pending_followups",
                    "inline_claims",
                    "unified_assets",
                    "workflow_steps",
                    "background_agents",
                ],
                "client_coordinates": None,
                "mentions": [],
                "dsl_query": query,
                "skip_search_enabled": True,
                "is_nav_suggestions_disabled": False,
                "source": "default",
                "always_search_override": False,
                "override_no_search": False,
                "client_search_results_cache_key": frontend_uuid,
                "should_ask_for_mcp_tool_confirmation": True,
                "browser_agent_allow_once_from_toggle": False,
                "force_enable_browser_agent": False,
                "supported_features": [
                    "browser_agent_permission_banner_v1.1",
                ],
                "extended_context": False,
                "version": "2.18",
                "rum_session_id": str(uuid.uuid4()),
            },
            "query_str": query,
        }

    def _parse_sse_line(self, line: str) -> Optional[dict]:
        """Parse a single SSE line."""
        if not line or not line.startswith("data:"):
            return None

        data_str = line[5:].strip()  # Remove "data:" prefix
        if not data_str:
            return None

        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            return None

    def ask_stream(
        self,
        query: str,
        mode: str = "copilot",
        model_preference: str = "gpt56_terra_thinking",
        search_focus: str = "internet",
        sources: Optional[list[str]] = None,
        is_incognito: bool = False,
        timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ) -> Generator[dict, None, None]:
        """
        Send a query to Perplexity and stream the response.

        Args:
            query: The search query
            mode: Search mode (copilot, search, etc.)
            model_preference: AI model to use
            search_focus: Search focus (internet, academic, etc.)
            sources: List of sources to search
            is_incognito: If True, query won't appear in Perplexity dashboard
            timeout_seconds: Upstream inactivity timeout in seconds

        Yields:
            Parsed SSE event dictionaries
        """
        request_id = str(uuid.uuid4())
        cookies = self._build_cookies()
        headers = self._build_headers(request_id)
        payload = self._build_payload(
            query=query,
            mode=mode,
            model_preference=model_preference,
            search_focus=search_focus,
            sources=sources,
            is_incognito=is_incognito,
        )

        url = f"{self.BASE_URL}{self.SSE_ENDPOINT}"

        # Use curl_cffi with impersonate to bypass Cloudflare
        response = cffi_requests.post(
            url,
            headers=headers,
            cookies=cookies,
            json=payload,
            impersonate="edge",
            timeout=timeout_seconds,
            curl_options={CurlOpt.TIMEOUT_MS: int(timeout_seconds * 1000)},
            stream=True,
        )
        try:
            if response.status_code != 200:
                raise Exception(
                    f"Request failed with status {response.status_code}: {response.text}"
                )

            # Parse SSE stream
            buffer = ""
            for chunk in response.iter_content():
                if chunk:
                    buffer += chunk.decode("utf-8", errors="ignore")

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()

                        if line.startswith("data:"):
                            event = self._parse_sse_line(line)
                            if event:
                                yield event
        finally:
            response.close()

    def ask(
        self,
        query: str,
        mode: str = "copilot",
        model_preference: str = "gpt56_terra_thinking",
        search_focus: str = "internet",
        sources: Optional[list[str]] = None,
        is_incognito: bool = False,
        timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS,
    ) -> PerplexityResponse:
        """
        Send a query to Perplexity and return the complete response.

        Args:
            query: The search query
            mode: Search mode (copilot, search, etc.)
            model_preference: AI model to use
            search_focus: Search focus (internet, academic, etc.)
            sources: List of sources to search
            is_incognito: If True, query won't appear in Perplexity dashboard
            timeout_seconds: Maximum total request time in seconds

        Returns:
            PerplexityResponse with parsed results
        """
        result = PerplexityResponse()
        chunk_state: dict[str, list[str]] = {}
        answer_state: dict[str, str] = {}
        seen_urls: set[str] = set()
        started_at = time.monotonic()
        deadline = started_at + timeout_seconds
        termination = "stream_ended"
        stream = self.ask_stream(
            query=query,
            mode=mode,
            model_preference=model_preference,
            search_focus=search_focus,
            sources=sources,
            is_incognito=is_incognito,
            timeout_seconds=timeout_seconds,
        )

        try:
            for event in stream:
                if not isinstance(event, dict):
                    continue
                result.raw_events.append(event)

                step_type = event.get("step_type", "")
                if step_type == "FINAL":
                    _process_legacy_final(event, result, seen_urls)

                block_complete = _process_current_blocks(
                    event,
                    result,
                    chunk_state,
                    answer_state,
                    seen_urls,
                )

                if step_type == "FINAL" or event.get("text_completed") is True:
                    termination = "completed"
                    break
                if block_complete:
                    termination = "answer_done"
                    break
                if time.monotonic() >= deadline:
                    raise CurlTimeout(
                        f"Perplexity request exceeded {timeout_seconds:g} seconds"
                    )
        except CurlTimeout as error:
            if not result.text:
                raise CurlTimeout(
                    "Perplexity request timed out with no answer text received "
                    f"within {timeout_seconds:g} seconds"
                ) from error
            result.partial = True
            result.warning = (
                f"Timed out after {timeout_seconds:g} seconds; "
                "returning partial answer."
            )
            termination = "timeout_partial"
        finally:
            close = getattr(stream, "close", None)
            if callable(close):
                close()
            logger.info(
                "Perplexity request finished model=%s mode=%s duration=%.2fs "
                "events=%d termination=%s partial=%s",
                model_preference,
                mode,
                time.monotonic() - started_at,
                len(result.raw_events),
                termination,
                result.partial,
            )

        return result


# Convenience function for simple usage
def perplexity_search(
    query: str,
    mode: str = "copilot",
    model_preference: str = "gpt56_terra_thinking",
) -> str:
    """
    Simple function to search using Perplexity.

    Args:
        query: The search query
        mode: Search mode
        model_preference: AI model to use

    Returns:
        The response text
    """
    client = PerplexityClient()
    response = client.ask(query, mode=mode, model_preference=model_preference)
    return response.text
