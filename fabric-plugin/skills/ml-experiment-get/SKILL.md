---
name: ml-experiment-get
description: Get detailed information about an ML experiment
---

# ml-experiment-get Skill

## Purpose
Get detailed information about an ML experiment (name, ID, description, dates).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-experiment-get/ml_experiment_get.py" "$@"
```

## Usage

```
ml_experiment_get.py <workspace> <mlexperiment>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<mlexperiment>` (required): ML experiment **name or GUID**

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-experiment-get/ml_experiment_get.py" "My Workspace" "Exp 01"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-experiment-get/ml_experiment_get.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, ML experiment details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
