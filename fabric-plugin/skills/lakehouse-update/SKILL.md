---
name: lakehouse-update
description: Update lakehouse name and description
---

# lakehouse-update Skill

## Purpose
Update a lakehouse's display name and/or description.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-update/lakehouse_update.py" "$@"
```

## Usage

```
lakehouse_update.py <workspace> <lakehouse> [--name NAME] [--description TEXT]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `--name NAME` (optional): New display name
- `--description TEXT` (optional): New description

At least one of `--name` or `--description` is required.

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-update/lakehouse_update.py" "My Workspace" Bronze --name Bronze_v2
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-update/lakehouse_update.py" a1b2c3d4-... b2c3d4e5-... --description "Updated"
```

## Returns
- Success: Exit code 0, updated lakehouse details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, conflict)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
