---
name: notebook-clone
description: Clone an existing notebook
---

# notebook-clone Skill

## Purpose
Clone a notebook in 3 steps (get definition + create + apply definition), with LRO polling per step.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-clone/notebook_clone.py" "$@"
```

## Usage

```
notebook_clone.py <workspace> <notebook> <new_name>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Source notebook **name or GUID** (names are resolved automatically)
- `<new_name>` (required): Display name for the cloned notebook (taken as-is, no resolution)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-clone/notebook_clone.py" "My Workspace" "Sales Analysis" "Sales Analysis Copy"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-clone/notebook_clone.py" a1b2c3d4-... b2c3d4e5-... "Clone"
```

## Returns
- Success: Exit code 0, clone name and ID
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, step failed)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
