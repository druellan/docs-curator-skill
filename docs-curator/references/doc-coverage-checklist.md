# Doc Coverage Checklist

Use this checklist during the doc-first and code-first passes. It is intentionally short - it is a scanning aid, not a substitute for reading the page.

## Feature Inventory Targets

- Public exports: classes, functions, types, and module entry points.
- Configuration options: `*Settings` types, default config objects, and builder patterns.
- Environment variables or runtime flags.
- CLI commands, scripts, and example entry points that define supported usage.
- Test suites, test runner commands, coverage entry points, and CI test jobs.
- User-facing behaviors: retry, timeouts, streaming, errors, logging, telemetry, and data handling.
- Deprecations, removals, or renamed settings.

## Doc-First Pass (Page by Page)

- Review each relevant page.
- Look for missing opt-in flags, env vars, or customization options that the page implies exist.
- Note features that belong on the page based on user intent and navigation.
- Flag sections that read as a quick-start but are actually doing deep reference work.

## Code-First Pass (Feature Inventory)

- Map features to the closest existing page based on the navigation in `/docs/index.md`.
- Prefer updating existing pages over creating new ones unless the topic is clearly new.
- Use conceptual pages for cross-cutting concerns (auth, errors, streaming, tracing, tools).
- Keep quick-start flows minimal; move advanced details into deeper pages.

## Evidence Capture

- Record the file path and symbol or setting name for every claim.
- Note defaults and behavior-critical details for accuracy checks.
- Avoid large code dumps in the report; a short identifier plus a one-line description is enough.
- For generated reference pages, cite the source symbol, not the generated output.

## Red Flags for Outdated or Incorrect Docs

- Option names or types no longer exist or differ from code.
- Default values or allowed ranges do not match implementation.
- Features removed in code but still documented.
- New behaviors introduced without corresponding docs updates.
- Examples that import paths or call signatures that no longer exist.

## When to Propose Structural Changes

- A page mixes unrelated audiences (quick-start and deep reference) without clear separation.
- Multiple pages duplicate the same concept without cross-links.
- New feature areas have no obvious home in the nav structure.
- A page is referenced from `/docs/index.md` but does not exist.

## OKF Conformance Pass

`/docs/` is an OKF v0.1 knowledge bundle. Every page must conform. Run `scripts/check-okf.py` and treat any violation as a doc gap.

- Every concept file (non-reserved `.md`) has parseable YAML frontmatter.
- Every frontmatter has a non-empty `type:` from the controlled vocabulary in `references/okf-conventions.md`.
- New concept types are added to the vocabulary before use.
- `index.md` files enumerate the directory contents for progressive disclosure.
- `status:` is set correctly for the type (see `references/okf-conventions.md`).
- Plans in `/docs/40-plans/` follow the delete-on-ship lifecycle.

## Diff Mode Guidance (Current Branch vs Base)

- Focus only on changed behavior: new exports or options, modified defaults, removed features, or renamed settings.
- Use `git diff <base>...HEAD` (or equivalent) to constrain analysis.
- Document removals explicitly so docs can be pruned if needed.
- Prefer citing the post-change symbol; if the symbol was renamed, note both the old and new names.
