"""Interactive template selection and placeholder prompting."""

import os
import subprocess
import tempfile
from pathlib import Path

import questionary
from rich.console import Console

from proplate.template import get_template_info

console = Console()


def select_template(templates_dir: Path) -> Path | None:
    """
    Show interactive fuzzy-searchable template selector.

    :param templates_dir: Directory containing template files
    :return: Selected template path, or None if cancelled
    """
    template_files = sorted(templates_dir.glob("*.md"))

    if not template_files:
        console.print("✗ No templates found in ~/.proplate/templates/", style="bold red")
        console.print("→ Add .md template files to that directory", style="yellow")
        return None

    # Build choices list with descriptions
    choices = list()
    template_map = dict()

    for template_path in template_files:
        info = get_template_info(template_path)
        name = info["name"]
        description = info["description"]

        if description:
            label = f"{name} - {description}"
        else:
            label = name

        choices.append(label)
        template_map[label] = template_path

    # Show interactive selector
    selected = questionary.select("Select a template:",
                                  choices=choices).ask()

    if selected is None:  # User cancelled
        return None

    return template_map[selected]


def prompt_for_value(placeholder: dict[str, str | None]) -> str:
    """
    Prompt user for a placeholder value.
    Supports single-line input, default values, or multi-line editor.
    Special trigger: Type '-' to open multi-line editor.

    :param placeholder: Dictionary with 'name', 'default', and 'raw' keys
    :return: User-provided value or default value if available
    """
    name = placeholder["name"]
    default = placeholder.get("default")

    # Build prompt message
    if default is not None:
        prompt_msg = f"→ {name} (default: {default}):"
        instruction = "(Enter=default, '-'=editor, or type value)"
    else:
        prompt_msg = f"→ {name}:"
        instruction = "(Enter=editor, '-'=editor, or type value)"

    # First, try simple text input
    value = questionary.text(prompt_msg, instruction=instruction).ask()

    if value is None:  # User cancelled
        return default if default is not None else ""

    # Check for multi-line editor trigger
    if value == "-":
        value = open_editor()
        return value

    # If user pressed Enter on empty input
    if value == "":
        # If default exists, use it
        if default is not None:
            return default

        # Otherwise, offer multi-line editor
        use_editor = questionary.confirm("Open multi-line editor?",
                                         default=True).ask()

        if use_editor:
            value = open_editor()
        else:
            # Fallback to multi-line text input
            console.print(f"[yellow]Enter value for {name} (Ctrl+D or Ctrl+Z when done):[/yellow]")
            lines = list()
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            value = "\n".join(lines)

    return value


def open_editor() -> str:
    """
    Open user's preferred editor for multi-line input.

    :return: Text entered in editor
    """
    editor = os.environ.get("EDITOR", "vim")

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tf:
        temp_path = tf.name

    try:
        # Open editor
        subprocess.run([editor, temp_path], check=True)

        # Read content
        with open(temp_path, "r") as f:
            content = f.read()

        return content.strip()
    except Exception as e:
        console.print(f"✗ Editor failed: {e}", style="bold red")
        return ""
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except Exception:
            pass
