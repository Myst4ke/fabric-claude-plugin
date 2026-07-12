---
name: table-load
description: Load data into a lakehouse table from a file
---

# table-load Skill

## Purpose
Load data from a file in the lakehouse Files section into a table,
with LRO polling handled automatically (up to 10 minutes).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-load/table_load.py" "$@"
```

## Usage

```
table_load.py <workspace> <lakehouse> <table_name> <file_path> [--mode {Overwrite,Append}]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<table_name>` (required): Target table name
- `<file_path>` (required): Path to file in lakehouse Files section (e.g. `Files/data/sales.csv`)
- `--mode` (optional): Load mode `Overwrite` (default) or `Append`

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-load/table_load.py" "My Workspace" Bronze sales Files/data/sales.csv
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-load/table_load.py" a1b2c3d4-... b2c3d4e5-... sales Files/data/sales.csv --mode Append
```

## Returns
- Success: Exit code 0, load confirmation with progress updates
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, table/file not found, forbidden)
- 2: Retryable error (rate limit, server error, LRO timeout)
- 3: Authentication error (run /fabric-plugin:setup:login)
