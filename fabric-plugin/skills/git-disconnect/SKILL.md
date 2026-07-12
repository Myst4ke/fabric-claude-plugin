---
name: git-disconnect
description: Disconnect a workspace from its Git repository
---

# git-disconnect Skill

## Purpose
Disconnect a workspace from its connected Git repository. Workspace items are preserved (not deleted).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-disconnect/git_disconnect.py" "$@"
```

## Usage

```
git_disconnect.py <workspace>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-disconnect/git_disconnect.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-disconnect/git_disconnect.py" a1b2c3d4-e5f6-...
```

## Returns
- Success: Exit code 0, disconnect confirmation (also 0 if workspace was not connected)
- Error: Exit code 1-3, error message (1 if Admin role missing)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
