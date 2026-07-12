---
name: kql-query
description: Execute a KQL query against a KQL database
---

# kql-query Skill

## Purpose
Execute a Kusto Query Language (KQL) query against a KQL database
(Kusto-audience token used for the queryservice endpoint).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/kql-query/kql_query.py" "$@"
```

## Usage

```
kql_query.py <workspace> <database> "<query>"
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<database>` (required): KQL database **name or GUID** (names are resolved automatically)
- `<query>` (required): KQL query string

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/kql-query/kql_query.py" "My Workspace" "EventsDB" "Events | take 10"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/kql-query/kql_query.py" a1b2-... c3d4-... "Events | where Timestamp > ago(1h) | count"
```

## Returns
- Success: Exit code 0, formatted result table (max 100 rows displayed)
- Error: Exit code 1-3, error message (1 on KQL syntax error)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, syntax error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
