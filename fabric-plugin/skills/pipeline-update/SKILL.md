---
name: pipeline-update
description: Update a data pipeline's name or description
---

# pipeline-update Skill

## Purpose
Update a data pipeline's display name and/or description.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-update/pipeline_update.py" "$@"
```

## Usage

```
pipeline_update.py <workspace> <pipeline> [--name NAME] [--description TEXT]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `--name NAME` (optional): New name for the pipeline
- `--description TEXT` (optional): New description for the pipeline

At least one of `--name` or `--description` is required.

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-update/pipeline_update.py" "My Workspace" "Daily ETL" --name "Daily ETL v2"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-update/pipeline_update.py" a1b2c3d4-... b2c3d4e5-... --description "Updated"
```

## Returns
- Success: Exit code 0, updated pipeline details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, name conflict)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
