---
name: kql-database-get
description: Get detailed information about a KQL database
---

# kql-database-get Skill

## Purpose
Get details of a KQL database: query/ingestion URIs, type, parent eventhouse.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/kql-database-get/kql_database_get.py" "$@"
```

## Usage

```
kql_database_get.py <workspace> <database>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<database>` (required): KQL database **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/kql-database-get/kql_database_get.py" "My Workspace" "EventsDB"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/kql-database-get/kql_database_get.py" a1b2c3d4-... c3d4e5f6-...
```

## Returns
- Success: Exit code 0, formatted database details (incl. query URI)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
