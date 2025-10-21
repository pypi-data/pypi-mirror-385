"""Clipboard operations with cross-platform error handling."""

import pyperclip
from rich.console import Console

console = Console()


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard with error handling.

    :param text: The text content to copy to clipboard
    :return: True if successful, False if clipboard unavailable
    """
    try:
        pyperclip.copy(text)
        console.print("✓ Copied to clipboard! Paste in Cursor with Cmd+V", style="bold green")
        return True
    except Exception as e:
        console.print(f"✗ Could not copy to clipboard: {e}", style="bold red")
        console.print("\n[bold]Generated content:[/bold]")
        console.print(text)
        return False

