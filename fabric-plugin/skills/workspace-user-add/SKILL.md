---
name: workspace-user-add
description: Add a user to Microsoft Fabric workspace with specified role. Accepts email or Azure AD Object ID. This skill should be used when adding workspace members.
---

# workspace-user-add Skill

## Purpose
Add a user to a workspace with a role. Emails are resolved to Object IDs via Microsoft Graph.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-add/workspace_user_add.py" "$@"
```

## Usage

```
workspace_user_add.py <workspace> <user> <role>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<user>` (required): User **email or Azure AD Object ID** (emails are resolved via Graph)
- `<role>` (required): `Admin` | `Member` | `Contributor` | `Viewer`

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-add/workspace_user_add.py" "My Workspace" user@example.com Member
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-user-add/workspace_user_add.py" a1b2c3d4-... b2c3d4e5-... Admin
```

## Returns
- Success: Exit code 0, confirmation message
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (invalid role, user/workspace not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
