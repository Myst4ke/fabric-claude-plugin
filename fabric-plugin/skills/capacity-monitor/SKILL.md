---
name: capacity-monitor
description: Monitor and analyze Fabric capacity usage and performance
---

# Capacity Monitor Skill

## Purpose
Provide capacity monitoring, usage analysis, and health check capabilities for Microsoft Fabric capacities.

## When to Use
- Before assigning workspaces to capacities
- When analyzing capacity utilization
- When troubleshooting performance issues
- When planning capacity scaling

## Implementation

### Check Capacity Health
```bash
check_capacity_health() {
  local capacity_id="$1"
  local access_token="$2"

  response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/capacities/$capacity_id" \
    -H "Authorization: Bearer $access_token")

  state=$(echo "$response" | jq -r '.state // "Unknown"')

  if [ "$state" = "Active" ]; then
    return 0
  else
    echo "⚠️  Capacity state: $state"
    return 1
  fi
}
```

### Get Capacity Workspace Count
```bash
get_capacity_workspace_count() {
  local capacity_id="$1"
  local access_token="$2"

  response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/capacities/$capacity_id/workspaces" \
    -H "Authorization: Bearer $access_token")

  echo "$response" | jq '.value | length'
}
```

### Validate Capacity Assignment
```bash
validate_capacity_assignment() {
  local workspace_id="$1"
  local capacity_id="$2"
  local access_token="$3"

  # Check capacity exists and is active
  if ! check_capacity_health "$capacity_id" "$access_token"; then
    echo "❌ Capacity is not active or accessible"
    return 1
  fi

  # Check workspace doesn't already have this capacity
  workspace_response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id" \
    -H "Authorization: Bearer $access_token")

  current_capacity=$(echo "$workspace_response" | jq -r '.capacityId // "none"')

  if [ "$current_capacity" = "$capacity_id" ]; then
    echo "ℹ️  Workspace already assigned to this capacity"
    return 2
  fi

  return 0
}
```

## Related Skills
- fabric-auth
- workspace-operations

## API Documentation
- Capacities API: https://learn.microsoft.com/en-us/rest/api/fabric/core/capacities
