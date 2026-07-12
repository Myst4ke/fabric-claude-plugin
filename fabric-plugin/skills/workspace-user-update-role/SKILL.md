---
name: workspace-user-update-role
description: Update a user's role in a Microsoft Fabric workspace. Changes permissions level.
---

# workspace-user-update-role Skill

## Purpose
Change a user's role/permissions in a workspace.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-update-role/workspace_user_update_role.py" "$@"
```

## Usage

```
workspace_user_update_role.py <workspace> <user_id> <role>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<user_id>` (required): User Azure AD Object ID (**GUID only** - use workspace-user-list to find it)
- `<role>` (required): `Admin` | `Member` | `Contributor` | `Viewer`

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-update-role/workspace_user_update_role.py" "My Workspace" b2c3d4e5-... Contributor
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-update-role/workspace_user_update_role.py" a1b2c3d4-... b2c3d4e5-... Admin
```

## Returns
- Success: Exit code 0, confirmation + role permission summary
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (invalid role/user ID, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
