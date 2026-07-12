---
name: environment-create
description: Create a new environment (Spark/Python configuration) in a workspace
---

# environment-create Skill

## Purpose
Create a new environment in a workspace (LRO polled automatically on 202).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-create/environment_create.py" "$@"
```

## Usage

```
environment_create.py <workspace> <name> [description]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): Display name for the new environment
- `[description]` (optional): Description for the environment

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-create/environment_create.py" "My Workspace" "ML Environment"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-create/environment_create.py" a1b2c3d4-... "Data Science" "Python ML libraries"
```

## Returns
- Success: Exit code 0, created environment name + ID
- Error: Exit code 1-3, error message (1 if an environment with this name already exists)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, duplicate name)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
