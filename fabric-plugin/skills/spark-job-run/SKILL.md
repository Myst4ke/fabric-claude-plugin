---
name: spark-job-run
description: Run a Spark job definition
---

# spark-job-run Skill

## Purpose
Trigger execution of a Spark job definition (asynchronous, returns immediately).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-run/spark_job_run.py" "$@"
```

## Usage

```
spark_job_run.py <workspace> <job>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<job>` (required): Spark job **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-run/spark_job_run.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-run/spark_job_run.py" a1b2c3d4-... d4e5f6a7-...
```

## Returns
- Success: Exit code 0, job started (request ID + monitor URL)
- Error: Exit code 1-3, error message (1 if already running)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, already running, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
