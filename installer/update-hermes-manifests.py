#!/usr/bin/env python3
"""Regenerate explicit support-file links consumed by Hermes Skills Hub."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = (
    "ibras-marketing-orchestrator",
    "ibras-brand-strategy-coach",
    "ibras-content-creator",
    "ibras-social-publishing",
    "ibras-waha-marketing",
    "ibras-email-marketing",
    "ibras-cloakserve-research",
)
SUPPORT_DIRS = ("references", "templates", "scripts", "assets", "examples")
START = "<!-- HERMES_BUNDLE_MANIFEST_START -->"
END = "<!-- HERMES_BUNDLE_MANIFEST_END -->"


def support_files(skill_dir: Path) -> list[str]:
    paths: list[str] = []
    for top in SUPPORT_DIRS:
        directory = skill_dir / top
        if not directory.exists():
            continue
        paths.extend(
            path.relative_to(skill_dir).as_posix()
            for path in directory.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        )
    return sorted(paths)


def render_manifest(paths: list[str]) -> str:
    lines = [
        START,
        "## Hermes bundle manifest",
        "",
        "Hermes Skills Hub installs only support files linked directly from this file.",
        "These links are the complete runtime manifest; load individual files only when needed.",
        "",
    ]
    current_group = ""
    for path in paths:
        group = path.split("/", 1)[0]
        if group != current_group:
            if current_group:
                lines.append("")
            lines.extend((f"### {group}", ""))
            current_group = group
        lines.append(f"- [{path}]({path})")
    lines.extend(("", END))
    return "\n".join(lines)


def update_skill(skill_name: str) -> int:
    skill_dir = ROOT / skill_name
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise SystemExit(f"missing skill file: {skill_file}")

    text = skill_file.read_text(encoding="utf-8").rstrip()
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1:
            raise SystemExit(f"malformed existing manifest markers: {skill_file}")
        before, remainder = text.split(START, 1)
        _old, after = remainder.split(END, 1)
        text = (before.rstrip() + "\n" + after.lstrip()).rstrip()

    paths = support_files(skill_dir)
    skill_file.write_text(text + "\n\n" + render_manifest(paths) + "\n", encoding="utf-8")
    return len(paths)


def main() -> int:
    total = 0
    for skill_name in SKILL_NAMES:
        count = update_skill(skill_name)
        total += count
        print(f"{skill_name}: {count} support files")
    print(f"updated 7 manifests ({total} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
