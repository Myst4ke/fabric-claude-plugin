---
description: Export pipeline definition with metadata to file
argument-hint: <workspace-id> <pipeline-id> <output-file>
---

# /fabric:export-pipeline

## Purpose
Export a complete pipeline package including definition, metadata, and configuration to a file. Useful for backup, version control, or migration between environments.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `output-file`: Required. Path for exported file (JSON format)

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
output_file="$3"

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ] || [ -z "$output_file" ]; then
  echo "❌ All arguments are required"
  echo "Usage: /fabric:export-pipeline <workspace-id> <pipeline-id> <output-file>"
  echo ""
  echo "Examples:"
  echo "  # Export with timestamp"
  echo "  /fabric:export-pipeline <ws-id> <pipe-id> \"pipeline-\$(date +%Y%m%d).json\""
  echo ""
  echo "  # Export to specific directory"
  echo "  /fabric:export-pipeline <ws-id> <pipe-id> \"./backups/my-pipeline.json\""
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

# Check if output file already exists
if [ -f "$output_file" ]; then
  read -p "⚠️  File exists. Overwrite? (y/N): " confirm
  if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ Export cancelled"
    exit 0
  fi
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📋 Fetching pipeline metadata..."

# Step 1: Get pipeline metadata
metadata_response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

meta_http_code=$(echo "$metadata_response" | tail -n1)
metadata=$(echo "$metadata_response" | head -n-1)

if [ "$meta_http_code" != "200" ]; then
  echo "❌ Failed to get pipeline metadata (HTTP $meta_http_code)"
  exit 1
fi

pipeline_name=$(echo "$metadata" | jq -r '.displayName')
pipeline_desc=$(echo "$metadata" | jq -r '.description // ""')

echo "   Pipeline: $pipeline_name"
echo ""
echo "📥 Retrieving pipeline definition..."

# Step 2: Get pipeline definition (LRO)
get_def_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/dataPipelines/$pipeline_id/getDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

get_http_code=$(echo "$get_def_response" | tail -n1)

if [ "$get_http_code" != "202" ]; then
  echo "❌ Failed to request definition (HTTP $get_http_code)"
  exit 1
fi

operation_id=$(echo "$get_def_response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')
location=$(echo "$get_def_response" | grep -i "^location:" | cut -d' ' -f2 | tr -d '\r')

echo "⏳ Waiting for definition retrieval..."

# Poll operation status
max_attempts=60
attempt=0
sleep_time=5

while [ $attempt -lt $max_attempts ]; do
  sleep $sleep_time
  attempt=$((attempt + 1))

  status_response=$(curl -s -w "\n%{http_code}" -X GET \
    "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  status_http_code=$(echo "$status_response" | tail -n1)
  status_body=$(echo "$status_response" | head -n-1)

  if [ "$status_http_code" != "200" ]; then
    echo "❌ Failed to check operation status"
    exit 1
  fi

  status=$(echo "$status_body" | jq -r '.status')
  percent=$(echo "$status_body" | jq -r '.percentComplete // 0')

  echo "   Progress: $percent%"

  if [ "$status" = "Succeeded" ]; then
    # Get result location (may be updated)
    result_location=$(echo "$status_body" | jq -r '.resourceLocation // empty')
    if [ -z "$result_location" ]; then
      result_location=$location
    fi

    # Fetch definition
    definition_response=$(curl -s -w "\n%{http_code}" -X GET \
      "$result_location" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    def_http_code=$(echo "$definition_response" | tail -n1)
    definition=$(echo "$definition_response" | head -n-1)

    if [ "$def_http_code" != "200" ]; then
      echo "❌ Failed to retrieve definition content"
      exit 1
    fi

    break
  elif [ "$status" = "Failed" ]; then
    echo "❌ Definition retrieval failed"
    exit 1
  fi

  # Exponential backoff
  sleep_time=$((sleep_time < 60 ? sleep_time * 2 : 60))
  if [ $sleep_time -gt 60 ]; then
    sleep_time=60
  fi
done

if [ "$status" != "Succeeded" ]; then
  echo "❌ Definition retrieval timed out"
  exit 1
fi

echo "✅ Definition retrieved"
echo "📦 Building export package..."

# Step 3: Build export package with metadata
export_timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

export_package=$(jq -n \
  --arg name "$pipeline_name" \
  --arg desc "$pipeline_desc" \
  --arg id "$pipeline_id" \
  --arg ws "$workspace_id" \
  --arg ts "$export_timestamp" \
  --argjson definition "$definition" \
  --argjson metadata "$metadata" \
  '{
    exportMetadata: {
      exportedAt: $ts,
      exportVersion: "1.0",
      sourceWorkspaceId: $ws,
      sourcePipelineId: $id
    },
    pipeline: {
      displayName: $name,
      description: $desc,
      type: "DataPipeline"
    },
    metadata: $metadata,
    definition: $definition
  }')

# Write to file
echo "$export_package" | jq '.' > "$output_file"

if [ $? -eq 0 ]; then
  file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
  file_size_kb=$((file_size / 1024))

  echo "✅ Pipeline exported successfully"
  echo ""
  echo "╔═══════════════════════════════════════════════════════════╗"
  echo "║              PIPELINE EXPORT COMPLETE                     ║"
  echo "╚═══════════════════════════════════════════════════════════╝"
  echo ""
  echo "Pipeline:     $pipeline_name"
  echo "Pipeline ID:  $pipeline_id"
  echo "Workspace ID: $workspace_id"
  echo ""
  echo "Output File:  $output_file"
  echo "File Size:    ${file_size_kb} KB"
  echo "Exported:     $export_timestamp"
  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo ""
  echo "💡 Next steps:"
  echo "  • View export: cat $output_file | jq ."
  echo "  • Import to workspace: /fabric:import-pipeline <workspace-id> $output_file"
  echo "  • Version control: git add $output_file && git commit"
  echo "  • Clone pipeline: /fabric:clone-pipeline $workspace_id $pipeline_id <new-name>"
else
  echo "❌ Failed to write export file"
  exit 1
fi
```

## Export Package Structure

The exported JSON file contains:

```json
{
  "exportMetadata": {
    "exportedAt": "2024-01-15T10:30:00Z",
    "exportVersion": "1.0",
    "sourceWorkspaceId": "abc-123-...",
    "sourcePipelineId": "def-456-..."
  },
  "pipeline": {
    "displayName": "My Pipeline",
    "description": "Pipeline description",
    "type": "DataPipeline"
  },
  "metadata": {
    // Complete Fabric item metadata
  },
  "definition": {
    // Complete pipeline definition
  }
}
```

## Use Cases

### Version Control
```bash
# Export with git versioning
/fabric:export-pipeline <ws-id> <pipe-id> "pipelines/production-v1.0.json"
git add pipelines/production-v1.0.json
git commit -m "Backup production pipeline v1.0"
```

### Pre-Deployment Backup
```bash
# Backup before changes
timestamp=$(date +%Y%m%d-%H%M%S)
/fabric:export-pipeline <ws-id> <pipe-id> "backups/pipeline-${timestamp}.json"
```

### Environment Migration
```bash
# Export from dev
/fabric:export-pipeline <dev-ws> <pipe-id> "dev-pipeline.json"

# Import to prod
/fabric:import-pipeline <prod-ws> "dev-pipeline.json"
```

### Disaster Recovery
```bash
# Regular automated backups
for pipeline_id in $(list_pipelines); do
  /fabric:export-pipeline <ws-id> $pipeline_id "backups/${pipeline_id}.json"
done
```

## Export Best Practices

**Naming Conventions:**
```bash
# Include pipeline name and timestamp
pipeline-name-20240115.json

# Include environment
production-etl-pipeline-20240115.json

# Version numbering
data-pipeline-v1.2.3.json
```

**Storage:**
- **Git Repository**: Best for version control and collaboration
- **Shared Network**: Team access and backup
- **Cloud Storage**: S3, Azure Blob, GCS for disaster recovery
- **Local Backup**: Quick access and testing

**Frequency:**
- **Before Changes**: Always export before modifications
- **Daily/Weekly**: Automated scheduled exports
- **After Major Updates**: Manual exports after significant changes
- **Pre-Production**: Before deploying to production

## File Management

### Organize by Environment
```
backups/
  ├── dev/
  │   ├── pipeline1.json
  │   └── pipeline2.json
  ├── test/
  │   └── pipeline1.json
  └── prod/
      └── pipeline1.json
```

### Organize by Date
```
backups/
  ├── 2024-01/
  │   ├── pipeline-20240115.json
  │   └── pipeline-20240122.json
  └── 2024-02/
      └── pipeline-20240205.json
```

## Related Commands
- `/fabric:import-pipeline <workspace-id> <file>` - Import exported pipeline
- `/fabric:clone-pipeline <workspace-id> <pipeline-id>` - Clone directly
- `/fabric:get-definition <workspace-id> <pipeline-id>` - Export definition only
- `/fabric:create-pipeline <workspace-id> <name>` - Create new pipeline

## API Reference
- **Get Metadata**: `GET .../items/{itemId}`
- **Get Definition**: `POST .../dataPipelines/{id}/getDefinition` (LRO)
- **Permissions**: Any workspace role (read access)

## Notes
- Export files can be large (100 KB - 10+ MB) for complex pipelines
- Exported files are portable across Fabric environments
- Sensitive data (credentials, secrets) should be removed before sharing
- Export includes complete pipeline logic but not execution history
- Schedules are not included in exports
- Use git LFS for large pipeline exports in version control
