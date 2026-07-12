---
name: lakehouse-list
description: List all lakehouses in a Microsoft Fabric workspace
---

# lakehouse-list Skill

## Purpose
List all lakehouses in a workspace, with pagination handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-list/lakehouse_list.py" "$@"
```

## Usage

```
lakehouse_list.py <workspace> [--limit N]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--limit N` (optional): Maximum number of lakehouses to return

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-list/lakehouse_list.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-list/lakehouse_list.py" a1b2c3d4-e5f6-... --limit 10
```

## Returns
- Success: Exit code 0, formatted table of lakehouses (name + ID)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
