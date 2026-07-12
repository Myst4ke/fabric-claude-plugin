---
name: lakehouse-create
description: Create a new lakehouse in a Microsoft Fabric workspace
---

# lakehouse-create Skill

## Purpose
Create a new lakehouse in a workspace, with LRO polling handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-create/lakehouse_create.py" "$@"
```

## Usage

```
lakehouse_create.py <workspace> <name> [--description TEXT]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): Display name for the new lakehouse
- `--description TEXT` (optional): Description for the lakehouse

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-create/lakehouse_create.py" "My Workspace" Bronze
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-create/lakehouse_create.py" a1b2c3d4-e5f6-... Silver --description "Curated data"
```

## Returns
- Success: Exit code 0, lakehouse name + ID
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, conflict)
- 2: Retryable error (rate limit, server error, LRO timeout)
- 3: Authentication error (run /fabric-plugin:setup:login)
