---
name: git-commit
description: Commit workspace changes to the connected Git repository
---

# git-commit Skill

## Purpose
Commit all pending workspace changes to the connected Git repository (LRO polled automatically on 202).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-commit/git_commit.py" "$@"
```

## Usage

```
git_commit.py <workspace> [--message MESSAGE]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--message` (optional): Commit message

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-commit/git_commit.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-commit/git_commit.py" a1b2c3d4-... --message "Updated pipeline definitions"
```

## Returns
- Success: Exit code 0, commit confirmation
- Error: Exit code 1-3, error message (1 if not connected to Git or remote changes to pull)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not connected, conflict, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
