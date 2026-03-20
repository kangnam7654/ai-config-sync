#!/usr/bin/env python3
"""
Quick validation script for agents - validates agent .md file structure.
"""

import re
import sys

import yaml
from pathlib import Path


def validate_agent(agent_path):
    """Basic validation of an agent .md file.

    Args:
        agent_path: Path to the agent .md file (not a directory).

    Returns:
        (bool, str) — (is_valid, message)
    """
    agent_path = Path(agent_path)

    if not agent_path.exists():
        return False, f"Agent file not found: {agent_path}"

    if not agent_path.suffix == ".md":
        return False, f"Agent file must be a .md file, got: {agent_path.suffix}"

    content = agent_path.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Allowed properties for agent .md
    ALLOWED_PROPERTIES = {"name", "description", "model", "tools", "memory"}

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Validate name (kebab-case)
    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Validate description
    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description and len(description) > 1024:
        return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    # Validate model (if present)
    model = frontmatter.get("model")
    if model is not None:
        valid_models = {"haiku", "sonnet", "opus"}
        if model not in valid_models:
            return False, f"Model must be one of {valid_models}, got '{model}'"

    # Validate memory (must be 'user')
    memory = frontmatter.get("memory")
    if memory is None:
        return False, "Missing 'memory' in frontmatter (must be 'user')"
    if memory != "user":
        return False, f"Memory must be 'user', got '{memory}'"

    # Check required body sections
    body = content[match.end():]
    required_sections = ["## Core Principle", "## Scope", "## Rules", "## Workflow", "## Edge Cases"]
    missing = [s for s in required_sections if s not in body]
    if missing:
        return False, f"Missing required sections: {', '.join(missing)}"

    return True, "Agent is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <agent.md>")
        sys.exit(1)

    valid, message = validate_agent(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
