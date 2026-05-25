#!/usr/bin/env python3
"""
Local Shell & Filesystem MCP Server

Provides standard shell execution and filesystem tools to the Perplexity CLI agentic loop.
"""

import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Local Shell & Filesystem")


@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List contents of a directory.

    Args:
        path: Path to the directory (default: ".").
    """
    try:
        resolved = os.path.abspath(path)
        items = os.listdir(resolved)
        lines = [f"Directory: {resolved}", ""]
        for item in sorted(items):
            full_path = os.path.join(resolved, item)
            suffix = "/" if os.path.isdir(full_path) else ""
            size = f" ({os.path.getsize(full_path)} bytes)" if os.path.isfile(full_path) else ""
            lines.append(f"- {item}{suffix}{size}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a local file.

    Args:
        path: Path to the file.
    """
    try:
        resolved = os.path.abspath(path)
        if not os.path.isfile(resolved):
            return f"Error: Path is not a file: {resolved}"
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def execute_command(command: str, cwd: str = ".") -> str:
    """Execute a bash shell command locally and return stdout/stderr.

    Args:
        command: The shell command to run (e.g. 'uname -a', 'python3 -m pip list').
        cwd: Working directory to run the command in (default: ".").
    """
    try:
        resolved_cwd = os.path.abspath(cwd)
        # Execute with 30s timeout to prevent hanging the CLI loop
        result = subprocess.run(
            command,
            shell=True,
            cwd=resolved_cwd,
            text=True,
            capture_output=True,
            timeout=30,
        )
        output = []
        if result.stdout:
            output.append("[Stdout]")
            output.append(result.stdout)
        if result.stderr:
            output.append("[Stderr]")
            output.append(result.stderr)
        if not output:
            output.append(f"[Process exited with code {result.returncode}]")
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {e}"


if __name__ == "__main__":
    mcp.run()
