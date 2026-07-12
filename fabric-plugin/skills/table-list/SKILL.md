---
name: table-list
description: List all tables in a lakehouse
---

# table-list Skill

## Purpose
List all tables in a lakehouse, with pagination handled automatically.
Note: returns HTTP 400 for schema-enabled lakehouses (use lakehouse-sql-query
or table-list-onelake instead - the script prints this hint).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-list/table_list.py" "$@"
```

## Usage

```
table_list.py <workspace> <lakehouse>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-list/table_list.py" "My Workspace" Bronze
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-list/table_list.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, formatted table list (name, type, location)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, schema-enabled lakehouse)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
