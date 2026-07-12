---
name: notebook-definition-update
description: Update notebook definition from .ipynb file
---

# notebook-definition-update Skill

## Purpose
Replace a notebook's definition with the content of a local .ipynb file, with LRO polling until completion.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-definition-update/notebook_definition_update.py" "$@"
```

## Usage

```
notebook_definition_update.py <workspace> <notebook> <ipynb_file>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Notebook **name or GUID** (names are resolved automatically)
- `<ipynb_file>` (required): Path to the local .ipynb file (must be valid JSON)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-definition-update/notebook_definition_update.py" "My Workspace" "Sales Analysis" ./analysis.ipynb
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-definition-update/notebook_definition_update.py" a1b2c3d4-... b2c3d4e5-... ./nb.ipynb
```

## Returns
- Success: Exit code 0, update confirmation
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, file not found/invalid, not found, forbidden, operation failed)
- 2: Retryable error (rate limit, server error, timeout)
- 3: Authentication error (run /fabric-plugin:\setup:login)
