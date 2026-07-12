---
name: pipeline-diagnose
description: Diagnose a failed pipeline run down to the real notebook/Spark error (drills into per-activity errors the standard logs do not expose)
---

# pipeline-diagnose Skill

## Purpose
Diagnose **why** a Fabric pipeline run failed by drilling into its per-activity
errors. Unlike `pipeline-run-details` / `pipeline-logs` (which only return the
job-instance summary and a top-level, often misleading `failureReason`), this
skill calls the Data Factory activity-runs endpoint and surfaces:

- every activity (including ForEach iterations) with status and duration
- the **real notebook/Spark error** (`ename` / `evalue` / traceback, e.g.
  `LIVY_JOB_TIMED_OUT`) for failed `TridentNotebook` activities
- the failing iteration's **parameters** (e.g. which table)
- the **Spark session id** and a direct **Spark monitor URL**
- a hint when the top-level `failureReason` (a `Fail` activity) is mislabeled

Works for **any** pipeline in **any** workspace.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-diagnose/pipeline_diagnose.py" "$@"
```

## Usage

```
pipeline_diagnose.py <workspace> <pipeline> <job_id> [--raw]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<job_id>` (required): The pipeline run / job instance ID
- `--raw` (optional): Also print the full raw activity-runs JSON

## How it works
1. Reads the run instance (`jobs/instances/{job_id}`) to derive a query time
   window around the run (and a run summary).
2. `POST /workspaces/{ws}/datapipelines/pipelineruns/{job_id}/queryactivityruns`
   with that window, following `continuationToken` pagination.
3. Parses failed `TridentNotebook` activities to extract the embedded Spark/Livy
   error from `output.result.error`, plus `sessionId` and `SparkMonitoringURL`.

## Extracting the run id from a portal URL
A monitoring URL looks like:
`.../pipelines/<pipelineId>/<runId>?experience=power-bi`
The last GUID before `?` is the `<job_id>` (run id); the GUID after `/pipelines/`
is the `<pipeline>`.

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-diagnose/pipeline_diagnose.py" "My Workspace" "Daily ETL" 9bb47f9b-...
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-diagnose/pipeline_diagnose.py" a1b2c3d4-... 57b84c77-... 9bb47f9b-... --raw
```

## Returns
- Success: Exit code 0, activity overview + root-cause diagnosis
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)

## Notes
- The activity-runs history is **time-windowed**; very old runs may return no
  activities even though the run summary still exists.
- A Spark **session death** (`LIVY_JOB_TIMED_OUT`) has no Python traceback or
  failing-cell info in the API — open the printed Spark monitor URL for driver/
  executor logs.
