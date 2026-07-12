---
name: pipeline-run-details
description: Get detailed information about a pipeline run
---

# pipeline-run-details Skill

## Purpose
Get status, timing, duration and failure details of a specific pipeline run.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-run-details/pipeline_run_details.py" "$@"
```

## Usage

```
pipeline_run_details.py <workspace> <pipeline> <job_id>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<job_id>` (required): The job instance ID

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-run-details/pipeline_run_details.py" "My Workspace" "Daily ETL" c3d4e5f6-...
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-run-details/pipeline_run_details.py" a1b2c3d4-... b2c3d4e5-... c3d4e5f6-...
```

## Returns
- Success: Exit code 0, run details (status, timing, duration) + raw JSON
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
