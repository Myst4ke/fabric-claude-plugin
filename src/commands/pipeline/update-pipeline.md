---
description: Update data pipeline properties
argument-hint: <workspace-id> <pipeline-id> [--name <name>] [--description <text>]
---

# /fabric:update-pipeline

## Purpose
Update properties of an existing data pipeline.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `--name <name>`: Optional. New display name
- `--description <text>`: Optional. New description

**Note**: At least one optional argument must be provided.

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
new_name=""
new_description=""

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ]; then
  echo "❌ Workspace ID and pipeline ID are required"
  echo "Usage: /fabric:update-pipeline <workspace-id> <pipeline-id> [--name <name>] [--description <text>]"
  exit 1
fi

shift 2
while [ "$#" -gt 0 ]; do
  case "$1" in
    --name) new_name="$2"; shift 2 ;;
    --description) new_description="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$new_name" ] && [ -z "$new_description" ]; then
  echo "❌ At least one property must be specified"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📝 Updating pipeline..."

request_body=$(jq -n \
  --arg name "$new_name" \
  --arg desc "$new_description" \
  '{}
  | if $name != "" then . + {displayName: $name} else . end
  | if $desc != "" then . + {description: $desc} else . end')

response=$(curl -s -w "\n%{http_code}" -X PATCH \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
  echo "✅ Pipeline updated successfully"
else
  echo "❌ Update failed (HTTP $http_code)"
  exit 1
fi
```

## API Reference
- **Endpoint**: `PATCH https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}`
- **Permissions**: Member, Contributor, or Admin role
