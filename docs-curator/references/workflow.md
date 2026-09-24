# Documentation sync workflow

## Documentation folders

| Folder | Purpose |
|---|---|
| `/docs/00-core/` | Foundational concepts, constraints, architecture, and shared conventions |
| `/docs/10-integrations/` | External integrations, services, and connectors |
| `/docs/20-features/` | Feature-specific behavior, usage, and capabilities |
| `/docs/25-patterns/` | Reusable guidance across multiple features |
| `/docs/30-operations/` | Runbooks, deployment, test procedures, and maintenance |
| `/docs/40-plans/` | Implementation plans, deleted on ship |
| `/docs/99-lessons/` | Lessons only when explicitly requested |
| `/docs/index.md` | Sectioned catalog of pages and descriptions |
| `/docs/log.md` | Optional update log, newest first |

## Step-by-step execution

1. **Confirm mode and base branch.** Identify the current and default branches without switching branches. The user's requested scope takes precedence.

2. **Build a feature inventory from the selected scope.**
   - In `full` mode: walk the codebase for public exports, configuration types, env vars, CLI commands, default values, and documented behaviors.
   - In `diff` mode: inspect committed changes against the base branch (`git diff <base>...HEAD`), uncommitted tracked changes (`git diff` and `git diff --cached`), and relevant untracked files. Do not mistake an empty committed diff for an empty change set.
   - In `concept` mode: read the named source plus its tests and references.
   - Search for project-specific configuration and environment-variable patterns. In `full` mode, also inspect test commands, suites, listing commands, and CI test jobs.
   - Record each item's `file:symbol` source and behavior notes. Keep this evidence in the working inventory and final report; use frontmatter `sources` for page provenance.

3. **Classify the diff into trigger categories.**
   - In `diff` mode, run the installed skill's `scripts/classify-diff.py <base>` with the target repository as the working directory, if available. It classifies committed changes only and assigns one category per file. Review uncommitted changes separately and inspect every applicable row in `references/trigger-matrix.md`.
   - In `full` mode, the matrix is a routing guide only.
   - If a skill script is unavailable, classify manually and note that in the final report. Skill scripts live with this skill, not necessarily in the target project.

4. **Doc-first pass: review existing pages.**
   - Walk each relevant page under `/docs/`.
   - Use the parsing template in `references/templates.md` to review content and frontmatter. Sections are conventional, not mandatory.
   - Identify missing mentions of important supported options: opt-in flags, env vars, customization points, new features from `src/` and `examples/`.
   - Identify where readers would reasonably expect missing material.
   - Route cross-cutting guidance to `25-patterns`, feature-specific behavior to `20-features`, foundations to `00-core`, and test procedures to `30-operations` (`type: Test Procedure`).

5. **Code-first pass: map features to docs.**
   - Review the docs information architecture in `/docs/index.md`.
   - For each feature in the inventory, determine the best existing page or section. Use `references/trigger-matrix.md` as a starting point.
   - Identify features with no doc page, or pages with no corresponding content.
   - Choose the existing type that best matches the page's primary purpose; do not add a type to the vocabulary.
   - For reference pages under `/docs/ref/*`, treat the source docstring as the source of truth; **prefer updating the source comment** so regenerated reference pages stay correct, instead of hand-editing the generated output.
   - Route candidate docs using the folder table above.

6. **Detect gaps and inaccuracies.**
   - **Missing.** Features or configs present in code but absent in docs.
   - **Incorrect or outdated.** Names, defaults, or behaviors that diverge from code.
   - **Structural (optional).** Pages overloaded, missing overviews, or mis-grouped topics.
   - **OKF (when the full bundle is adopted).** A concept has no `type:`, the wrong `type:` for its directory, a stale `generated.at`, or is missing from an index.
   - If the same guidance appears in 2+ pages, run the Pattern Extraction pass in `references/passes.md`.

7. **Apply source-backed changes without waiting for approval.**
   - Keep edits scoped to the existing tone, format, and information architecture.
   - For new concept pages: apply the `references/technical-writing.md` guidelines; use the per-type section template in `references/templates.md` matching the page's `type:`; sections are conventional, not required; omit sections the concept does not warrant.
   - Update `/docs/index.md` when adding or renaming pages, and keep each entry's description in sync with the page's `description:` field.
   - Bump `generated.at` on every page created or edited, and append an entry to `/docs/log.md` when the bundle keeps one (see `references/okf-conventions.md`).
   - Every new or edited concept file MUST have a `type:` in its frontmatter from the controlled vocabulary in `references/okf-conventions.md`.
   - When a plan in `/docs/40-plans/` ships, follow this ordered procedure:
     1. **Delete the plan file** from `/docs/40-plans/`.
     2. **Remove the plan entry** from `/docs/40-plans/index.md` (if present).
     3. **Remove the plan entry** from `/docs/index.md`.
     4. **Grep for stale cross-references.** Search the deleted plan's path across `/docs/` and update any cross-references in feature or integration docs to point at the shipped feature doc instead.
   - If env vars changed, update `.env.example` in the same pass.
   - If evidence is insufficient or sources conflict, report the uncertainty rather than guessing. After editing, run the applicable checks and report the outcome.

## Final report

After editing and verification, report the outcome. Include only sections relevant to the scope:

```
Docs Sync Final Report

Mode: <full | diff | concept>
Base branch: <branch, if diff mode>
Scope: <path list or "single: <symbol>">

Files changed
- <Path> -> <what changed; supporting file:symbol>

Env / config changes
- <Var name> -> <change, if applicable>

Verification
- <Checks run and results; unavailable checks>

Unresolved
- <Evidence gap or conflict and affected page, if any>
```

If no changes were needed, say "No documentation changes were required for this scope" and report the checks run and any uncertainty.

## Verification

Before declaring the sync complete:

- Confirm that each edit has supporting `file:symbol` evidence and stays within the editing boundary in `SKILL.md`.
- Preserve existing frontmatter fields and bump `generated.at` on edited concept pages. Check type vocabulary, page descriptions, `/docs/index.md`, and any optional `/docs/log.md`.
- Check affected patterns, `.env.example`, test procedures, and source docstrings when triggered.
- Run the installed skill's `scripts/check-integrity.py` against the target `/docs/` directory after edits. If it is unavailable, report that and check frontmatter, catalog entries, and links manually. A clean run does not establish that claims match code.
- Run relevant project documentation checks when available. For shipped plans, verify that index entries and cross-references to the deleted file are gone.
