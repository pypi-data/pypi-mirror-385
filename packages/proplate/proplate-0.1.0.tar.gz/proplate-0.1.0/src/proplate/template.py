"""Template parsing, placeholder extraction, and rendering."""

import re
from pathlib import Path

import yaml


def parse_template(content: str) -> dict[str, dict | str]:
    """
    Parse template with optional YAML frontmatter.
    Only the first --- block at the start is treated as frontmatter.
    All subsequent --- in the body are preserved as-is.

    :param content: Raw template file content
    :return: Dictionary with 'metadata' and 'body' keys
    """
    if content.startswith("---\n"):
        parts = content.split("---", 2)  # maxsplit=2 is critical!
        if len(parts) >= 3:
            _, frontmatter, body = parts
            try:
                metadata = yaml.safe_load(frontmatter)
                # Ensure metadata is a dict (YAML can return str, int, list, etc.)
                if not isinstance(metadata, dict):
                    metadata = dict()
                return {"metadata": metadata or dict(), "body": body.strip()}
            except yaml.YAMLError:
                # Invalid YAML, treat entire file as body
                return {"metadata": dict(), "body": content}

    return {"metadata": dict(), "body": content}


def find_placeholders(text: str) -> list[str]:
    """
    Find all unique {{placeholder}} patterns in text.
    Supports descriptive placeholders with spaces, punctuation, etc.

    :param text: Template text to search
    :return: List of unique placeholder names
    """
    # Find all {{...}} patterns, allowing any content except closing braces
    # This supports descriptive placeholders like {{Your request here}}
    matches = re.findall(r"\{\{([^}]+)\}\}", text)
    # Return unique values while preserving order (strip whitespace for consistency)
    seen = set()
    result = list()
    for match in matches:
        cleaned = match.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def fill_placeholders(text: str, values: dict[str, str]) -> str:
    """
    Replace all {{key}} with values[key].
    Handles placeholders with varying whitespace (e.g., {{key}}, {{ key }}).

    :param text: Template text with placeholders
    :param values: Dictionary mapping placeholder names to their values
    :return: Text with all placeholders replaced
    """
    # Use regex to find and replace, handling whitespace variations
    def replace_func(match):
        placeholder = match.group(1).strip()
        return values.get(placeholder, match.group(0))

    return re.sub(r"\{\{([^}]+)\}\}", replace_func, text)


def get_template_info(template_path: Path) -> dict[str, str]:
    """
    Extract metadata from a template file.

    :param template_path: Path to template file
    :return: Dictionary with 'name', 'title', and 'description'
    """
    content = template_path.read_text()
    parsed = parse_template(content)
    metadata = parsed["metadata"]

    name = template_path.stem
    title = metadata.get("title", name)
    description = metadata.get("description", "")

    return {"name": name,
            "title": title,
            "description": description}
