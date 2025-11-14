---
description: Get detailed information about a data pipeline
argument-hint: <workspace-id> <pipeline-id>
---

# /fabric:get-pipeline

## Purpose
Retrieve comprehensive details about a specific data pipeline including metadata and configuration.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline

## Prerequisites
- Access to the workspace
- Configured credentials

## Instructions

### 1. Validate and Fetch
```bash
workspace_id="$1"
pipeline_id="$2"

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ]; then
  echo "❌ Both workspace ID and pipeline ID are required"
  echo "Usage: /fabric:get-pipeline <workspace-id> <pipeline-id>"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📋 Fetching pipeline details..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to get pipeline (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

### 2. Display Details
```bash
name=$(echo "$response_body" | jq -r '.displayName')
description=$(echo "$response_body" | jq -r '.description // "No description"')
type=$(echo "$response_body" | jq -r '.type')

echo "✅ Pipeline retrieved successfully"
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║               DATA PIPELINE DETAILS                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Name:        $name"
echo "ID:          $pipeline_id"
echo "Type:        $type"
echo "Description: $description"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "💡 Next steps:"
echo "  • Run pipeline: /fabric:run-pipeline $workspace_id $pipeline_id"
echo "  • View history: /fabric:get-run-history $workspace_id $pipeline_id"
echo "  • Get definition: /fabric:get-definition $workspace_id $pipeline_id"
echo "  • Create schedule: /fabric:create-schedule $workspace_id $pipeline_id"
```

## Related Commands
- `/fabric:list-pipelines <workspace-id>` - List all pipelines
- `/fabric:run-pipeline <workspace-id> <pipeline-id>` - Execute pipeline
- `/fabric:delete-pipeline <workspace-id> <pipeline-id>` - Delete pipeline

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}`
- **Permissions**: Any workspace role
