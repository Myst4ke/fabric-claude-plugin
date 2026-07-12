---
name: capacity-get
description: Get detailed information about a Fabric capacity
---

# capacity-get Skill

## Purpose
Get detailed information about a specific Microsoft Fabric capacity (SKU, region, state, admins).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/capacity-get/capacity_get.py" "$@"
```

## Usage

```
capacity_get.py <capacity_id>
```

## Parameters
- `<capacity_id>` (required): Capacity GUID (find with capacity-list)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/capacity-get/capacity_get.py" a1b2c3d4-e5f6-...
```

## Returns
- Success: Exit code 0, formatted capacity details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
