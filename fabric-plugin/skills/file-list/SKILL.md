---
name: file-list
description: List files in lakehouse storage
---

# file-list Skill

## Purpose
List files and folders in a lakehouse's OneLake storage (DFS API).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-list/file_list.py" "$@"
```

## Usage

```
file_list.py <workspace> <lakehouse> [--path FOLDER]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `--path FOLDER` (optional): Folder path to list (default: `Files/`; also accepts `Tables`)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-list/file_list.py" "My Workspace" Bronze
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-list/file_list.py" a1b2c3d4-... b2c3d4e5-... --path Files/raw
```

## Returns
- Success: Exit code 0, formatted listing (type, name, size, last modified)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, path not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
