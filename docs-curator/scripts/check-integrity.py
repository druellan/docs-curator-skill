#!/usr/bin/env python3
"""Check documentation integrity for an OKF v0.2 docs bundle.

Usage: check-integrity.py [DOCS_DIR] [--lenient] [--only okf,index,links]
  DOCS_DIR defaults to ./docs.
  --lenient drops the project-field checks (title, description, generated,
  status, okf_version); the OKF v0.2 §11 conformance checks always run.
  --only runs a subset of checks (default: okf,index,links).

Checks:
  okf    - OKF v0.2 §11 conformance: parseable frontmatter, non-empty `type`,
           reserved index and log structure. The default (strict) mode also
           requires title, description, generated, and a valid status.
  index  - index.md coverage: every concept listed, every sub-index linked,
           every entry carrying the linked page's frontmatter description.
  links  - markdown links: no broken local targets, root-absolute style.

Exits 0 if clean, 1 if any issue, 2 on usage error.
"""
import re
import sys
from pathlib import Path

RESERVED = {"index.md", "log.md"}
VALID_SECTIONS = ("okf", "index", "links")

TYPE_RE = re.compile(r"^\s*type\s*:\s*(.+?)\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^(#{2,})\s+(.+?)\s*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
STATUS_VALUES = ("draft", "stable", "deprecated")
STRICT_FIELDS = ("title", "description")

ENTRY_RE = re.compile(r"^\s*[-*]\s+\[[^\]]+\]\(([^)]+)\)\s*(.*)$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
DESCRIPTION_RE = re.compile(r"^\s*description\s*:\s*(.+?)\s*$", re.MULTILINE)
FENCE_RE = re.compile(r"^(```|~~~)")
EXTERNAL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


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


def field_value(frontmatter_text: str, key: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", frontmatter_text, re.MULTILINE)
    if not match:
        return None
    raw = match.group(1).strip().strip("'\"")
    return raw or None


def mapping_fields(frontmatter_text: str, key: str) -> dict[str, str] | None:
    """Return the subfields of an inline ({a: 1}) or indented mapping field."""
    lines = frontmatter_text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.split(":", 1)[0].strip() != key:
            continue
        inline = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
        if inline.startswith("{") and inline.endswith("}"):
            fields: dict[str, str] = {}
            for part in inline[1:-1].split(","):
                name, sep, value = part.partition(":")
                if sep and name.strip():
                    fields[name.strip()] = value.strip().strip("'\"")
            return fields
        fields = {}
        base_indent = len(line) - len(line.lstrip())
        for following in lines[index + 1 :]:
            if not following.strip():
                continue
            if len(following) - len(following.lstrip()) <= base_indent:
                break
            name, sep, value = following.strip().partition(":")
            if sep and name.strip():
                fields[name.strip()] = value.strip().strip("'\"")
        return fields
    return None


def page_description(path: Path) -> str | None:
    content = read_text(path)
    if content is None or not content.startswith("---"):
        return None
    end_match = re.search(r"\n---\s*(?:\n|$)", content[3:])
    if not end_match:
        return None
    frontmatter_text = content[3 : 3 + end_match.start() + 1]
    match = DESCRIPTION_RE.search(frontmatter_text)
    if not match:
        return None
    raw = match.group(1).strip().strip("'\"")
    return raw or None


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


def validate_concept(frontmatter_text: str, strict: bool) -> list[str]:
    problems: list[str] = []
    type_value, strict_error = parse_type_strict(frontmatter_text)
    if strict_error:
        return [strict_error]
    if not type_value or not type_value.strip():
        return ["missing or empty `type:` in frontmatter"]
    if not strict:
        return problems

    for key in STRICT_FIELDS:
        if not field_value(frontmatter_text, key):
            problems.append(f"strict: missing or empty `{key}:`")

    generated = mapping_fields(frontmatter_text, "generated")
    if generated is None:
        if field_value(frontmatter_text, "timestamp"):
            problems.append(
                "strict: missing `generated:` (legacy `timestamp:` found, migrate to "
                "`generated: { by, at }`)"
            )
        else:
            problems.append("strict: missing `generated:` mapping")
    else:
        for key in ("by", "at"):
            if not generated.get(key):
                problems.append(f"strict: `generated.{key}` is missing or empty")
        at = generated.get("at")
        if at and not ISO_DATETIME_RE.match(at):
            problems.append(f"strict: `generated.at` is not an ISO 8601 datetime with UTC offset: {at}")

    status = field_value(frontmatter_text, "status")
    if status and status not in STATUS_VALUES:
        problems.append(
            f"strict: `status` value '{status}' is not one of {', '.join(STATUS_VALUES)}"
        )
    return problems


def validate_root_index(content: str, strict: bool) -> list[str]:
    problems: list[str] = []
    if not content.startswith("---"):
        if strict:
            problems.append("strict: root index.md must declare `okf_version`")
        return problems

    frontmatter_text = extract_frontmatter(content)
    if frontmatter_text is None or frontmatter_text == "":
        return ["unclosed frontmatter in index.md"]

    keys = [
        line.split(":", 1)[0].strip()
        for line in frontmatter_text.splitlines()
        if ":" in line and not line.strip().startswith("#")
    ]
    extra = [key for key in keys if key != "okf_version"]
    if extra:
        problems.append(
            f"index.md frontmatter may only declare `okf_version` (found: {', '.join(extra)})"
        )
    if strict and not field_value(frontmatter_text, "okf_version"):
        problems.append("strict: root index.md must declare `okf_version`")
    return problems


def validate_sub_index(content: str) -> list[str]:
    if content.startswith("---"):
        return ["index.md must not carry frontmatter (OKF index rules)"]
    return []


def validate_log(content: str) -> list[str]:
    problems: list[str] = []
    previous: str | None = None
    for line in content.splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        heading = match.group(2).strip()
        if not ISO_DATE_RE.match(heading):
            problems.append(f"log.md heading '{heading}' is not an ISO 8601 YYYY-MM-DD date")
            continue
        if previous is not None and heading > previous:
            problems.append(f"log.md entries are not newest first: {heading} follows {previous}")
        previous = heading
    return problems


def run_okf(docs_dir: Path, strict: bool) -> tuple[list[str], str]:
    issues: list[str] = []
    checked = 0

    for md_file in sorted(docs_dir.rglob("*.md")):
        checked += 1
        content = read_text(md_file)
        if content is None:
            issues.append(f"{md_file}: cannot read")
            continue

        if md_file.name == "index.md":
            if md_file.parent == docs_dir:
                problems = validate_root_index(content, strict)
            else:
                problems = validate_sub_index(content)
            issues.extend(f"{md_file}: {problem}" for problem in problems)
            continue

        if md_file.name == "log.md":
            issues.extend(f"{md_file}: {problem}" for problem in validate_log(content))
            continue

        frontmatter_text = extract_frontmatter(content)
        if frontmatter_text is None:
            issues.append(f"{md_file}: missing frontmatter (file must start with '---')")
            continue
        if frontmatter_text == "":
            issues.append(f"{md_file}: unclosed frontmatter (no closing '---' on its own line)")
            continue
        issues.extend(
            f"{md_file}: {problem}" for problem in validate_concept(frontmatter_text, strict)
        )

    return issues, f"{checked} file(s) checked"


def run_index(docs_dir: Path) -> tuple[list[str], str]:
    index_files = sorted(f for f in docs_dir.rglob("*.md") if f.name == "index.md")
    concept_pages = sorted(f for f in docs_dir.rglob("*.md") if f.name not in RESERVED)
    root_index = docs_dir / "index.md"

    if not index_files:
        return [f"no index.md found under {docs_dir}"], "0 index file(s)"

    linked: set[Path] = set()
    uncovered: list[str] = []
    orphans: list[str] = []
    description_issues: list[str] = []
    entries = 0

    for index_file in index_files:
        text = read_text(index_file)
        if text is None:
            issues = [f"UNREADABLE {index_file}: cannot read"]
            continue
        in_code = False
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if FENCE_RE.match(stripped):
                in_code = not in_code
                continue
            if in_code:
                continue
            match = ENTRY_RE.match(line)
            if not match:
                continue
            entries += 1
            target = parse_link_target(match.group(1))
            if not target or target.startswith("#") or EXTERNAL_SCHEME_RE.match(target):
                continue
            path_target = target.split("#", 1)[0].split("?", 1)[0]
            if not path_target or not path_target.endswith(".md"):
                continue
            resolved = resolve_local_target(docs_dir, index_file, path_target).resolve()
            linked.add(resolved)
            if resolved.name == "index.md" or not resolved.is_file():
                continue
            remainder = match.group(2).strip()
            if not remainder.startswith("- "):
                description_issues.append(
                    f"MISSING    {index_file}:{line_no} entry has no ' - description' after the link"
                )
                continue
            expected = page_description(resolved)
            if expected is None:
                continue
            actual = remainder[2:].strip()
            if actual != expected:
                description_issues.append(
                    f"MISMATCH   {index_file}:{line_no} description does not match {resolved}\n"
                    f"             index: {actual}\n"
                    f"             page:  {expected}"
                )

    root_resolved = root_index.resolve() if root_index.is_file() else None
    for page in concept_pages:
        if page.resolve() not in linked:
            uncovered.append(f"UNCOVERED  {page} is not listed in any index.md")
    for index_file in index_files:
        resolved = index_file.resolve()
        if resolved == root_resolved:
            continue
        if resolved not in linked:
            orphans.append(f"ORPHAN     {index_file} is not linked from any index.md")

    issues = uncovered + orphans + description_issues
    summary = (
        f"{len(concept_pages)} page(s), {len(index_files)} index file(s), {entries} entries"
    )
    return issues, summary


def run_links(docs_dir: Path) -> tuple[list[str], str]:
    checked_files = 0
    checked_links = 0
    broken: list[str] = []
    style_violations: list[str] = []

    for md_file in sorted(docs_dir.rglob("*.md")):
        checked_files += 1
        text = read_text(md_file)
        if text is None:
            broken.append(f"UNREADABLE {md_file}: cannot read")
            continue
        in_code = False
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if FENCE_RE.match(stripped):
                in_code = not in_code
                continue
            if in_code:
                continue
            for match in LINK_RE.finditer(line):
                checked_links += 1
                target = parse_link_target(match.group(1))
                if not target or target.startswith("#") or EXTERNAL_SCHEME_RE.match(target):
                    continue
                path_target = target.split("#", 1)[0].split("?", 1)[0]
                if not path_target:
                    continue
                if path_target.endswith(".md") and not path_target.startswith("/docs/"):
                    style_violations.append(
                        f"STYLE   {md_file}:{line_no} -> {target} (link is not root-absolute (/docs/...))"
                    )
                if not path_target.endswith(".md"):
                    continue
                if resolve_local_target(docs_dir, md_file, path_target).exists():
                    continue
                broken.append(
                    f"BROKEN  {md_file}:{line_no} -> {target} (target markdown file not found)"
                )

    issues = broken + style_violations
    summary = f"{checked_files} file(s), {checked_links} link(s)"
    return issues, summary


def parse_args(argv: list[str]) -> tuple[Path, bool, list[str]] | None:
    docs_dir = Path("docs")
    lenient = False
    selected: list[str] = list(VALID_SECTIONS)

    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--lenient":
            lenient = True
        elif arg == "--only":
            index += 1
            if index >= len(argv):
                print("--only requires a value", file=sys.stderr)
                return None
            names = [name.strip() for name in argv[index].split(",") if name.strip()]
            invalid = [name for name in names if name not in VALID_SECTIONS]
            if not names or invalid:
                print(
                    f"invalid --only value: {', '.join(invalid) or argv[index]} "
                    f"(valid: {', '.join(VALID_SECTIONS)})",
                    file=sys.stderr,
                )
                return None
            selected = names
        elif arg.startswith("--"):
            print(f"unknown option: {arg}", file=sys.stderr)
            return None
        else:
            docs_dir = Path(arg)
        index += 1

    return docs_dir, lenient, selected


def main() -> int:
    parsed = parse_args(sys.argv[1:])
    if parsed is None:
        return 2
    docs_dir, lenient, selected = parsed

    if not docs_dir.is_dir():
        print(f"docs directory '{docs_dir}' not found", file=sys.stderr)
        return 2

    strict = not lenient
    runners = {
        "okf": lambda: run_okf(docs_dir, strict),
        "index": lambda: run_index(docs_dir),
        "links": lambda: run_links(docs_dir),
    }

    results = {name: runners[name]() for name in selected}

    counts: dict[str, int] = {}
    for name, (issues, summary) in results.items():
        counts[name] = len(issues)
        print(f"== {name.upper()} == ({summary})")
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  clean")
        print()

    total = sum(counts.values())
    breakdown = ", ".join(f"{counts[name]} {name}" for name in selected)
    print(f"Summary: {total} issue(s) ({breakdown}).")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
