---
name: lakehouse-get
description: Get detailed information about a specific lakehouse
---

# lakehouse-get Skill

## Purpose
Get details (name, ID, type, description, workspace) of a lakehouse.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-get/lakehouse_get.py" "$@"
```

## Usage

```
lakehouse_get.py <workspace> <lakehouse>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-get/lakehouse_get.py" "My Workspace" Bronze
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-get/lakehouse_get.py" a1b2c3d4-e5f6-... b2c3d4e5-f6a7-...
```

## Returns
- Success: Exit code 0, formatted lakehouse details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
