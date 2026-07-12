---
name: spark-job-get
description: Get detailed information about a Spark job definition
---

# spark-job-get Skill

## Purpose
Get details of a Spark job definition: name, ID, description, root path, dates.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-get/spark_job_get.py" "$@"
```

## Usage

```
spark_job_get.py <workspace> <job>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<job>` (required): Spark job **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-get/spark_job_get.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-get/spark_job_get.py" a1b2c3d4-... d4e5f6a7-...
```

## Returns
- Success: Exit code 0, formatted Spark job details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
