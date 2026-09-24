---
name: docs-curator
description: Keep /docs/ accurate during development. Use after code changes affect endpoints, migrations, integrations, jobs, listeners, commands, schedules, deployment, environment setup, architecture, patterns, or implementation plans. Use when the user asks to "update docs", "sync documentation", or "check docs integrity". Use when planning a new feature.
license: MIT
metadata:
  author: https://github.com/darioruellan
  domain: frontend/backend
  triggers: docs, document, documentation, update docs, synchronize docs, plan, implement
  role: specialist
  scope: documentation
---
# docs-curator: keep documentation current

Inspect the relevant code and documentation, make source-backed updates within scope, run the applicable checks, and report what changed. If the evidence is insufficient or sources conflict, report the uncertainty rather than guessing. Do not wait for approval before making supported edits.

Use this skill to sync `/docs/` with code changes or audit existing code-backed documentation. Do not use it to write docs that are not derived from existing code or to polish unrelated prose.

## Decide the scope

| Mode | When | Inventory |
|---|---|---|
| **full** | On the default branch, or for a comprehensive audit | The full public surface, configuration, behavior, and test procedures |
| **diff** | On a feature branch, before review | Changes against the base branch, including uncommitted work |
| **concept** | The user names a feature or symbol | Its source, tests, docs, and cross-references |

Prefer the user's requested scope over the branch default. Never switch branches to select a mode or disrupt local changes.

## Work in order

1. Establish the mode and scope; load `references/workflow.md` for the detailed procedure. In diff mode, load `references/trigger-matrix.md` and classify the changes. In concept mode, stay focused on the named concept and its dependencies.
2. Inspect code and existing docs from both directions. Record a `file:symbol` source for each behavior or configuration change; do not invent architecture or resolve conflicting evidence by guessing.
3. Route changes to existing pages when possible. Load `references/okf-conventions.md` for frontmatter, indexes, links, and plan lifecycle; load `references/templates.md` when creating or restructuring a concept page. Use `references/technical-writing.md` for writing or substantive prose edits. Load `references/passes.md` only when its conditional trigger fires.
4. Apply supported edits without an approval gate. Keep `/docs/99-lessons/` creation and edits behind an explicit user request. Keep generated reference pages in sync by editing their source docstrings instead of their generated output.
5. Run the applicable integrity and project checks, then report files changed, supporting sources, checks run, and any unresolved uncertainty. If no changes are needed, say so.

## Editing boundary

Update documentation under `/docs/` and its catalog. Companion changes may include `.env.example` for changed env vars, the `README.md` docs-section link, and source comments or docstrings. Do not rewrite unrelated README prose, create unrelated documentation outside `/docs/`, or remove historical lessons without an explicit request. Plans under `/docs/40-plans/` are delete-on-ship; preserve shipped behavior in the appropriate docs and clear stale links. Follow `references/workflow.md` for the ordered procedure.

## References and tools

- `references/workflow.md`: Mode-specific inventory, doc/code passes, editing, verification, and final report.
- `references/trigger-matrix.md`: Diff routing guide; a file may affect more than one doc category.
- `references/doc-coverage-checklist.md`: Scanning aid for documentation coverage and OKF checks.
- `references/okf-conventions.md`: OKF v0.2 fields, type vocabulary, indexes, links, and plan lifecycle.
- `references/templates.md`: Conventional per-type page sections and the doc-first parsing template.
- `references/technical-writing.md`: Writing guidelines.
- `references/passes.md`: Conditional pattern extraction and quality guardrails.
- `scripts/classify-diff.py`: Classifies committed changes against a base ref; inspect uncommitted changes separately.
- `scripts/check-integrity.py`: Checks frontmatter fields, index coverage, and local links. A clean run does not replace source review.

Resolve reference and script paths relative to the installed skill directory, not the target project's root.
