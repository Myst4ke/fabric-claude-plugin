---
name: workspace-delete
description: Delete a Microsoft Fabric workspace. Asks for confirmation unless --force is used.
---

# workspace-delete Skill

## Purpose
Delete a workspace permanently (all content is destroyed). Interactive confirmation unless `--force`.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-delete/workspace_delete.py" "$@"
```

## Usage

```
workspace_delete.py <workspace> [--force]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--force` (optional): Skip the interactive confirmation prompt

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-delete/workspace_delete.py" "Old Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/workspace-delete/workspace_delete.py" a1b2c3d4-... --force
```

## Returns
- Success: Exit code 0, deletion confirmation message
- Cancelled or error: Exit code 1-3, message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, cancelled)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
