---
name: file-delete
description: Delete file from lakehouse storage
---

# file-delete Skill

## Purpose
Delete a file from a lakehouse's OneLake storage (DFS API). IRREVERSIBLE.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-delete/file_delete.py" "$@"
```

## Usage

```
file_delete.py <workspace> <lakehouse> <file_path>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<file_path>` (required): Path to file in lakehouse (e.g. `Files/raw/data.csv`; `Files/` prefix added if missing)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-delete/file_delete.py" "My Workspace" Bronze Files/raw/old.csv
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-delete/file_delete.py" a1b2c3d4-... b2c3d4e5-... Files/tmp/scratch.json
```

## Returns
- Success: Exit code 0, deletion confirmation
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, file not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
