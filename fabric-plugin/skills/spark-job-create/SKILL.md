---
name: spark-job-create
description: Create a new Spark job definition in a workspace
---

# spark-job-create Skill

## Purpose
Create a Spark job definition (long-running operation polled automatically).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-create/spark_job_create.py" "$@"
```

## Usage

```
spark_job_create.py <workspace> <name> [description]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): Spark job display name
- `[description]` (optional): Job description

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-create/spark_job_create.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/spark-job-create/spark_job_create.py" a1b2c3d4-... "Daily ETL" "Nightly data load"
```

## Returns
- Success: Exit code 0, created job name + ID
- Error: Exit code 1-3, error message (1 on name conflict)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, conflict, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
