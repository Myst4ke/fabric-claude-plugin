---
name: table-schema
description: Get table schema information
---

# table-schema Skill

## Purpose
Get the column schema of a lakehouse table (via `DESCRIBE TABLE`).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-schema/table_schema.py" "$@"
```

## Usage

```
table_schema.py <workspace> <lakehouse> <table_name>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<table_name>` (required): Table name

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-schema/table_schema.py" "My Workspace" Bronze customers
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-schema/table_schema.py" a1b2c3d4-... b2c3d4e5-... sales
```

## Returns
- Success: Exit code 0, column names, data types and nullability
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, invalid table)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
