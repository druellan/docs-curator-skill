#!/usr/bin/env python3
"""Validate OKF v0.1 conformance for a docs bundle.

Usage: check-okf.py [DOCS_DIR]
  DOCS_DIR defaults to ./docs.

Conformance rules (per OKF v0.1 §9):
    1. Every non-reserved .md file contains parseable YAML frontmatter fenced by '---'.
    2. Every frontmatter block contains a non-empty `type:` field.

Exits 0 if conformant, 1 if any violation, 2 on usage error.
"""
import re
import sys
from pathlib import Path

RESERVED = {"index.md", "log.md"}

TYPE_RE = re.compile(r"^\s*type\s*:\s*(.+?)\s*$", re.MULTILINE)


def extract_frontmatter(content: str) -> str | None:
    if not content.startswith("---"):
        return None
    end_match = re.search(r"\n---\s*(?:\n|$)", content[3:])
    if not end_match:
        return ""
    return content[3 : 3 + end_match.start() + 1]


def parse_type_strict(frontmatter_text: str) -> tuple[str | None, str | None]:
    for line in frontmatter_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped and not stripped.startswith("-"):
            return None, f"invalid YAML frontmatter: malformed line '{line.strip()}'"

    match = TYPE_RE.search(frontmatter_text)
    if not match:
        return None, None

    raw = match.group(1).strip().strip("'\"")
    if not raw or raw.startswith("#"):
        return None, None
    return raw, None


def main() -> int:
    docs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")

    if not docs_dir.is_dir():
        print(f"docs directory '{docs_dir}' not found", file=sys.stderr)
        return 2

    violations: list[tuple[str, str]] = []
    checked = 0

    for md_file in sorted(docs_dir.rglob("*.md")):
        if md_file.name in RESERVED:
            continue
        checked += 1
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError as exc:
            violations.append((str(md_file), f"cannot read: {exc}"))
            continue

        frontmatter_text = extract_frontmatter(content)
        if frontmatter_text is None:
            violations.append((str(md_file), "missing frontmatter (file must start with '---')"))
            continue
        if frontmatter_text == "":
            violations.append((str(md_file), "unclosed frontmatter (no closing '---' on its own line)"))
            continue

        type_value, strict_error = parse_type_strict(frontmatter_text)
        if strict_error:
            violations.append((str(md_file), strict_error))
            continue

        if not type_value or not type_value.strip():
            violations.append((str(md_file), "missing or empty `type:` in frontmatter"))

    if violations:
        print(f"OKF conformance: {len(violations)} violation(s) in {checked} file(s) checked:")
        for path, msg in violations:
            print(f"  {path}: {msg}")
    else:
        print(f"OKF conformance: {checked} file(s) checked, all conformant.")

    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
