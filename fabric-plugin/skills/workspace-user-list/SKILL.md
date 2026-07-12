---
name: workspace-user-list
description: List all users and their roles in a Microsoft Fabric workspace.
---

# workspace-user-list Skill

## Purpose
List all users (role assignments) of a workspace, with pagination handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-list/workspace_user_list.py" "$@"
```

## Usage

```
workspace_user_list.py <workspace> [--limit N]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--limit N` (optional): Maximum number of users to return

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-list/workspace_user_list.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-list/workspace_user_list.py" a1b2c3d4-... --limit 20
```

## Returns
- Success: Exit code 0, formatted table (principal ID, type, role, display name)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
