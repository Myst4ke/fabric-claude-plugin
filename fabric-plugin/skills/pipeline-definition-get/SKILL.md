---
name: pipeline-definition-get
description: Get the definition of a data pipeline (decoded JSON)
---

# pipeline-definition-get Skill

## Purpose
Retrieve a pipeline definition; the base64 payload is decoded and pretty-printed.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-definition-get/pipeline_definition_get.py" "$@"
```

## Usage

```
pipeline_definition_get.py <workspace> <pipeline>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-definition-get/pipeline_definition_get.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-definition-get/pipeline_definition_get.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, decoded pipeline definition JSON
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, decode failure)
- 2: Retryable error (rate limit, server error, LRO still in progress)
- 3: Authentication error (run /fabric-plugin:\setup:login)
