---
name: warehouse-list-tables
description: List all tables and views in a SQL warehouse using INFORMATION_SCHEMA
---

# warehouse-list-tables Skill

## Purpose
List all tables and views in a warehouse via INFORMATION_SCHEMA
(executeQuery API first, silent pyodbc fallback).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-list-tables/warehouse_list_tables.py" "$@"
```

## Usage

```
warehouse_list_tables.py <workspace> <warehouse>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<warehouse>` (required): Warehouse **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-list-tables/warehouse_list_tables.py" "My Workspace" "Sales DW"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-list-tables/warehouse_list_tables.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, formatted table (schema, table name, type)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error, both methods failed)
- 3: Authentication error (run /fabric-plugin:setup:login)
