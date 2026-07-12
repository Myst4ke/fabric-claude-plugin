---
name: pipeline-export
description: Export a data pipeline definition to a local file
---

# pipeline-export Skill

## Purpose
Export a pipeline definition to a local JSON file (decodes the base64 payload and pretty-prints it).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-export/pipeline_export.py" "$@"
```

## Usage

```
pipeline_export.py <workspace> <pipeline> <output_file>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<output_file>` (required): Local path to save the exported JSON definition

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-export/pipeline_export.py" "My Workspace" "Daily ETL" ./pipeline.json
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-export/pipeline_export.py" a1b2c3d4-... b2c3d4e5-... ./export/pipeline.json
```

## Returns
- Success: Exit code 0, output file path and size
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, save failure)
- 2: Retryable error (rate limit, server error, LRO still in progress)
- 3: Authentication error (run /fabric-plugin:\setup:login)
