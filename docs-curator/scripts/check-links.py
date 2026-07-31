#!/usr/bin/env python3
"""Walk /docs/ and report broken internal links.

Usage: check-links.py [DOCS_DIR]
  DOCS_DIR defaults to ./docs.

Scans markdown links, checks local markdown targets, and reports missing files.
External URLs are not checked.
"""
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^(```|~~~)")
EXTERNAL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def parse_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if " " in target and not target.startswith("<"):
        target = target.split(" ", 1)[0]
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target


def resolve_local_target(docs_dir: Path, source_file: Path, target: str) -> Path:
    if target.startswith("/"):
        return docs_dir.parent / target.lstrip("/")
    return (source_file.parent / target).resolve()


def main() -> int:
    docs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    if not docs_dir.is_dir():
        print(f"docs directory '{docs_dir}' not found", file=sys.stderr)
        return 2

    checked_files = 0
    checked_links = 0
    broken: list[dict[str, str | int]] = []
    style_violations: list[dict[str, str | int]] = []

    for md_file in sorted(docs_dir.rglob("*.md")):
        checked_files += 1
        in_code = False
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"cannot read {md_file}: {exc}", file=sys.stderr)
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if FENCE_RE.match(stripped):
                in_code = not in_code
                continue
            if in_code:
                continue

            for match in LINK_RE.finditer(line):
                checked_links += 1
                raw_target = match.group(1)
                target = parse_link_target(raw_target)
                if not target or target.startswith("#"):
                    continue

                if EXTERNAL_SCHEME_RE.match(target):
                    continue

                path_target = target.split("#", 1)[0].split("?", 1)[0]
                if not path_target:
                    continue

                if path_target.endswith(".md") and not path_target.startswith("/docs/"):
                    style_violations.append(
                        {
                            "source": str(md_file),
                            "line": line_no,
                            "target": target,
                            "message": "link is not root-absolute (/docs/...)",
                        }
                    )

                if not path_target.endswith(".md"):
                    continue

                fs_path = resolve_local_target(docs_dir, md_file, path_target)
                if fs_path.exists():
                    continue

                broken.append(
                    {
                        "source": str(md_file),
                        "line": line_no,
                        "target": target,
                        "message": "target markdown file not found",
                    }
                )

    for item in broken:
        print(f"BROKEN  {item['source']}:{item['line']} -> {item['target']}")
    for item in style_violations:
        print(f"STYLE   {item['source']}:{item['line']} -> {item['target']} ({item['message']})")
    print(
        f"\nScanned {checked_files} file(s), checked {checked_links} link(s), "
        f"{len(broken)} broken, {len(style_violations)} style violation(s)."
    )

    return 0 if not broken and not style_violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
