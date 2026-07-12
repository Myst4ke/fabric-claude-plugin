---
name: warehouse-list
description: List all warehouses in a Microsoft Fabric workspace
---

# warehouse-list Skill

## Purpose
List all warehouses in a workspace, with pagination handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-list/warehouse_list.py" "$@"
```

## Usage

```
warehouse_list.py <workspace> [--limit N]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--limit N` (optional): Maximum number of warehouses to return

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-list/warehouse_list.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-list/warehouse_list.py" a1b2c3d4-e5f6-... --limit 10
```

## Returns
- Success: Exit code 0, formatted table of warehouses (name + ID)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
