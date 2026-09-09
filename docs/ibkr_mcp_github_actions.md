# IBKR MCP in GitHub Actions

IBKR MCP stays disabled in GitHub Actions unless both conditions are true:

- repository variable `IBKR_MCP_GITHUB_ACTIONS_ENABLED` is explicitly `true`;
- Actions secret `IBKR_MCP_CREDENTIALS_JSON` contains a valid read-only OAuth token payload.

The workflow exposes the secret only as a process environment variable. The
scanner loads it in memory when no local credentials file exists. It rejects a
token containing write scope, never logs the token, and never commits it.

Interactive browser OAuth is not dependable in a headless Actions runner.
Access and refresh tokens may also expire during or between runs. Therefore the
environment-secret path is suitable only while the provider accepts refreshes
from an ephemeral runner and the secret is rotated securely.

For production, the preferred architecture is:

`IBKR MCP -> authenticated private backend -> scanner`

The backend owns OAuth, refreshes tokens, restricts calls to the read-only tool
allow-list, caches market/contract/options responses, and exposes short-lived
authenticated responses to the workflow. GitHub Actions then stores only a
backend credential, not the IBKR MCP token. The repository must never contain
either credential.

If either opt-in or authentication is absent, the scan continues without MCP
and records Options/Portfolio evidence as unavailable instead of inventing a
neutral observed value.
