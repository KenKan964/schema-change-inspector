# Changelog

## v0.1.0 — experimental candidate (2026-11-14)

- Introduced a local read-only inspector for **input-acceptance** backward compatibility in a limited JSON Schema 2020-12 subset.
- Added validated breaking-change counterexamples, conservative `UNKNOWN`, JSON Pointer diagnostics, and opt-in `--unknown allow` policy.
- FIX-01: made test evidence output exclusive-create, refusing existing files and static symlink paths.
- FIX-01: prevent false `NON_BREAKING` caused by decimal precision loss; report `UNSUPPORTED_NUMERIC_PRECISION` / `UNKNOWN` for unsupported numeric inputs.
- Existing 39 acceptance cases retained; 14 regression cases added (53 tests total).
- Prepared bilingual publication documentation and MIT attribution `KenKan964` before first GitHub release.

**Verification:** Original developer Python 3.12/3.13 test evidence and an independent Linux Python 3.13.5 review (53/53) predate GitHub registration. Actual GitHub CI status is available on [Actions](https://github.com/KenKan964/schema-change-inspector/actions); the checked-in `evidence/ci_status.json` is an earlier historical snapshot, not a live status report.
