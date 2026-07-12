---
name: workspace-unassign-capacity
description: Unassign a workspace from its capacity
---

# workspace-unassign-capacity Skill

## Purpose
Unassign a Microsoft Fabric workspace from its current capacity.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-unassign-capacity/workspace_unassign_capacity.py" "$@"
```

## Usage

```
workspace_unassign_capacity.py <workspace>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-unassign-capacity/workspace_unassign_capacity.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-unassign-capacity/workspace_unassign_capacity.py" a1b2c3d4-...
```

## Returns
- Success: Exit code 0, confirmation with workspace ID
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
