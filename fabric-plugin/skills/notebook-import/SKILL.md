---
name: notebook-import
description: Import notebook from .ipynb file
---

# notebook-import Skill

## Purpose
Create a new notebook in a workspace from a local .ipynb file, with LRO polling until completion.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-import/notebook_import.py" "$@"
```

## Usage

```
notebook_import.py <workspace> <name> <ipynb_file>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): Name for the new notebook (taken as-is, no resolution)
- `<ipynb_file>` (required): Path to the local .ipynb file to import (must be valid JSON)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-import/notebook_import.py" "My Workspace" "Imported NB" ./nb.ipynb
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-import/notebook_import.py" a1b2c3d4-... "ETL" ./etl.ipynb
```

## Returns
- Success: Exit code 0, new notebook name and ID
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, file not found/invalid, forbidden, operation failed)
- 2: Retryable error (rate limit, server error, timeout)
- 3: Authentication error (run /fabric-plugin:setup:login)
