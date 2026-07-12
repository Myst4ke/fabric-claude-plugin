---
name: workspace-user-remove
description: Remove a user from Microsoft Fabric workspace. Accepts email or Azure AD Object ID. Asks for confirmation unless --force is used.
---

# workspace-user-remove Skill

## Purpose
Remove a user's access from a workspace. Emails are resolved to Object IDs via Microsoft Graph.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-remove/workspace_user_remove.py" "$@"
```

## Usage

```
workspace_user_remove.py <workspace> <user> [--force]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<user>` (required): User **email or Azure AD Object ID** (emails are resolved via Graph)
- `--force` (optional): Skip the interactive confirmation prompt

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-remove/workspace_user_remove.py" "My Workspace" user@example.com
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-remove/workspace_user_remove.py" a1b2c3d4-... b2c3d4e5-... --force
```

## Returns
- Success: Exit code 0, confirmation message
- Cancelled or error: Exit code 1-3, message

## Exit Codes
- 0: Success
- 1: Permanent error (user/workspace not found, forbidden, cancelled)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
