---
name: notebook-update
description: Update a notebook's name or description
---

# notebook-update Skill

## Purpose
Update the name and/or description of an existing notebook.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-update/notebook_update.py" "$@"
```

## Usage

```
notebook_update.py <workspace> <notebook> [--name NAME] [--description TEXT]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Notebook **name or GUID** (names are resolved automatically)
- `--name NAME` (optional): New name for the notebook
- `--description TEXT` (optional): New description for the notebook

At least one of `--name` / `--description` is required.

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-update/notebook_update.py" "My Workspace" "Old Name" --name "New Name"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-update/notebook_update.py" a1b2c3d4-... b2c3d4e5-... --description "Updated"
```

## Returns
- Success: Exit code 0, updated notebook details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
