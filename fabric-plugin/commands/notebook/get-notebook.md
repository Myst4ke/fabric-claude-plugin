---
description: Get detailed information about a notebook
argument-hint: <workspace-id> <notebook-id>
---

# /fabric:get-notebook

## Purpose
Retrieve detailed information about a specific Fabric notebook including metadata, properties, and workspace context.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `notebook-id`: Required. GUID of the notebook

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"

if [ -z "$workspace_id" ] || [ -z "$notebook_id" ]; then
  echo "❌ Workspace ID and notebook ID are required"
  echo "Usage: /fabric:get-notebook <workspace-id> <notebook-id>"
  exit 1
fi

# Validate GUIDs
if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format (must be GUID)"
  exit 1
fi

if ! [[ "$notebook_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid notebook ID format (must be GUID)"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📓 Fetching notebook details..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$notebook_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to get notebook (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"

  if [ "$http_code" = "404" ]; then
    echo ""
    echo "💡 Notebook may not exist. List notebooks:"
    echo "   /fabric:list-notebooks $workspace_id"
  fi

  exit 1
fi

# Extract notebook details
notebook_name=$(echo "$response_body" | jq -r '.displayName')
notebook_desc=$(echo "$response_body" | jq -r '.description // "No description"')
notebook_type=$(echo "$response_body" | jq -r '.type')
created_date=$(echo "$response_body" | jq -r '.createdDate // "N/A"')
modified_date=$(echo "$response_body" | jq -r '.lastModifiedDate // "N/A"')

echo "✅ Notebook retrieved"
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              NOTEBOOK DETAILS                             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Name:          $notebook_name"
echo "ID:            $notebook_id"
echo "Type:          $notebook_type"
echo "Description:   $notebook_desc"
echo ""
echo "Created:       $created_date"
echo "Last Modified: $modified_date"
echo ""
echo "Workspace ID:  $workspace_id"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "💡 Available operations:"
echo "  • View definition: /fabric:get-notebook-definition $workspace_id $notebook_id"
echo "  • Update name/desc: /fabric:update-notebook $workspace_id $notebook_id"
echo "  • Execute notebook: /fabric:run-notebook $workspace_id $notebook_id"
echo "  • Export notebook: /fabric:export-notebook $workspace_id $notebook_id"
echo "  • Clone notebook: /fabric:clone-notebook $workspace_id $notebook_id \"Copy Name\""
echo "  • Delete notebook: /fabric:delete-notebook $workspace_id $notebook_id"
echo ""
echo "💡 View execution history:"
echo "   /fabric:get-notebook-run-history $workspace_id $notebook_id"
```

## Use Cases

### Before Editing
```bash
# Check notebook details before editing
/fabric:get-notebook <workspace-id> <notebook-id>

# Get full definition for editing
/fabric:get-notebook-definition <workspace-id> <notebook-id>
```

### Verification
```bash
# Verify notebook exists after creation
/fabric:create-notebook <workspace-id> "New Notebook"
# ... note the notebook ID from output
/fabric:get-notebook <workspace-id> <notebook-id>
```

### Metadata Review
```bash
# Check when notebook was last modified
/fabric:get-notebook <workspace-id> <notebook-id> | grep "Last Modified"

# View complete notebook information
/fabric:get-notebook <workspace-id> <notebook-id>
```

## Output Example

```
✅ Notebook retrieved

╔═══════════════════════════════════════════════════════════╗
║              NOTEBOOK DETAILS                             ║
╚═══════════════════════════════════════════════════════════╝

Name:          Sales Analysis Notebook
ID:            abc123-def456-ghi789-jkl012
Type:          Notebook
Description:   Monthly sales data analysis and visualization

Created:       2024-01-10T08:30:00Z
Last Modified: 2024-01-15T14:22:00Z

Workspace ID:  workspace-abc123-def456

═══════════════════════════════════════════════════════════

💡 Available operations:
  • View definition: /fabric:get-notebook-definition workspace-id notebook-id
  • Execute notebook: /fabric:run-notebook workspace-id notebook-id
  ...
```

## Related Commands
- `/fabric:list-notebooks <workspace-id>` - List all notebooks
- `/fabric:get-notebook-definition <workspace-id> <notebook-id>` - Get notebook code/cells
- `/fabric:update-notebook <workspace-id> <notebook-id>` - Update metadata
- `/fabric:run-notebook <workspace-id> <notebook-id>` - Execute notebook
- `/fabric:delete-notebook <workspace-id> <notebook-id>` - Delete notebook

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}`
- **Response**: 200 OK with notebook metadata
- **Permissions**: Any workspace role

## Notes
- Returns metadata only (name, description, dates)
- For notebook cells/code, use `/fabric:get-notebook-definition`
- Created and modified dates are in ISO 8601 format (UTC)
- Notebook must be of type "Notebook"
