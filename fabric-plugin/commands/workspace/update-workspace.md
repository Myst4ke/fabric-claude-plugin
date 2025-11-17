---
description: Update Microsoft Fabric workspace properties
argument-hint: <workspace-id> [--name <name>] [--description <text>]
---

# /fabric:update-workspace

## Purpose
Update properties of an existing Microsoft Fabric workspace, such as display name or description.

## Arguments
- `workspace-id`: Required. GUID of the workspace to update
- `--name <name>`: Optional. New display name for the workspace
- `--description <text>`: Optional. New description for the workspace

**Note**: At least one optional argument (--name or --description) must be provided.

## Prerequisites
- Admin or Member role in the workspace
- Configured credentials

## Instructions

### 1. Parse and Validate Inputs
```bash
workspace_id="$1"
new_name=""
new_description=""

if [ -z "$workspace_id" ]; then
  echo "❌ Workspace ID is required"
  echo "Usage: /fabric:update-workspace <workspace-id> [--name <name>] [--description <text>]"
  exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format"
  exit 1
fi

shift
while [ "$#" -gt 0 ]; do
  case "$1" in
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
      exit 1
      ;;
  esac
done

if [ -z "$new_name" ] && [ -z "$new_description" ]; then
  echo "❌ At least one property must be specified (--name or --description)"
  exit 1
fi
```

### 2. Build Update Request
```bash
echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📝 Updating workspace..."

# Build JSON with only specified fields
request_body=$(jq -n \
  --arg name "$new_name" \
  --arg desc "$new_description" \
  '{}
  | if $name != "" then . + {displayName: $name} else . end
  | if $desc != "" then . + {description: $desc} else . end')
```

### 3. Execute Update
```bash
response=$(curl -s -w "\n%{http_code}" -X PATCH \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  echo "✅ Workspace updated successfully"
  echo ""
  if [ -n "$new_name" ]; then
    echo "  New name: $new_name"
  fi
  if [ -n "$new_description" ]; then
    echo "  New description: $new_description"
  fi
else
  echo "❌ Update failed (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Example Usage
```bash
# Update name only
/fabric:update-workspace abc-123-def --name "New Analytics Workspace"

# Update description only
/fabric:update-workspace abc-123-def --description "Updated production environment"

# Update both
/fabric:update-workspace abc-123-def --name "Analytics" --description "Main workspace"
```

## Related Commands
- `/fabric:get-workspace <id>` - View workspace details
- `/fabric:list-workspaces` - List all workspaces

## API Reference
- **Endpoint**: `PATCH https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}`
- **Response**: 200 OK
- **Permissions**: Admin or Member role required
