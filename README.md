# Document curator skill

> This skill is experimental and a WIP. I appreciate any feedback.

![Version](https://img.shields.io/github/v/release/druellan/docs-curator-skill?label=version)
![License](https://img.shields.io/badge/license-MIT-green)

Help keep your `/docs/` accurate during development.

## The problem

Documentation drift is the most common silent failure in agentic coding workflows: code moves, docs stay. This skill keeps your docs aligned with shipped behavior so nothing falls through the cracks.

## How it works

- **Scope-aware** - works in three modes depending on what you need:
  - `full` - comprehensive audit of the full public surface
  - `diff` - only changes compared to the base branch
  - `concept` - a single feature or symbol you name
- **Evidence-driven** - every finding cites file and symbol evidence, so you can verify it.

## Documentation standards (OKF)

This skill enforces **OKF v0.2** (Open Knowledge Format) conformance across your `/docs/` bundle. OKF is an [open specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) by Google Cloud for representing knowledge as interconnected Markdown files with structured YAML frontmatter. This makes your docs both human-readable and machine-parseable. Version 0.2 records provenance (`sources`), trust (`generated`, `verified`), and lifecycle (`status`, `stale_after`) in frontmatter, so consumers can tell where a page came from and whether it is still current.

### Why OKF matters

Without structure, docs become a flat pile of Markdown. OKF gives every page a **type** (is this an API reference, a runbook, a feature doc, or a plan?), a **directory home**, and predictable frontmatter so tools (and agents) can navigate, filter, and validate the knowledge bundle without guessing.

See [`references/okf-conventions.md`](docs-curator/references/okf-conventions.md) for the full type vocabulary and project-specific rules, [`references/trigger-matrix.md`](docs-curator/references/trigger-matrix.md) for the file-to-doc routing table, and [`references/templates.md`](docs-curator/references/templates.md) for per-type section templates. Test procedures ("which tests exist and how to run them") live as `type: Test Procedure` pages under `/docs/30-operations/`.

## Documentation folders it maintains

When the skill updates or creates documentation, it uses a predictable folder structure under your project's `/docs/` tree:

- `/docs/00-core/`: foundational concepts, constraints, architecture, and shared conventions.
- `/docs/10-integrations/`: documentation for external integrations, services, and connectors.
- `/docs/20-features/`: feature-specific behavior, usage, and capabilities.
- `/docs/25-patterns/`: reusable guidance and playbooks that apply across multiple features.
- `/docs/30-operations/`: operational procedures, runbooks, deployment details, and maintenance guidance.
- `/docs/40-plans/`: implementation plans; these are typically removed once the work ships.
- `/docs/99-lessons/`: retrospective lessons and postmortems when explicitly requested.
- `/docs/index.md`: the sectioned catalog of every page with its `description` and the bundle `okf_version` (OKF §8).
- `/docs/log.md`: chronological update log when the bundle keeps one, newest first (OKF §9).

The skill creates or updates pages in the most appropriate folder rather than scattering content arbitrarily.

## Project structure

```
skills/
├── SKILL.md                          # Agent instructions (the brain)
├── scripts/
│   ├── classify-diff.py              # Maps git diffs to trigger categories
│   └── check-integrity.py            # Checks OKF conformance, index coverage, and links
└── references/
    ├── trigger-matrix.md             # Which file changes need which docs
    ├── okf-conventions.md            # Frontmatter rules and type vocabulary
    ├── doc-coverage-checklist.md     # Page-by-page audit checklist
    ├── templates.md                  # Per-type section templates and parsing template
    ├── passes.md                     # Pattern extraction pass and quality guardrails
    └── technical-writing.md          # Universal writing guidelines
```

## Scripts

| Script | What it does |
|---|---|
| `classify-diff.py [BASE_REF]` | Classifies a `git diff` into trigger-matrix categories (endpoints, models, tests, deployments, docs, ...), including rename-safe parsing |
| `check-integrity.py [DOCS_DIR] [--lenient] [--only okf,index,links]` | Validates OKF v0.2 conformance, index coverage and description sync, and markdown links. Strict project-field checks are on by default; `--lenient` drops them and `--only` scopes the run |

Scripts are Python 3, cross-platform, and dependency-free (stdlib only).

## License

MIT
