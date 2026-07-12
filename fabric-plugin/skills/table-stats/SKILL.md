---
name: table-stats
description: Get table statistics (row count, size, etc.)
---

# table-stats Skill

## Purpose
Get table statistics: row count, file count, size, partitions, format
(via `SELECT COUNT(*)` and `DESCRIBE DETAIL`). The table name is validated
(letters, digits, `_`, `.`, `[`, `]` only) before being used in SQL.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-stats/table_stats.py" "$@"
```

## Usage

```
table_stats.py <workspace> <lakehouse> <table_name>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<table_name>` (required): Table name (identifier characters only)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-stats/table_stats.py" "My Workspace" Bronze customers
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-stats/table_stats.py" a1b2c3d4-... b2c3d4e5-... dbo.sales
```

## Returns
- Success: Exit code 0, formatted statistics
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, invalid table name, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
