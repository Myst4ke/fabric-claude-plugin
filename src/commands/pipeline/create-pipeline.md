---
description: Create a new data pipeline
argument-hint: <workspace-id> <name> [--description <text>]
---

# /fabric:create-pipeline

## Purpose
Create a new data pipeline in a Microsoft Fabric workspace. This is a long-running operation.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `name`: Required. Display name for the pipeline (1-256 characters)
- `--description <text>`: Optional. Description for the pipeline

## Prerequisites
- Member, Contributor, or Admin role in workspace
- Configured credentials

## Instructions

### 1. Validate and Prepare
```bash
workspace_id="$1"
pipeline_name="$2"
description=""

if [ -z "$workspace_id" ] || [ -z "$pipeline_name" ]; then
  echo "❌ Workspace ID and pipeline name are required"
  echo "Usage: /fabric:create-pipeline <workspace-id> <name> [--description <text>]"
  exit 1
fi

shift 2
while [ "$#" -gt 0 ]; do
  case "$1" in
    --description)
      description="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [ ${#pipeline_name} -lt 1 ] || [ ${#pipeline_name} -gt 256 ]; then
  echo "❌ Pipeline name must be 1-256 characters"
  exit 1
fi
```

### 2. Create Pipeline (LRO)
```bash
echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🏗️  Creating pipeline: $pipeline_name"

request_body=$(jq -n \
  --arg name "$pipeline_name" \
  --arg desc "$description" \
  --arg type "DataPipeline" \
  '{displayName: $name, type: $type}
  | if $desc != "" then . + {description: $desc} else . end')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "202" ]; then
  echo "⏳ Pipeline creation in progress..."
  # Use lro-handler skill to poll
  sleep 5
  echo "✅ Pipeline created successfully"
elif [ "$http_code" = "201" ]; then
  pipeline_id=$(echo "$response_body" | jq -r '.id')
  echo "✅ Pipeline created: $pipeline_id"
else
  echo "❌ Failed to create pipeline (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Related Commands
- `/fabric:list-pipelines <workspace-id>` - List all pipelines
- `/fabric:get-pipeline <workspace-id> <pipeline-id>` - View details
- `/fabric:update-definition <workspace-id> <pipeline-id>` - Add activities

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items`
- **Response**: 202 Accepted (LRO) or 201 Created
- **Permissions**: Member, Contributor, or Admin role
