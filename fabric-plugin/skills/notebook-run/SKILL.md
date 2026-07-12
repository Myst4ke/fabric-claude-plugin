---
name: notebook-run
description: Execute a notebook in Microsoft Fabric
---

# notebook-run Skill

## Purpose
Start a notebook execution and return the job ID immediately (fire-and-forget: no status polling).
Use notebook-run-details to check progress.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-run/notebook_run.py" "$@"
```

## Usage

```
notebook_run.py <workspace> <notebook>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Notebook **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-run/notebook_run.py" "My Workspace" "Sales Analysis"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-run/notebook_run.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, job ID of the started run
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success (job started)
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
