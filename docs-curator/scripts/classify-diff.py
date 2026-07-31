#!/usr/bin/env python3
"""Classify a git diff into trigger-matrix categories.

Usage: classify-diff.py [BASE_REF]
    BASE_REF defaults to main.
Prints a count per category and a per-file list. Exits 0 on success, 1 on no diff.
"""
import subprocess
import sys
from collections import OrderedDict
from pathlib import PurePosixPath

ORDER = [
        "endpoint",
        "model",
        "integration",
        "event-or-job",
        "command-or-schedule",
        "deployment",
        "setup",
        "plan",
        "nav",
        "generated-ref",
        "docs",
        "other",
]


def parse_base_ref() -> str:
    return sys.argv[1] if len(sys.argv) > 1 else "main"


def git_rev_parse(ref: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref],
        capture_output=True,
    )
    return result.returncode == 0


def classify(path: str) -> str:
    p = PurePosixPath(path)
    parts = p.parts

    if any(seg in parts for seg in ("routes", "controllers", "api", "endpoints")):
        return "endpoint"
    if any(seg in parts for seg in ("migrations", "models", "schema", "factories")):
        return "model"
    if "integrations" in parts:
        return "integration"
    if any(seg in parts for seg in ("events", "listeners", "jobs", "queues", "subscribers")):
        return "event-or-job"
    if any(seg in parts for seg in ("console", "commands", "scheduler")):
        return "command-or-schedule"
    if "Kernel" in p.name or "Kernel." in path:
        return "command-or-schedule"

    if any(seg in parts for seg in ("deploy", "k8s", "terraform")):
        return "deployment"
    if p.name.startswith("Dockerfile") or "docker-compose" in path:
        return "deployment"
    if ".github/workflows" in path:
        return "deployment"

    if "plan" in parts or "docs/40-plans" in path:
        return "plan"
    if p.name.startswith(".env") or any(seg in parts for seg in ("config", "settings")):
        return "setup"
    if p.name == "index.md" and "docs" in parts:
        return "nav"
    if p.match("mkdocs.yml") or p.match("nav.*") or p.match("sidebar.*"):
        return "nav"
    if p.parts[:2] == ("docs", "ref"):
        return "generated-ref"
    if "docs" in parts:
        return "docs"
    return "other"


def run_diff(base: str) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "diff", "--name-status", "-z", "--find-renames", f"{base}...HEAD"],
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return result
    return subprocess.run(
        ["git", "diff", "--name-status", "-z", "--find-renames", base, "HEAD"],
        capture_output=True,
        check=False,
    )


def parse_name_status_z(raw: bytes) -> list[dict[str, str | None]]:
    entries: list[dict[str, str | None]] = []
    parts = raw.decode("utf-8", errors="replace").split("\0")
    i = 0
    while i < len(parts):
        status = parts[i]
        i += 1
        if not status:
            continue
        code = status[0]
        if code in ("R", "C"):
            if i + 1 >= len(parts):
                break
            old_path = parts[i]
            new_path = parts[i + 1]
            i += 2
            entries.append(
                {
                    "status": status,
                    "path": new_path,
                    "old_path": old_path,
                    "new_path": new_path,
                }
            )
            continue

        if i >= len(parts):
            break
        path = parts[i]
        i += 1
        entries.append(
            {
                "status": status,
                "path": path,
                "old_path": None,
                "new_path": None,
            }
        )
    return entries


def main() -> int:
    base = parse_base_ref()

    if not git_rev_parse("--git-dir"):
        print("not a git repository", file=sys.stderr)
        return 2
    if not git_rev_parse(base):
        print(f"base ref '{base}' not found", file=sys.stderr)
        return 2

    try:
        diff_result = run_diff(base)
    except FileNotFoundError:
        print("git not found on PATH", file=sys.stderr)
        return 2

    records = parse_name_status_z(diff_result.stdout)
    if not records:
        print(f"no changes between {base} and HEAD")
        return 1


    buckets: dict[str, list[str]] = OrderedDict((cat, []) for cat in ORDER)
    classified_records: list[dict[str, str | None]] = []

    for record in records:
        path = record["path"]
        if not path:
            continue
        bucket = classify(path)
        buckets[bucket].append(path)
        classified = dict(record)
        classified["category"] = bucket
        classified_records.append(classified)

    buckets = OrderedDict((k, v) for k, v in buckets.items() if v)

    print(f"Diff classification ({base}...HEAD):\n")
    for cat in ORDER:
        files = buckets.get(cat)
        if not files:
            continue
        print(f"{cat:<22} {len(files):3d} file(s)")
        for path in files:
            print(f"  - {path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
