---
name: workspace-operations
description: Common workspace CRUD operation patterns and validations
---

# Workspace Operations Skill

## Purpose
Provide reusable patterns for common workspace operations including validation, error handling, and standard workflows.

## When to Use
- Before creating, updating, or deleting workspaces
- When validating workspace IDs or names
- When checking workspace accessibility
- When performing batch workspace operations

## Implementation

### Validate Workspace ID
```bash
validate_workspace_id() {
  local workspace_id="$1"

  if [ -z "$workspace_id" ]; then
    echo "❌ Workspace ID is required"
    return 1
  fi

  if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
    echo "❌ Invalid workspace ID format (must be GUID)"
    return 1
  fi

  return 0
}
```

### Check Workspace Exists
```bash
workspace_exists() {
  local workspace_id="$1"
  local access_token="$2"

  response=$(curl -s -w "\n%{http_code}" -X GET \
    "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id" \
    -H "Authorization: Bearer $access_token")

  http_code=$(echo "$response" | tail -n1)

  if [ "$http_code" = "200" ]; then
    return 0
  else
    return 1
  fi
}
```

### Get Workspace Name
```bash
get_workspace_name() {
  local workspace_id="$1"
  local access_token="$2"

  response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id" \
    -H "Authorization: Bearer $access_token")

  echo "$response" | jq -r '.displayName // "Unknown"'
}
```

### Count Workspace Items
```bash
count_workspace_items() {
  local workspace_id="$1"
  local access_token="$2"

  response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items" \
    -H "Authorization: Bearer $access_token")

  echo "$response" | jq '.value | length'
}
```

## Related Skills
- fabric-auth
- error-handler
- lro-handler

## API Documentation
- Workspaces API: https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces
