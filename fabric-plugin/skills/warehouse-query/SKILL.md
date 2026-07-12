---
name: warehouse-query
description: Execute read-only SQL query on a Microsoft Fabric warehouse
---

# warehouse-query Skill

## Purpose
Execute a read-only (SELECT) SQL query on a warehouse with security controls
(SQL validation, row limits, audit logging).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-query/warehouse_query.py" "$@"
```

## Usage

```
warehouse_query.py <workspace> <warehouse> "<query>" [--limit N]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<warehouse>` (required): Warehouse **name or GUID** (names are resolved automatically)
- `<query>` (required): SQL query (SELECT only)
- `--limit N` (optional): Maximum rows to return (TOP N injected if missing)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-query/warehouse_query.py" "My Workspace" "Sales DW" "SELECT TOP 10 * FROM dim_customer"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-query/warehouse_query.py" a1b2c3d4-... b2c3d4e5-... "SELECT * FROM fact_sales" --limit 100
```

## Returns
- Success: Exit code 0, formatted result table (max 100 rows displayed)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, SQL rejected, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
