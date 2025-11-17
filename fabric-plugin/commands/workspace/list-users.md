---
description: List users and role assignments for a workspace
argument-hint: <workspace-id>
---

# /fabric:list-users

## Purpose
List all users who have access to a Microsoft Fabric workspace and their assigned roles.

## Arguments
- `workspace-id`: Required. GUID of the workspace

## Prerequisites
- Admin, Member, or Contributor role in the workspace
- Configured credentials

## Instructions

### 1. Validate and Authenticate
```bash
workspace_id="$1"

if [ -z "$workspace_id" ]; then
  echo "❌ Workspace ID is required"
  echo "Usage: /fabric:list-users <workspace-id>"
  exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)
```

### 2. Fetch Role Assignments
```bash
echo "📋 Fetching role assignments..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/roleAssignments" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to get role assignments (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

### 3. Display Results
```bash
user_count=$(echo "$response_body" | jq '.value | length')

echo "✅ Found $user_count user(s) with access"
echo ""

if [ "$user_count" -eq 0 ]; then
  echo "No users found (workspace may have no explicit role assignments)"
  exit 0
fi

echo "Workspace Role Assignments"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Display as table
echo "$response_body" | jq -r '
  ["PRINCIPAL", "TYPE", "ROLE", "ID"],
  ["─────────", "────", "────", "──"],
  (.value[] |
    [
      .principal.displayName // .principal.userPrincipalName // "Unknown",
      .principal.type,
      .role,
      .id[0:16] + "..."
    ]
  )
  | @tsv
' | column -t -s $'\t'

echo ""
echo "═══════════════════════════════════════════════════════════"

# Show summary by role
echo ""
echo "Summary by role:"
echo "$response_body" | jq -r '
  .value | group_by(.role) |
  map("  • \(.[0].role): \(length)") | .[]
'
```

## Example Output
```
/fabric:list-users abc-123-def-456

🔐 Authenticating...
📋 Fetching role assignments...
✅ Found 8 user(s) with access

Workspace Role Assignments
═══════════════════════════════════════════════════════════

PRINCIPAL                TYPE    ROLE          ID
─────────                ────    ────          ──
john.doe@example.com     User    Admin         abc123...
jane.smith@example.com   User    Member        def456...
analytics-team           Group   Contributor   ghi789...
viewer-group             Group   Viewer        jkl012...

═══════════════════════════════════════════════════════════

Summary by role:
  • Admin: 2
  • Member: 3
  • Contributor: 2
  • Viewer: 1
```

## Related Commands
- `/fabric:add-user <workspace-id> <email> <role>` - Add user
- `/fabric:remove-user <workspace-id> <user-id>` - Remove user
- `/fabric:update-user-role <workspace-id> <user-id> <role>` - Update role

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/roleAssignments`
- **Permissions**: Admin, Member, or Contributor role
