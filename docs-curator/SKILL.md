---
name: docs-curator
description: Keep /docs/ accurate during development. Use after code changes affect endpoints, migrations, integrations, jobs, listeners, commands, schedules, deployment, environment setup, architecture, patterns, or implementation plans. Use when the user asks to "update docs", "sync documentation", or "check docs integrity". Use when planning a new feature under `/docs/40-plans/` that will later be implemented.
license: MIT
metadata:
  author: https://github.com/darioruellan
  version: "0.1.1"
  domain: frontend/backend
  triggers: docs, document, documentation, update docs, synchronize docs, plan, implement
  role: specialist
  scope: documentation
---
# docs-curator - Keep Documentation Current

## Overview

This skill helps keep `/docs/` aligned with shipped behavior by comparing the change scope to the existing documentation, inventorying the relevant code surface, and proposing updates for review before anything is changed.

The skill is **scope-aware** (full audit vs current-branch diff vs single concept) and **evidence-driven** (every claim cites a file path and symbol).

**When NOT to use:**

- Creating new docs that are not derived from existing code (use a writing skill).
- Fixing typos or prose polish in docs unrelated to a code change.

## Scope

**Included:**

- Updating files under `/docs/00-core/`, `/docs/10-integrations/`, `/docs/20-features/`, `/docs/25-patterns/`, and `/docs/30-operations/`.
- Maintaining `/docs/index.md` navigation.
- Keeping implementation plans under `/docs/40-plans/` aligned with shipped behavior. Plans are **delete-on-ship**: when a feature ships, the plan file is removed (see `references/okf-conventions.md`).
- Enforcing OKF v0.1 conformance across `/docs/` (parseable frontmatter, `type:` in every concept, controlled type vocabulary).
- Syncing `.env.example` with new environment variables.
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
- Project's docs build command (e.g. `make build-docs`).

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
   - Use targeted searches: `rg "Settings"`, `rg "Config"`, `rg "os.environ"`, `rg "<PROJECT_PREFIX>_"` (or project-specific pattern for env vars).
   - Capture evidence for each item: `file path` + `symbol/setting` + behavior notes.

3. **Classify the diff into trigger categories** (optional but recommended on large changes).
   - Run `python scripts/classify-diff.py` (or the project's equivalent) to map changed files into the categories in `references/trigger-matrix.md`.
   - This shrinks the doc tree to the sections that actually need attention.
   - For changes to `/docs/` itself, also run `python scripts/check-okf.py` to catch frontmatter or `type:` regressions in the same pass.

4. **Doc-first pass: review existing pages.**
   - Walk each relevant page under `/docs/`.
   - Identify missing mentions of important supported options: opt-in flags, env vars, customization points, new features from `src/` and `examples/`.
   - Propose additions where users would reasonably expect to find them on that page.

   Documentation routing rule:
   - Put **cross-cutting reusable guidance** in `/docs/25-patterns/` (for example: composition rules, interaction behaviors, validation/check flows, accessibility patterns, naming conventions, or integration playbooks that apply in multiple places).
   - Keep `/docs/20-features/` for **feature-specific behavior** tied to concrete components, modules, pages, commands, or services.
   - Keep `/docs/00-core/` for **foundational primitives and constraints** (tokens, global architecture, base conventions, shared constraints).

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

7. **Apply the proposed changes**
   - Keep edits scoped to the existing tone, format, and information architecture.
   - Update `/docs/index.md` when adding or renaming pages.
   - Every new or edited concept file MUST have a `type:` in its frontmatter from the controlled vocabulary in `references/okf-conventions.md`.
   - When a plan in `/docs/40-plans/` ships: **delete the plan file**, remove it from `/docs/40-plans/index.md` (if present) and `/docs/index.md`, then grep for its path across `/docs/` and update any cross-references in feature or integration docs to point at the shipped feature doc instead.
   - Run the project's docs build (e.g. `make build-docs`) after edits to verify the docs site still builds.
   - If env vars changed, update `.env.example` in the same pass.
   - After every change has landed, emit the **Final Report** (see next section) summarizing what was changed and what evidence supports it. 

## Pattern Extraction (when relevant)

When a change set includes guidance that appears in 2+ places, add this mini-pass after inventory and before proposing edits:

1. Identify repeated guidance in docs or code (behavioral flow, composition, validation, operational sequence, accessibility, integration sequence).
2. Propose moving that repeated guidance into `/docs/25-patterns/` as canonical reusable patterns.
3. Replace duplicated prose in feature/operations pages with concise links to the canonical pattern page.
4. Keep examples implementation-ready, but avoid page-specific copy in pattern pages.

## Final Report

After all edits land, emit a Final Report describing what changed in the documentation. Use this template verbatim:

```
Docs Sync Final Report

Mode: <full | diff | concept>
Base branch: <main | other>
Scope: <path list or "single: <symbol>">

Doc-first findings
- <Page path> + <missing content> -> <evidence: file:symbol> + <suggested insertion point>

Code-first gaps
- <Feature> + <evidence: file:symbol> -> <suggested doc page/section> (or "no page exists")

Incorrect or outdated docs
- <Doc file> + <issue> + <correct info> + <evidence: file:symbol>

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

## Anti-Rationalization

Common excuses agents use to skip steps. Rebut each one before editing.

| Rationalization | Reality |
|---|---|
| "The change is small, just edit the one page" | Small changes often miss cross-references, env examples, and `index.md` updates. Run the full pass. |
| "I'll remember the evidence, no need to cite file paths" | Future you and the user cannot verify a change without `file:symbol` evidence. Cite it every time. |
| "The diff is too big to inventory" | That is exactly when the inventory matters most. Use `scripts/classify-diff.py` to shrink the work. |
| "I'll just rewrite the page to be safe" | Rewrites are how style drift happens. Keep edits surgical; update the source comment, not the generated page. |
| "I'll just fix the docs as I go" | Each fix needs evidence and a matching entry in the inventory. Capture it before editing. |
| "Translated docs are just stale copies" | Out of scope. Translated docs have their own maintainers. Leave them alone. |
| "The doc is already correct enough" | "Correct enough" is the seed of every docs bug. Cite the code symbol, compare to the doc line, decide. |
| "I can't find the feature in docs, so it isn't documented" | Check the code, the index, and the plan. Then propose the page that should exist. |

## Red Flags

Stop and reconsider when any of these appear.

- A page mixes quick-start content with deep reference and has no clear boundary.
- The same concept is duplicated across multiple pages with no cross-link.
- A new feature area has no obvious home in the navigation.
- Reusable guidance is buried in feature or operations pages instead of `/docs/25-patterns/`.
- The proposed edit hand-edits a generated reference page instead of the source.
- The inventory lists features the diff adds but the docs already cover, while missing features the diff actually changed.
- `.env.example` is out of sync with the new env vars in the diff.

## Verification

Before declaring the sync complete, confirm:

- [ ] Every change is backed by `file:symbol` evidence.
- [ ] Documentation content edits are inside `docs/**`.
- [ ] A Final Report was emitted summarizing files changed, new frontmatter/index entries, env changes, evidence, and verification runs.
- [ ] Allowed companion edits outside `docs/**` were applied only when triggered (`.env.example` and `README.md` docs section).
- [ ] `docs/index.md` is current (new pages added, renames reflected).
- [ ] If the change introduces reusable guidance, `/docs/25-patterns/index.md` and related pattern pages were reviewed or updated.
- [ ] `.env.example` matches the new env vars (if any).
- [ ] For reference pages, source docstrings were updated, not the generated output.
- [ ] Every new or edited concept file has a `type:` in frontmatter from the controlled vocabulary.
- [ ] `scripts/check-okf.py` reports zero OKF conformance violations.
- [ ] Docs build command passes (e.g. `make build-docs`).
- [ ] `scripts/check-links.py` reports no broken internal links.
- [ ] Shipped plans in `/docs/40-plans/` were deleted, removed from index files (if present), and no stale cross-references remain (verified with `rg "path/to/deleted/plan"`).

## Safety / DONTs

- Do not edit without `file:symbol` evidence backing the change.
- Do not add speculative architecture notes not backed by code.
- Do not remove historical notes from `/docs/99-lessons/` unless explicitly requested.
- Do not create new pages when an existing page already covers the topic.
- Do not create concept files without a `type:` in frontmatter from the controlled vocabulary.
- Do not keep shipped plans around for reference; delete them (see `references/okf-conventions.md`).
- Do not drop or reformat YAML frontmatter when editing a concept file. Preserve existing `type:`, `title:`, `description:`, `tags:`, and `timestamp:` fields.

## Gotchas

- Relative links in docs break when pages are moved; always use root-absolute paths (`/docs/...`).
- The trigger matrix in `references/trigger-matrix.md` is a guide, not exhaustive; use judgment when a change spans multiple domains.

## References

- `references/trigger-matrix.md` - File-classification table for diff impact.
- `references/doc-coverage-checklist.md` - Page-by-page audit checklist (includes OKF pass).
- `references/okf-conventions.md` - OKF v0.1 conformance, type vocabulary, plan lifecycle.
- `scripts/classify-diff.py` - Classifies a `git diff` into trigger categories.
- `scripts/check-okf.py` - Validates strict YAML frontmatter and `type:` for `/docs/`.
- `scripts/check-links.py` - Checks internal markdown links and enforces root-absolute paths.
