---
name: workspace-create
description: Create a new Microsoft Fabric workspace with optional capacity assignment. Returns workspace ID on success.
---

# workspace-create Skill

## Purpose
Create a new workspace with optional description and capacity assignment (LRO handled automatically).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-create/workspace_create.py" "$@"
```

## Usage

```
workspace_create.py <name> [--description TEXT] [--capacity CAPACITY_ID]
```

## Parameters
- `<name>` (required): Display name for the new workspace (no resolution)
- `--description TEXT` (optional): Workspace description
- `--capacity CAPACITY_ID` (optional): Capacity GUID to assign

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-create/workspace_create.py" "Analytics WS"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-create/workspace_create.py" "Analytics WS" --description "Team workspace" --capacity a1b2c3d4-...
```

## Returns
- Success: Exit code 0, created workspace details (ID, name)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, conflict, forbidden)
- 2: Retryable error (rate limit, server error, timeout)
- 3: Authentication error (run /fabric-plugin:setup:login)
