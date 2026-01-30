"""
Perplexity API Client

A Python wrapper for the Perplexity AI web interface API.
Uses curl_cffi to bypass Cloudflare protection.
"""

import json
import os
import uuid
from typing import Generator, Optional, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
from curl_cffi import requests as cffi_requests


@dataclass
class PerplexityResponse:
    """Structured response from Perplexity API."""

    text: str = ""
    citations: list[dict] = field(default_factory=list)
    media_items: list[dict] = field(default_factory=list)
    related_queries: list[str] = field(default_factory=list)
    raw_events: list[dict] = field(default_factory=list)


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

        if not all([self.session_token, self.cf_clearance, self.visitor_id]):
            raise ValueError(
                "Missing required environment variables. "
                "Please set PERPLEXITY_SESSION_TOKEN, PERPLEXITY_CF_CLEARANCE, "
                "and PERPLEXITY_VISITOR_ID in your .env file."
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
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": self.BASE_URL,
            "referer": f"{self.BASE_URL}/?",
            "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "x-perplexity-request-reason": "perplexity-query-state-provider",
            "x-request-id": request_id,
        }

    def _build_payload(
        self,
        query: str,
        mode: str = "copilot",
        model_preference: str = "claude45sonnetthinking",
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
                "search_recency_filter": None,
                "frontend_uuid": frontend_uuid,
                "mode": mode,
                "model_preference": model_preference,
                "is_related_query": False,
                "is_sponsored": False,
                "frontend_context_uuid": context_uuid,
                "prompt_source": "user",
                "query_source": "home",
                "is_incognito": is_incognito,
                "time_from_first_type": 2000.0,
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
                    "in_context_suggestions",
                ],
                "dsl_query": query,
                "skip_search_enabled": True,
                "version": "2.18",
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
        model_preference: str = "claude45sonnetthinking",
        search_focus: str = "internet",
        sources: Optional[list[str]] = None,
        is_incognito: bool = False,
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
            timeout=1800,
            stream=True,
        )

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

    def ask(
        self,
        query: str,
        mode: str = "copilot",
        model_preference: str = "claude45sonnetthinking",
        search_focus: str = "internet",
        sources: Optional[list[str]] = None,
        is_incognito: bool = False,
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

        Returns:
            PerplexityResponse with parsed results
        """
        result = PerplexityResponse()

        for event in self.ask_stream(
            query=query,
            mode=mode,
            model_preference=model_preference,
            search_focus=search_focus,
            sources=sources,
            is_incognito=is_incognito,
        ):
            result.raw_events.append(event)

            step_type = event.get("step_type", "")

            # Handle FINAL event - contains the complete response as nested JSON
            if step_type == "FINAL":
                # Get related queries from top level
                result.related_queries = event.get("related_queries", [])

                # Parse the nested text field which contains all step data as JSON
                text_json = event.get("text", "")
                if text_json:
                    try:
                        steps = json.loads(text_json)
                        for step in steps:
                            step_content = step.get("content", {})
                            inner_step_type = step.get("step_type", "")

                            # Extract citations from SEARCH_RESULTS
                            if inner_step_type == "SEARCH_RESULTS":
                                web_results = step_content.get("web_results", [])
                                for wr in web_results:
                                    if wr.get("name") and wr.get("url"):
                                        result.citations.append(
                                            {
                                                "title": wr.get("name", ""),
                                                "url": wr.get("url", ""),
                                                "snippet": wr.get("snippet", ""),
                                            }
                                        )

                            # Extract answer from inner FINAL step
                            if inner_step_type == "FINAL":
                                answer_str = step_content.get("answer", "")
                                if answer_str:
                                    try:
                                        answer_data = json.loads(answer_str)
                                        if "answer" in answer_data:
                                            result.text = answer_data["answer"]
                                    except json.JSONDecodeError:
                                        # answer might be plain text
                                        result.text = answer_str

                            # Also check for structured_answer in other steps
                            if "structured_answer" in step_content:
                                for item in step_content.get("structured_answer", []):
                                    if item.get("type") == "markdown" and item.get(
                                        "text"
                                    ):
                                        result.text = item["text"]
                    except json.JSONDecodeError:
                        pass

        return result


# Convenience function for simple usage
def perplexity_search(
    query: str,
    mode: str = "copilot",
    model_preference: str = "claude45sonnetthinking",
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
