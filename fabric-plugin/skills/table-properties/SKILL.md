---
name: table-properties
description: Get table properties and metadata
---

# table-properties Skill

## Purpose
Get table properties and metadata (via `SHOW TBLPROPERTIES`).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-properties/table_properties.py" "$@"
```

## Usage

```
table_properties.py <workspace> <lakehouse> <table_name>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<table_name>` (required): Table name

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-properties/table_properties.py" "My Workspace" Bronze customers
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-properties/table_properties.py" a1b2c3d4-... b2c3d4e5-... sales
```

## Returns
- Success: Exit code 0, property/value table
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, invalid table)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
