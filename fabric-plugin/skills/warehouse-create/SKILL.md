---
name: warehouse-create
description: Create a new SQL warehouse in a workspace
---

# warehouse-create Skill

## Purpose
Create a new SQL warehouse (long-running operation polled automatically).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-create/warehouse_create.py" "$@"
```

## Usage

```
warehouse_create.py <workspace> <name> [description]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): Warehouse display name
- `[description]` (optional): Warehouse description

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-create/warehouse_create.py" "My Workspace" "Sales DW"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/warehouse-create/warehouse_create.py" a1b2c3d4-... "Sales DW" "Sales data warehouse"
```

## Returns
- Success: Exit code 0, created warehouse name + ID
- Error: Exit code 1-3, error message (1 on name conflict)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, conflict, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
