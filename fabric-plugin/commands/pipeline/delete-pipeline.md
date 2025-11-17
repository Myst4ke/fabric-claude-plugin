---
description: Delete a data pipeline
argument-hint: <workspace-id> <pipeline-id> [--force]
---

# /fabric:delete-pipeline

## Purpose
Permanently delete a data pipeline. This operation cannot be undone.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `--force`: Optional. Skip confirmation prompt

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
force_delete=false

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ]; then
  echo "❌ Workspace ID and pipeline ID are required"
  echo "Usage: /fabric:delete-pipeline <workspace-id> <pipeline-id> [--force]"
  exit 1
fi

shift 2
if [ "$1" = "--force" ]; then
  force_delete=true
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

# Get pipeline name for confirmation
pipeline_response=$(curl -s -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

pipeline_name=$(echo "$pipeline_response" | jq -r '.displayName // "Unknown"')

if [ "$force_delete" = false ]; then
  echo ""
  echo "⚠️  WARNING: This will permanently delete the pipeline!"
  echo ""
  echo "Pipeline: $pipeline_name"
  echo "ID: $pipeline_id"
  echo ""
  echo "Type 'DELETE' to confirm: "
  read -r confirmation

  if [ "$confirmation" != "DELETE" ]; then
    echo "❌ Deletion cancelled"
    exit 0
  fi
fi

echo ""
echo "🗑️  Deleting pipeline: $pipeline_name"

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ] || [ "$http_code" = "204" ]; then
  echo "✅ Pipeline deleted successfully"
else
  echo "❌ Deletion failed (HTTP $http_code)"
  exit 1
fi
```

## API Reference
- **Endpoint**: `DELETE https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}`
- **Permissions**: Admin role required
