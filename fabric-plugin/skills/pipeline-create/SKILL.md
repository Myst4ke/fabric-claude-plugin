---
name: pipeline-create
description: Create a new data pipeline in a Microsoft Fabric workspace
---

# pipeline-create Skill

## Purpose
Create a new data pipeline in a workspace, with long-running operation (LRO) polling handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-create/pipeline_create.py" "$@"
```

## Usage

```
pipeline_create.py <workspace> <name> [--description TEXT]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): Name for the new pipeline
- `--description TEXT` (optional): Description for the pipeline

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-create/pipeline_create.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-create/pipeline_create.py" a1b2c3d4-e5f6-... "New Pipeline" --description "Ingestion"
```

## Returns
- Success: Exit code 0, created pipeline details (or LRO progress + pipeline ID)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, name conflict)
- 2: Retryable error (rate limit, server error, LRO timeout)
- 3: Authentication error (run /fabric-plugin:setup:login)
