---
name: warehouse-get
description: Get detailed information about a SQL warehouse
---

# warehouse-get Skill

## Purpose
Get details of a warehouse: name, ID, description, SQL endpoint, dates.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-get/warehouse_get.py" "$@"
```

## Usage

```
warehouse_get.py <workspace> <warehouse>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<warehouse>` (required): Warehouse **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-get/warehouse_get.py" "My Workspace" "Sales DW"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-get/warehouse_get.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, formatted warehouse details (incl. SQL endpoint)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
