# Schema Change Inspector

**Check input-acceptance backward compatibility between two small JSON Schema contracts without silently treating unknown changes as safe.**

**v0.1.0 · Experimental · Python 3.11+ · Standard library only · MIT**

**English** | [日本語](README_ja.md)

## What does it check?

Schema Change Inspector (SCI) compares **the set of JSON instances accepted by an old input schema** with those accepted by a new input schema. It asks whether every instance accepted by the old contract would also be accepted by the new contract:

`L(old) ⊆ L(new)` — **input-acceptance** backward compatibility, **not** output-schema compatibility.

A new required field, a narrower type, or removal of an enum value may break existing callers. SCI attempts a **sufficient proof** of inclusion within a documented, limited subset; otherwise it may produce a checked counterexample or mark the decision as unknown. This is **not** a complete JSON Schema 2020-12 or OpenAPI compatibility analyzer.

## Quick start

Requirements: Python 3.11 or later. No pip installation, server, account, network connection, or third-party Python packages. From the repository directory:

```sh
python sci.py --old samples/old.json --new samples/new.json --out example-breaking
python sci.py --old samples/new.json --new samples/old.json --out example-reverse
```

The first sample **intentionally adds a required `name` field** and should report `BREAKING` with exit code **1**. The output directory must be **new** each run; the tool refuses an existing directory and does not modify input schemas. On Windows, you may use `py -3` instead of `python`. Each run prints JSON and saves `report.json` in the output directory.

```sh
python -m unittest discover -s tests -v
```

A negative-control test passing means the tool correctly **detected a defect**; it does not mean the bad schema was accepted as safe.

## Interpret results

| Classification | Exit code (default) | Meaning |
| --- | ---: | --- |
| `NON_BREAKING` | `0` | A sufficient input-inclusion proof was established in the supported subset |
| `BREAKING` | `1` | A concrete instance was checked: old accepts, new rejects |
| `UNKNOWN` | `2` | Inclusion could not be established; **not** a safety pass |
| `INVALID_SCHEMA` | `2` | Invalid input, unsupported input conditions or I/O problem |

For controlled workflows that deliberately permit uncertain cases, add `--unknown allow`. This makes `UNKNOWN` exit **0** but **does not change its classification to `NON_BREAKING`**. Treat that option as a conscious CI policy decision, not a proof of compatibility.

Reports include stable `sci-report-v1` / `sci-rules-v1` identifiers, changed JSON Pointers, before/after fragments, rule IDs, and a global classification. A `BREAKING` result includes a checked counterexample where available. `counterexample_available` distinguishes a missing witness from the valid JSON `null` witness. A pointer locates changed syntax; it does **not** independently prove that the particular line caused the global verdict.

## Supported subset and conservative unknowns

| Handled within documented limits | `UNKNOWN` rather than a safety claim |
| --- | --- |
| Boolean schemas; `type` and type unions; `integer` included in `number` | `oneOf`, `allOf`, `anyOf`, `$ref`, `$dynamicRef` |
| `properties`, `required`, nested objects | `items`, `prefixItems` and complex array rules |
| Finite `enum` with exact-supported values | `pattern` / regular expressions and other unsupported keywords |
| Boolean `additionalProperties` | Schema-form `additionalProperties` |
| `title` / `description` annotations and explicit 2020-12 dialect | Other JSON Schema dialects / unrecognized semantics |

Arrays may be treated as **unconstrained** array-type values, not element-by-element validated arrays. External `$ref` URLs are never fetched; no external commands, script execution, code generation or input mutation occurs.

**Numeric precision is intentionally conservative (FIX-01).** Parsing first checks the original JSON numeric token. A decimal requiring lossy conversion to binary64—such as `0.1`, `1.0000000000000001` or `1e-400`—is marked `UNKNOWN` with rule `UNSUPPORTED_NUMERIC_PRECISION`, rather than rounded to falsely prove compatibility. `1` and `1.0` are mathematically equal; `true` and numeric `1` are different. Exact values such as `1.5` remain supported. Numeric token length is limited to 256 characters, exponent magnitude to 400 (at most four exponent digits), and integer digits to 128; valid JSON numbers outside these limits also yield `UNKNOWN`. Nonfinite JSON tokens and duplicate object keys are rejected as invalid.

If calling the Python `compare(old, new)` function with already-decoded dictionaries, the tool **cannot recover precision lost by the caller's JSON parser**. Use the included `parse()` or command-line entry point when original decimal semantics matter.

## Reproduce verification

The accepted FIX-01 candidate includes **53 automated tests**: 39 original cases and 14 added regression cases. An independent Linux/Python 3.13.5 review passed all 53 and verified numerical corner cases and evidence file collision protection. The originally delivered Python 3.12.14 run is historical evidence, not an independently rerun claim.

GitHub Actions is configured for **Ubuntu and Windows × Python 3.11, 3.12 and 3.13**; consult the [actual Actions results](https://github.com/KenKan964/schema-change-inspector/actions). The file `evidence/ci_status.json` is a **pre-repository historical snapshot**, not live CI status.

```sh
python -m unittest discover -s tests -v
```

Optionally, set `SCI_EVIDENCE` to a **fresh** directory before invoking the tests to persist case evidence. Existing evidence files, direct symlinks and symlink-containing path components cause a test failure instead of an overwrite. This does not promise isolation against hostile same-user races.

## Scope, safety and limits

- Inspection is read-only with respect to old/new schema files; output is a new directory with a JSON report.
- Raw schema fragments and generated counterexamples may be written to reports. **Do not place confidential values or secrets in schemas intended for publication**; keep private reports private.
- Input is limited to 65,536 bytes per schema; lexical nesting to 32; schema nesting to 12; properties to 16 per object; candidate recursion to 5 and candidate search fuel to 2,000. These are limited guards, not a malicious-input sandbox.
- Lack of a generated witness does **not** imply a safe change. Unsupported semantics remain `UNKNOWN`, even if schemas otherwise look identical.
- Local, controlled inputs only. No claim of comprehensive JSON Schema 2020-12 coverage, superior accuracy against existing OSS, saved engineering hours, ROI, or business demand.

## Documentation and license

[日本語 README](README_ja.md) · [Rule identifiers](RULES.md) · [Technical specification](TECHNICAL_SPEC.md) · [Security](SECURITY.md) · [OSS comparison](OSS_COMPARISON.md) · [FIX-01 details](FIX01_CHANGES.md) · [Developer report](REPORT_ja.md) · [Change log](CHANGELOG.md) · [MIT License](LICENSE)

**License:** MIT · Copyright (c) 2026 KenKan964.
