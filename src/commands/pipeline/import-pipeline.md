---
description: Import pipeline from exported file
argument-hint: <workspace-id> <import-file> [--name <override-name>]
---

# /fabric:import-pipeline

## Purpose
Import a pipeline from a previously exported file. Creates a new pipeline with the definition and configuration from the export package.

## Arguments
- `workspace-id`: Required. GUID of the target workspace
- `import-file`: Required. Path to exported pipeline JSON file
- `--name <override-name>`: Optional. Override pipeline name from file

## Instructions

```bash
workspace_id="$1"
import_file="$2"
override_name=""

# Parse optional name override
shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --name)
      override_name="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:import-pipeline <workspace-id> <import-file> [--name <override-name>]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$import_file" ]; then
  echo "❌ Workspace ID and import file are required"
  echo "Usage: /fabric:import-pipeline <workspace-id> <import-file> [--name <override-name>]"
  echo ""
  echo "Examples:"
  echo "  # Import with original name"
  echo "  /fabric:import-pipeline <ws-id> \"backup/pipeline.json\""
  echo ""
  echo "  # Import with new name"
  echo "  /fabric:import-pipeline <ws-id> \"backup/pipeline.json\" --name \"Prod Pipeline\""
  exit 1
fi

# Validate workspace GUID
if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format (must be GUID)"
  exit 1
fi

# Validate import file exists
if [ ! -f "$import_file" ]; then
  echo "❌ Import file not found: $import_file"
  exit 1
fi

# Validate JSON format
if ! jq empty "$import_file" 2>/dev/null; then
  echo "❌ Invalid JSON in import file"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📋 Reading import file..."

# Read import package
import_data=$(cat "$import_file")

# Validate export package structure
if ! echo "$import_data" | jq -e '.definition' > /dev/null 2>&1; then
  echo "❌ Invalid export file: missing definition"
  echo "   This file may not be a valid pipeline export"
  exit 1
fi

# Extract data from import package
pipeline_name=$(echo "$import_data" | jq -r '.pipeline.displayName')
pipeline_desc=$(echo "$import_data" | jq -r '.pipeline.description // ""')
definition=$(echo "$import_data" | jq -c '.definition')
source_ws=$(echo "$import_data" | jq -r '.exportMetadata.sourceWorkspaceId // "Unknown"')
source_pipe=$(echo "$import_data" | jq -r '.exportMetadata.sourcePipelineId // "Unknown"')
export_date=$(echo "$import_data" | jq -r '.exportMetadata.exportedAt // "Unknown"')

# Use override name if provided
if [ -n "$override_name" ]; then
  pipeline_name="$override_name"
fi

# Validate name length
if [ ${#pipeline_name} -lt 1 ] || [ ${#pipeline_name} -gt 256 ]; then
  echo "❌ Pipeline name must be between 1 and 256 characters"
  exit 1
fi

echo ""
echo "Import Details:"
echo "══════════════════════════════════════════════════════════"
echo "Pipeline Name:       $pipeline_name"
echo "Description:         ${pipeline_desc:-None}"
echo "Source Workspace:    $source_ws"
echo "Source Pipeline:     $source_pipe"
echo "Exported:            $export_date"
echo "Target Workspace:    $workspace_id"
echo "══════════════════════════════════════════════════════════"
echo ""

read -p "Proceed with import? (Y/n): " confirm
if [ "$confirm" = "n" ] || [ "$confirm" = "N" ]; then
  echo "❌ Import cancelled"
  exit 0
fi

echo ""
echo "📤 Creating pipeline..."

# Step 1: Create new pipeline
create_body=$(jq -n \
  --arg name "$pipeline_name" \
  --arg desc "$pipeline_desc" \
  '{
    displayName: $name,
    description: $desc,
    type: "DataPipeline"
  }')

create_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$create_body")

create_http_code=$(echo "$create_response" | tail -n1)
create_body_response=$(echo "$create_response" | head -n-1)

if [ "$create_http_code" != "201" ] && [ "$create_http_code" != "202" ]; then
  echo "❌ Failed to create pipeline (HTTP $create_http_code)"
  error_msg=$(echo "$create_body_response" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi

new_pipeline_id=$(echo "$create_body_response" | jq -r '.id')

# Handle LRO if needed
if [ "$create_http_code" = "202" ]; then
  echo "⏳ Waiting for pipeline creation..."

  create_op_id=$(echo "$create_response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

  max_attempts=30
  attempt=0
  while [ $attempt -lt $max_attempts ]; do
    sleep 2
    attempt=$((attempt + 1))

    op_response=$(curl -s -X GET \
      "https://api.fabric.microsoft.com/v1/operations/$create_op_id" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    op_status=$(echo "$op_response" | jq -r '.status')

    if [ "$op_status" = "Succeeded" ]; then
      new_pipeline_id=$(echo "$op_response" | jq -r '.resourceId')
      break
    elif [ "$op_status" = "Failed" ]; then
      echo "❌ Pipeline creation failed"
      exit 1
    fi
  done

  if [ "$op_status" != "Succeeded" ]; then
    echo "❌ Pipeline creation timed out"
    exit 1
  fi
fi

echo "✅ Pipeline created: $new_pipeline_id"
echo "📝 Importing definition..."

# Step 2: Update pipeline definition (LRO)
update_def_body=$(jq -n \
  --argjson definition "$definition" \
  '{definition: $definition}')

update_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/dataPipelines/$new_pipeline_id/updateDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$update_def_body")

update_http_code=$(echo "$update_response" | tail -n1)

if [ "$update_http_code" != "202" ]; then
  echo "❌ Failed to update definition (HTTP $update_http_code)"
  echo "⚠️  Pipeline created but definition not applied"
  echo "   Pipeline ID: $new_pipeline_id"
  echo ""
  echo "💡 You can manually apply the definition:"
  echo "   /fabric:update-definition $workspace_id $new_pipeline_id $import_file"
  exit 1
fi

update_op_id=$(echo "$update_response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

echo "⏳ Applying definition..."

max_attempts=60
attempt=0
sleep_time=5

while [ $attempt -lt $max_attempts ]; do
  sleep $sleep_time
  attempt=$((attempt + 1))

  update_status_response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/operations/$update_op_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  update_status=$(echo "$update_status_response" | jq -r '.status')
  percent=$(echo "$update_status_response" | jq -r '.percentComplete // 0')

  echo "   Progress: $percent%"

  if [ "$update_status" = "Succeeded" ]; then
    break
  elif [ "$update_status" = "Failed" ]; then
    echo "❌ Definition import failed"
    error=$(echo "$update_status_response" | jq -r '.error.message // "Unknown error"')
    echo "Error: $error"
    echo ""
    echo "⚠️  Pipeline exists with ID: $new_pipeline_id"
    echo "   You may need to update definition manually or delete and retry"
    exit 1
  fi

  # Exponential backoff
  sleep_time=$((sleep_time < 60 ? sleep_time * 2 : 60))
  if [ $sleep_time -gt 60 ]; then
    sleep_time=60
  fi
done

if [ "$update_status" != "Succeeded" ]; then
  echo "❌ Definition import timed out"
  echo "   Pipeline ID: $new_pipeline_id"
  echo "   Operation ID: $update_op_id"
  exit 1
fi

echo "✅ Pipeline imported successfully"
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              PIPELINE IMPORT COMPLETE                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Pipeline Name:   $pipeline_name"
echo "Pipeline ID:     $new_pipeline_id"
echo "Workspace:       $workspace_id"
echo ""
echo "Source Details:"
echo "  Original ID:   $source_pipe"
echo "  Exported:      $export_date"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "💡 Next steps:"
echo "  • View pipeline: /fabric:get-pipeline $workspace_id $new_pipeline_id"
echo "  • Test execution: /fabric:run-pipeline $workspace_id $new_pipeline_id"
echo "  • Create schedule: /fabric:create-schedule $workspace_id $new_pipeline_id --cron \"0 2 * * *\""
echo "  • Review definition: /fabric:get-definition $workspace_id $new_pipeline_id"
```

## Use Cases

### Restore from Backup
```bash
# Restore pipeline from backup file
/fabric:import-pipeline <workspace-id> "backups/pipeline-20240115.json"
```

### Environment Promotion
```bash
# Export from dev
/fabric:export-pipeline <dev-ws> <pipe-id> "dev-pipeline.json"

# Import to test
/fabric:import-pipeline <test-ws> "dev-pipeline.json" --name "Test Pipeline"

# Import to production
/fabric:import-pipeline <prod-ws> "dev-pipeline.json" --name "Production Pipeline"
```

### Disaster Recovery
```bash
# Restore multiple pipelines from backups
for backup_file in backups/*.json; do
  /fabric:import-pipeline <workspace-id> "$backup_file"
done
```

### Template Deployment
```bash
# Deploy standard pipeline template
/fabric:import-pipeline <new-ws> "templates/etl-template.json" \
  --name "Customer ETL Pipeline"
```

## Import Validation

The import process validates:
- **File Format**: Valid JSON structure
- **Required Fields**: Pipeline definition present
- **Name Length**: 1-256 characters
- **Definition Schema**: Valid pipeline configuration

## Post-Import Checklist

1. **Verify Pipeline**: Check configuration is correct
2. **Update Connections**: Modify linked services for target environment
3. **Test Execution**: Run pipeline manually to verify functionality
4. **Configure Schedules**: Set up scheduling if needed
5. **Grant Access**: Configure workspace permissions

## Common Issues

### Definition Validation Errors
```
❌ Definition import failed
Error: Activity validation failed
```
**Solution**: Definition may reference resources that don't exist in target workspace

### Linked Service References
```
⚠️  Pipeline imported but may fail at runtime
```
**Solution**: Update linked service references to match target environment

### Name Conflicts
```
❌ Pipeline name already exists
```
**Solution**: Use `--name` flag to provide different name

## File Compatibility

**Supported Formats:**
- Exports from `/fabric:export-pipeline`
- Valid pipeline definition JSON
- Fabric export package format

**Required Structure:**
```json
{
  "exportMetadata": { ... },
  "pipeline": {
    "displayName": "...",
    "type": "DataPipeline"
  },
  "definition": { ... }
}
```

## Related Commands
- `/fabric:export-pipeline <workspace-id> <pipeline-id>` - Create export file
- `/fabric:clone-pipeline <workspace-id> <pipeline-id>` - Clone directly
- `/fabric:create-pipeline <workspace-id> <name>` - Create blank pipeline
- `/fabric:update-definition <workspace-id> <pipeline-id>` - Update existing

## API Reference
- **Create Pipeline**: `POST .../items` (LRO)
- **Update Definition**: `POST .../dataPipelines/{id}/updateDefinition` (LRO)
- **Permissions**: Contributor, Member, or Admin role in target workspace

## Best Practices

### Version Control Integration
```bash
# Pull latest from git
git pull origin main

# Import to workspace
/fabric:import-pipeline <workspace-id> "pipelines/production.json"
```

### Environment-Specific Imports
```bash
# Import with environment-specific names
/fabric:import-pipeline <dev-ws> "pipeline.json" --name "Dev - ETL Pipeline"
/fabric:import-pipeline <prod-ws> "pipeline.json" --name "Prod - ETL Pipeline"
```

### Automated Deployments
```bash
# CI/CD pipeline script
#!/bin/bash
workspace_id="$PROD_WORKSPACE_ID"

for pipeline_file in exports/*.json; do
  echo "Importing $pipeline_file..."
  /fabric:import-pipeline "$workspace_id" "$pipeline_file"
done
```

## Notes
- Import creates a NEW pipeline (does not update existing)
- Original pipeline ID is not preserved
- Schedules must be recreated after import
- Execution history is not imported
- Import takes 15-90 seconds depending on pipeline complexity
- Linked service references may need updating for target environment
- Import confirmation can be skipped in scripts using `yes | /fabric:import-pipeline ...`
