---
name: environment-staging
description: Get or modify the staging area of an environment (pending library changes)
---

# environment-staging Skill

## Purpose
Show the staging area of an environment: pending library and Spark compute changes that will be applied on next publish.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-staging/environment_staging.py" "$@"
```

## Usage

```
environment_staging.py <workspace> <environment>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<environment>` (required): Environment **name or GUID**

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-staging/environment_staging.py" "My Workspace" "ML Environment"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-staging/environment_staging.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, pending library changes + staged Spark compute settings
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
