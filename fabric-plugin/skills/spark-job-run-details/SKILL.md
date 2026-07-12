---
name: spark-job-run-details
description: Get run details and status of a Spark job execution
---

# spark-job-run-details Skill

## Purpose
Show run history of a Spark job definition: status, start/end time, duration.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-run-details/spark_job_run_details.py" "$@"
```

## Usage

```
spark_job_run_details.py <workspace> <job>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<job>` (required): Spark job **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-run-details/spark_job_run_details.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-run-details/spark_job_run_details.py" a1b2c3d4-... d4e5f6a7-...
```

## Returns
- Success: Exit code 0, run history table (last 20 runs, failure reasons shown)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
