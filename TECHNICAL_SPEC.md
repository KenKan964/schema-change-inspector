# Technical specification

compare(old,new) returns deterministic sci-report-v1. parse(path) performs bounded strict JSON parsing.
Both schema operands are validated against the documented subset shape, not the complete2020-12 meta-schema.
Unknown keyword semantics take precedence over equivalence/inclusion claims, including unchanged schemas.
Unsupported keyword contents are not recursively meta-schema validated; malformed content there can remain UNKNOWN rather than INVALID_SCHEMA.
Known type/required/properties/enum shapes are checked; additionalProperties schema objects are UNKNOWN.
Recursive sufficient proof or bounded candidate generation produces the global classification.
Witnesses are rechecked by old/new subset validators. Acceptance tests additionally use an independent evaluator.

Enum uses JSON numeric equality, keeps booleans distinct from numbers, and compares nested arrays/objects structurally.
Annotations title/description do not constrain values. Type arrays are sets and integer is a number subtype.
Array membership is unrestricted without items; any unsupported keyword blocks NON_BREAKING.
Input/candidate limits can cause conservative UNKNOWN/INVALID_SCHEMA. This is not a complete solver or denial-of-service sandbox.
Report fragments may contain enum values; use synthetic or nonsensitive schemas for public reports.
No network, subprocess or reference resolution in the product. Paths in $ref are data only.
Outputs remain for review and can be removed by deleting the newly created directory.
External source changes during inspection or same-user filesystem races are outside isolation guarantees.

References: https://json-schema.org/specification

## FIX-01 numeric boundary

The lexical number hook constructs Decimal(token) exactly, then compares Decimal.from_float(float(token)) with that decimal.
If unequal or nonfinite after conversion, parsing raises UnsupportedNumber and CLI emits UNKNOWN/UNSUPPORTED_NUMERIC_PRECISION.
No inclusion proof, rounded before/after fragment or counterexample is emitted for that inspection.
The numeric JSON Pointer is the whole-document root because precision refusal occurs before schema-tree construction.
Old/new fragments are null when parsing cannot be completed safely; the exact original input strings are retained in synthetic regression evidence.
Arithmetic is not performed on large decimal exponents; token256/exponent400/integer128-digit guards precede conversions.
Exponent text longer than4 digits is conservatively UNKNOWN even for leading-zero representations.
Supported floating representations are exact binary64 values; output round-trip preserves their mathematical value.
Integer/1.0 equivalence and boolean distinction are retained. Numeric refusal is not INVALID_SCHEMA.
Known invalid JSON such as NaN remains INVALID_SCHEMA. Unsupported numeric semantics take precedence if encountered before another error.
Direct dictionary API accepts already-built Python values and cannot reconstruct any precision lost by caller's decoder.

Test preserve() writes UTF-8 through exclusive x mode, refuses symlink destinations/ancestors and fails on write errors.
Static path protection is not same-user race isolation. Product output path behaviour is otherwise unchanged.
