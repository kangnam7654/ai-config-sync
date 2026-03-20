"""Shared utilities for agent-creator scripts."""

from pathlib import Path


def parse_agent_md(agent_path: Path) -> tuple[str, str, str]:
    """Parse an agent .md file, returning (name, description, full_content).

    Unlike parse_skill_md which takes a directory and reads SKILL.md inside it,
    this takes the .md file path directly since agents are single files.
    """
    content = agent_path.read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError(f"{agent_path.name} missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError(f"{agent_path.name} missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            # Handle YAML multiline indicators (>, |, >-, |-)
            if value in (">", "|", ">-", "|-"):
                continuation_lines: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            else:
                # Handle quoted multiline descriptions
                description = value.strip('"').strip("'")
        i += 1

    return name, description, content
