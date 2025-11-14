---
description: Update pipeline JSON definition
argument-hint: <workspace-id> <pipeline-id> <definition-file>
---

# /fabric:update-definition

## Purpose
Update a data pipeline's complete JSON definition from a file. Used for programmatic pipeline modifications, CI/CD deployments, or applying exported definitions.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `definition-file`: Required. Path to JSON file containing pipeline definition

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
definition_file="$3"

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ] || [ -z "$definition_file" ]; then
  echo "❌ All arguments are required"
  echo "Usage: /fabric:update-definition <workspace-id> <pipeline-id> <definition-file>"
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

# Validate definition file exists
if [ ! -f "$definition_file" ]; then
  echo "❌ Definition file not found: $definition_file"
  exit 1
fi

# Validate JSON format
if ! jq empty "$definition_file" 2>/dev/null; then
  echo "❌ Invalid JSON in definition file"
  echo "   File: $definition_file"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📤 Uploading pipeline definition..."
echo "   File: $definition_file"

file_size=$(stat -f%z "$definition_file" 2>/dev/null || stat -c%s "$definition_file" 2>/dev/null)
echo "   Size: $file_size bytes"

# Read and prepare definition
definition=$(cat "$definition_file")

# Create request body with definition
request_body=$(jq -n \
  --argjson definition "$definition" \
  '{definition: $definition}')

# Initiate updateDefinition operation (LRO)
response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/dataPipelines/$pipeline_id/updateDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "202" ]; then
  echo "❌ Failed to update definition (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  error_code=$(echo "$response_body" | jq -r '.error.code // ""')
  echo "Error: $error_msg"

  if [ -n "$error_code" ]; then
    echo "Code: $error_code"
  fi

  # Provide helpful hints for common errors
  if [[ "$error_msg" == *"schema"* ]] || [[ "$error_msg" == *"validation"* ]]; then
    echo ""
    echo "💡 Definition validation failed. Common issues:"
    echo "  • Missing required properties"
    echo "  • Invalid activity types or configurations"
    echo "  • Circular dependencies in activities"
    echo "  • Invalid linked service references"
  fi

  exit 1
fi

# Extract operation details for polling
operation_id=$(echo "$response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')
retry_after=$(echo "$response" | grep -i "^retry-after:" | cut -d' ' -f2 | tr -d '\r')
retry_after=${retry_after:-5}

echo "⏳ Update operation initiated (ID: $operation_id)"
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
    echo "✅ Pipeline definition updated successfully"
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║           PIPELINE DEFINITION UPDATED                     ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Pipeline ID: $pipeline_id"
    echo "Workspace:   $workspace_id"
    echo "Source File: $definition_file"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "💡 Next steps:"
    echo "  • Test pipeline: /fabric:run-pipeline $workspace_id $pipeline_id"
    echo "  • View details: /fabric:get-pipeline $workspace_id $pipeline_id"
    echo "  • Get definition: /fabric:get-definition $workspace_id $pipeline_id"
    echo "  • View history: /fabric:get-run-history $workspace_id $pipeline_id"

    exit 0
  elif [ "$status" = "Failed" ]; then
    echo "❌ Update operation failed"
    error=$(echo "$status_body" | jq -r '.error.message // "Unknown error"')
    error_code=$(echo "$status_body" | jq -r '.error.code // ""')

    echo "Error: $error"
    if [ -n "$error_code" ]; then
      echo "Code: $error_code"
    fi

    echo ""
    echo "💡 Troubleshooting tips:"
    echo "  • Verify definition format: jq . $definition_file"
    echo "  • Check for syntax errors in activities"
    echo "  • Ensure all referenced resources exist"
    echo "  • Validate against current pipeline: /fabric:get-definition $workspace_id $pipeline_id"

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
echo ""
echo "💡 The update may still be processing. Check operation status:"
echo "   /fabric:check-operation $operation_id"
exit 1
```

## Use Cases
1. **CI/CD Deployment:** Apply pipeline definitions from version control
2. **Bulk Updates:** Programmatically modify multiple pipelines
3. **Template Application:** Deploy standard pipeline patterns
4. **Configuration Management:** Update pipeline settings across environments
5. **Restore from Backup:** Revert to previous working definition

## Common Validation Errors
- **Missing Required Properties:** Ensure all activities have required fields
- **Invalid References:** Verify linked services and datasets exist
- **Schema Violations:** Check activity types are valid and properly configured
- **Circular Dependencies:** Ensure activity dependencies don't create loops

## Related Commands
- `/fabric:get-definition <workspace-id> <pipeline-id>` - Export current definition
- `/fabric:import-pipeline <workspace-id> <file>` - Create pipeline from definition
- `/fabric:clone-pipeline <workspace-id> <pipeline-id>` - Duplicate pipeline

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/dataPipelines/{dataPipelineId}/updateDefinition`
- **Response**: 202 Accepted (Long-Running Operation)
- **Permissions**: Contributor, Member, or Admin role

## Definition Structure
Pipeline definitions are JSON objects containing:
- **properties**: Pipeline configuration and parameters
- **activities**: Array of pipeline activities (Copy, Execute, etc.)
- **parameters**: Pipeline-level parameters
- **variables**: Pipeline variables
- **annotations**: Metadata tags

Example minimal structure:
```json
{
  "properties": {
    "activities": [
      {
        "name": "CopyActivity1",
        "type": "Copy",
        "inputs": [...],
        "outputs": [...],
        "typeProperties": {...}
      }
    ]
  }
}
```

## Notes
- This is a long-running operation that may take 10-60 seconds
- The entire definition is replaced (not merged)
- Always export current definition before updating for backup
- Validate JSON syntax before attempting update
- Large definitions (>1MB) may take longer to process
- Failed updates don't modify the existing pipeline
