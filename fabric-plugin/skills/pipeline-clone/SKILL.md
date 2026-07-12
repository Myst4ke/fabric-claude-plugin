---
name: pipeline-clone
description: Clone an existing data pipeline within a workspace
---

# pipeline-clone Skill

## Purpose
Clone a data pipeline (get definition + create + apply definition) within the same workspace, with LRO polling handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-clone/pipeline_clone.py" "$@"
```

## Usage

```
pipeline_clone.py <workspace> <pipeline> <new_name>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Source pipeline **name or GUID** to clone (names are resolved automatically)
- `<new_name>` (required): Display name for the cloned pipeline

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-clone/pipeline_clone.py" "My Workspace" "Daily ETL" "Daily ETL - Copy"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-clone/pipeline_clone.py" a1b2c3d4-... b2c3d4e5-... "Cloned Pipeline"
```

## Returns
- Success: Exit code 0, clone summary (source, clone name, clone ID)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, name conflict)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
