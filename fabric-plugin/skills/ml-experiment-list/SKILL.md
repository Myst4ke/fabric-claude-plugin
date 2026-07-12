---
name: ml-experiment-list
description: List all ML experiments in a workspace
---

# ml-experiment-list Skill

## Purpose
List all ML experiments in a workspace, with pagination handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-experiment-list/ml_experiment_list.py" "$@"
```

## Usage

```
ml_experiment_list.py <workspace>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-experiment-list/ml_experiment_list.py" "My Workspace"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/ml-experiment-list/ml_experiment_list.py" a1b2c3d4-e5f6-...
```

## Returns
- Success: Exit code 0, formatted table of ML experiments (name + ID + description)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
