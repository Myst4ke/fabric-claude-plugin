---
name: capacity-metrics
description: Get usage metrics and workload information for a Fabric capacity
---

# capacity-metrics Skill

## Purpose
Get capacity details, assigned workspaces, and workload states for monitoring and cost optimization.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/capacity-metrics/capacity_metrics.py" "$@"
```

## Usage

```
capacity_metrics.py <capacity_id>
```

## Parameters
- `<capacity_id>` (required): Capacity GUID (find with capacity-list)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/capacity-metrics/capacity_metrics.py" a1b2c3d4-e5f6-...
```

## Returns
- Success: Exit code 0, capacity summary + workspaces on capacity + workload states
  (workload details require Capacity Admin access; degrades gracefully)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
