---
name: ml-model-create
description: Create a new ML model in a workspace
---

# ml-model-create Skill

## Purpose
Create a new ML model in a workspace (LRO polled automatically on 202).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-model-create/ml_model_create.py" "$@"
```

## Usage

```
ml_model_create.py <workspace> <name> [description]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): Display name for the new ML model
- `[description]` (optional): Description for the ML model

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-model-create/ml_model_create.py" "My Workspace" "Churn Model"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-model-create/ml_model_create.py" a1b2c3d4-... "Forecast" "Sales forecast model"
```

## Returns
- Success: Exit code 0, created model name + ID
- Error: Exit code 1-3, error message (1 if a model with this name already exists)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, duplicate name)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
