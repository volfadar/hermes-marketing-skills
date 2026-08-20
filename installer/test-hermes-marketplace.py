#!/usr/bin/env python3
"""Contract test for Hermes-installable, globally namespaced skill bundles."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
BASE_NAMES = (
    "marketing-orchestrator",
    "brand-strategy-coach",
    "content-creator",
    "social-publishing",
    "waha-marketing",
    "email-marketing",
    "cloakserve-research",
    "setup",
    "discipline",
)
SKILL_NAMES = tuple(f"ibras-{name}" for name in BASE_NAMES)
ALLOWED_SUPPORT_DIRS = frozenset(
    {"references", "templates", "scripts", "assets", "examples"}
)
LOCAL_LINK_RE = re.compile(
    r"(?:\]\(|`|(?:^|[\s\"']))"
    r"((?:references|templates|scripts|assets|examples)/[^\s)`\"'<>]+)",
    re.MULTILINE,
)
FRONTMATTER_NAME_RE = re.compile(r"\A---\s*\n.*?^name:\s*([^\n]+)$", re.MULTILINE | re.DOTALL)
LEGACY_DOC_REF_RE = re.compile(
    r"(?<!scripts/)\b(?:lib|hooks)/|"
    r"(?<!assets/)\bdata/(?:options|platforms|sources)\.yaml|"
    r"\bshared/scripts/"
)
NONCANONICAL_SKILL_ID_RE = re.compile(
    r"\bskill-ibras-(?:" + "|".join(map(re.escape, BASE_NAMES)) + r")\b|"
    r"`(?:" + "|".join(map(re.escape, BASE_NAMES)) + r")(?:/[^`]*)?`"
)


def referenced_support_paths(skill_md: str) -> set[str]:
    """Mirror Hermes v0.20.2 support-path extraction for bundle downloads."""
    paths: set[str] = set()
    for match in LOCAL_LINK_RE.finditer(skill_md.replace("\\", "/")):
        raw = unquote(urlsplit(match.group(1).rstrip(".,;:")).path)
        posix = PurePosixPath(raw)
        parts = [part for part in posix.parts if part not in {"", "."}]
        if raw.startswith("/") or not parts or ".." in parts:
            raise AssertionError(f"unsafe manifest path: {raw}")
        normalized = "/".join(parts)
        if parts[0] in ALLOWED_SUPPORT_DIRS:
            paths.add(normalized)
    return paths


def shipped_support_files(skill_dir: Path) -> set[str]:
    files: set[str] = set()
    for top in ALLOWED_SUPPORT_DIRS:
        directory = skill_dir / top
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                files.add(path.relative_to(skill_dir).as_posix())
    return files


def check_uninstaller(errors: list[str]) -> None:
    """Prove --only cannot escape skills/ while valid exact names still work."""
    script = ROOT / "installer" / "uninstall.sh"
    if not script.is_file():
        errors.append("installer/uninstall.sh missing")
        return

    with tempfile.TemporaryDirectory(prefix="ibras-uninstall-contract-") as tmp:
        home = Path(tmp) / "hermes"
        profile = home / "business" / "profile.yaml"
        valid_skill = home / "skills" / SKILL_NAMES[0]
        profile.parent.mkdir(parents=True)
        valid_skill.mkdir(parents=True)
        profile.write_text("usaha: aman\n", encoding="utf-8")

        traversal = subprocess.run(
            ["bash", str(script), "--home", str(home), "--only", "../business"],
            text=True,
            capture_output=True,
            check=False,
        )
        if traversal.returncode == 0:
            errors.append("uninstall --only accepts an unknown traversal target")
        if not profile.is_file():
            errors.append("uninstall --only traversal deleted business/profile.yaml")

        valid = subprocess.run(
            ["bash", str(script), "--home", str(home), "--only", SKILL_NAMES[0]],
            text=True,
            capture_output=True,
            check=False,
        )
        if valid.returncode != 0 or valid_skill.exists():
            errors.append("uninstall --only rejects or fails to remove a canonical skill")
        if not profile.is_file():
            errors.append("valid uninstall modified business/profile.yaml")


def main() -> int:
    errors: list[str] = []

    for old_name, skill_name in zip(BASE_NAMES, SKILL_NAMES):
        old_dir = ROOT / old_name
        skill_dir = ROOT / skill_name
        if old_dir.exists():
            errors.append(f"legacy marketplace directory still exists: {old_name}")
        if not skill_dir.is_dir():
            errors.append(f"canonical skill directory missing: {skill_name}")
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{skill_name}: SKILL.md missing")
            continue

        skill_md = skill_file.read_text(encoding="utf-8")
        name_match = FRONTMATTER_NAME_RE.search(skill_md)
        actual_name = name_match.group(1).strip() if name_match else ""
        if actual_name != skill_name:
            errors.append(
                f"{skill_name}: frontmatter name is {actual_name!r}, expected {skill_name!r}"
            )

        for forbidden in ("lib", "hooks", "data"):
            if (skill_dir / forbidden).exists():
                errors.append(
                    f"{skill_name}: unsupported root runtime directory remains: {forbidden}/"
                )

        doctor_common = skill_dir / "scripts" / "doctor-common.sh"
        if doctor_common.is_file() and "test -x" in doctor_common.read_text(encoding="utf-8"):
            errors.append(
                f"{skill_name}: doctor-common requires executable bits that Hermes Hub "
                "does not preserve"
            )

        try:
            referenced = referenced_support_paths(skill_md)
        except AssertionError as exc:
            errors.append(f"{skill_name}: {exc}")
            continue
        shipped = shipped_support_files(skill_dir)
        missing = sorted(shipped - referenced)
        stale = sorted(referenced - shipped)
        if missing:
            errors.append(
                f"{skill_name}: {len(missing)} support file(s) absent from SKILL.md manifest: "
                + ", ".join(missing[:8])
            )
        if stale:
            errors.append(
                f"{skill_name}: {len(stale)} manifest path(s) do not exist: "
                + ", ".join(stale[:8])
            )

        readable_files = {skill_file}
        readable_files.update(
            path
            for path in skill_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".yaml", ".yml"}
        )
        for readable in sorted(readable_files):
            text = readable.read_text(encoding="utf-8", errors="replace")
            match = LEGACY_DOC_REF_RE.search(text)
            if match:
                rel = readable.relative_to(skill_dir).as_posix()
                errors.append(
                    f"{skill_name}: legacy support path in agent-readable {rel}: "
                    f"{match.group(0)}"
                )
            identity_match = NONCANONICAL_SKILL_ID_RE.search(text)
            if identity_match:
                rel = readable.relative_to(skill_dir).as_posix()
                errors.append(
                    f"{skill_name}: noncanonical skill identity in agent-readable {rel}: "
                    f"{identity_match.group(0)}"
                )

    check_uninstaller(errors)

    if errors:
        print(f"marketplace contract: FAIL ({len(errors)} issue(s))", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"marketplace contract: PASS ({len(SKILL_NAMES)} namespaced, "
          "complete Hermes bundles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
