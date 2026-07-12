---
name: workspace-get
description: Get detailed information about a specific Microsoft Fabric workspace including ID, name, type, capacity assignment, and metadata.
---

# workspace-get Skill

## Purpose
Get detailed information about a workspace (ID, name, description, type, state, capacity).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-get/workspace_get.py" "$@"
```

## Usage

```
workspace_get.py <workspace>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-get/workspace_get.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-get/workspace_get.py" a1b2c3d4-e5f6-...
```

## Returns
- Success: Exit code 0, formatted workspace details + raw JSON
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
