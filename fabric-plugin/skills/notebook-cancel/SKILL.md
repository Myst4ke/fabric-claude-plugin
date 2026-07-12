---
name: notebook-cancel
description: Cancel a running notebook job
---

# notebook-cancel Skill

## Purpose
Request cancellation of a running notebook job (cancellation may take a moment to complete).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-cancel/notebook_cancel.py" "$@"
```

## Usage

```
notebook_cancel.py <workspace> <notebook> <job_id>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Notebook **name or GUID** (names are resolved automatically)
- `<job_id>` (required): The job instance ID to cancel

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-cancel/notebook_cancel.py" "My Workspace" "Sales Analysis" c3d4e5f6-...
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-cancel/notebook_cancel.py" a1b2c3d4-... b2c3d4e5-... c3d4e5f6-...
```

## Returns
- Success: Exit code 0, cancellation confirmation
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, job already finished)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
