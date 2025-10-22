"""Debug utilities for logging LLM and Kimina server responses."""

from __future__ import annotations

import os
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Create console for debug output
_debug_console = Console()

# Check if debug mode is enabled
_DEBUG_ENABLED = os.environ.get("GOEDELS_POETRY_DEBUG", "").lower() in ("1", "true", "yes")


def is_debug_enabled() -> bool:
    """
    Check if debug mode is enabled via the GOEDELS_POETRY_DEBUG environment variable.

    Returns
    -------
    bool
        True if debug mode is enabled, False otherwise.
    """
    return _DEBUG_ENABLED


def log_llm_response(agent_name: str, response: str, response_type: str = "response") -> None:
    """
    Log an LLM response if debug mode is enabled.

    Parameters
    ----------
    agent_name : str
        The name of the agent (e.g., "FORMALIZER_AGENT_LLM", "PROVER_AGENT_LLM")
    response : str
        The response content from the LLM
    response_type : str, optional
        The type of response (e.g., "response", "parsed"), by default "response"
    """
    if not _DEBUG_ENABLED:
        return

    title = f"[bold cyan]{agent_name}[/bold cyan] - {response_type}"

    # Try to detect if response is Lean code
    if "```lean" in response or "theorem" in response or "lemma" in response:
        # Display as Lean syntax
        syntax = Syntax(response, "lean", theme="monokai", line_numbers=False)
        _debug_console.print(Panel(syntax, title=title, border_style="cyan"))
    else:
        # Display as regular text
        _debug_console.print(Panel(response, title=title, border_style="cyan"))


def log_kimina_response(operation: str, response: dict[str, Any]) -> None:
    """
    Log a Kimina server response if debug mode is enabled.

    Parameters
    ----------
    operation : str
        The operation performed (e.g., "check", "ast_code")
    response : dict
        The parsed response from the Kimina server
    """
    if not _DEBUG_ENABLED:
        return

    title = f"[bold magenta]KIMINA_SERVER[/bold magenta] - {operation}"

    # Format the response nicely
    import json

    formatted_response = json.dumps(response, indent=2, default=str)
    syntax = Syntax(formatted_response, "json", theme="monokai", line_numbers=False)
    _debug_console.print(Panel(syntax, title=title, border_style="magenta"))


def log_debug_message(message: str, style: str = "yellow") -> None:
    """
    Log a general debug message if debug mode is enabled.

    Parameters
    ----------
    message : str
        The debug message to log
    style : str, optional
        The style to apply to the message, by default "yellow"
    """
    if not _DEBUG_ENABLED:
        return

    _debug_console.print(f"[{style}][DEBUG][/{style}] {message}")
