# Security / 安全条件

Schema Change Inspector is a **local, read-only** inspector of controlled JSON Schema contract files. There is no external `$ref` fetching, network access, script execution, package installation, or code generation in the product CLI. The provided tests use synthetic fixtures only.

- Use **small, trusted, nonsensitive** local schema files. Size and complexity limits are bounded guards, **not** a complete hostile-input sandbox.
- Reports intentionally contain old/new schema fragments and synthetic counterexamples; source enum values or paths might be sensitive. Keep private reports private.
- Unsupported semantics yield `UNKNOWN` by default, not a false inclusion claim. `--unknown allow` changes only the exit code and requires a conscious CI policy decision.
- FIX-01 refuses lossy decimal-to-binary64 numeric conversion. `0.1` and other non-exact values may yield `UNKNOWN`; callers using raw Python dictionaries cannot recover already-lost numeric precision.
- Normal CLI inputs are not edited. The CLI creates a fresh report directory; tests use exclusive evidence output and reject static symlink paths. No hostile same-user race isolation guarantee is made.
- Private vulnerability reporting on this repository has **not been independently confirmed enabled**. Do **not** disclose confidential schema contents or unpatched vulnerabilities in public issues; use a verified private reporting channel when available.
- The MIT copyright notice is attributed to `KenKan964` in [LICENSE](LICENSE). This is not a claim about unknown third-party contributions or rights.

See [README.md](README.md) and [TECHNICAL_SPEC.md](TECHNICAL_SPEC.md) for detailed supported-vocabulary limits and diagnostic semantics.
