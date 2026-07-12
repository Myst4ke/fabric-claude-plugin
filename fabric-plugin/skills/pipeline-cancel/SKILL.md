---
name: pipeline-cancel
description: Cancel a running pipeline job
---

# pipeline-cancel Skill

## Purpose
Request cancellation of a running pipeline job instance.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-cancel/pipeline_cancel.py" "$@"
```

## Usage

```
pipeline_cancel.py <workspace> <pipeline> <job_id>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<job_id>` (required): The job instance ID to cancel

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-cancel/pipeline_cancel.py" "My Workspace" "Daily ETL" c3d4e5f6-...
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-cancel/pipeline_cancel.py" a1b2c3d4-... b2c3d4e5-... c3d4e5f6-...
```

## Returns
- Success: Exit code 0, cancellation confirmation
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, job already completed)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
