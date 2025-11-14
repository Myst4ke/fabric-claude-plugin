---
description: Delete a Microsoft Fabric workspace
argument-hint: <workspace-id> [--force]
---

# /fabric:delete-workspace

## Purpose
Permanently delete a Microsoft Fabric workspace and all its contents. This operation cannot be undone.

## Arguments
- `workspace-id`: Required. GUID of the workspace to delete
- `--force`: Optional. Skip confirmation prompt

## Prerequisites
- Admin role in the workspace
- Configured credentials

## Instructions

### 1. Validate Input
```bash
workspace_id="$1"
force_delete=false

if [ -z "$workspace_id" ]; then
  echo "❌ Workspace ID is required"
  echo "Usage: /fabric:delete-workspace <workspace-id> [--force]"
  exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format"
  exit 1
fi

shift
if [ "$1" = "--force" ]; then
  force_delete=true
fi
```

### 2. Get Workspace Details and Confirm
```bash
echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

# Get workspace details for confirmation
workspace_response=$(curl -s -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

workspace_name=$(echo "$workspace_response" | jq -r '.displayName // "Unknown"')

if [ "$workspace_name" = "Unknown" ]; then
  echo "❌ Workspace not found or access denied"
  exit 1
fi

# Get item count
items_response=$(curl -s -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

item_count=$(echo "$items_response" | jq '.value | length')

# Confirmation prompt
if [ "$force_delete" = false ]; then
  echo ""
  echo "⚠️  WARNING: This will permanently delete the workspace and all its contents!"
  echo ""
  echo "Workspace: $workspace_name"
  echo "ID: $workspace_id"
  echo "Items: $item_count"
  echo ""
  echo "Type 'DELETE' to confirm: "
  read -r confirmation

  if [ "$confirmation" != "DELETE" ]; then
    echo "❌ Deletion cancelled"
    exit 0
  fi
fi
```

### 3. Delete Workspace
```bash
echo ""
echo "🗑️  Deleting workspace: $workspace_name"

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ] || [ "$http_code" = "204" ]; then
  echo "✅ Workspace deleted successfully"
else
  response_body=$(echo "$response" | head -n-1)
  echo "❌ Deletion failed (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Example Usage
```bash
# With confirmation prompt
/fabric:delete-workspace abc-123-def-456

# Skip confirmation
/fabric:delete-workspace abc-123-def-456 --force
```

## Safety Features
- Requires explicit "DELETE" confirmation (unless --force is used)
- Shows workspace name and item count before deletion
- Cannot be undone - workspace and all contents are permanently deleted

## Related Commands
- `/fabric:list-workspaces` - List all workspaces
- `/fabric:get-workspace <id>` - View workspace details before deleting

## API Reference
- **Endpoint**: `DELETE https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}`
- **Response**: 200 OK or 204 No Content
- **Permissions**: Admin role required
