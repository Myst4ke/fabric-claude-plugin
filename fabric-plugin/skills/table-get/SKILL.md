---
name: table-get
description: Get detailed information about a table
---

# table-get Skill

## Purpose
Get details (name, type, location, format) of a lakehouse table.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-get/table_get.py" "$@"
```

## Usage

```
table_get.py <workspace> <lakehouse> <table_name>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<table_name>` (required): Table name

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-get/table_get.py" "My Workspace" Bronze customers
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/table-get/table_get.py" a1b2c3d4-... b2c3d4e5-... sales
```

## Returns
- Success: Exit code 0, formatted table details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
