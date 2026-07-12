---
name: environment-get
description: Get detailed information about an environment including published libraries
---

# environment-get Skill

## Purpose
Get detailed information about an environment, including Spark compute settings and published libraries.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-get/environment_get.py" "$@"
```

## Usage

```
environment_get.py <workspace> <environment>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<environment>` (required): Environment **name or GUID**

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-get/environment_get.py" "My Workspace" "ML Environment"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/environment-get/environment_get.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, environment details + Spark compute + published libraries
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
