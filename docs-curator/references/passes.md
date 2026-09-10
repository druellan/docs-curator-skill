# Passes and Guardrails

Conditional procedures and quality controls applied at specific points in the main workflow. Load the relevant section only when its trigger fires; these are not always-on instructions.

## Pattern Extraction Pass

**Trigger:** a change set includes guidance that appears in 2+ places. Runs after inventory and before proposing edits.

1. Identify repeated guidance in docs or code (behavioral flow, composition, validation, operational sequence, accessibility, integration sequence).
2. Propose moving that repeated guidance into `/docs/25-patterns/` as canonical reusable patterns.
3. Replace duplicated prose in feature/operations pages with concise links to the canonical pattern page.
4. Keep examples implementation-ready, but avoid page-specific copy in pattern pages.

## Anti-Rationalization

Common excuses agents use to skip steps. Rebut each one before editing.

| Rationalization | Reality |
|---|---|
| "The change is small, just edit the one page" | Small changes often miss cross-references, env examples, and `index.md` updates. Run the full pass. |
| "I'll remember the source, no need to cite file paths" | Future you and the user cannot verify a change without a `file:symbol` source. Cite it every time. |
| "The diff is too big to inventory" | That is exactly when the inventory matters most. Use `scripts/classify-diff.py` to shrink the work. |
| "I'll just rewrite the page to be safe" | Rewrites are how style drift happens. Keep edits surgical; update the source comment, not the generated page. |
| "I'll just fix the docs as I go" | Each fix needs a source and a matching entry in the inventory. Record it before editing. |
| "Translated docs are just stale copies" | Out of scope. Translated docs have their own maintainers. Leave them alone. |
| "The doc is already correct enough" | "Correct enough" is the seed of every docs bug. Cite the code symbol, compare to the doc line, decide. |
| "I can't find the feature in docs, so it isn't documented" | Check the code, the index, and the plan. Then propose the page that should exist. |

## Red Flags

Stop and reconsider when any of these appear.

- A page mixes quick-start content with deep reference and has no clear boundary.
- The same concept is duplicated across multiple pages with no cross-link.
- A new feature area has no obvious home in the navigation.
- Reusable guidance is buried in feature or operations pages instead of `/docs/25-patterns/`.
- A `Test Procedure` page's run commands, suite inventory, or available-tests list diverge from the test config in the diff.
- The proposed edit hand-edits a generated reference page instead of the source.
- The inventory lists features the diff adds but the docs already cover, while missing features the diff actually changed.
- `.env.example` is out of sync with the new env vars in the diff.
