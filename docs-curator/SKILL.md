---
name: docs-curator
description: Keep /docs/ accurate during development. Use after code changes affect endpoints, migrations, integrations, jobs, listeners, commands, schedules, deployment, environment setup, architecture, patterns, or implementation plans. Use when the user asks to "update docs", "sync documentation", or "check docs integrity". Use when planning a new feature.
license: MIT
metadata:
  author: https://github.com/darioruellan
  version: "0.2.2"
  domain: frontend/backend
  triggers: docs, document, documentation, update docs, synchronize docs, plan, implement
  role: specialist
  scope: documentation
---
# docs-curator - Keep Documentation Current

## Overview

This skill helps keep `/docs/` aligned with shipped behavior by comparing the change scope to the existing documentation, inventorying the relevant code surface, and proposing updates for review before anything is changed.

The skill is **scope-aware** (full audit vs current-branch diff vs single concept) and **source-anchored** (every claim cites a file path and symbol).

**When NOT to use:**

- Creating new docs that are not derived from existing code (use a writing skill).
- Fixing typos or prose polish in docs unrelated to a code change.

## Documentation Folders

| Folder | Purpose | Scope |
|---|---|---|
| `/docs/00-core/` | Foundational concepts, constraints, architecture, and shared conventions | Included |
| `/docs/10-integrations/` | External integrations, services, and connectors | Included |
| `/docs/20-features/` | Feature-specific behavior, usage, and capabilities | Included |
| `/docs/25-patterns/` | Reusable guidance and playbooks that apply across multiple features | Included |
| `/docs/30-operations/` | Operational procedures, runbooks, deployment details, and maintenance guidance | Included |
| `/docs/40-plans/` | Implementation plans; **deleted on ship** (see `references/okf-conventions.md`) | Included |
| `/docs/99-lessons/` | Retrospective lessons and postmortems; only when the user explicitly mentions lessons, postmortem, or retrospective in their request | Excluded by default |
| `/docs/index.md` | Main navigation hub for the docs set | Included |
| `/docs/log.md` | Reserved log file for document history or change tracking when needed | — |

## Scope

**Included:**

- Updating files under `/docs/00-core/`, `/docs/10-integrations/`, `/docs/20-features/`, `/docs/25-patterns/`, and `/docs/30-operations/`.
- Maintaining `/docs/index.md` navigation.
- Keeping `/docs/40-plans/` plans aligned with the code as it evolves during implementation. Plans are **delete-on-ship**: when a feature ships, the plan file is removed and any relevant behavior is documented under the appropriate feature or integration page (see `references/okf-conventions.md`).
- Enforcing OKF v0.1 conformance across `/docs/` (parseable frontmatter, `type:` in every concept, controlled type vocabulary).
- Syncing `.env.example` with new environment variables.
- Keeping `/docs/30-operations/` test procedure pages (e.g. `testing.md`, `type: Test Procedure`) aligned with the test surface: framework, run commands, available-test inventory.
- Source code comments and docstrings (preferred over hand-editing generated reference pages).

**Excluded:**

- Creating new documentation files outside `/docs/`.
- Updating `README.md` prose (only the docs section link).
- Writing `/docs/99-lessons/` entries without an explicit trigger.
- Reference pages under `/docs/ref/*` if they are generated from source; update the source docstring instead.

## Inputs

- Changed source files (controllers, models, services, jobs, listeners, commands, config, migrations, routes, plan files).
- Git diff of the current change.
- Existing doc tree under `/docs/` and the navigation file `/docs/index.md`.

## Operating Modes

Choose the right mode for the change size. The mode is determined by the user's intent and the working branch.

| Mode | When | What to inventory |
|---|---|---|
| **full** | On `main`, or when asked for a comprehensive audit | The full public surface: exports, settings, env vars, CLI commands, default values, behaviors |
| **diff** | On a feature branch, before review | Only changes vs the base branch: additions, modifications, removals |
| **concept** | User names a single feature or symbol | One concept's docs and any cross-referenced pages |

Default to `diff` on a feature branch and `full` on `main`. Never switch branches to gain access to a different mode; use `git show main:<path>`, `git worktree add`, or read files from the base ref directly.

## Step-by-Step Execution

1. **Confirm mode and base branch.**
   - Identify the current branch and the default branch (usually `main`).
   - On a non-default branch, prefer `diff` mode against the default branch.
   - Avoid `git checkout` if it would disrupt local changes.

2. **Build a feature inventory from the selected scope.**
   - In `full` mode: walk the codebase for public exports, configuration types, env vars, CLI commands, default values, and documented behaviors.
   - In `diff` mode: constrain to the diff using `git diff main...HEAD` (or equivalent).
   - In `concept` mode: read the named source plus its tests and references.
   - Use targeted searches: `grep "Settings"`, `grep "Config"`, `grep "os.environ"`, `grep "<PROJECT_PREFIX>_"` (or project-specific pattern for env vars).
      - In `full` mode, also walk the test surface: test runner command, suites, listing commands (`--list-tests`, `--collect-only`, `--listTests`), and CI test jobs.
      - Record the source for each item: `file path` + `symbol/setting` + behavior notes.

3. **Classify the diff into trigger categories.**
   - In `diff` mode this step is mandatory: run `python scripts/classify-diff.py` (or the project's equivalent) to map changed files into the categories in `references/trigger-matrix.md`, then inspect every matching row.
   - In `full` mode, the matrix is a routing guide only.
   - If referenced scripts or reference files do not exist in the project, skip that step and note the missing dependency in the Final Report under Verification.
   - This shrinks the doc tree to the sections that actually need attention.
   - For changes to `/docs/` itself, also run `python scripts/check-okf.py` to catch frontmatter or `type:` regressions in the same pass.

4. **Doc-first pass: review existing pages.**
   - Walk each relevant page under `/docs/`.
   - Use `references/templates.md` as the parsing template: check each page against its `type:`'s expected sections (Overview, core sections, Options/params, Examples, Source, Cross-links, Status).
   - Identify missing mentions of important supported options: opt-in flags, env vars, customization points, new features from `src/` and `examples/`.
   - Propose additions where users would reasonably expect to find them on that page.

   Documentation routing rule:
   - Put **cross-cutting reusable guidance** in `/docs/25-patterns/` (for example: composition rules, interaction behaviors, validation/check flows, accessibility patterns, naming conventions, or integration playbooks that apply in multiple places).
   - Keep `/docs/20-features/` for **feature-specific behavior** tied to concrete components, modules, pages, commands, or services.
   - Keep `/docs/00-core/` for **foundational primitives and constraints** (tokens, global architecture, base conventions, shared constraints).
      - Put **test procedures** (how to run the suite, how to list available tests, suite inventory) in `/docs/30-operations/` with `type: Test Procedure` (see `references/okf-conventions.md`).

5. **Code-first pass: map features to docs.**
   - Review the docs information architecture in `/docs/index.md`.
   - For each feature in the inventory, determine the best existing page or section. Use `references/trigger-matrix.md` as a starting point.
   - Identify features with no doc page, or pages with no corresponding content.
   - For new concept types not in the controlled vocabulary, propose the type and add it to `references/okf-conventions.md` in the same pass.
   - For reference pages under `/docs/ref/*`, treat the source docstring as the source of truth; **prefer updating the source comment** so regenerated reference pages stay correct, instead of hand-editing the generated output.
   - Classify candidate docs as one of: **foundation** (`00-core`), **feature** (`20-features`), or **pattern** (`25-patterns`) before proposing edits.

6. **Detect gaps and inaccuracies.**
   - **Missing**: features/configs present in code but absent in docs.
   - **Incorrect / outdated**: names, defaults, or behaviors that diverge from code.
   - **Structural** (optional): pages overloaded, missing overviews, or mis-grouped topics.
   - **OKF** (when full bundle is adopted): concept has no `type:`, wrong `type:` for its directory, or missing from its subdirectory `index.md`.
   - If the same guidance appears in 2+ pages, run the Pattern Extraction pass in `references/passes.md`.

7. **Apply the proposed changes**
   - Keep edits scoped to the existing tone, format, and information architecture.
   - For new concept pages, use the per-type section template in `references/templates.md` matching the page's `type:`. Sections are conventional, not required; omit sections the concept does not warrant.
   - Update `/docs/index.md` when adding or renaming pages.
   - Every new or edited concept file MUST have a `type:` in its frontmatter from the controlled vocabulary in `references/okf-conventions.md`.
   - When a plan in `/docs/40-plans/` ships, follow this ordered procedure:
     1. **Delete the plan file** from `/docs/40-plans/`.
     2. **Remove the plan entry** from `/docs/40-plans/index.md` (if present).
     3. **Remove the plan entry** from `/docs/index.md`.
     4. **Grep for stale cross-references**: search for the deleted plan's path across `/docs/` and update any cross-references in feature or integration docs to point at the shipped feature doc instead.
   - Run the project's docs build (e.g. `make build-docs`) after edits to verify the docs site still builds.
   - If env vars changed, update `.env.example` in the same pass.
   - After every change has landed, emit the **Final Report** (see next section) summarizing what was changed and the source that supports it. 

## Final Report

After all edits land, emit a Final Report describing what changed in the documentation. Use this template verbatim:

```
Docs Sync Final Report

Mode: <full | diff | concept>
Base branch: <main | other>
Scope: <path list or "single: <symbol>">

Doc-first findings
- <Page path> + <missing content> -> <source: file:symbol> + <suggested insertion point>

Code-first gaps
- <Feature> + <source: file:symbol> -> <suggested doc page/section> (or "no page exists")

Incorrect or outdated docs
- <Doc file> + <issue> + <correct info> + <source: file:symbol>

Structural suggestions (optional)
- <Proposed change> + <rationale> (if any)

Files changed
- <Doc file> -> <concise change summary>

Env / config changes
- <var name> + <where it shows up> + <action: add to .env.example | update docs>

Verification
- <which checks ran: scripts/check-okf.py, scripts/check-links.py, make build-docs, etc.>
```

If the sync found no issues to fix, emit a short "No documentation changes were required for this scope." line in place of the template.

## Verification

Before declaring the sync complete, confirm:

- [ ] Every change is backed by a `file:symbol` source.
- [ ] Documentation content edits are inside `docs/**`.
- [ ] A Final Report was emitted summarizing files changed, new frontmatter/index entries, env changes, sources, and verification runs.
- [ ] Allowed companion edits outside `docs/**` were applied only when triggered (`.env.example` and `README.md` docs section).
- [ ] `docs/index.md` is current (new pages added, renames reflected).
- [ ] If the change introduces reusable guidance, `/docs/25-patterns/index.md` and related pattern pages were reviewed or updated.
- [ ] `.env.example` matches the new env vars (if any).
- [ ] For reference pages, source docstrings were updated, not the generated output.
- [ ] Every new or edited concept file has a `type:` in frontmatter from the controlled vocabulary.
- [ ] `scripts/check-okf.py` reports zero OKF conformance violations.
- [ ] Docs build command passes (e.g. `make build-docs`).
- [ ] `scripts/check-links.py` reports no broken internal links.
- [ ] Shipped plans in `/docs/40-plans/` were deleted, removed from index files (if present), and no stale cross-references remain (verified with `grep "path/to/deleted/plan"`).

## Safety / DONTs

- Do not edit without a `file:symbol` source backing the change.
- Do not add speculative architecture notes not backed by code.
- Do not remove historical notes from `/docs/99-lessons/` unless explicitly requested.
- Do not create new pages when an existing page already covers the topic.
- Do not create concept files without a `type:` in frontmatter from the controlled vocabulary.
- Do not keep shipped plans around for reference; delete them (see `references/okf-conventions.md`).
- Do not drop or reformat YAML frontmatter when editing a concept file. Preserve existing `type:`, `title:`, `description:`, `tags:`, and `timestamp:` fields.

## Gotchas

- Commands shown in this skill (`grep`, `python scripts/...`, `git`, `make`) are examples. Use the environment's equivalent tool when a binary is unavailable; the steps matter, not the exact invocation.
- Relative links in docs break when pages are moved; always use root-absolute paths (`/docs/...`).
- The trigger matrix in `references/trigger-matrix.md` is a guide, not exhaustive; use judgment when a change spans multiple domains.

## References

- `references/trigger-matrix.md` - File-classification table for diff impact.
- `references/doc-coverage-checklist.md` - Page-by-page audit checklist (includes OKF pass).
- `references/okf-conventions.md` - OKF v0.1 conformance, type vocabulary, plan lifecycle.
- `references/templates.md` - Per-type section templates and parsing template for the doc-first pass.
- `references/passes.md` - Pattern Extraction pass, Anti-Rationalization, and Red Flags.
- `scripts/classify-diff.py` - Classifies a `git diff` into trigger categories.
- `scripts/check-okf.py` - Validates strict YAML frontmatter and `type:` for `/docs/`.
- `scripts/check-links.py` - Checks internal markdown links and enforces root-absolute paths.
