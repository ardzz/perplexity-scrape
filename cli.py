#!/usr/bin/env python3
"""
Perplexity Interactive CLI

An interactive terminal interface for Perplexity AI with:
- Multi-turn conversation history
- Streaming real-time output
- MCP tool integration (BurpSuite, filesystem, custom servers)
- Rich markdown rendering

Usage:
    python3 cli.py
    python3 cli.py --model sonar-pro
    python3 cli.py --mcp ./mcp_tools.json
    python3 cli.py --load ~/sessions/chat.json
"""

import argparse
import json
import os
import sys
import time
import signal
from pathlib import Path
from typing import Optional

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

from src.core.perplexity_client import PerplexityClient, PerplexityResponse
from src.cli.session import ChatSession, AVAILABLE_MODELS, DEFAULT_MODEL, _ALL_MODELS, get_model_name
from src.cli.renderer import Renderer, console
from src.cli.mcp_bridge import MCPToolBridge


# ─── Prompt style ────────────────────────────────────────────────────────────

PROMPT_STYLE = Style.from_dict({
    "prompt":       "#00d7ff bold",
    "prompt.arrow": "#888888",
})


# ─── Multi-strategy text extraction ─────────────────────────────────────────

def _deep_find_text(obj, depth: int = 0, max_depth: int = 6) -> str:
    """Recursively search a dict/list for the longest meaningful text string."""
    if depth > max_depth:
        return ""
    best = ""

    if isinstance(obj, str):
        cleaned = obj.strip()
        if len(cleaned) > len(best) and len(cleaned) > 20:
            best = cleaned
        # Try to parse as JSON too
        if cleaned.startswith(("{", "[")):
            try:
                parsed = json.loads(cleaned)
                candidate = _deep_find_text(parsed, depth + 1, max_depth)
                if len(candidate) > len(best):
                    best = candidate
            except (json.JSONDecodeError, TypeError):
                pass
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("url", "query", "id", "uuid", "sha", "hash", "frontend_uuid",
                     "context_uuid", "request_id", "visitor_id"):
                continue
            candidate = _deep_find_text(v, depth + 1, max_depth)
            if len(candidate) > len(best):
                best = candidate
    elif isinstance(obj, list):
        for item in obj:
            candidate = _deep_find_text(item, depth + 1, max_depth)
            if len(candidate) > len(best):
                best = candidate

    return best


def _extract_text_from_events(events: list[dict]) -> tuple[str, list[dict]]:
    """
    Multi-strategy text extraction from Perplexity SSE events.
    Handles different response formats across models (claude, gpt-4o, sonar, r1, etc.)

    Returns (text, citations).
    """
    text = ""
    citations: list[dict] = []

    # ── Strategy 1: streaming diff blocks (claude/sonar models) ───────────
    buffer = ""
    for event in events:
        for block in event.get("blocks", []):
            usage = block.get("intended_usage", "")
            if usage in ("ask_text_0_markdown", "ask_text", "answer"):
                for patch in block.get("diff_block", {}).get("patches", []):
                    op = patch.get("op")
                    value = patch.get("value")
                    if op == "replace" and isinstance(value, dict):
                        buffer = "".join(value.get("chunks", []))
                    elif op == "add":
                        if isinstance(value, str):
                            buffer += value
                        elif isinstance(value, dict):
                            buffer += "".join(value.get("chunks", []))
    if buffer.strip():
        text = buffer.strip()

    # ── Strategy 2: FINAL event nested JSON (all models) ──────────────────
    for event in events:
        if event.get("step_type") != "FINAL":
            continue

        text_field = event.get("text", "")
        if not text_field:
            # Some models put the answer directly in other fields
            for field in ("answer", "output", "response", "content"):
                val = event.get(field, "")
                if isinstance(val, str) and val.strip():
                    if not text:
                        text = val.strip()
            continue

        # text_field might be a JSON array of step objects OR plain text
        if isinstance(text_field, str) and text_field.strip().startswith("["):
            try:
                steps = json.loads(text_field)
                for step in steps:
                    step_content = step.get("content", {})
                    inner_type = step.get("step_type", "")

                    # Citations from SEARCH_RESULTS step
                    if inner_type == "SEARCH_RESULTS":
                        for wr in step_content.get("web_results", []):
                            if wr.get("name") and wr.get("url"):
                                citations.append({
                                    "title": wr.get("name", ""),
                                    "url": wr.get("url", ""),
                                    "snippet": wr.get("snippet", ""),
                                })

                    # Answer from inner FINAL step
                    if inner_type == "FINAL":
                        answer_str = step_content.get("answer", "")
                        if answer_str:
                            try:
                                answer_data = json.loads(answer_str)
                                if "answer" in answer_data and not text:
                                    text = answer_data["answer"]
                                # structured_answer overrides plain answer
                                for item in answer_data.get("structured_answer", []):
                                    if item.get("type") == "markdown" and item.get("text"):
                                        text = item["text"]
                                # Additional citations from answer's web_results
                                for wr in answer_data.get("web_results", []):
                                    if wr.get("name") and wr.get("url"):
                                        citations.append({
                                            "title": wr.get("name", ""),
                                            "url": wr.get("url", ""),
                                            "snippet": wr.get("snippet", ""),
                                        })
                            except (json.JSONDecodeError, AttributeError):
                                # answer_str is plain text already
                                if not text and answer_str.strip():
                                    text = answer_str.strip()

                    # structured_answer at step level
                    if not text:
                        for item in step_content.get("structured_answer", []):
                            if item.get("type") == "markdown" and item.get("text"):
                                text = item["text"]
                                break

            except (json.JSONDecodeError, TypeError, ValueError):
                # Not valid JSON — treat text_field as plain text
                if not text and isinstance(text_field, str) and text_field.strip():
                    text = text_field.strip()

        elif isinstance(text_field, str) and text_field.strip():
            # Plain text in text_field (some model formats)
            if not text:
                text = text_field.strip()

    # ── Strategy 3: direct top-level fields in any event ──────────────────
    if not text:
        for event in events:
            for field in ("answer", "output", "response", "content", "message", "text"):
                val = event.get(field, "")
                if isinstance(val, str) and val.strip() and len(val.strip()) > 10:
                    # Ignore if it looks like JSON (handled above)
                    stripped = val.strip()
                    if not stripped.startswith(("[", "{")):
                        text = stripped
                        break
            if text:
                break

    # ── Strategy 4: recursive deep scan of FINAL event ────────────────────
    if not text:
        for event in events:
            if event.get("step_type") == "FINAL":
                candidate = _deep_find_text(event)
                if len(candidate) > 20:
                    text = candidate
                    break

    # Deduplicate citations
    seen_urls = set()
    unique_citations = []
    for c in citations:
        if c["url"] not in seen_urls:
            seen_urls.add(c["url"])
            unique_citations.append(c)

    return text, unique_citations


# ─── Streaming handler ───────────────────────────────────────────────────────

def stream_perplexity(
    client: PerplexityClient,
    query: str,
    model: str,
    mode: str,
    search_focus: str,
    is_incognito: bool,
    renderer: Renderer,
) -> PerplexityResponse:
    """
    Stream a query to Perplexity and render output in real time.
    Uses multi-strategy text extraction to support all models.
    Returns the complete PerplexityResponse when done.
    """
    result = PerplexityResponse()
    text_buffer = ""
    start_time = time.time()

    with renderer.start_assistant_stream(model) as live:
        try:
            for event in client.ask_stream(
                query=query,
                mode=mode,
                model_preference=model,
                search_focus=search_focus,
                is_incognito=is_incognito,
            ):
                result.raw_events.append(event)

                # Live preview: track streaming chunks for spinner feedback
                for block in event.get("blocks", []):
                    usage = block.get("intended_usage", "")
                    if usage in ("ask_text_0_markdown", "ask_text", "answer"):
                        for patch in block.get("diff_block", {}).get("patches", []):
                            op = patch.get("op")
                            value = patch.get("value")
                            if op == "replace" and isinstance(value, dict):
                                text_buffer = "".join(value.get("chunks", []))
                            elif op == "add":
                                if isinstance(value, str):
                                    text_buffer += value
                                elif isinstance(value, dict):
                                    text_buffer += "".join(value.get("chunks", []))

                if text_buffer:
                    spinner_text = Text()
                    spinner_text.append(" Streaming ", style="dim")
                    spinner_text.append(f"({len(text_buffer)} chars)", style="dim bright_cyan")
                    live.update(Spinner("dots2", text=spinner_text, style="bright_cyan"))

        except KeyboardInterrupt:
            raise
        except Exception as e:
            renderer.print_error(f"Stream error: {e}")

    # ── Multi-strategy extraction ─────────────────────────────────────────
    extracted_text, citations = _extract_text_from_events(result.raw_events)

    # Final fallback: use the live-streamed buffer
    if not extracted_text and text_buffer.strip():
        extracted_text = text_buffer.strip()

    result.text = extracted_text
    result.citations = citations

    elapsed = time.time() - start_time

    if result.text:
        renderer.print_assistant_response(
            text=result.text,
            citations=result.citations,
            model=model,
            elapsed=elapsed,
        )
    else:
        renderer.print_assistant_response(
            text="*(no response — model may not be available or session token expired)*",
            citations=[],
            model=model,
            elapsed=elapsed,
        )
        renderer.print_warning(
            f"Got {len(result.raw_events)} SSE events but could not extract text. "
            "Check your session token or try a different model."
        )

    return result


# ─── Command handlers ─────────────────────────────────────────────────────────

def handle_command(
    cmd: str,
    session: ChatSession,
    renderer: Renderer,
    bridge: MCPToolBridge,
) -> Optional[str]:
    """
    Handle a slash command.
    Returns None if handled, or 'exit' to quit.
    """
    parts = cmd.strip().split(None, 1)
    command = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if command in ("/help", "/?"):
        renderer.print_help()

    elif command == "/model":
        if not arg:
            renderer.print_models_table(_ALL_MODELS, session.model)
        else:
            old = session.model
            session.set_model(arg)
            display = get_model_name(arg)
            renderer.print_success(f"Model changed: [dim]{old}[/] → [bold bright_cyan]{arg}[/] [dim]({display})[/]")

    elif command == "/models":
        renderer.print_models_table(_ALL_MODELS, session.model)

    elif command == "/clear":
        session.clear()
        renderer.print_cleared()

    elif command == "/save":
        path = session.save(arg if arg else None)
        renderer.print_success(f"Session saved to: [dim]{path}[/]")

    elif command == "/load":
        if not arg:
            renderer.print_error("Usage: /load <path>")
        else:
            try:
                loaded = ChatSession.load(arg)
                session.__dict__.update(loaded.__dict__)
                renderer.print_success(
                    f"Session loaded: [dim]{loaded.session_id}[/]  "
                    f"({loaded.message_count} messages)"
                )
            except Exception as e:
                renderer.print_error(f"Failed to load: {e}")

    elif command == "/sessions":
        sessions = ChatSession.list_saved_sessions()
        renderer.print_sessions_table(sessions)

    elif command == "/system":
        if arg:
            session.set_system_prompt(arg)
            renderer.print_success("System prompt updated.")
        else:
            if session.system_prompt:
                renderer.print_info(f"System prompt: [dim]{session.system_prompt}[/]")
            else:
                renderer.print_info("No system prompt set.")

    elif command == "/mode":
        VALID_MODES = ["copilot", "search", "reasoning", "writing"]
        if arg in VALID_MODES:
            session.mode = arg
            renderer.print_success(f"Mode set to: [bold bright_cyan]{arg}[/]")
        else:
            renderer.print_error(f"Invalid mode. Choose from: {', '.join(VALID_MODES)}")

    elif command == "/focus":
        VALID_FOCUS = ["internet", "academic", "writing", "wolfram", "youtube", "reddit"]
        if arg in VALID_FOCUS:
            session.search_focus = arg
            renderer.print_success(f"Search focus set to: [bold bright_cyan]{arg}[/]")
        else:
            renderer.print_error(f"Invalid focus. Choose from: {', '.join(VALID_FOCUS)}")

    elif command == "/incognito":
        session.is_incognito = not session.is_incognito
        state = "ON 🕵" if session.is_incognito else "OFF"
        renderer.print_success(f"Incognito mode: [bold]{state}[/]")

    elif command == "/tools":
        tools = bridge.get_all_tools()
        renderer.print_tools_table(tools)

    elif command == "/tool":
        if not arg:
            renderer.print_error("Usage: /tool <name> [key=value ...]")
        else:
            tool_parts = arg.split(None, 1)
            tool_name = tool_parts[0]
            tool_args_str = tool_parts[1] if len(tool_parts) > 1 else ""
            try:
                args = bridge.parse_tool_args(tool_args_str)
                renderer.print_tool_call(tool_name, args)
                result, elapsed = bridge.call_tool(tool_name, args)
                renderer.print_tool_result(tool_name, result, elapsed)
                session.add_tool_result(tool_name, result)
            except KeyError as e:
                renderer.print_error(f"Tool not found: {e}")
            except Exception as e:
                renderer.print_tool_error(tool_name, str(e))

    elif command == "/mcp":
        if not arg:
            renderer.print_error("Usage: /mcp <config.json>")
        else:
            try:
                loaded = bridge.load_config(arg)
                renderer.print_info(f"Loaded {len(loaded)} server(s): {', '.join(loaded)}")
                renderer.print_info("Connecting…")
                results = bridge.connect_all()
                for name, ok in results.items():
                    if ok:
                        tools = [t for t in bridge.get_all_tools() if t["server"] == name]
                        renderer.print_success(f"[{name}] Connected ({len(tools)} tools)")
                    else:
                        renderer.print_error(f"[{name}] Connection failed")
            except FileNotFoundError as e:
                renderer.print_error(str(e))
            except Exception as e:
                renderer.print_error(f"MCP load error: {e}")

    elif command == "/history":
        renderer.print_history(session.get_history_for_display())

    elif command == "/status":
        renderer.print_status(session)

    elif command == "/debug":
        # Show last N raw events for debugging
        events = session.messages
        n = int(arg) if arg.isdigit() else 3
        renderer.print_info(f"Last {n} raw SSE events from previous response:")
        # This is a dev tool — users shouldn't normally need it
        console.print("[dim]Use /debug <n> to show raw event structures[/]")

    elif command in ("exit", "quit", "/exit", "/quit"):
        return "exit"

    else:
        renderer.print_error(f"Unknown command: [bold]{command}[/]  — type [bold]/help[/] for help")

    return None


# ─── Main REPL ────────────────────────────────────────────────────────────────

def run_cli(
    model: str = DEFAULT_MODEL,
    mcp_config: Optional[str] = None,
    load_session: Optional[str] = None,
    mode: str = "copilot",
    search_focus: str = "internet",
    system_prompt: Optional[str] = None,
    incognito: bool = False,
) -> None:
    """Main CLI entry point."""

    # ── Init client ───────────────────────────────────────
    try:
        client = PerplexityClient()
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")
        console.print(
            "[dim]Create a .env file with PERPLEXITY_SESSION_TOKEN and other required vars.[/]"
        )
        sys.exit(1)

    renderer = Renderer()
    bridge = MCPToolBridge()

    # ── Load or create session ────────────────────────────
    if load_session:
        try:
            session = ChatSession.load(load_session)
            renderer.print_success(f"Session loaded: {session.session_id}")
        except Exception as e:
            renderer.print_error(f"Could not load session: {e}")
            session = ChatSession(model=model, mode=mode, search_focus=search_focus,
                                  system_prompt=system_prompt, is_incognito=incognito)
    else:
        session = ChatSession(
            model=model,
            mode=mode,
            search_focus=search_focus,
            system_prompt=system_prompt,
            is_incognito=incognito,
        )

    # ── Load MCP config ───────────────────────────────────
    connected_tools = []
    if mcp_config:
        try:
            loaded = bridge.load_config(mcp_config)
            results = bridge.connect_all()
            for name, ok in results.items():
                if ok:
                    tools = [t["full_name"] for t in bridge.get_all_tools() if t["server"] == name]
                    connected_tools.extend(tools)
        except Exception as e:
            renderer.print_warning(f"MCP load error: {e}")

    # ── Print banner ──────────────────────────────────────
    renderer.print_banner(
        model=session.model,
        tools=connected_tools if connected_tools else None,
    )

    # ── Input session (history + autocomplete) ────────────
    history_dir = Path.home() / ".perplexity_cli"
    history_dir.mkdir(parents=True, exist_ok=True)

    prompt_session = PromptSession(
        history=FileHistory(str(history_dir / "input_history")),
        auto_suggest=AutoSuggestFromHistory(),
        style=PROMPT_STYLE,
        mouse_support=False,
    )

    # ── Ctrl+C handler ────────────────────────────────────
    def handle_interrupt(sig, frame):
        console.print("\n[dim]Use [bold]exit[/] to quit, or press Ctrl+D.[/]")

    signal.signal(signal.SIGINT, handle_interrupt)

    def get_tools_context() -> str:
        tools = bridge.get_all_tools()
        if not tools:
            return ""
        
        lines = [
            "\n=== LOCAL SYSTEM ACCESS & MCP TOOLS ===",
            "You have direct access to the local machine via the following Model Context Protocol (MCP) tools:",
        ]
        
        for t in tools:
            schema_str = json.dumps(t.get("input_schema", {}).get("properties", {}))
            lines.append(f"- {t['full_name']}: {t['description']}")
            lines.append(f"  Schema: {schema_str}")
        
        lines.extend([
            "",
            "CRITICAL DIRECTIVES FOR TOOL CALLS:",
            "1. If the user asks you to perform local tasks (e.g., list files, check folder, read file, run shell command, check system stats), you MUST execute the appropriate tool instead of claiming you cannot access the system.",
            "2. To invoke a tool, you MUST output exactly one line at the very start of your reply in this format:",
            "   TOOL_CALL: <tool_name> <json_arguments>",
            "   Example: TOOL_CALL: local.list_directory {\"path\": \".\"}",
            "   Example: TOOL_CALL: local.execute_command {\"command\": \"ls -la\"}",
            "3. DO NOT search the web for local operations. Just call the tool directly.",
            "4. Do NOT output any preamble, thoughts, markdown formatting, or conversational text. Output ONLY the TOOL_CALL line.",
            "=========================================\n"
        ])
        return "\n".join(lines)

    # ── Main REPL loop ────────────────────────────────────
    while True:
        try:
            user_input = prompt_session.prompt(
                HTML('<prompt>You</prompt>  <dimmed>▸  </dimmed>'),
                style=PROMPT_STYLE,
            ).strip()
        except KeyboardInterrupt:
            continue
        except EOFError:
            console.print("\n[dim]Goodbye![/]")
            break

        if not user_input:
            continue

        # ── Slash commands ────────────────────────────────
        if user_input.startswith("/") or user_input.lower() in ("exit", "quit"):
            result = handle_command(user_input, session, renderer, bridge)
            if result == "exit":
                console.print("[dim]Goodbye! 👋[/]")
                bridge.disconnect_all()
                break
            continue

        # ── Send to Perplexity ────────────────────────────────────────
        session.add_user_message(user_input)

        try:
            max_steps = 3
            step = 0
            while step < max_steps:
                query_with_context = session.build_query_with_context(user_input)
                
                # Check if we are feeding back a tool result in the history
                is_feedback = session.messages and session.messages[-1]["role"] == "tool"
                
                tools_context = get_tools_context()
                if tools_context:
                    if is_feedback:
                        # Append an overriding system directive telling the LLM to synthesize the final answer
                        query_with_context += (
                            "\n\n[SYSTEM DIRECTIVE: The requested tool has been successfully executed, "
                            "and the results are provided above in your Conversation History. "
                            "Do NOT output another TOOL_CALL directive. Use the results from the tool "
                            "to answer the user's original question directly now in plain, friendly text.]"
                        )
                    else:
                        query_with_context += tools_context

                response = stream_perplexity(
                    client=client,
                    query=query_with_context,
                    model=session.model,
                    mode=session.mode,
                    search_focus=session.search_focus,
                    is_incognito=session.is_incognito,
                    renderer=renderer,
                )

                if not response.text:
                    break

                session.add_assistant_message(response.text, response.citations)
                
                # Execute tool call and check if one was triggered
                tool_called = _maybe_handle_tool_call(response.text, bridge, session, renderer)
                if not tool_called:
                    # Final response generated, break loop
                    break
                
                # Increment step and prepare to re-ask Perplexity
                step += 1
                if step < max_steps:
                    console.print("\n[dim]Feeding tool results back to Perplexity...[/]\n")

        except KeyboardInterrupt:
            console.print("\n[dim]Request cancelled.[/]\n")
        except Exception as e:
            renderer.print_error(f"Request failed: {e}")

    # ── Auto-save on exit ─────────────────────────────────
    if session.message_count > 0:
        try:
            saved_path = session.save()
            console.print(f"[dim]Session auto-saved to: {saved_path}[/]")
        except Exception:
            pass


def _maybe_handle_tool_call(
    response_text: str,
    bridge: MCPToolBridge,
    session: ChatSession,
    renderer: Renderer,
) -> bool:
    """Auto-execute tool calls if LLM response contains TOOL_CALL: directives.
    Uses highly robust splits and JSON substring balancing to handle duplicate,
    concatenated, or conversation-polluted tool calls.
    Returns True if at least one tool call was executed.
    """
    if not bridge.has_tools:
        return False

    import re
    # Split by case-insensitive 'TOOL_CALL:'
    parts = re.split(r'(?i)TOOL_CALL:', response_text)
    if len(parts) <= 1:
        return False

    called = False
    seen_calls = set()

    for part in parts[1:]:
        part = part.strip()
        if not part:
            continue

        # Split by first whitespace to separate tool name from arguments
        sub_parts = part.split(None, 1)
        tool_name = sub_parts[0].strip()
        args_str = sub_parts[1].strip() if len(sub_parts) > 1 else "{}"

        # Highly robust JSON cleaning: if it starts with '{', find the longest valid JSON substring
        if args_str.startswith("{"):
            for idx in range(len(args_str), 0, -1):
                sub = args_str[:idx]
                if sub.endswith("}"):
                    try:
                        # Test if this substring is valid JSON
                        json.loads(sub)
                        args_str = sub
                        break
                    except json.JSONDecodeError:
                        pass

        # Deduplicate identical tool calls in the same turn
        call_key = (tool_name, args_str)
        if call_key in seen_calls:
            continue
        seen_calls.add(call_key)

        try:
            args = json.loads(args_str) if args_str.startswith("{") else bridge.parse_tool_args(args_str)
            renderer.print_tool_call(tool_name, args)
            result, elapsed = bridge.call_tool(tool_name, args)
            renderer.print_tool_result(tool_name, result, elapsed)
            session.add_tool_result(tool_name, result)
            called = True
        except Exception as e:
            renderer.print_tool_error(tool_name, str(e))
            called = True

    return called


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Perplexity Interactive CLI — multi-turn chat with MCP tool support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cli.py
  python3 cli.py --model sonar-pro
  python3 cli.py --model claude46sonnetthinking --mcp ./mcp_tools.json
  python3 cli.py --load ~/.perplexity_cli/sessions/session_20240525.json
  python3 cli.py --system "You are a cybersecurity expert."
  python3 cli.py --incognito
        """,
    )
    parser.add_argument(
        "--model", "-m",
        default=os.getenv("DEFAULT_MODEL", DEFAULT_MODEL),
        help=f"Model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--mcp",
        metavar="CONFIG_JSON",
        help="Path to MCP tools config JSON file",
    )
    parser.add_argument(
        "--load",
        metavar="SESSION_JSON",
        help="Load a saved session file",
    )
    parser.add_argument(
        "--mode",
        default=os.getenv("DEFAULT_MODE", "copilot"),
        choices=["copilot", "search", "reasoning", "writing"],
        help="Search mode (default: copilot)",
    )
    parser.add_argument(
        "--focus",
        default=os.getenv("DEFAULT_SEARCH_FOCUS", "internet"),
        choices=["internet", "academic", "writing", "wolfram", "youtube", "reddit"],
        help="Search focus (default: internet)",
    )
    parser.add_argument(
        "--system",
        default=os.getenv("CLI_SYSTEM_PROMPT", ""),
        help="System prompt to prepend to all queries",
    )
    parser.add_argument(
        "--incognito",
        action="store_true",
        help="Enable incognito mode",
    )

    args = parser.parse_args()

    run_cli(
        model=args.model,
        mcp_config=args.mcp,
        load_session=args.load,
        mode=args.mode,
        search_focus=args.focus,
        system_prompt=args.system or None,
        incognito=args.incognito,
    )


if __name__ == "__main__":
    main()
