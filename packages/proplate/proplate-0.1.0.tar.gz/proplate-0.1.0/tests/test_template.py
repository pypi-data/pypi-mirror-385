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

    assert placeholders == ["name"]


def test_find_placeholders_multiple():
    """Test finding multiple unique placeholders."""
    text = "Hello {{name}}, your {{item}} is ready. Thanks {{name}}!"
    placeholders = find_placeholders(text)

    # Should return unique values, preserving order of first appearance
    assert placeholders == ["name", "item"]


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

    assert placeholders == ["title", "context", "details"]


def test_find_placeholders_with_spaces_and_punctuation():
    """Test finding descriptive placeholders with spaces and punctuation."""
    text = """{{Your feature, refactoring, or change request here. Be specific about WHAT you want and WHY it is valuable.}}

Additional context: {{Any relevant background information, constraints, or dependencies}}"""

    placeholders = find_placeholders(text)

    assert len(placeholders) == 2
    assert placeholders[0] == "Your feature, refactoring, or change request here. Be specific about WHAT you want and WHY it is valuable."
    assert placeholders[1] == "Any relevant background information, constraints, or dependencies"


def test_find_placeholders_with_whitespace_variations():
    """Test that placeholders with different whitespace are normalized."""
    text = """{{name}}
{{ name }}
{{  name  }}"""

    placeholders = find_placeholders(text)

    # Should deduplicate to single 'name' after stripping
    assert placeholders == ["name"]


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
    assert set(placeholders) == {"file_path", "context", "focus_areas", "reviewer"}

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
