# Document Curator Skill

> This skill is experimental and a WIP. I appreciate any feedback.

![Version](https://img.shields.io/badge/version-0.1.2-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Help keep your `/docs/` accurate during development.

## The Problem

Documentation drift is the most common silent failure in agentic coding workflows: code moves, docs stay. This skill keeps your docs aligned with shipped behavior so nothing falls through the cracks.

## How It Works

- **Scope-aware** - works in three modes depending on what you need:
  - `full` - comprehensive audit of the full public surface
  - `diff` - only changes compared to the base branch
  - `concept` - a single feature or symbol you name
- **Evidence-driven** - every finding cites file and symbol evidence, so you can verify it.

## Documentation Standards (OKF)

This skill enforces **OKF v0.1** (Open Knowledge Format) conformance across your `/docs/` bundle. OKF is an [open specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) by Google Cloud for representing knowledge as interconnected Markdown files with structured YAML frontmatter — making your docs both human-readable and machine-parseable.

### Why OKF matters

Without structure, docs become a flat pile of Markdown. OKF gives every page a **type** (is this an API reference, a runbook, a feature doc, or a plan?), a **directory home**, and predictable frontmatter so tools (and agents) can navigate, filter, and validate the knowledge bundle without guessing.

See [`references/okf-conventions.md`](docs-curator/references/okf-conventions.md) for the full type vocabulary and project-specific rules, and [`references/trigger-matrix.md`](docs-curator/references/trigger-matrix.md) for the file-to-doc routing table.

## Documentation Folders It Maintains

When the skill updates or creates documentation, it uses a predictable folder structure under your project's `/docs/` tree:

- `/docs/00-core/` - foundational concepts, constraints, architecture, and shared conventions.
- `/docs/10-integrations/` - documentation for external integrations, services, and connectors.
- `/docs/20-features/` - feature-specific behavior, usage, and capabilities.
- `/docs/25-patterns/` - reusable guidance and playbooks that apply across multiple features.
- `/docs/30-operations/` - operational procedures, runbooks, deployment details, and maintenance guidance.
- `/docs/40-plans/` - implementation plans; these are typically removed once the work ships.
- `/docs/99-lessons/` - retrospective lessons and postmortems when explicitly requested.
- `/docs/index.md` - the main navigation hub for the docs set.
- `/docs/log.md` - reserved log file for document history or change tracking when needed.

The skill will create or update pages in the most appropriate folder rather than scattering content arbitrarily.

## Project Structure

```
skills/
├── SKILL.md                          # Agent instructions (the brain)
├── scripts/
│   ├── classify-diff.py              # Maps git diffs to trigger categories
│   ├── check-okf.py                  # Validates OKF v0.1 frontmatter
│   └── check-links.py                # Finds broken internal links
└── references/
    ├── trigger-matrix.md             # Which file changes need which docs
    ├── okf-conventions.md            # Frontmatter rules and type vocabulary
    └── doc-coverage-checklist.md     # Page-by-page audit checklist
```

## Scripts

| Script | What it does |
|---|---|
| `classify-diff.py [BASE_REF]` | Classifies a `git diff` into trigger-matrix categories, including rename-safe parsing |
| `check-okf.py [DOCS_DIR]` | Validates strict YAML frontmatter and required `type:` fields |
| `check-links.py [DOCS_DIR]` | Checks markdown links, missing local targets, and enforces root-absolute link style |

Scripts are Python 3 and cross-platform; `check-okf.py` requires `PyYAML` for strict YAML parsing.

## License

MIT
