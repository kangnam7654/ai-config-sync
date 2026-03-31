#!/usr/bin/env python3
"""Token measurement script for Claude Code system prompt optimization.

Usage:
    uv run python scripts/measure.py [--project-dir PATH] [--global] [--json]

Measures tokens consumed by agent descriptions, skill descriptions,
CLAUDE.md files, and memory files. Identifies optimization opportunities.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken not installed. Run: uv pip install tiktoken", file=sys.stderr)
    sys.exit(1)

enc = tiktoken.encoding_for_model("gpt-4")


def count_tokens(text: str) -> int:
    return len(enc.encode(text))


def has_korean(text: str, threshold: int = 10) -> bool:
    kr_chars = sum(1 for c in text if "\uac00" <= c <= "\ud7a3" or "\u3131" <= c <= "\u3163")
    return kr_chars > threshold


def has_examples_section(text: str) -> bool:
    return "\\nExamples:\\n" in text or "\\nNOT this agent:" in text


def get_description(path: str) -> str:
    text = open(path).read()
    m = re.search(r'description:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
    if not m:
        m = re.search(r"description:\s*(.+?)$", text, re.MULTILINE)
    return m.group(1) if m else ""


def scan_agents(claude_dir: str) -> list[dict]:
    agents_dir = os.path.join(claude_dir, "agents")
    if not os.path.isdir(agents_dir):
        return []
    results = []
    for f in sorted(os.listdir(agents_dir)):
        if not f.endswith(".md"):
            continue
        path = os.path.join(agents_dir, f)
        desc = get_description(path)
        tokens = count_tokens(desc)
        results.append({
            "name": f.replace(".md", ""),
            "file": path,
            "tokens": tokens,
            "korean": has_korean(desc),
            "has_examples": has_examples_section(desc),
            "desc_preview": desc[:100],
        })
    return results


def scan_skills(claude_dir: str) -> list[dict]:
    skills_dir = os.path.join(claude_dir, "skills")
    if not os.path.isdir(skills_dir):
        return []
    results = []
    for d in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        desc = get_description(skill_path)
        tokens = count_tokens(desc)
        results.append({
            "name": d,
            "file": skill_path,
            "tokens": tokens,
            "korean": has_korean(desc),
            "has_examples": has_examples_section(desc),
            "desc_preview": desc[:100],
        })
    return results


def scan_file(path: str, label: str) -> dict | None:
    if not os.path.isfile(path):
        return None
    text = open(path).read()
    return {
        "label": label,
        "file": path,
        "tokens": count_tokens(text),
        "lines": len(text.splitlines()),
        "korean": has_korean(text),
    }


def find_project_memory_dir(project_dir: str, claude_dir: str) -> str | None:
    """Find the project-specific memory directory."""
    normalized = project_dir.replace("/", "-")
    projects_dir = os.path.join(claude_dir, "projects")
    if not os.path.isdir(projects_dir):
        return None
    for d in os.listdir(projects_dir):
        if normalized in d:
            mem_dir = os.path.join(projects_dir, d, "memory")
            if os.path.isdir(mem_dir):
                return mem_dir
    return None


def scan_memory(memory_dir: str) -> dict:
    result = {"dir": memory_dir, "files": [], "total_tokens": 0, "issues": []}
    if not os.path.isdir(memory_dir):
        return result
    memory_md = os.path.join(memory_dir, "MEMORY.md")
    if os.path.isfile(memory_md):
        text = open(memory_md).read()
        tokens = count_tokens(text)
        result["files"].append({"name": "MEMORY.md", "tokens": tokens})
        result["total_tokens"] += tokens

    # Check for misplaced files (non-memory files in memory dir)
    for root, dirs, files in os.walk(memory_dir):
        for f in files:
            if f == "MEMORY.md":
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, memory_dir)
            if not f.endswith(".md"):
                result["issues"].append(f"Non-memory file in memory/: {rel}")
    return result


def build_report(
    agents: list[dict],
    skills: list[dict],
    files: list[dict],
    memory: dict | None,
    scope: str,
) -> dict:
    report = {"scope": scope, "categories": [], "total_tokens": 0, "opportunities": []}

    if agents:
        agent_total = sum(a["tokens"] for a in agents)
        report["categories"].append({
            "name": "Agent descriptions",
            "count": len(agents),
            "tokens": agent_total,
        })
        report["total_tokens"] += agent_total
        korean_agents = [a for a in agents if a["korean"]]
        if korean_agents:
            report["opportunities"].append({
                "type": "korean_to_english",
                "target": "agents",
                "count": len(korean_agents),
                "estimated_savings": sum(a["tokens"] for a in korean_agents) * 0.6,
                "items": [a["name"] for a in korean_agents],
            })
        verbose_agents = [a for a in agents if a["has_examples"]]
        if verbose_agents:
            report["opportunities"].append({
                "type": "compress_descriptions",
                "target": "agents",
                "count": len(verbose_agents),
                "estimated_savings": sum(a["tokens"] for a in verbose_agents) * 0.5,
                "items": [a["name"] for a in verbose_agents],
            })

    if skills:
        skill_total = sum(s["tokens"] for s in skills)
        report["categories"].append({
            "name": "Skill descriptions",
            "count": len(skills),
            "tokens": skill_total,
        })
        report["total_tokens"] += skill_total
        korean_skills = [s for s in skills if s["korean"]]
        if korean_skills:
            report["opportunities"].append({
                "type": "korean_to_english",
                "target": "skills",
                "count": len(korean_skills),
                "estimated_savings": sum(s["tokens"] for s in korean_skills) * 0.6,
                "items": [s["name"] for s in korean_skills],
            })

    for f in files:
        if f:
            report["categories"].append({
                "name": f["label"],
                "tokens": f["tokens"],
                "lines": f["lines"],
                "korean": f["korean"],
            })
            report["total_tokens"] += f["tokens"]
            if f["korean"]:
                report["opportunities"].append({
                    "type": "korean_to_english",
                    "target": f["label"],
                    "count": 1,
                    "estimated_savings": f["tokens"] * 0.6,
                    "items": [f["file"]],
                })

    if memory and memory.get("issues"):
        report["opportunities"].append({
            "type": "misplaced_files",
            "target": "memory",
            "count": len(memory["issues"]),
            "items": memory["issues"],
        })

    return report


def print_report(report: dict) -> None:
    print(f"\n{'='*60}")
    print(f"  Token Measurement Report (scope: {report['scope']})")
    print(f"{'='*60}\n")

    print(f"{'Category':<30} {'Tokens':>8} {'Details':>20}")
    print(f"{'-'*30} {'-'*8} {'-'*20}")
    for cat in report["categories"]:
        details = ""
        if "count" in cat:
            details = f"{cat['count']} items"
        elif "lines" in cat:
            details = f"{cat['lines']} lines"
            if cat.get("korean"):
                details += " [KR]"
        print(f"{cat['name']:<30} {cat['tokens']:>8} {details:>20}")
    print(f"{'-'*30} {'-'*8} {'-'*20}")
    print(f"{'TOTAL':<30} {report['total_tokens']:>8}")

    if report["opportunities"]:
        print(f"\n{'Optimization Opportunities':}")
        print(f"{'-'*60}")
        for opp in report["opportunities"]:
            savings = f"~{int(opp.get('estimated_savings', 0))} tokens" if opp.get("estimated_savings") else ""
            print(f"  [{opp['type']}] {opp['target']}: {opp['count']} items {savings}")
            for item in opp["items"][:5]:
                print(f"    - {item}")
            if len(opp["items"]) > 5:
                print(f"    ... and {len(opp['items'])-5} more")
    else:
        print("\nNo optimization opportunities found.")


def main():
    parser = argparse.ArgumentParser(description="Measure Claude Code token consumption")
    parser.add_argument("--project-dir", default=os.getcwd(), help="Project directory path")
    parser.add_argument("--global", dest="include_global", action="store_true", help="Include global agents/skills")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    claude_dir = os.path.expanduser("~/.claude")
    scope = "global+project" if args.include_global else "project"

    agents = scan_agents(claude_dir) if args.include_global else []
    skills = scan_skills(claude_dir) if args.include_global else []

    files = []
    if args.include_global:
        files.append(scan_file(os.path.join(claude_dir, "CLAUDE.md"), "Global CLAUDE.md"))

    project_claude = os.path.join(args.project_dir, "CLAUDE.md")
    files.append(scan_file(project_claude, "Project CLAUDE.md"))

    memory_dir = find_project_memory_dir(args.project_dir, claude_dir)
    memory = scan_memory(memory_dir) if memory_dir else None
    if memory:
        files.append({
            "label": "Project MEMORY.md",
            "file": os.path.join(memory_dir, "MEMORY.md"),
            "tokens": memory["total_tokens"],
            "lines": 0,
            "korean": False,
        })

    report = build_report(agents, skills, files, memory, scope)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
