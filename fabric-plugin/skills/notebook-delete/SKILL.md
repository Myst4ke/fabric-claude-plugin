---
name: notebook-delete
description: Delete a notebook from a Microsoft Fabric workspace
---

# notebook-delete Skill

## Purpose
Permanently delete a notebook from a workspace.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-delete/notebook_delete.py" "$@"
```

## Usage

```
notebook_delete.py <workspace> <notebook> [--force]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Notebook **name or GUID** (names are resolved automatically)
- `--force` (optional): Skip the confirmation warning

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-delete/notebook_delete.py" "My Workspace" "Old Notebook"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-delete/notebook_delete.py" a1b2c3d4-... b2c3d4e5-... --force
```

## Returns
- Success: Exit code 0, deletion confirmation
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
