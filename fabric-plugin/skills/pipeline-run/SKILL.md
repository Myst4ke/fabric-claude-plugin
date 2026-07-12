---
name: pipeline-run
description: Execute a data pipeline in Microsoft Fabric
---

# pipeline-run Skill

## Purpose
Start an on-demand execution of a data pipeline. Returns the job ID for status tracking.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-run/pipeline_run.py" "$@"
```

## Usage

```
pipeline_run.py <workspace> <pipeline>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-run/pipeline_run.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-run/pipeline_run.py" a1b2c3d4-e5f6-... b2c3d4e5-f6a7-...
```

## Returns
- Success: Exit code 0, job ID and Location header for status tracking
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
