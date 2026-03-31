# Security Policy

## Scope

echo-ecp-fullauto is a local reasoning engine with no network calls,
no authentication, and no external data sources in its core.

**Attack surface is minimal:**
- File writes: `echo_memory.jsonl` and `echo_graph.json` (local only)
- No network requests
- No API keys or credentials
- No user authentication

## Reporting

If you find a security issue, open a private issue or contact
the maintainer directly via GitHub.

## Known design decisions

**No input sanitization for file paths in GraphMemory.**
If you call `GraphMemory(db_path=user_input)` with untrusted input,
a path traversal is possible. The default path is safe.
Do not expose the `db_path` parameter to untrusted users.

**No rate limiting on the CLI.**
The CLI processes one input at a time. Not a web service.
If you wrap this in a web API, add rate limiting yourself.

---

*2026-03-31*
