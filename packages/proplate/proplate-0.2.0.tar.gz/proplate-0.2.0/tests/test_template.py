"""Tests for template parsing and rendering."""

from proplate.template import fill_placeholders, find_placeholders, parse_template


def test_parse_template_without_frontmatter():
    """Test parsing a template without YAML frontmatter."""
    content = "# Simple Template\n\nHello {{name}}!"
    result = parse_template(content)

    assert result["metadata"] == dict()
    assert result["body"] == "# Simple Template\n\nHello {{name}}!"


def test_parse_template_with_frontmatter():
    """Test parsing a template with YAML frontmatter."""
    content = """---
title: Test Template
description: A test template
---

# {{topic}}

Content here."""

    result = parse_template(content)

    assert result["metadata"]["title"] == "Test Template"
    assert result["metadata"]["description"] == "A test template"
    assert "# {{topic}}" in result["body"]
    assert "Content here." in result["body"]


def test_parse_template_with_body_separators():
    """Test that --- in body is preserved (critical maxsplit=2 test)."""
    content = """---
title: Template with Separators
---
# Main Content

---

This separator should be preserved.

---

And this one too."""

    result = parse_template(content)

    assert result["metadata"]["title"] == "Template with Separators"
    # Count separators in body - should have 2 (the ones after frontmatter)
    assert result["body"].count("---") == 2


def test_parse_template_invalid_yaml():
    """Test that invalid YAML frontmatter falls back gracefully."""
    content = """---
title: Test
invalid yaml [[[
---

Body content"""

    result = parse_template(content)

    # Should treat entire content as body when YAML is invalid
    assert result["metadata"] == dict()
    assert "title: Test" in result["body"]


def test_parse_template_non_dict_yaml():
    """Test that non-dict YAML (plain text, numbers, etc.) is handled gracefully."""
    # Case 1: Plain text between separators
    content1 = """---
Just some random text
---

Body content"""

    result1 = parse_template(content1)
    assert result1["metadata"] == dict()
    assert result1["body"] == "Body content"

    # Case 2: Number between separators
    content2 = """---
42
---

Template body"""

    result2 = parse_template(content2)
    assert result2["metadata"] == dict()
    assert result2["body"] == "Template body"

    # Case 3: List between separators
    content3 = """---
- item1
- item2
---

Body here"""

    result3 = parse_template(content3)
    assert result3["metadata"] == dict()
    assert result3["body"] == "Body here"


def test_find_placeholders_single():
    """Test finding a single placeholder."""
    text = "Hello {{name}}!"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 1
    assert placeholders[0]["name"] == "name"
    assert placeholders[0]["default"] is None


def test_find_placeholders_multiple():
    """Test finding multiple unique placeholders."""
    text = "Hello {{name}}, your {{item}} is ready. Thanks {{name}}!"
    placeholders = find_placeholders(text)

    # Should return unique values, preserving order of first appearance
    assert len(placeholders) == 2
    assert placeholders[0]["name"] == "name"
    assert placeholders[1]["name"] == "item"


def test_find_placeholders_none():
    """Test finding placeholders when none exist."""
    text = "No placeholders here!"
    placeholders = find_placeholders(text)

    assert placeholders == list()


def test_find_placeholders_complex():
    """Test finding placeholders in complex template."""
    text = """# {{title}}

## Context
{{context}}

## Details
{{details}}

Remember: {{title}} is important!"""

    placeholders = find_placeholders(text)

    assert len(placeholders) == 3
    assert placeholders[0]["name"] == "title"
    assert placeholders[1]["name"] == "context"
    assert placeholders[2]["name"] == "details"


def test_find_placeholders_with_spaces_and_punctuation():
    """Test finding descriptive placeholders with spaces and punctuation."""
    text = """{{Your feature, refactoring, or change request here. Be specific about WHAT you want and WHY it is valuable.}}

Additional context: {{Any relevant background information, constraints, or dependencies}}"""

    placeholders = find_placeholders(text)

    assert len(placeholders) == 2
    assert placeholders[0]["name"] == "Your feature, refactoring, or change request here. Be specific about WHAT you want and WHY it is valuable."
    assert placeholders[1]["name"] == "Any relevant background information, constraints, or dependencies"


def test_find_placeholders_with_whitespace_variations():
    """Test that placeholders with different whitespace are normalized."""
    text = """{{name}}
{{ name }}
{{  name  }}"""

    placeholders = find_placeholders(text)

    # Should deduplicate to single 'name' after stripping
    assert len(placeholders) == 1
    assert placeholders[0]["name"] == "name"


def test_fill_placeholders_single():
    """Test filling a single placeholder."""
    text = "Hello {{name}}!"
    values = {"name": "Alice"}
    result = fill_placeholders(text, values)

    assert result == "Hello Alice!"


def test_fill_placeholders_multiple():
    """Test filling multiple placeholders."""
    text = "Hello {{name}}, your {{item}} is ready."
    values = {"name": "Bob", "item": "package"}
    result = fill_placeholders(text, values)

    assert result == "Hello Bob, your package is ready."


def test_fill_placeholders_repeated():
    """Test that repeated placeholders are all replaced."""
    text = "{{greeting}} {{name}}! Welcome {{name}}!"
    values = {"greeting": "Hi", "name": "Charlie"}
    result = fill_placeholders(text, values)

    assert result == "Hi Charlie! Welcome Charlie!"


def test_fill_placeholders_multiline():
    """Test filling placeholders with multi-line values."""
    text = "# Review\n\n{{content}}\n\n---\n{{footer}}"
    values = {
        "content": "Line 1\nLine 2\nLine 3",
        "footer": "End of review"
    }
    result = fill_placeholders(text, values)

    assert "Line 1\nLine 2\nLine 3" in result
    assert "End of review" in result


def test_fill_placeholders_with_spaces_and_punctuation():
    """Test filling descriptive placeholders with spaces and punctuation."""
    text = "Request: {{Your feature request here. Be specific!}}\n\nContext: {{Background info}}"
    values = {
        "Your feature request here. Be specific!": "Add dark mode to the settings page",
        "Background info": "Users have been requesting this for months"
    }
    result = fill_placeholders(text, values)

    assert "Request: Add dark mode to the settings page" in result
    assert "Context: Users have been requesting this for months" in result


def test_fill_placeholders_with_whitespace_variations():
    """Test that placeholders with different whitespace still get replaced."""
    text = "{{name}} and {{ name }} and {{  name  }}"
    values = {"name": "Alice"}
    result = fill_placeholders(text, values)

    assert result == "Alice and Alice and Alice"


def test_full_workflow():
    """Test complete workflow: parse, find, fill."""
    template_content = """---
title: Code Review
description: Template for code reviews
---

# Code Review: {{file_path}}

## Context
{{context}}

## Focus Areas
{{focus_areas}}

---

Reviewed by: {{reviewer}}"""

    # Parse
    parsed = parse_template(template_content)
    assert parsed["metadata"]["title"] == "Code Review"

    # Find placeholders
    placeholders = find_placeholders(parsed["body"])
    placeholder_names = [p["name"] for p in placeholders]
    assert set(placeholder_names) == {"file_path", "context", "focus_areas", "reviewer"}

    # Fill
    values = {
        "file_path": "src/auth.py",
        "context": "Adding OAuth support",
        "focus_areas": "Security, error handling",
        "reviewer": "Alice"
    }
    result = fill_placeholders(parsed["body"], values)

    assert "src/auth.py" in result
    assert "Adding OAuth support" in result
    assert "Security, error handling" in result
    assert "Alice" in result
    # Verify the --- separator in body is preserved
    assert "---" in result


def test_find_placeholders_with_defaults():
    """Test finding placeholders with default values."""
    text = "Hello {{name:Guest}}! Your status: {{status:Active}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 2
    assert placeholders[0]["name"] == "name"
    assert placeholders[0]["default"] == "Guest"
    assert placeholders[0]["raw"] == "name:Guest"
    assert placeholders[1]["name"] == "status"
    assert placeholders[1]["default"] == "Active"


def test_find_placeholders_without_defaults():
    """Test finding placeholders without defaults (backward compatibility)."""
    text = "Hello {{name}}! Your status: {{status}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 2
    assert placeholders[0]["name"] == "name"
    assert placeholders[0]["default"] is None
    assert placeholders[1]["name"] == "status"
    assert placeholders[1]["default"] is None


def test_find_placeholders_mixed():
    """Test finding mix of placeholders with and without defaults."""
    text = "{{title:Untitled}} by {{author}} - {{year:2024}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 3
    assert placeholders[0]["name"] == "title"
    assert placeholders[0]["default"] == "Untitled"
    assert placeholders[1]["name"] == "author"
    assert placeholders[1]["default"] is None
    assert placeholders[2]["name"] == "year"
    assert placeholders[2]["default"] == "2024"


def test_find_placeholders_empty_default():
    """Test placeholder with empty default value."""
    text = "{{name:}} - {{value: }}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 2
    assert placeholders[0]["name"] == "name"
    assert placeholders[0]["default"] == ""
    assert placeholders[1]["name"] == "value"
    assert placeholders[1]["default"] == ""


def test_find_placeholders_default_with_colon():
    """Test default value containing a colon."""
    text = "{{url:https://example.com}} and {{time:12:30:00}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 2
    assert placeholders[0]["name"] == "url"
    assert placeholders[0]["default"] == "https://example.com"
    assert placeholders[1]["name"] == "time"
    assert placeholders[1]["default"] == "12:30:00"


def test_find_placeholders_default_with_spaces():
    """Test default value with spaces and punctuation."""
    text = "{{greeting:Hello, World!}} {{message:This is a default message.}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 2
    assert placeholders[0]["name"] == "greeting"
    assert placeholders[0]["default"] == "Hello, World!"
    assert placeholders[1]["name"] == "message"
    assert placeholders[1]["default"] == "This is a default message."


def test_find_placeholders_whitespace_normalization_with_defaults():
    """Test whitespace normalization with default values."""
    text = "{{ name : Guest }} and {{name:Guest}} and {{  name  :  Guest  }}"
    placeholders = find_placeholders(text)

    # Should deduplicate to single 'name' entry
    assert len(placeholders) == 1
    assert placeholders[0]["name"] == "name"
    assert placeholders[0]["default"] == "Guest"


def test_fill_placeholders_with_defaults_syntax():
    """Test filling placeholders that have default syntax in template."""
    text = "Hello {{name:Guest}}! Status: {{status:Active}}"
    values = {"name": "Alice", "status": "Online"}
    result = fill_placeholders(text, values)

    assert result == "Hello Alice! Status: Online"


def test_fill_placeholders_mixed_syntax():
    """Test filling mix of placeholders with and without default syntax."""
    text = "{{title:Untitled}} by {{author}} ({{year:2024}})"
    values = {"title": "My Book", "author": "Bob", "year": "2023"}
    result = fill_placeholders(text, values)

    assert result == "My Book by Bob (2023)"


def test_fill_placeholders_default_with_colon_in_value():
    """Test filling placeholder where default contains colon."""
    text = "URL: {{url:https://example.com}}"
    values = {"url": "https://newsite.com:8080"}
    result = fill_placeholders(text, values)

    assert result == "URL: https://newsite.com:8080"


def test_fill_placeholders_repeated_with_defaults():
    """Test that repeated placeholders with defaults are all replaced."""
    text = "{{greeting:Hi}} {{name:Guest}}! {{greeting:Hi}} again, {{name:Guest}}!"
    values = {"greeting": "Hello", "name": "Alice"}
    result = fill_placeholders(text, values)

    assert result == "Hello Alice! Hello again, Alice!"


def test_default_values_full_workflow():
    """Test complete workflow with default values: parse, find, fill."""
    template_content = """---
title: Greeting Template
description: Template with default values
---

# {{title:Welcome}}

Hello {{name:Guest}}!

Your message: {{message:No message provided}}

Contact: {{email:}}"""

    # Parse
    parsed = parse_template(template_content)
    assert parsed["metadata"]["title"] == "Greeting Template"

    # Find placeholders
    placeholders = find_placeholders(parsed["body"])
    assert len(placeholders) == 4

    placeholder_dict = {p["name"]: p for p in placeholders}
    assert placeholder_dict["title"]["default"] == "Welcome"
    assert placeholder_dict["name"]["default"] == "Guest"
    assert placeholder_dict["message"]["default"] == "No message provided"
    assert placeholder_dict["email"]["default"] == ""

    # Fill with some values, leaving some to use defaults
    values = {
        "title": "Greetings",
        "name": "Guest",  # Using default value explicitly
        "message": "Hello from tests!",
        "email": ""  # Using empty default
    }
    result = fill_placeholders(parsed["body"], values)

    assert "# Greetings" in result
    assert "Hello Guest!" in result
    assert "Your message: Hello from tests!" in result
    assert "Contact:" in result


def test_find_placeholders_escaped_colon_in_name():
    """Test placeholder with escaped colon in name (no default)."""
    text = "{{What time\\: HH\\:MM}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 1
    assert placeholders[0]["name"] == "What time: HH:MM"
    assert placeholders[0]["default"] is None


def test_find_placeholders_escaped_colon_in_default():
    """Test placeholder with escaped colon in default value."""
    text = "{{url:https\\://example.com}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 1
    assert placeholders[0]["name"] == "url"
    assert placeholders[0]["default"] == "https://example.com"


def test_find_placeholders_escaped_colon_in_both():
    """Test placeholder with escaped colons in both name and default."""
    text = "{{API\\: endpoint:https\\://api.example.com/v1}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 1
    assert placeholders[0]["name"] == "API: endpoint"
    assert placeholders[0]["default"] == "https://api.example.com/v1"


def test_find_placeholders_multiple_escaped_colons():
    """Test default value with multiple colons (time format)."""
    text = "{{timestamp:12\\:30\\:45}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 1
    assert placeholders[0]["name"] == "timestamp"
    assert placeholders[0]["default"] == "12:30:45"


def test_find_placeholders_mixed_escaped_unescaped():
    """Test mix of escaped colons (in name/default) and separator colon."""
    text = "Meeting at {{time (HH\\:MM):14\\:30}} for {{topic:Project\\: Review}}"
    placeholders = find_placeholders(text)

    assert len(placeholders) == 2
    assert placeholders[0]["name"] == "time (HH:MM)"
    assert placeholders[0]["default"] == "14:30"
    assert placeholders[1]["name"] == "topic"
    assert placeholders[1]["default"] == "Project: Review"


def test_fill_placeholders_escaped_colon_in_name():
    """Test filling placeholder with escaped colon in name."""
    text = "Time format: {{HH\\:MM\\:SS}}"
    values = {"HH:MM:SS": "14:30:45"}
    result = fill_placeholders(text, values)

    assert result == "Time format: 14:30:45"


def test_fill_placeholders_escaped_colon_in_template():
    """Test filling placeholder with escaped colon in template default."""
    text = "URL: {{url:https\\://example.com}}"
    values = {"url": "https://newsite.com"}
    result = fill_placeholders(text, values)

    assert result == "URL: https://newsite.com"


def test_fill_placeholders_preserve_escaped_colons_unfilled():
    """Test that escaped colons are preserved if placeholder not filled."""
    text = "Time: {{time\\: HH\\:MM:12\\:00}}"
    values = {}  # Not providing value
    result = fill_placeholders(text, values)

    # Should preserve original escaped syntax since not replaced
    assert "{{time\\: HH\\:MM:12\\:00}}" in result


def test_escaped_colons_full_workflow():
    """Test complete workflow with escaped colons: parse, find, fill."""
    template_content = """---
title: API Configuration
description: Template with URLs and colons
---

# API Endpoint: {{endpoint}}

**Base URL:** {{base_url:https\\://api.example.com}}
**Timeout:** {{timeout:30\\:00 (mm\\:ss)}}
**Notes:** {{notes:Connection via HTTPS\\: protocol}}"""

    # Parse
    parsed = parse_template(template_content)
    assert parsed["metadata"]["title"] == "API Configuration"

    # Find placeholders
    placeholders = find_placeholders(parsed["body"])
    assert len(placeholders) == 4

    placeholder_dict = {p["name"]: p for p in placeholders}
    assert "endpoint" in placeholder_dict
    assert placeholder_dict["endpoint"]["default"] is None

    assert "base_url" in placeholder_dict
    assert placeholder_dict["base_url"]["default"] == "https://api.example.com"

    assert "timeout" in placeholder_dict
    assert placeholder_dict["timeout"]["default"] == "30:00 (mm:ss)"

    assert "notes" in placeholder_dict
    assert placeholder_dict["notes"]["default"] == "Connection via HTTPS: protocol"

    # Fill
    values = {
        "endpoint": "/api/v1/users",
        "base_url": "https://api.example.com",  # Using default
        "timeout": "60:00 (mm:ss)",  # Override
        "notes": "Secure connection"
    }
    result = fill_placeholders(parsed["body"], values)

    assert "API Endpoint: /api/v1/users" in result
    assert "https://api.example.com" in result
    assert "60:00 (mm:ss)" in result
    assert "Secure connection" in result
