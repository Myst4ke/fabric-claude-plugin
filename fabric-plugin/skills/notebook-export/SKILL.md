---
name: notebook-export
description: Export notebook to .ipynb file
---

# notebook-export Skill

## Purpose
Export a notebook's definition to a local .ipynb file (decodes the definition payload).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-export/notebook_export.py" "$@"
```

## Usage

```
notebook_export.py <workspace> <notebook> <output_file>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Notebook **name or GUID** (names are resolved automatically)
- `<output_file>` (required): Path to save the .ipynb file (directories are created if needed)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-export/notebook_export.py" "My Workspace" "Sales Analysis" ./sales.ipynb
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-export/notebook_export.py" a1b2c3d4-... b2c3d4e5-... ./out/nb.ipynb
```

## Returns
- Success: Exit code 0, output file path and size
- Error: Exit code 1-3, error message (2 if the API answers with a deferred LRO; retry shortly)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, save failure)
- 2: Retryable error (rate limit, server error, deferred LRO)
- 3: Authentication error (run /fabric-plugin:setup:login)
