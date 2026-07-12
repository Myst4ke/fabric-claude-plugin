---
name: ml-model-list
description: List all ML models in a workspace
---

# ml-model-list Skill

## Purpose
List all ML models in a workspace, with pagination handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-model-list/ml_model_list.py" "$@"
```

## Usage

```
ml_model_list.py <workspace>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-model-list/ml_model_list.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-model-list/ml_model_list.py" a1b2c3d4-e5f6-...
```

## Returns
- Success: Exit code 0, formatted table of ML models (name + ID + description)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
