---
name: table-read
description: Read data from a lakehouse table (supports schema-enabled lakehouses) using OneLake File API
---

# table-read Skill

## Purpose
Read Delta table data directly from OneLake (ADLS) using the deltalake
library. Works with both schema-enabled and classic lakehouses.
Requires `pip install deltalake pandas pyarrow`.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-read/table_read.py" "$@"
```

## Usage

```
table_read.py <workspace> <lakehouse> <table_name> [--limit N] [--schema NAME]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<table_name>` (required): Table name (e.g. "customers")
- `--limit N` (optional): Maximum rows to return (default: 100)
- `--schema NAME` (optional): Schema name (default: "dbo")

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-read/table_read.py" "My Workspace" Bronze customers --limit 10
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-read/table_read.py" a1b2c3d4-... b2c3d4e5-... sales --schema dbo
```

## Returns
- Success: Exit code 0, data preview + column info
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, missing libraries)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
