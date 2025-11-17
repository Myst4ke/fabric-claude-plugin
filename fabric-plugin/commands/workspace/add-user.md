---
description: Add a user to a workspace with specified role
argument-hint: <workspace-id> <email> <role>
---

# /fabric:add-user

## Purpose
Grant a user or group access to a workspace with a specified role.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `email`: Required. Email address or principal name
- `role`: Required. Role to assign (Admin, Member, Contributor, Viewer)

## Prerequisites
- Admin role in the workspace
- Configured credentials

## Instructions

### 1. Validate Inputs
```bash
workspace_id="$1"
email="$2"
role="$3"

if [ -z "$workspace_id" ] || [ -z "$email" ] || [ -z "$role" ]; then
  echo "❌ Missing required arguments"
  echo "Usage: /fabric:add-user <workspace-id> <email> <role>"
  echo "Roles: Admin, Member, Contributor, Viewer"
  exit 1
fi

# Validate role
if [[ ! "$role" =~ ^(Admin|Member|Contributor|Viewer)$ ]]; then
  echo "❌ Invalid role: $role"
  echo "Valid roles: Admin, Member, Contributor, Viewer"
  exit 1
fi
```

### 2. Add User
```bash
echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "👤 Adding user: $email as $role"

request_body=$(jq -n \
  --arg email "$email" \
  --arg role "$role" \
  '{
    principal: {
      type: "User",
      userPrincipalName: $email
    },
    role: $role
  }')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/roleAssignments" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
  echo "✅ User added successfully"
else
  response_body=$(echo "$response" | head -n-1)
  echo "❌ Failed (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Example Usage
```bash
/fabric:add-user abc-123-def john.doe@example.com Admin
/fabric:add-user abc-123-def jane.smith@example.com Member
```

## Related Commands
- `/fabric:list-users <workspace-id>` - List current users
- `/fabric:remove-user <workspace-id> <user-id>` - Remove user
- `/fabric:update-user-role <workspace-id> <user-id> <role>` - Update role

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/roleAssignments`
- **Permissions**: Admin role required
