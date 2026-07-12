---
name: git-update
description: Update workspace from Git (pull remote changes)
---

# git-update Skill

## Purpose
Pull remote Git changes into the workspace (LRO polled automatically on 202).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-update/git_update.py" "$@"
```

## Usage

```
git_update.py <workspace> [--conflict-resolution {PreferWorkspace,PreferRemote}]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--conflict-resolution` (optional): Conflict resolution strategy (default: `PreferRemote`)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-update/git_update.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-update/git_update.py" a1b2c3d4-... --conflict-resolution PreferWorkspace
```

## Returns
- Success: Exit code 0, update confirmation
- Error: Exit code 1-3, error message (1 if not connected to Git or conflict)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not connected, conflict, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
