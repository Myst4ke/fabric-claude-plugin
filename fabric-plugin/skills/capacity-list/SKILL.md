---
name: capacity-list
description: List all Fabric capacities accessible to the user
---

# capacity-list Skill

## Purpose
List all Microsoft Fabric capacities accessible to the authenticated user, with pagination handled automatically.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/capacity-list/capacity_list.py" "$@"
```

## Usage

```
capacity_list.py [--limit N]
```

## Parameters
- `--limit N` (optional): Maximum number of capacities to return

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/capacity-list/capacity_list.py"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/capacity-list/capacity_list.py" --limit 5
```

## Returns
- Success: Exit code 0, formatted table (name, ID, SKU, region, state)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
