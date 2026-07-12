---
name: onelake-list-files
description: List files in OneLake lakehouse storage (ADLS Gen2 compatible API)
---

# onelake-list-files Skill

## Purpose
List files in a lakehouse's OneLake storage using the ADLS Gen2 compatible
API. Read-only operation with audit logging.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/onelake-list-files/onelake_list_files.py" "$@"
```

## Usage

```
onelake_list_files.py <workspace> <lakehouse> [--path PATH]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<lakehouse>` (required): Lakehouse **name or GUID** (names are resolved automatically)
- `--path PATH` (optional): Path to list (default: `/Files`; also accepts `/Tables`)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/onelake-list-files/onelake_list_files.py" "My Workspace" Bronze
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/onelake-list-files/onelake_list_files.py" a1b2c3d4-... b2c3d4e5-... --path "/Files/raw"
```

## Returns
- Success: Exit code 0, directories and files (name, size, last modified)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, path not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
