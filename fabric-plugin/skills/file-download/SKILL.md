---
name: file-download
description: Download file from lakehouse storage
---

# file-download Skill

## Purpose
Download a file from a lakehouse's OneLake storage (DFS API) to a local path.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-download/file_download.py" "$@"
```

## Usage

```
file_download.py <workspace> <lakehouse> <file_path> <local_destination>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<file_path>` (required): Path to file in lakehouse (e.g. `Files/data/sales.csv`; `Files/` prefix added if missing)
- `<local_destination>` (required): Local path to save the file (parent folders created automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-download/file_download.py" "My Workspace" Bronze Files/raw/sales.csv ./sales.csv
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-download/file_download.py" a1b2c3d4-... b2c3d4e5-... Files/export.json ./out/export.json
```

## Returns
- Success: Exit code 0, download confirmation with size and local path
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, file not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
