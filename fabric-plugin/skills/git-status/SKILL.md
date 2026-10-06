---
name: git-status
description: Get Git connection status and sync state of a workspace
---

# git-status Skill

## Purpose
Show the Git connection details of a workspace and which items have workspace/remote changes.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-status/git_status.py" "$@"
```

## Usage

```
git_status.py <workspace>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)

## Limitation: workspaces not connected to Git
This skill only reports meaningful data for a workspace that has a Git connection.
A workspace that was never connected answers HTTP **200** with `gitProviderDetails: null`
(not a 404), so the skill reports `NOT connected to Git` and exits 0 — there is no
status to show. Such a workspace receives changes only through **deployment pipelines**
or direct edits, and `git-update` does not apply to it either.

This is common for Test/Production workspaces, where only the Development workspace
is wired to the repository.

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-status/git_status.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-status/git_status.py" a1b2c3d4-e5f6-...
```

## Returns
- Success: Exit code 0, connection details + changed items (or "not connected to Git" info)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
