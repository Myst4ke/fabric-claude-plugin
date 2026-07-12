---
name: pipeline-get
description: Get detailed information about a data pipeline
---

# pipeline-get Skill

## Purpose
Get detailed information about a data pipeline (name, ID, description, raw JSON).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-get/pipeline_get.py" "$@"
```

## Usage

```
pipeline_get.py <workspace> <pipeline>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-get/pipeline_get.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-get/pipeline_get.py" a1b2c3d4-e5f6-... b2c3d4e5-f6a7-...
```

## Returns
- Success: Exit code 0, pipeline details + raw JSON
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
