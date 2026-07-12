---
name: email-to-guid
description: Convert user email address to Azure AD Object ID (GUID) using Microsoft Graph API. Accepts both emails and GUIDs (pass-through). This skill should be used when commands need to resolve user identifiers.
---

# email-to-guid Skill

## Purpose
Resolve a user email to its Azure AD Object ID via Microsoft Graph. GUIDs pass through unchanged.
Outputs ONLY the GUID on stdout (single line) for programmatic use.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/email-to-guid/resolve_user.py" "$@"
```

## Usage

```
resolve_user.py <input> [--verbose]
```

## Parameters
- `<input>` (required): User **email address or GUID** (GUIDs are returned as-is)
- `--verbose` (optional): Verbose debugging output on stderr

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/email-to-guid/resolve_user.py" user@example.com
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/email-to-guid/resolve_user.py" a1b2c3d4-e5f6-... --verbose
```

## Returns
- Success: Exit code 0, resolved GUID on stdout
- Error: Exit code 1-3, error message on stderr

## Exit Codes
- 0: Success
- 1: Permanent error (user not found, usage error)
- 2: Retryable error (rate limit, Graph API error)
- 3: Authentication error (run /fabric-plugin:setup:login)
