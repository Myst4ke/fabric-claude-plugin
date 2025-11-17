---
description: Clone a pipeline to create a duplicate
argument-hint: <workspace-id> <source-pipeline-id> <new-name> [--target-workspace <id>]
---

# /fabric:clone-pipeline

## Purpose
Create a duplicate of an existing pipeline, optionally in a different workspace. Preserves complete pipeline definition including activities, datasets, and configuration.

## Arguments
- `workspace-id`: Required. GUID of the source workspace
- `source-pipeline-id`: Required. GUID of the pipeline to clone
- `new-name`: Required. Name for the cloned pipeline
- `--target-workspace <id>`: Optional. Target workspace ID (default: same workspace)

## Instructions

```bash
workspace_id="$1"
source_pipeline_id="$2"
new_name="$3"
target_workspace_id=""

# Parse optional target workspace
shift 3
while [[ $# -gt 0 ]]; do
  case $1 in
    --target-workspace)
      target_workspace_id="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:clone-pipeline <workspace-id> <source-pipeline-id> <new-name> [--target-workspace <id>]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$source_pipeline_id" ] || [ -z "$new_name" ]; then
  echo "❌ Workspace ID, source pipeline ID, and new name are required"
  echo "Usage: /fabric:clone-pipeline <workspace-id> <source-pipeline-id> <new-name> [--target-workspace <id>]"
  echo ""
  echo "Examples:"
  echo "  # Clone within same workspace"
  echo "  /fabric:clone-pipeline <ws-id> <pipe-id> \"My Pipeline Copy\""
  echo ""
  echo "  # Clone to different workspace"
  echo "  /fabric:clone-pipeline <ws-id> <pipe-id> \"Prod Pipeline\" --target-workspace <prod-ws-id>"
  exit 1
fi

# Default target to source workspace if not specified
if [ -z "$target_workspace_id" ]; then
  target_workspace_id="$workspace_id"
fi

# Validate GUID formats
if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format (must be GUID)"
  exit 1
fi

if ! [[ "$source_pipeline_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid source pipeline ID format (must be GUID)"
  exit 1
fi

if ! [[ "$target_workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid target workspace ID format (must be GUID)"
  exit 1
fi

# Validate name length
if [ ${#new_name} -lt 1 ] || [ ${#new_name} -gt 256 ]; then
  echo "❌ Pipeline name must be between 1 and 256 characters"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📥 Retrieving source pipeline definition..."

# Step 1: Get definition from source pipeline (LRO)
get_def_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/dataPipelines/$source_pipeline_id/getDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

get_http_code=$(echo "$get_def_response" | tail -n1)

if [ "$get_http_code" != "202" ]; then
  echo "❌ Failed to request definition (HTTP $get_http_code)"
  exit 1
fi

operation_id=$(echo "$get_def_response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

echo "⏳ Waiting for definition retrieval..."

# Poll for definition (simplified)
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
  sleep 2
  attempt=$((attempt + 1))

  status_response=$(curl -s -w "\n%{http_code}" -X GET \
    "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  status=$(echo "$status_response" | head -n-1 | jq -r '.status')

  if [ "$status" = "Succeeded" ]; then
    break
  elif [ "$status" = "Failed" ]; then
    echo "❌ Failed to retrieve definition"
    exit 1
  fi
done

if [ "$status" != "Succeeded" ]; then
  echo "❌ Definition retrieval timed out"
  exit 1
fi

# Get the actual definition
location=$(echo "$get_def_response" | grep -i "^location:" | cut -d' ' -f2 | tr -d '\r')
definition_response=$(curl -s -X GET "$location" -H "Authorization: Bearer $ACCESS_TOKEN")
definition=$(echo "$definition_response" | jq -c '.')

echo "✅ Definition retrieved"
echo "📤 Creating cloned pipeline..."

# Step 2: Create new pipeline in target workspace
create_body=$(jq -n \
  --arg name "$new_name" \
  '{displayName: $name, type: "DataPipeline"}')

create_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$target_workspace_id/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$create_body")

create_http_code=$(echo "$create_response" | tail -n1)
create_body_response=$(echo "$create_response" | head -n-1)

if [ "$create_http_code" != "201" ] && [ "$create_http_code" != "202" ]; then
  echo "❌ Failed to create pipeline (HTTP $create_http_code)"
  exit 1
fi

new_pipeline_id=$(echo "$create_body_response" | jq -r '.id')

# If LRO, wait for completion
if [ "$create_http_code" = "202" ]; then
  echo "⏳ Waiting for pipeline creation..."
  create_op_id=$(echo "$create_response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

  attempt=0
  while [ $attempt -lt 30 ]; do
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
fi

echo "✅ Pipeline created: $new_pipeline_id"
echo "📝 Applying definition to cloned pipeline..."

# Step 3: Update definition on new pipeline (LRO)
update_def_body=$(jq -n \
  --argjson definition "$definition" \
  '{definition: $definition}')

update_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$target_workspace_id/dataPipelines/$new_pipeline_id/updateDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$update_def_body")

update_http_code=$(echo "$update_response" | tail -n1)

if [ "$update_http_code" != "202" ]; then
  echo "❌ Failed to update definition (HTTP $update_http_code)"
  echo "⚠️  Pipeline created but definition not applied. You can manually update it."
  echo "   Pipeline ID: $new_pipeline_id"
  exit 1
fi

update_op_id=$(echo "$update_response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

echo "⏳ Waiting for definition update..."

attempt=0
while [ $attempt -lt 60 ]; do
  sleep 3
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
    echo "❌ Definition update failed"
    echo "⚠️  Pipeline exists but may have incomplete definition"
    echo "   Pipeline ID: $new_pipeline_id"
    exit 1
  fi
done

echo "✅ Pipeline cloned successfully"
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              PIPELINE CLONED                              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Source Pipeline:  $source_pipeline_id"
echo "Source Workspace: $workspace_id"
echo ""
echo "New Pipeline:     $new_pipeline_id"
echo "New Name:         $new_name"
echo "Target Workspace: $target_workspace_id"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "💡 Next steps:"
echo "  • View cloned pipeline: /fabric:get-pipeline $target_workspace_id $new_pipeline_id"
echo "  • Test execution: /fabric:run-pipeline $target_workspace_id $new_pipeline_id"
echo "  • Create schedule: /fabric:create-schedule $target_workspace_id $new_pipeline_id --cron \"0 2 * * *\""
echo "  • Modify definition: /fabric:update-definition $target_workspace_id $new_pipeline_id <file>"
```

## Use Cases

### Development to Production
```bash
# Clone from dev to prod workspace
/fabric:clone-pipeline <dev-ws-id> <pipeline-id> "Production Pipeline" \
  --target-workspace <prod-ws-id>
```

### Create Pipeline Template
```bash
# Clone template within same workspace
/fabric:clone-pipeline <ws-id> <template-id> "New Project Pipeline"
```

### Backup Before Changes
```bash
# Create backup copy before modifying
/fabric:clone-pipeline <ws-id> <pipeline-id> "Backup - $(date +%Y%m%d)"
```

### Multi-Region Deployment
```bash
# Clone to different regional workspaces
/fabric:clone-pipeline <us-ws> <pipe-id> "EU Pipeline" --target-workspace <eu-ws>
/fabric:clone-pipeline <us-ws> <pipe-id> "APAC Pipeline" --target-workspace <apac-ws>
```

## What Gets Cloned

**Included:**
- Complete pipeline definition (all activities)
- Activity configurations and dependencies
- Parameters and variables
- Annotations and metadata
- Data flow logic

**Not Included:**
- Schedules (must be recreated)
- Execution history
- Access permissions
- Original pipeline ID

## Post-Clone Checklist

1. **Verify Definition**: Review cloned pipeline configuration
2. **Update Connections**: Verify linked services point to correct resources
3. **Test Execution**: Run manually to ensure functionality
4. **Create Schedule**: Set up scheduling if needed
5. **Configure Access**: Grant appropriate permissions

## Related Commands
- `/fabric:export-pipeline <workspace-id> <pipeline-id>` - Export to file
- `/fabric:import-pipeline <workspace-id> <file>` - Import from file
- `/fabric:get-definition <workspace-id> <pipeline-id>` - View definition
- `/fabric:create-pipeline <workspace-id> <name>` - Create blank pipeline

## API Reference
- **Get Definition**: `POST .../dataPipelines/{id}/getDefinition` (LRO)
- **Create Pipeline**: `POST .../items` (LRO)
- **Update Definition**: `POST .../dataPipelines/{id}/updateDefinition` (LRO)
- **Permissions**: Source workspace read access, target workspace contributor

## Notes
- This is a multi-step process involving 3 API operations
- Total time: 10-90 seconds depending on pipeline complexity
- Large pipelines may take longer to clone
- Cross-workspace cloning requires permissions in both workspaces
- Schedules are not cloned (create new schedules after cloning)
- Execution history is not preserved
