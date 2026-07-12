---
name: notebook-cell-results
description: Get cell execution results from a notebook run
---

# notebook-cell-results Skill

## Purpose
Display cell-level outputs (when available) from a notebook run, plus the raw run JSON.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-cell-results/notebook_cell_results.py" "$@"
```

## Usage

```
notebook_cell_results.py <workspace> <notebook> <job_id>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Notebook **name or GUID** (names are resolved automatically)
- `<job_id>` (required): The job instance ID

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-cell-results/notebook_cell_results.py" "My Workspace" "Sales Analysis" c3d4e5f6-...
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-cell-results/notebook_cell_results.py" a1b2c3d4-... b2c3d4e5-... c3d4e5f6-...
```

## Returns
- Success: Exit code 0, cell outputs (if available) + failure reason + raw JSON
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
