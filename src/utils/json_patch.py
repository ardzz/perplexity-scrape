"""
JSON Patch utilities.

Helper functions for working with JSON Patch operations (RFC 6902).
Used to process Perplexity's diff_block patches.
"""

from typing import Any, Optional


def extract_chunk_index(path: str) -> Optional[int]:
    """
    Extract chunk index from a JSON Patch path.

    Args:
        path: JSON Patch path (e.g., "/chunks/5")

    Returns:
        The chunk index if path is a chunk path, None otherwise.

    Examples:
        >>> extract_chunk_index("/chunks/5")
        5
        >>> extract_chunk_index("/progress")
        None
    """
    if not path.startswith("/chunks/"):
        return None
    try:
        return int(path.split("/")[-1])
    except (ValueError, IndexError):
        return None


def is_chunk_add(op: str, path: str) -> bool:
    """
    Check if a patch operation adds a new chunk.

    Args:
        op: The operation type ("add", "replace", "remove")
        path: The JSON Patch path

    Returns:
        True if this is an add operation to chunks array.
    """
    return op == "add" and path.startswith("/chunks/")


def is_progress_update(op: str, path: str) -> bool:
    """
    Check if a patch operation updates progress status.

    Args:
        op: The operation type
        path: The JSON Patch path

    Returns:
        True if this updates the progress field.
    """
    return op == "replace" and path == "/progress"


def is_initial_block(op: str, path: str) -> bool:
    """
    Check if a patch operation is an initial block setup.

    Args:
        op: The operation type
        path: The JSON Patch path

    Returns:
        True if this is a replace operation at root path.
    """
    return op == "replace" and path == ""


def get_nested_value(data: dict, path: str) -> Any:
    """
    Get a value from a nested dict using JSON Patch path notation.

    Args:
        data: The dictionary to traverse
        path: JSON Patch path (e.g., "/chunks/0" or "/progress")

    Returns:
        The value at the path, or None if not found.
    """
    if not path or path == "/":
        return data

    # Remove leading slash and split
    parts = path.lstrip("/").split("/")
    current = data

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list):
            try:
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            except ValueError:
                return None
        else:
            return None

    return current
