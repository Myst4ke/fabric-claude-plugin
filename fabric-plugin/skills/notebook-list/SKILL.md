---
name: notebook-list
description: List all notebooks in a Microsoft Fabric workspace
---

# notebook-list Skill

## Purpose
List all notebooks in a workspace, with pagination handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-list/notebook_list.py" "$@"
```

## Usage

```
notebook_list.py <workspace> [--limit N]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--limit N` (optional): Maximum number of notebooks to return

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-list/notebook_list.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-list/notebook_list.py" a1b2c3d4-e5f6-... --limit 10
```

## Returns
- Success: Exit code 0, formatted table of notebooks (name + ID)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
