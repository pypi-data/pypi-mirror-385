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


def find_placeholders(text: str) -> list[dict[str, str | None]]:
    """
    Find all unique {{placeholder}} or {{placeholder:default}} patterns in text.
    Supports descriptive placeholders with spaces, punctuation, etc.
    Supports default values using colon separator syntax.
    Supports escaping colons with backslash (\\:) for literal colons.

    :param text: Template text to search
    :return: List of unique placeholder dictionaries with 'name', 'default', and 'raw' keys
    """
    # Find all {{...}} patterns, allowing any content except closing braces
    # This supports descriptive placeholders like {{Your request here}}
    matches = re.findall(r"\{\{([^}]+)\}\}", text)
    # Return unique values while preserving order (strip whitespace for consistency)
    seen = set()
    result = list()

    # Placeholder token for escaped colons (unlikely to appear in user text)
    ESCAPED_COLON = "\x00ESCAPED_COLON\x00"

    for match in matches:
        # Parse placeholder:default syntax with escape handling
        raw = match.strip()
        if not raw:
            continue

        # Temporarily replace escaped colons to protect them from splitting
        escaped = raw.replace("\\:", ESCAPED_COLON)

        # Split on first unescaped colon to separate name from default
        if ":" in escaped:
            parts = escaped.split(":", 1)
            name = parts[0].strip().replace(ESCAPED_COLON, ":")
            default = parts[1].strip().replace(ESCAPED_COLON, ":") if len(parts) > 1 else ""
        else:
            name = escaped.strip().replace(ESCAPED_COLON, ":")
            default = None

        # Deduplicate by name only
        if name not in seen:
            seen.add(name)
            result.append({"name": name, "default": default, "raw": raw})

    return result


def fill_placeholders(text: str, values: dict[str, str]) -> str:
    """
    Replace all {{key}} or {{key:default}} with values[key].
    Handles placeholders with varying whitespace (e.g., {{key}}, {{ key }}).
    Extracts placeholder name from default value syntax if present.
    Handles escaped colons (\\:) in placeholder names.

    :param text: Template text with placeholders
    :param values: Dictionary mapping placeholder names to their values
    :return: Text with all placeholders replaced
    """
    # Placeholder token for escaped colons
    ESCAPED_COLON = "\x00ESCAPED_COLON\x00"

    # Use regex to find and replace, handling whitespace variations and defaults
    def replace_func(match):
        raw = match.group(1).strip()

        # Temporarily replace escaped colons
        escaped = raw.replace("\\:", ESCAPED_COLON)

        # Extract placeholder name (before unescaped colon if default syntax used)
        if ":" in escaped:
            name = escaped.split(":", 1)[0].strip().replace(ESCAPED_COLON, ":")
        else:
            name = escaped.strip().replace(ESCAPED_COLON, ":")

        return values.get(name, match.group(0))

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
