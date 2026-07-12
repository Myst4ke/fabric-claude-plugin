---
name: file-upload
description: Upload file to lakehouse storage
---

# file-upload Skill

## Purpose
Upload a local file to a lakehouse's OneLake storage using the ADLS Gen2
protocol (create + append + flush).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-upload/file_upload.py" "$@"
```

## Usage

```
file_upload.py <workspace> <lakehouse> <local_file> <destination_path>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `<local_file>` (required): Path to local file to upload
- `<destination_path>` (required): Destination path in lakehouse (e.g. `Files/raw/data.csv`; `Files/` prefix added if missing)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-upload/file_upload.py" "My Workspace" Bronze ./data.csv Files/raw/data.csv
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/file-upload/file_upload.py" a1b2c3d4-... b2c3d4e5-... ./report.json reports/report.json
```

## Returns
- Success: Exit code 0, upload confirmation with destination path
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, local file missing, path not found, conflict, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
