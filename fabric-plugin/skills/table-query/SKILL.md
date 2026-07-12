---
name: table-query
description: Execute SQL query against lakehouse
---

# table-query Skill

## Purpose
Execute a SQL query against a lakehouse and return results.

## Usage

From agent:
```
Use Skill tool with skill="fabric-plugin:table-query"
Arguments: <workspace-id> <lakehouse-id> "<query>"
```

## Implementation

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-query/table_query.py" "$@"
```

## Parameters
- `<workspace-id>` (required): The workspace GUID
- `<lakehouse-id>` (required): The lakehouse GUID
- `<query>` (required): SQL query to execute

## Returns
- Success: Exit code 0, query results in tabular format
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (invalid query, not found)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (token expired)

## Notes
- Use LIMIT clause for large result sets
- Supports standard SQL syntax
