---
description: Get detailed information about a specific Microsoft Fabric workspace
argument-hint: <workspace-id>
---

# /fabric:get-workspace

## Purpose
Retrieve comprehensive details about a specific Microsoft Fabric workspace, including its configuration, capacity assignment, and your permissions.

## Arguments
- `workspace-id`: Required. The GUID identifier of the workspace

## Prerequisites
- Configured credentials
- Access to the specified workspace (any role: Admin, Member, Contributor, or Viewer)

## Instructions

### 1. Validate Input
Check that workspace ID is provided and valid:

```bash
workspace_id="$1"

if [ -z "$workspace_id" ]; then
  echo "❌ Workspace ID is required"
  echo ""
  echo "Usage: /fabric:get-workspace <workspace-id>"
  echo ""
  echo "Example:"
  echo "  /fabric:get-workspace abc-123-def-456-ghi-789-jkl-012"
  echo ""
  echo "To find workspace IDs, run: /fabric:list-workspaces"
  exit 1
fi

# Validate GUID format
if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format"
  echo ""
  echo "Workspace ID must be a GUID (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)"
  echo ""
  echo "Example: abc-123-def-456-ghi-789-jkl-012"
  echo ""
  echo "Run /fabric:list-workspaces to see available workspace IDs"
  exit 1
fi
```

### 2. Authenticate
Use fabric-auth skill to get access token:

```bash
echo "🔐 Authenticating..."

ACCESS_TOKEN=$(fabric_auth_skill)

if [ $? -ne 0 ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Authentication failed"
  echo "Please run /fabric:configure"
  exit 1
fi
```

### 3. Fetch Workspace Details
Make API request to get workspace information:

```bash
echo "📋 Fetching workspace details..."

ENDPOINT="https://api.fabric.microsoft.com/v1/workspaces/${workspace_id}"

response=$(curl -s -w "\n%{http_code}" -X GET "$ENDPOINT" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to get workspace (HTTP $http_code)"
  echo ""

  error_code=$(echo "$response_body" | jq -r '.error.code // "Unknown"')
  error_msg=$(echo "$response_body" | jq -r '.error.message // "No message"')

  echo "Error: $error_code"
  echo "Message: $error_msg"
  echo ""

  case "$http_code" in
    "404")
      echo "Workspace not found. Possible reasons:"
      echo "  • Workspace doesn't exist"
      echo "  • Workspace ID is incorrect"
      echo "  • You don't have access to this workspace"
      echo ""
      echo "Run /fabric:list-workspaces to see accessible workspaces"
      ;;
    "403")
      echo "Access denied to this workspace."
      echo "Ask workspace admin to grant you access."
      ;;
    "401")
      echo "Authentication issue."
      echo "Run /fabric:test-connection to diagnose"
      ;;
  esac

  exit 1
fi
```

### 4. Display Workspace Information
Format and display comprehensive workspace details:

```bash
echo "✅ Workspace retrieved successfully"
echo ""

# Extract key fields
name=$(echo "$response_body" | jq -r '.displayName')
description=$(echo "$response_body" | jq -r '.description // "No description"')
type=$(echo "$response_body" | jq -r '.type // "Workspace"')
capacity_id=$(echo "$response_body" | jq -r '.capacityId // "Not assigned"')

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                       WORKSPACE DETAILS                           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Name:        $name"
echo "ID:          $workspace_id"
echo "Type:        $type"
echo "Description: $description"
echo ""
echo "Capacity:"
echo "  ID:     $capacity_id"

if [ "$capacity_id" != "Not assigned" ]; then
  capacity_status=$(echo "$response_body" | jq -r '.capacityAssignmentProgress // "Active"')
  echo "  Status: $capacity_status"
fi

echo ""
echo "───────────────────────────────────────────────────────────────────"
```

### 5. Fetch Additional Details (Optional)
Get items count and role assignments:

```bash
echo ""
echo "📊 Fetching additional details..."

# Get items count
items_response=$(curl -s -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/${workspace_id}/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

items_count=$(echo "$items_response" | jq '.value | length')

echo ""
echo "Content:"
echo "  Items: $items_count"

if [ "$items_count" -gt 0 ]; then
  # Count by type
  echo ""
  echo "  By type:"
  echo "$items_response" | jq -r '
    .value | group_by(.type) |
    map("    • \(.[0].type): \(length)") | .[]
  '
fi

# Get role assignments (requires admin permissions)
echo ""
echo "Permissions:"

roles_response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/${workspace_id}/roleAssignments" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

roles_http_code=$(echo "$roles_response" | tail -n1)

if [ "$roles_http_code" = "200" ]; then
  roles_body=$(echo "$roles_response" | head -n-1)
  user_count=$(echo "$roles_body" | jq '.value | length')
  echo "  Users with access: $user_count"

  # Show summary by role
  echo "$roles_body" | jq -r '
    .value | group_by(.role) |
    map("    • \(.[0].role): \(length)") | .[]
  '
else
  echo "  (Admin role required to view permissions)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
```

### 6. Provide Next Steps
Suggest relevant actions:

```bash
echo ""
echo "💡 Next steps:"
echo "  • List items: /fabric:list-items $workspace_id"
echo "  • Create lakehouse: /fabric:create-lakehouse $workspace_id <name>"
echo "  • Manage users: /fabric:list-users $workspace_id"
echo ""
```

## Example Output

### Successful Retrieval
```
/fabric:get-workspace abc-123-def-456-ghi-789-jkl-012

🔐 Authenticating...
📋 Fetching workspace details...
✅ Workspace retrieved successfully

╔═══════════════════════════════════════════════════════════════════╗
║                       WORKSPACE DETAILS                           ║
╚═══════════════════════════════════════════════════════════════════╝

Name:        Production Analytics
ID:          abc-123-def-456-ghi-789-jkl-012
Type:        Workspace
Description: Main production workspace for analytics and reporting

Capacity:
  ID:     cap-prod-001
  Status: Active

───────────────────────────────────────────────────────────────────

📊 Fetching additional details...

Content:
  Items: 47

  By type:
    • Lakehouse: 5
    • Notebook: 12
    • DataPipeline: 8
    • SemanticModel: 15
    • Report: 7

Permissions:
  Users with access: 23
    • Admin: 3
    • Member: 8
    • Contributor: 9
    • Viewer: 3

═══════════════════════════════════════════════════════════════════

💡 Next steps:
  • List items: /fabric:list-items abc-123-def-456-ghi-789-jkl-012
  • Create lakehouse: /fabric:create-lakehouse abc-123-def-456-ghi-789-jkl-012 <name>
  • Manage users: /fabric:list-users abc-123-def-456-ghi-789-jkl-012
```

### Non-Admin User (Limited Permissions)
```
/fabric:get-workspace abc-123-def-456-ghi-789-jkl-012

🔐 Authenticating...
📋 Fetching workspace details...
✅ Workspace retrieved successfully

╔═══════════════════════════════════════════════════════════════════╗
║                       WORKSPACE DETAILS                           ║
╚═══════════════════════════════════════════════════════════════════╝

Name:        Dev Workspace
ID:          abc-123-def-456-ghi-789-jkl-012
Type:        Workspace
Description: Development environment

Capacity:
  ID:     cap-dev-001
  Status: Active

───────────────────────────────────────────────────────────────────

📊 Fetching additional details...

Content:
  Items: 12

  By type:
    • Lakehouse: 2
    • Notebook: 6
    • DataPipeline: 4

Permissions:
  (Admin role required to view permissions)

═══════════════════════════════════════════════════════════════════

💡 Next steps:
  • List items: /fabric:list-items abc-123-def-456-ghi-789-jkl-012
  • Create lakehouse: /fabric:create-lakehouse abc-123-def-456-ghi-789-jkl-012 <name>
```

## Error Scenarios

### Scenario 1: Missing Workspace ID
```
/fabric:get-workspace

❌ Workspace ID is required

Usage: /fabric:get-workspace <workspace-id>

Example:
  /fabric:get-workspace abc-123-def-456-ghi-789-jkl-012

To find workspace IDs, run: /fabric:list-workspaces
```

### Scenario 2: Invalid Workspace ID Format
```
/fabric:get-workspace invalid-id

❌ Invalid workspace ID format

Workspace ID must be a GUID (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

Example: abc-123-def-456-ghi-789-jkl-012

Run /fabric:list-workspaces to see available workspace IDs
```

### Scenario 3: Workspace Not Found
```
/fabric:get-workspace abc-000-def-000-ghi-000-jkl-000

🔐 Authenticating...
📋 Fetching workspace details...
❌ Failed to get workspace (HTTP 404)

Error: WorkspaceNotFound
Message: The specified workspace does not exist

Workspace not found. Possible reasons:
  • Workspace doesn't exist
  • Workspace ID is incorrect
  • You don't have access to this workspace

Run /fabric:list-workspaces to see accessible workspaces
```

### Scenario 4: Access Denied
```
/fabric:get-workspace def-456-ghi-789-jkl-012-mno-345

🔐 Authenticating...
📋 Fetching workspace details...
❌ Failed to get workspace (HTTP 403)

Error: Forbidden
Message: Insufficient permissions

Access denied to this workspace.
Ask workspace admin to grant you access.
```

## Performance Considerations
- Typical response time: 200-400ms
- With additional details (items, roles): +400-800ms
- Total time: Usually <1 second

## Related Commands
- `/fabric:list-workspaces` - List all accessible workspaces
- `/fabric:list-items <workspace-id>` - List items in workspace
- `/fabric:list-users <workspace-id>` - List users with access
- `/fabric:create-workspace <name> <capacity-id>` - Create new workspace

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}`
- **Authentication**: Bearer token
- **Response**: Workspace object with metadata
- **Permissions**: Any role (Admin, Member, Contributor, Viewer)

## Testing Checklist
- [ ] Valid workspace ID → Details displayed correctly
- [ ] Invalid ID format → Validation error
- [ ] Workspace not found → 404 with clear message
- [ ] No access → 403 with instructions
- [ ] Admin user → Full details including permissions
- [ ] Non-admin user → Limited details, permissions hidden
- [ ] Empty workspace → Shows 0 items correctly
- [ ] Workspace with many items → All types counted correctly
