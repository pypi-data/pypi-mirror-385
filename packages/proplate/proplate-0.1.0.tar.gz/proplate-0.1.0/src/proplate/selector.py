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


def prompt_for_value(placeholder: str) -> str:
    """
    Prompt user for a placeholder value.
    Supports single-line input or multi-line editor.

    :param placeholder: Name of the placeholder
    :return: User-provided value
    """
    # First, try simple text input
    value = questionary.text(f"→ {placeholder}:",
                             instruction="(Press Enter for multi-line editor, or type directly)").ask()

    if value is None:  # User cancelled
        return ""

    # If user pressed Enter on empty input, offer multi-line editor
    if value == "":
        use_editor = questionary.confirm("Open multi-line editor?",
                                         default=True).ask()

        if use_editor:
            value = open_editor()
        else:
            # Fallback to multi-line text input
            console.print(f"[yellow]Enter value for {placeholder} (Ctrl+D or Ctrl+Z when done):[/yellow]")
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
