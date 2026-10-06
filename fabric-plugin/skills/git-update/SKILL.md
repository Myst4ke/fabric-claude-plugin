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
                          [--allow-override-items]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--conflict-resolution` (optional): which side wins on conflict (default: `PreferRemote`)
- `--allow-override-items` (optional): authorize replacing existing workspace items.
  The API **requires** this consent as soon as an incoming item already exists in the
  workspace; without it the call fails with `OverrideItemsNotAllowed`.

## API contract (why the body is built this way)
`POST /workspaces/{id}/git/updateFromGit` requires four things, all of which the skill
now resolves automatically by reading `/git/status` first:
- `workspaceHead` and `remoteCommitHash` — both mandatory, and they pin the update to
  the state actually observed, so a concurrent commit cannot be applied silently.
- `conflictResolution.conflictResolutionType` — the side being resolved, always
  `Workspace`. It is **not** the policy: sending `PreferRemote` here is rejected.
- `conflictResolution.conflictResolutionPolicy` — who wins (`PreferRemote` /
  `PreferWorkspace`), which is what `--conflict-resolution` sets.

## Limitation: workspaces not connected to Git
Only a Git-connected workspace can be updated. On a workspace with no connection the
skill exits 1 with a clear message — such a workspace is fed by **deployment pipelines**
or direct edits instead.

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
- 3: Authentication error (run /fabric-plugin:setup:login)
