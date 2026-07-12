---
name: lakehouse-sql-query
description: Execute SQL queries on lakehouse using SQL Analytics Endpoint with full T-SQL support
---

# lakehouse-sql-query Skill

## Purpose
Execute T-SQL queries (JOIN, GROUP BY, CTEs, subqueries) on a lakehouse via its
SQL Analytics Endpoint. Authentication is **silent** (cached token) - no
browser prompt. Requires `pyodbc` + ODBC Driver 17/18 for SQL Server.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-sql-query/lakehouse_sql_query.py" "$@"
```

## Usage

```
lakehouse_sql_query.py <workspace> <lakehouse> <query> [--limit N] [--verbose]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<query>` (required): SQL query in T-SQL syntax (schema prefix required, e.g. `dbo.table`)
- `--limit N` (optional): Maximum rows to return (adds TOP clause)
- `--verbose` (optional): Enable verbose debug output

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-sql-query/lakehouse_sql_query.py" "My Workspace" Bronze "SELECT TOP 10 * FROM dbo.customers"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-sql-query/lakehouse_sql_query.py" a1b2c3d4-... b2c3d4e5-... "SELECT COUNT(*) FROM dbo.orders" --verbose
```

## Returns
- Success: Exit code 0, formatted result table (max 100 rows displayed)
- Error: Exit code 1-3, error message with SQL hints

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, SQL error, missing pyodbc)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
