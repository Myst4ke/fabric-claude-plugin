---
name: notebook-create
description: Create a new notebook in a Microsoft Fabric workspace
---

# notebook-create Skill

## Purpose
Create a new (empty) notebook in a workspace, with LRO polling until creation completes.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-create/notebook_create.py" "$@"
```

## Usage

```
notebook_create.py <workspace> <name> [--description TEXT]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): Name for the new notebook (taken as-is, no resolution)
- `--description TEXT` (optional): Description for the new notebook

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-create/notebook_create.py" "My Workspace" "Sales Analysis"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-create/notebook_create.py" a1b2c3d4-... "ETL" --description "Daily ETL"
```

## Returns
- Success: Exit code 0, new notebook ID
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, operation failed)
- 2: Retryable error (rate limit, server error, timeout)
- 3: Authentication error (run /fabric-plugin:setup:login)
