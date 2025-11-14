---
description: Update a user's role in a workspace
argument-hint: <workspace-id> <role-assignment-id> <new-role>
---

# /fabric:update-user-role

## Purpose
Change a user's role assignment in a workspace.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `role-assignment-id`: Required. ID of the role assignment to update
- `new-role`: Required. New role (Admin, Member, Contributor, Viewer)

## Prerequisites
- Admin role in the workspace
- Use `/fabric:list-users` to find role assignment IDs

## Instructions

```bash
workspace_id="$1"
role_assignment_id="$2"
new_role="$3"

if [ -z "$workspace_id" ] || [ -z "$role_assignment_id" ] || [ -z "$new_role" ]; then
  echo "❌ Missing required arguments"
  echo "Usage: /fabric:update-user-role <workspace-id> <role-assignment-id> <new-role>"
  echo "Roles: Admin, Member, Contributor, Viewer"
  exit 1
fi

if [[ ! "$new_role" =~ ^(Admin|Member|Contributor|Viewer)$ ]]; then
  echo "❌ Invalid role: $new_role"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📝 Updating role to: $new_role"

request_body=$(jq -n --arg role "$new_role" '{role: $role}')

response=$(curl -s -w "\n%{http_code}" -X PATCH \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/roleAssignments/$role_assignment_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
  echo "✅ Role updated successfully"
else
  echo "❌ Failed (HTTP $http_code)"
  exit 1
fi
```

## API Reference
- **Endpoint**: `PATCH https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/roleAssignments/{roleAssignmentId}`
- **Permissions**: Admin role required
