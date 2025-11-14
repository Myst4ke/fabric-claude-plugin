---
description: Create a new Microsoft Fabric workspace
argument-hint: <name> <capacity-id> [--description <text>]
---

# /fabric:create-workspace

## Purpose
Create a new Microsoft Fabric workspace and assign it to a specified capacity. This is a long-running operation that may take several seconds to complete.

## Arguments
- `name`: Required. Display name for the workspace (1-256 characters)
- `capacity-id`: Required. GUID of the capacity to assign the workspace to
- `--description <text>`: Optional. Description for the workspace

## Prerequisites
- Configured credentials with appropriate permissions
- Permission to create workspaces in the tenant
- Access to the target capacity (capacity contributor or admin role)

## Instructions

### 1. Validate Inputs
```bash
workspace_name="$1"
capacity_id="$2"
description=""

if [ -z "$workspace_name" ]; then
  echo "❌ Workspace name is required"
  echo ""
  echo "Usage: /fabric:create-workspace <name> <capacity-id>"
  echo "Example: /fabric:create-workspace \"Analytics Workspace\" cap-abc-123"
  exit 1
fi

if [ -z "$capacity_id" ]; then
  echo "❌ Capacity ID is required"
  echo "To find capacities: /fabric:list-capacities"
  exit 1
fi

# Validate workspace name length
if [ ${#workspace_name} -lt 1 ] || [ ${#workspace_name} -gt 256 ]; then
  echo "❌ Workspace name must be 1-256 characters (current: ${#workspace_name})"
  exit 1
fi

# Validate capacity ID format
if ! [[ "$capacity_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid capacity ID format (must be GUID)"
  exit 1
fi
```

### 2. Authenticate and Create
```bash
echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🏗️  Creating workspace: $workspace_name"

request_body=$(jq -n \
  --arg name "$workspace_name" \
  --arg cap "$capacity_id" \
  '{displayName: $name, capacityId: $cap}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)
```

### 3. Handle Long-Running Operation
```bash
if [ "$http_code" = "202" ]; then
  echo "⏳ Creation in progress..."
  # Use lro-handler skill for polling
  operation_id=$(extract_operation_id_from_headers)
  lro_handler_poll "$operation_id"
  echo "✅ Workspace created successfully!"
elif [ "$http_code" = "201" ]; then
  workspace_id=$(echo "$response_body" | jq -r '.id')
  echo "✅ Workspace created: $workspace_id"
else
  echo "❌ Failed (HTTP $http_code)"
  handle_error "$response_body"
  exit 1
fi
```

## Related Commands
- `/fabric:list-workspaces` - List all workspaces
- `/fabric:delete-workspace <id>` - Delete workspace
- `/fabric:add-user <workspace-id> <email> <role>` - Add user

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces`
- **Response**: 202 Accepted (LRO) or 201 Created
