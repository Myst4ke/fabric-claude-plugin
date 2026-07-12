---
name: lakehouse-delete
description: Delete a lakehouse from workspace
---

# lakehouse-delete Skill

## Purpose
Delete a lakehouse permanently (tables, files and metadata). Asks for a typed
name confirmation unless `--force` is used. IRREVERSIBLE.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-delete/lakehouse_delete.py" "$@"
```

## Usage

```
lakehouse_delete.py <workspace> <lakehouse> [--force]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `--force` (optional): Skip the confirmation prompt

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-delete/lakehouse_delete.py" "My Workspace" Bronze
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/lakehouse-delete/lakehouse_delete.py" a1b2c3d4-... b2c3d4e5-... --force
```

## Returns
- Success: Exit code 0, deletion confirmation
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, cancelled)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
