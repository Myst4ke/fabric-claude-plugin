---
name: workspace-update
description: Update Microsoft Fabric workspace properties like name and description.
---

# workspace-update Skill

## Purpose
Update workspace properties (name and/or description).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-update/workspace_update.py" "$@"
```

## Usage

```
workspace_update.py <workspace> [--name NEW_NAME] [--description TEXT]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--name NEW_NAME` (optional): New workspace display name
- `--description TEXT` (optional): New workspace description

At least one of `--name` or `--description` is required.

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-update/workspace_update.py" "My Workspace" --name "New Name"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-update/workspace_update.py" a1b2c3d4-... --description "Updated"
```

## Returns
- Success: Exit code 0, updated workspace details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, name conflict)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
