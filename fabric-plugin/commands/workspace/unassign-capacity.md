---
description: Remove capacity assignment from a workspace
argument-hint: <workspace-id>
---

# /fabric:unassign-capacity

## Purpose
Remove the capacity assignment from a workspace, moving it back to shared capacity or unassigned state.

## Arguments
- `workspace-id`: Required. GUID of the workspace

## Prerequisites
- Admin role in the workspace
- Capacity permissions on the currently assigned capacity

## Instructions

```bash
workspace_id="$1"

if [ -z "$workspace_id" ]; then
  echo "❌ Workspace ID is required"
  echo "Usage: /fabric:unassign-capacity <workspace-id>"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🔓 Unassigning workspace from capacity..."

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/unassignFromCapacity" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
  echo "✅ Workspace unassigned from capacity successfully"
else
  response_body=$(echo "$response" | head -n-1)
  echo "❌ Failed (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Related Commands
- `/fabric:assign-capacity <workspace-id> <capacity-id>` - Assign to capacity
- `/fabric:get-workspace <workspace-id>` - View current capacity assignment

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/unassignFromCapacity`
- **Permissions**: Admin role + capacity permissions
