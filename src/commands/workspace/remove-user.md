---
description: Remove a user from a workspace
argument-hint: <workspace-id> <role-assignment-id>
---

# /fabric:remove-user

## Purpose
Remove a user's access to a workspace by deleting their role assignment.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `role-assignment-id`: Required. ID of the role assignment to remove

## Prerequisites
- Admin role in the workspace
- Use `/fabric:list-users` to find role assignment IDs

## Instructions

```bash
workspace_id="$1"
role_assignment_id="$2"

if [ -z "$workspace_id" ] || [ -z "$role_assignment_id" ]; then
  echo "❌ Missing required arguments"
  echo "Usage: /fabric:remove-user <workspace-id> <role-assignment-id>"
  echo ""
  echo "To find role assignment IDs, run: /fabric:list-users <workspace-id>"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🗑️  Removing user access..."

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/roleAssignments/$role_assignment_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ] || [ "$http_code" = "204" ]; then
  echo "✅ User removed successfully"
else
  echo "❌ Failed (HTTP $http_code)"
  exit 1
fi
```

## API Reference
- **Endpoint**: `DELETE https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/roleAssignments/{roleAssignmentId}`
- **Permissions**: Admin role required
