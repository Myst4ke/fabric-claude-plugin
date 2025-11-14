---
description: Assign a workspace to a capacity
argument-hint: <workspace-id> <capacity-id>
---

# /fabric:assign-capacity

## Purpose
Assign a workspace to a specific Microsoft Fabric capacity.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `capacity-id`: Required. GUID of the target capacity

## Prerequisites
- Admin or Member role in the workspace
- Capacity contributor or admin permissions on the target capacity

## Instructions

```bash
workspace_id="$1"
capacity_id="$2"

if [ -z "$workspace_id" ] || [ -z "$capacity_id" ]; then
  echo "❌ Missing required arguments"
  echo "Usage: /fabric:assign-capacity <workspace-id> <capacity-id>"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🔗 Assigning workspace to capacity..."

request_body=$(jq -n --arg cap "$capacity_id" '{capacityId: $cap}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/assignToCapacity" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
  echo "✅ Workspace assigned to capacity successfully"
else
  response_body=$(echo "$response" | head -n-1)
  echo "❌ Failed (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Related Commands
- `/fabric:unassign-capacity <workspace-id>` - Remove capacity assignment
- `/fabric:list-capacities` - View available capacities

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/assignToCapacity`
- **Permissions**: Admin/Member role + capacity contributor permissions
