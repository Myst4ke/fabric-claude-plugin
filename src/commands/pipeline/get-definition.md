---
description: Get pipeline JSON definition
argument-hint: <workspace-id> <pipeline-id> [--output <file>]
---

# /fabric:get-definition

## Purpose
Retrieve the complete JSON definition of a data pipeline for viewing, backup, or version control.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `--output <file>`: Optional. Save definition to file instead of displaying

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
output_file=""

# Parse optional output argument
shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --output)
      output_file="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:get-definition <workspace-id> <pipeline-id> [--output <file>]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ]; then
  echo "❌ Workspace ID and pipeline ID are required"
  echo "Usage: /fabric:get-definition <workspace-id> <pipeline-id> [--output <file>]"
  exit 1
fi

# Validate GUID formats
if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format (must be GUID)"
  exit 1
fi

if ! [[ "$pipeline_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid pipeline ID format (must be GUID)"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📥 Requesting pipeline definition..."

# Initiate getDefinition operation (LRO)
response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/dataPipelines/$pipeline_id/getDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "202" ]; then
  echo "❌ Failed to request definition (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi

# Extract operation details for polling
location=$(echo "$response" | grep -i "^location:" | cut -d' ' -f2 | tr -d '\r')
operation_id=$(echo "$response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')
retry_after=$(echo "$response" | grep -i "^retry-after:" | cut -d' ' -f2 | tr -d '\r')
retry_after=${retry_after:-5}

echo "⏳ Operation initiated (ID: $operation_id)"
echo "   Polling for completion..."

# Poll operation status with exponential backoff
max_attempts=60
attempt=0
sleep_time=$retry_after

while [ $attempt -lt $max_attempts ]; do
  sleep $sleep_time
  attempt=$((attempt + 1))

  status_response=$(curl -s -w "\n%{http_code}" -X GET \
    "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  status_http_code=$(echo "$status_response" | tail -n1)
  status_body=$(echo "$status_response" | head -n-1)

  if [ "$status_http_code" != "200" ]; then
    echo "❌ Failed to check operation status (HTTP $status_http_code)"
    exit 1
  fi

  status=$(echo "$status_body" | jq -r '.status')
  percent=$(echo "$status_body" | jq -r '.percentComplete // 0')

  echo "   Progress: $percent% - $status"

  if [ "$status" = "Succeeded" ]; then
    echo "✅ Definition retrieved successfully"

    # Get the actual definition from the result location
    # The location may be updated in the response
    result_location=$(echo "$status_body" | jq -r '.resourceLocation // empty')
    if [ -z "$result_location" ]; then
      result_location=$location
    fi

    # Fetch the definition content
    definition_response=$(curl -s -w "\n%{http_code}" -X GET \
      "$result_location" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    def_http_code=$(echo "$definition_response" | tail -n1)
    definition=$(echo "$definition_response" | head -n-1)

    if [ "$def_http_code" != "200" ]; then
      echo "❌ Failed to retrieve definition content (HTTP $def_http_code)"
      exit 1
    fi

    # Handle output
    if [ -n "$output_file" ]; then
      echo "$definition" | jq '.' > "$output_file"
      echo ""
      echo "📄 Definition saved to: $output_file"
      file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
      echo "   Size: $file_size bytes"
    else
      echo ""
      echo "Pipeline Definition:"
      echo "══════════════════════════════════════════════════════════"
      echo "$definition" | jq '.'
      echo "══════════════════════════════════════════════════════════"
    fi

    echo ""
    echo "💡 Next steps:"
    echo "  • Edit definition: /fabric:update-definition $workspace_id $pipeline_id <definition-file>"
    echo "  • Export for backup: /fabric:export-pipeline $workspace_id $pipeline_id"
    echo "  • View pipeline: /fabric:get-pipeline $workspace_id $pipeline_id"

    exit 0
  elif [ "$status" = "Failed" ]; then
    echo "❌ Operation failed"
    error=$(echo "$status_body" | jq -r '.error.message // "Unknown error"')
    echo "Error: $error"
    exit 1
  fi

  # Exponential backoff (5s -> 10s -> 20s -> 30s -> max 60s)
  sleep_time=$((sleep_time < 60 ? sleep_time * 2 : 60))
  if [ $sleep_time -gt 60 ]; then
    sleep_time=60
  fi
done

echo "❌ Operation timed out after $max_attempts attempts"
echo "   Operation ID: $operation_id"
echo "   Check status: /fabric:check-operation $operation_id"
exit 1
```

## Use Cases
1. **Backup:** Export pipeline definitions before making changes
2. **Version Control:** Store definitions in git repositories
3. **Migration:** Copy pipelines between environments
4. **Documentation:** Review pipeline structure and dependencies
5. **Debugging:** Inspect configuration for troubleshooting

## Related Commands
- `/fabric:update-definition <workspace-id> <pipeline-id> <file>` - Update definition
- `/fabric:export-pipeline <workspace-id> <pipeline-id>` - Export with metadata
- `/fabric:clone-pipeline <workspace-id> <pipeline-id>` - Duplicate pipeline

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/dataPipelines/{dataPipelineId}/getDefinition`
- **Response**: 202 Accepted (Long-Running Operation)
- **Permissions**: Any workspace role

## Notes
- This is a long-running operation (LRO) that may take several seconds
- Large pipelines with many activities may take longer to retrieve
- The definition includes complete pipeline JSON with all activities, datasets, and linked services
- Definitions can be large (several MB) for complex pipelines
