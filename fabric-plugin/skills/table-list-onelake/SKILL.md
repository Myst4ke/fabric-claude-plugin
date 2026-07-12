---
name: table-list-onelake
description: List all tables in a lakehouse using OneLake Table API (supports schema-enabled lakehouses)
---

# table-list-onelake Skill

## Purpose
List schemas and tables in a lakehouse via the OneLake Table API
(Unity Catalog compatible). Works with schema-enabled and classic lakehouses.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-list-onelake/table_list_onelake.py" "$@"
```

## Usage

```
table_list_onelake.py <workspace> <lakehouse>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-list-onelake/table_list_onelake.py" "My Workspace" Bronze
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-list-onelake/table_list_onelake.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, tables grouped by schema (name + format)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error, schema listing failure)
- 3: Authentication error (run /fabric-plugin:\setup:login)
