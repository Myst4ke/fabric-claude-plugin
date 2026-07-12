---
name: workspace-list
description: List all Microsoft Fabric workspaces accessible to the authenticated user with formatted table output
---

# workspace-list Skill

## Purpose
List all workspaces accessible to the user, with pagination handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-list/list_workspaces.py" "$@"
```

## Usage

```
list_workspaces.py [--limit N]
```

## Parameters
- `--limit N` (optional): Maximum number of workspaces to return

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-list/list_workspaces.py"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-list/list_workspaces.py" --limit 10
```

## Returns
- Success: Exit code 0, formatted table of workspaces (ID, name, type, capacity ID)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
