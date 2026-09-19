# Security

- Package names are constrained before they can become identifiers.
- All expected sections must be present exactly once and owned by one package.
- JSON bodies are parsed as data; embedded logic is never executed here.
- Hashes establish byte identity, not trust or authorship.

Treat emitted logic as source code requiring review before it reaches an execution system.
