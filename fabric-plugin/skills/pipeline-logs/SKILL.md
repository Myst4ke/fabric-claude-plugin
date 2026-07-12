---
name: pipeline-logs
description: Get execution logs for a pipeline run
---

# pipeline-logs Skill

## Purpose
Get execution logs (failure reason, error details, activity runs) for a pipeline run.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-logs/pipeline_logs.py" "$@"
```

## Usage

```
pipeline_logs.py <workspace> <pipeline> <job_id>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<job_id>` (required): The job instance ID

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-logs/pipeline_logs.py" "My Workspace" "Daily ETL" c3d4e5f6-...
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-logs/pipeline_logs.py" a1b2c3d4-... b2c3d4e5-... c3d4e5f6-...
```

## Returns
- Success: Exit code 0, log details (failures, errors, activities) + raw JSON
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
