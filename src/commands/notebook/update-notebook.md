---
description: Update notebook metadata (name and/or description)
argument-hint: <workspace-id> <notebook-id> [--name <new-name>] [--description <desc>]
---

# /fabric:update-notebook

## Purpose
Update a notebook's display name and/or description. For updating notebook cells/code, use `/fabric:update-notebook-definition`.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `notebook-id`: Required. GUID of the notebook
- `--name <new-name>`: Optional. New display name
- `--description <desc>`: Optional. New description

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"
new_name=""
new_description=""

# Parse optional arguments
shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --name)
      new_name="$2"
      shift 2
      ;;
    --description)
      new_description="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:update-notebook <workspace-id> <notebook-id> [--name <new-name>] [--description <desc>]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$notebook_id" ]; then
  echo "❌ Workspace ID and notebook ID are required"
  echo "Usage: /fabric:update-notebook <workspace-id> <notebook-id> [--name <new-name>] [--description <desc>]"
  exit 1
fi

# Validate at least one update field
if [ -z "$new_name" ] && [ -z "$new_description" ]; then
  echo "❌ At least one field (--name or --description) must be specified"
  echo "Usage: /fabric:update-notebook <workspace-id> <notebook-id> [--name <new-name>] [--description <desc>]"
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

# Validate name length if provided
if [ -n "$new_name" ] && ([ ${#new_name} -lt 1 ] || [ ${#new_name} -gt 256 ]); then
  echo "❌ Notebook name must be between 1 and 256 characters"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📓 Updating notebook..."

# Build request body with only specified fields
request_body="{"
first_field=true

if [ -n "$new_name" ]; then
  request_body="$request_body\"displayName\":\"$new_name\""
  first_field=false
fi

if [ -n "$new_description" ]; then
  if [ "$first_field" = false ]; then
    request_body="$request_body,"
  fi
  request_body="$request_body\"description\":\"$new_description\""
fi

request_body="$request_body}"

response=$(curl -s -w "\n%{http_code}" -X PATCH \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$notebook_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  echo "✅ Notebook updated successfully"
  echo ""
  echo "╔═══════════════════════════════════════════════════════════╗"
  echo "║              NOTEBOOK UPDATED                             ║"
  echo "╚═══════════════════════════════════════════════════════════╝"
  echo ""

  if [ -n "$new_name" ]; then
    echo "New Name: $new_name"
  fi

  if [ -n "$new_description" ]; then
    echo "New Description: $new_description"
  fi

  echo ""
  echo "Notebook ID:  $notebook_id"
  echo "Workspace ID: $workspace_id"
  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo ""
  echo "💡 Next steps:"
  echo "  • View changes: /fabric:get-notebook $workspace_id $notebook_id"
  echo "  • Update code: /fabric:update-notebook-definition $workspace_id $notebook_id <file>"
  echo "  • Execute: /fabric:run-notebook $workspace_id $notebook_id"

else
  echo "❌ Failed to update notebook (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Use Cases

### Update Name Only
```bash
# Rename notebook
/fabric:update-notebook <workspace-id> <notebook-id> \
  --name "New Notebook Name"
```

### Update Description Only
```bash
# Update description
/fabric:update-notebook <workspace-id> <notebook-id> \
  --description "Updated description with more details"
```

### Update Both
```bash
# Update name and description
/fabric:update-notebook <workspace-id> <notebook-id> \
  --name "Quarterly Sales Analysis" \
  --description "Q1 2024 sales data analysis and forecasting"
```

### Standardize Naming
```bash
# Batch rename notebooks with consistent naming
notebook_ids=$(/fabric:list-notebooks <ws-id> --format json | jq -r '.[].id')

counter=1
for notebook_id in $notebook_ids; do
  /fabric:update-notebook <ws-id> $notebook_id \
    --name "Notebook_$(printf '%03d' $counter)"
  counter=$((counter + 1))
done
```

## Output Example

```
✅ Notebook updated successfully

╔═══════════════════════════════════════════════════════════╗
║              NOTEBOOK UPDATED                             ║
╚═══════════════════════════════════════════════════════════╝

New Name: Quarterly Sales Analysis
New Description: Q1 2024 sales data analysis and forecasting

Notebook ID:  abc123-def456-ghi789
Workspace ID: workspace-abc123-def456

═══════════════════════════════════════════════════════════

💡 Next steps:
  • View changes: /fabric:get-notebook workspace-id notebook-id
  ...
```

## Update Scope

**This Command Updates:**
- Display name
- Description

**This Command Does NOT Update:**
- Notebook cells/code
- Cell outputs
- Notebook configuration
- Execution settings

**For Code Updates, Use:**
- `/fabric:update-notebook-definition <workspace-id> <notebook-id> <file>`

## Related Commands
- `/fabric:get-notebook <workspace-id> <notebook-id>` - View current metadata
- `/fabric:update-notebook-definition <workspace-id> <notebook-id>` - Update code/cells
- `/fabric:list-notebooks <workspace-id>` - List all notebooks
- `/fabric:delete-notebook <workspace-id> <notebook-id>` - Delete notebook

## API Reference
- **Endpoint**: `PATCH https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}`
- **Response**: 200 OK
- **Permissions**: Contributor, Member, or Admin role

## Notes
- Updates are applied immediately
- Name length: 1-256 characters
- Description can be empty string to clear
- Partial updates supported (specify only fields to change)
- Does not affect notebook execution or code
- Last modified date is updated automatically
