---
name: pipeline-history
description: Get pipeline execution history
---

# pipeline-history Skill

## Purpose
List the execution history (job instances) of a data pipeline, with pagination handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-history/pipeline_history.py" "$@"
```

## Usage

```
pipeline_history.py <workspace> <pipeline> [--limit N]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `--limit N` (optional): Maximum number of runs to return

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-history/pipeline_history.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-history/pipeline_history.py" a1b2c3d4-... b2c3d4e5-... --limit 10
```

## Returns
- Success: Exit code 0, formatted table of runs (job ID, status, start/end time)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
