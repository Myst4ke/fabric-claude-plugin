---
name: workspace-assign-capacity
description: Assign a workspace to a capacity
---

# workspace-assign-capacity Skill

## Purpose
Assign a Microsoft Fabric workspace to a specific capacity.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-assign-capacity/workspace_assign_capacity.py" "$@"
```

## Usage

```
workspace_assign_capacity.py <workspace> <capacity_id>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<capacity_id>` (required): Capacity GUID to assign (find with capacity-list)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-assign-capacity/workspace_assign_capacity.py" "My Workspace" b2c3d4e5-...
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-assign-capacity/workspace_assign_capacity.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, confirmation with workspace and capacity IDs
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
