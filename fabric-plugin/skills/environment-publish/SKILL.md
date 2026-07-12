---
name: environment-publish
description: Publish pending staging changes to an environment
---

# environment-publish Skill

## Purpose
Publish pending staging changes (libraries, Spark config) to an environment. Long-running operation (library install), polled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-publish/environment_publish.py" "$@"
```

## Usage

```
environment_publish.py <workspace> <environment>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<environment>` (required): Environment **name or GUID**

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-publish/environment_publish.py" "My Workspace" "ML Environment"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-publish/environment_publish.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, publish confirmation (can take several minutes)
- Error: Exit code 1-3, error message (1 if a publish is already in progress)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, publish in progress)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
