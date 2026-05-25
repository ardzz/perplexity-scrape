"""
Terminal Renderer

Rich-based output renderer for the Perplexity CLI.
Handles markdown, streaming tokens, citations, and tool call display.
"""

import sys
from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
from rich import box


console = Console()
error_console = Console(stderr=True, style="bold red")


class Renderer:
    """Handles all terminal output formatting."""

    BRAND_COLOR = "bright_cyan"
    USER_COLOR = "bright_green"
    ASSISTANT_COLOR = "bright_white"
    TOOL_COLOR = "bright_yellow"
    DIM_COLOR = "dim"
    ERROR_COLOR = "bright_red"
    CITATION_COLOR = "cyan"

    def __init__(self, no_color: bool = False, compact: bool = False):
        self.no_color = no_color
        self.compact = compact

    def print_banner(self, model: str, tools: list[str] | None = None) -> None:
        """Print the startup banner."""
        tool_str = ", ".join(tools) if tools else "none"

        banner = Text()
        banner.append("  Perplexity", style="bold bright_cyan")
        banner.append(" CLI  ", style="bold white")
        banner.append("⚡", style="bright_yellow")

        subtitle = Text()
        subtitle.append("  Model: ", style="dim")
        subtitle.append(model, style="bold bright_cyan")
        subtitle.append("   Tools: ", style="dim")
        subtitle.append(tool_str, style="bright_yellow" if tools else "dim")

        console.print()
        console.print(Panel(
            f"{banner}\n{subtitle}",
            border_style="bright_cyan",
            padding=(0, 1),
        ))
        console.print(
            "  Type [bold]/help[/bold] for commands · [bold]exit[/bold] to quit",
            style="dim"
        )
        console.print()

    def print_help(self) -> None:
        """Print the help table."""
        table = Table(
            title="Available Commands",
            box=box.ROUNDED,
            border_style="bright_cyan",
            show_header=True,
            header_style="bold bright_cyan",
            padding=(0, 1),
        )
        table.add_column("Command", style="bold bright_yellow", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Example", style="dim")

        commands = [
            ("/model <name>",  "Switch active model",             "/model sonar-pro"),
            ("/models",        "List all available models",        "/models"),
            ("/clear",         "Clear conversation history",       "/clear"),
            ("/save [path]",   "Save session to JSON file",        "/save ~/chat.json"),
            ("/load <path>",   "Load a saved session",             "/load ~/chat.json"),
            ("/sessions",      "List saved sessions",              "/sessions"),
            ("/system <text>", "Set system prompt",                "/system You are a security expert"),
            ("/system",        "Show current system prompt",       "/system"),
            ("/mode <name>",   "Set search mode (copilot/search)", "/mode search"),
            ("/focus <name>",  "Set search focus",                 "/focus academic"),
            ("/incognito",     "Toggle incognito mode",            "/incognito"),
            ("/tools",         "List connected MCP tools",         "/tools"),
            ("/tool <n> [a]",  "Call MCP tool manually",           "/tool burpsuite.scan url=..."),
            ("/mcp <config>",  "Load MCP servers from JSON file",  "/mcp ./mcp_tools.json"),
            ("/history",       "Show conversation history",        "/history"),
            ("/status",        "Show session status",              "/status"),
            ("/help",          "Show this help",                   "/help"),
            ("exit / quit",    "Exit the CLI",                     "exit"),
        ]

        for cmd, desc, example in commands:
            table.add_row(cmd, desc, example)

        console.print(table)
        console.print()

    def print_status(self, session) -> None:
        """Print current session status."""
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column("Key", style="dim")
        table.add_column("Value", style="bright_white")

        table.add_row("Model", f"[bold bright_cyan]{session.model}[/]")
        table.add_row("Mode", session.mode)
        table.add_row("Focus", session.search_focus)
        table.add_row("Messages", str(session.message_count))
        table.add_row("Incognito", "✓ On" if session.is_incognito else "✗ Off")
        table.add_row("Session ID", session.session_id)
        if session.system_prompt:
            prompt_preview = session.system_prompt[:60] + "…" if len(session.system_prompt) > 60 else session.system_prompt
            table.add_row("System", prompt_preview)
        else:
            table.add_row("System", "[dim]not set[/]")

        console.print(Panel(table, title="Session Status", border_style="bright_cyan"))
        console.print()

    def print_user_prompt(self) -> str:
        """Print user prompt prefix (for manual input loops)."""
        return ""

    def print_user_message(self, content: str) -> None:
        """Echo the user message with styling."""
        console.print()
        console.print(f"[bold {self.USER_COLOR}]You[/]  [dim]▸[/]  {content}")
        console.print()

    def start_assistant_stream(self, model: str) -> Live:
        """Start a live spinner while waiting for first token."""
        spinner = Spinner("dots2", text=f" [dim]Thinking ({model})…[/]", style="bright_cyan")
        return Live(spinner, console=console, refresh_per_second=10, transient=True)

    def print_assistant_response(
        self,
        text: str,
        citations: list[dict] | None = None,
        model: str = "",
        elapsed: float = 0,
    ) -> None:
        """Render the full assistant response with markdown and citations."""
        # Header
        header = Text()
        header.append("Perplexity", style=f"bold {self.BRAND_COLOR}")
        if model:
            header.append(f"  [{model}]", style="dim")
        if elapsed:
            header.append(f"  {elapsed:.1f}s", style="dim")

        console.print(header)
        console.print(Rule(style="dim cyan"))

        # Main response (markdown rendered)
        md = Markdown(text, code_theme="monokai")
        console.print(md)

        # Citations
        if citations:
            self._print_citations(citations)

        console.print()

    def _print_citations(self, citations: list[dict]) -> None:
        """Print citations as a compact footnote list."""
        console.print()
        console.print("[dim]── Sources ──────────────────────────────────────[/]")
        for i, cite in enumerate(citations[:8], 1):  # limit to 8
            title = cite.get("title", "Unknown")
            url = cite.get("url", "")
            console.print(
                f"  [{self.CITATION_COLOR}][{i}][/] [link={url}]{title}[/link]",
                style="dim"
            )

    def print_tool_call(self, tool_name: str, args: dict) -> None:
        """Print a tool call being executed."""
        args_str = "  ".join(f"[dim]{k}=[/][bright_white]{v}[/]" for k, v in args.items())
        console.print(
            f"  [bright_yellow]🔧 Tool[/]  [bold]{tool_name}[/]  {args_str}"
        )

    def print_tool_result(self, tool_name: str, result: str, elapsed: float = 0) -> None:
        """Print a tool result."""
        elapsed_str = f" ({elapsed:.1f}s)" if elapsed else ""
        preview = result[:200] + "…" if len(result) > 200 else result
        console.print(
            f"  [green]✓ Result[/] [dim]{tool_name}{elapsed_str}[/]"
        )
        if preview:
            console.print(f"  [dim]{preview}[/]")
        console.print()

    def print_tool_error(self, tool_name: str, error: str) -> None:
        """Print a tool execution error."""
        console.print(
            f"  [bright_red]✗ Tool Error[/] [bold]{tool_name}[/]: {error}"
        )

    def print_models_table(self, models: list, current: str) -> None:
        """Print available models. Accepts list of str IDs or dicts {id, name, thinking}."""
        table = Table(
            title="Available Models",
            box=box.ROUNDED,
            border_style="bright_cyan",
            show_header=True,
            header_style="bold bright_cyan",
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("ID", style="bold", no_wrap=True)
        table.add_column("Name", style="white")
        table.add_column("", justify="center", width=10)  # thinking badge
        table.add_column("Active", justify="center", width=6)

        for i, m in enumerate(models, 1):
            if isinstance(m, dict):
                mid = m["id"]
                mname = m.get("name", mid)
                thinking = m.get("thinking", False)
            else:
                mid = m
                mname = ""
                thinking = False

            is_active = mid == current
            active_mark = "[bold bright_green]●[/]" if is_active else "[dim]○[/]"
            id_style = "bold bright_cyan" if is_active else "white"
            think_badge = "[bright_yellow]⚡ thinking[/]" if thinking else ""

            table.add_row(str(i), f"[{id_style}]{mid}[/]", mname, think_badge, active_mark)

        console.print(table)
        console.print()

    def print_tools_table(self, tools: list[dict]) -> None:
        """Print connected MCP tools."""
        if not tools:
            console.print("[dim]No MCP tools connected. Use /mcp <config.json> to load.[/]")
            console.print()
            return

        table = Table(
            title="Connected MCP Tools",
            box=box.ROUNDED,
            border_style="bright_yellow",
            show_header=True,
            header_style="bold bright_yellow",
        )
        table.add_column("Tool Name", style="bold bright_yellow")
        table.add_column("Server", style="dim")
        table.add_column("Description", style="white")

        for tool in tools:
            table.add_row(
                tool.get("name", "?"),
                tool.get("server", "?"),
                tool.get("description", "")[:60],
            )

        console.print(table)
        console.print()

    def print_history(self, messages: list[dict]) -> None:
        """Print conversation history."""
        if not messages:
            console.print("[dim]No conversation history yet.[/]")
            return

        console.print(Rule("Conversation History", style="bright_cyan"))
        for msg in messages:
            role = msg["role"]
            content = msg.get("content", "")
            ts = msg.get("timestamp", "")[:19] if msg.get("timestamp") else ""

            if role == "user":
                console.print(f"\n[bold bright_green]You[/] [dim]{ts}[/]")
                console.print(f"  {content}")
            elif role == "assistant":
                console.print(f"\n[bold bright_cyan]Perplexity[/] [dim]{ts}[/]")
                md = Markdown(content[:500] + ("…" if len(content) > 500 else ""))
                console.print(md)
            elif role == "tool":
                console.print(
                    f"\n[bold bright_yellow]Tool: {msg.get('tool_name', '?')}[/] [dim]{ts}[/]"
                )
                console.print(f"  [dim]{content[:200]}[/]")

        console.print(Rule(style="bright_cyan"))
        console.print()

    def print_sessions_table(self, sessions: list[dict]) -> None:
        """Print saved sessions."""
        if not sessions:
            console.print("[dim]No saved sessions found.[/]")
            console.print()
            return

        table = Table(
            title="Saved Sessions",
            box=box.ROUNDED,
            border_style="bright_cyan",
            show_header=True,
            header_style="bold bright_cyan",
        )
        table.add_column("Session ID", style="bold")
        table.add_column("Created", style="dim")
        table.add_column("Model", style="bright_cyan")
        table.add_column("Messages", justify="right")
        table.add_column("Path", style="dim")

        for s in sessions:
            table.add_row(
                s["session_id"],
                s["created_at"][:19],
                s["model"],
                str(s["message_count"]),
                s["path"],
            )

        console.print(table)
        console.print()

    def print_info(self, msg: str) -> None:
        console.print(f"[bright_cyan]ℹ[/]  {msg}")

    def print_success(self, msg: str) -> None:
        console.print(f"[bright_green]✓[/]  {msg}")

    def print_warning(self, msg: str) -> None:
        console.print(f"[bright_yellow]⚠[/]  {msg}")

    def print_error(self, msg: str) -> None:
        console.print(f"[bright_red]✗[/]  {msg}")

    def print_divider(self) -> None:
        console.print(Rule(style="dim"))

    def print_cleared(self) -> None:
        console.clear()
        console.print("[bright_green]✓[/]  Conversation history cleared.")
        console.print()
