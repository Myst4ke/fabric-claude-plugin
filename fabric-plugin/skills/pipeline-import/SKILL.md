---
name: pipeline-import
description: Import a data pipeline from a local definition file
---

# pipeline-import Skill

## Purpose
Import a pipeline from a local JSON definition file (create + upload base64-encoded definition), with LRO polling handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-import/pipeline_import.py" "$@"
```

## Usage

```
pipeline_import.py <workspace> <name> <definition_file>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): Display name for the new pipeline
- `<definition_file>` (required): Local path to the JSON definition file

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-import/pipeline_import.py" "My Workspace" "Daily ETL" ./pipeline.json
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-import/pipeline_import.py" a1b2c3d4-... "New Pipeline" ./export/pipeline.json
```

## Returns
- Success: Exit code 0, import summary (name, pipeline ID, workspace)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, file not found, forbidden, name conflict)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
