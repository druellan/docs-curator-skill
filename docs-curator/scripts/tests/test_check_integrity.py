import importlib.util
import unittest
from pathlib import Path


CHECKER_PATH = Path(__file__).resolve().parents[1] / "check-integrity.py"
SPEC = importlib.util.spec_from_file_location("check_integrity", CHECKER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load integrity checker at {CHECKER_PATH}")
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class ValidateSourcesTests(unittest.TestCase):
    def test_strict_concept_validation_checks_sources(self) -> None:
        frontmatter = """type: Feature
title: Example
description: Example page
generated: { by: docs-curator/1.0, at: 2026-09-01T00:00:00Z }
sources: []
"""
        strict_issues = CHECKER.validate_concept(frontmatter, strict=True)
        self.assertTrue(any("sources" in issue for issue in strict_issues))
        self.assertEqual(CHECKER.validate_concept(frontmatter, strict=False), [])

    def test_accepts_source_entries_with_paired_usage_metadata(self) -> None:
        frontmatter = """sources:
  - id: orders-schema
    resource: https://example.com/orders-schema
    usage_count: 125
    usage_window: { from: 2026-09-01T00:00:00Z, to: 2026-09-30T00:00:00Z }
"""
        self.assertEqual(CHECKER.validate_sources(frontmatter), [])

    def test_sources_may_be_omitted_when_a_page_has_no_traceable_source(self) -> None:
        self.assertEqual(CHECKER.validate_sources("type: Feature\n"), [])

    def test_requires_id_and_resource(self) -> None:
        issues = CHECKER.validate_sources("sources:\n  - id: example\n")
        self.assertTrue(any("resource" in issue for issue in issues))

        issues = CHECKER.validate_sources(
            "sources:\n  - resource: https://example.com/source\n"
        )
        self.assertTrue(any("id" in issue for issue in issues))

    def test_source_ids_must_be_unique(self) -> None:
        frontmatter = """sources:
  - id: duplicate
    resource: https://example.com/one
  - id: duplicate
    resource: https://example.com/two
"""
        issues = CHECKER.validate_sources(frontmatter)
        self.assertTrue(any("duplicate" in issue for issue in issues))

    def test_source_ids_must_be_lowercase_kebab_case(self) -> None:
        issues = CHECKER.validate_sources(
            'sources:\n  - id: "Orders Schema"\n    resource: https://example.com/source\n'
        )
        self.assertTrue(any("lowercase kebab-case" in issue for issue in issues))

    def test_usage_count_and_window_must_be_paired(self) -> None:
        frontmatter = """sources:
  - id: example
    resource: https://example.com/source
    usage_count: 1
"""
        issues = CHECKER.validate_sources(frontmatter)
        self.assertTrue(any("usage_count" in issue and "usage_window" in issue for issue in issues))

    def test_resource_must_be_a_uri(self) -> None:
        issues = CHECKER.validate_sources("sources:\n  - id: example\n    resource: relative/path\n")
        self.assertTrue(any("resource" in issue and "URI" in issue for issue in issues))

    def test_sources_must_use_a_non_empty_block_sequence(self) -> None:
        issues = CHECKER.validate_sources("sources: []\n")
        self.assertTrue(any("block sequence" in issue for issue in issues))
        issues = CHECKER.validate_sources("sources:\n")
        self.assertTrue(any("at least one source" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
