---
description: Create a new notebook
argument-hint: <workspace-id> <name> [--description <desc>]
---

# /fabric:create-notebook

## Purpose
Create a new Fabric notebook in a workspace. Notebooks are interactive documents for data analysis, visualization, and development using Python, Scala, R, or SQL.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `name`: Required. Display name for the notebook (1-256 characters)
- `--description <desc>`: Optional. Description of the notebook

## Instructions

```bash
workspace_id="$1"
notebook_name="$2"
description=""

# Parse optional description
shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --description)
      description="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:create-notebook <workspace-id> <name> [--description <desc>]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$notebook_name" ]; then
  echo "❌ Workspace ID and notebook name are required"
  echo "Usage: /fabric:create-notebook <workspace-id> <name> [--description <desc>]"
  exit 1
fi

# Validate workspace GUID
if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format (must be GUID)"
  exit 1
fi

# Validate name length
if [ ${#notebook_name} -lt 1 ] || [ ${#notebook_name} -gt 256 ]; then
  echo "❌ Notebook name must be between 1 and 256 characters"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📓 Creating notebook..."

# Build request body
if [ -n "$description" ]; then
  request_body=$(jq -n \
    --arg name "$notebook_name" \
    --arg desc "$description" \
    '{
      displayName: $name,
      description: $desc,
      type: "Notebook"
    }')
else
  request_body=$(jq -n \
    --arg name "$notebook_name" \
    '{
      displayName: $name,
      type: "Notebook"
    }')
fi

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "201" ] || [ "$http_code" = "202" ]; then
  notebook_id=$(echo "$response_body" | jq -r '.id')

  # Handle LRO if 202
  if [ "$http_code" = "202" ]; then
    echo "⏳ Notebook creation in progress..."

    operation_id=$(echo "$response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
      sleep 2
      attempt=$((attempt + 1))

      op_response=$(curl -s -X GET \
        "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

      op_status=$(echo "$op_response" | jq -r '.status')

      if [ "$op_status" = "Succeeded" ]; then
        notebook_id=$(echo "$op_response" | jq -r '.resourceId')
        break
      elif [ "$op_status" = "Failed" ]; then
        echo "❌ Notebook creation failed"
        error=$(echo "$op_response" | jq -r '.error.message // "Unknown error"')
        echo "Error: $error"
        exit 1
      fi
    done

    if [ "$op_status" != "Succeeded" ]; then
      echo "❌ Notebook creation timed out"
      exit 1
    fi
  fi

  echo "✅ Notebook created successfully"
  echo ""
  echo "╔═══════════════════════════════════════════════════════════╗"
  echo "║              NOTEBOOK CREATED                             ║"
  echo "╚═══════════════════════════════════════════════════════════╝"
  echo ""
  echo "Name:         $notebook_name"
  echo "Notebook ID:  $notebook_id"
  echo "Workspace ID: $workspace_id"
  if [ -n "$description" ]; then
    echo "Description:  $description"
  fi
  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo ""
  echo "💡 Next steps:"
  echo "  • View notebook: /fabric:get-notebook $workspace_id $notebook_id"
  echo "  • Edit definition: /fabric:update-notebook-definition $workspace_id $notebook_id <file>"
  echo "  • Execute notebook: /fabric:run-notebook $workspace_id $notebook_id"
  echo "  • Export notebook: /fabric:export-notebook $workspace_id $notebook_id"

else
  echo "❌ Failed to create notebook (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  error_code=$(echo "$response_body" | jq -r '.error.code // ""')
  echo "Error: $error_msg"

  if [ -n "$error_code" ]; then
    echo "Code: $error_code"
  fi

  exit 1
fi
```

## Use Cases

### Quick Development
```bash
# Create notebook for analysis
/fabric:create-notebook <workspace-id> "Sales Analysis"

# Create with description
/fabric:create-notebook <workspace-id> "ETL Processing" \
  --description "Daily ETL notebook for data processing"
```

### Batch Creation
```bash
# Create multiple notebooks
for name in "Analysis_Q1" "Analysis_Q2" "Analysis_Q3" "Analysis_Q4"; do
  /fabric:create-notebook <workspace-id> "$name"
done
```

### Project Setup
```bash
# Create notebook structure for new project
/fabric:create-notebook <ws-id> "1_Data_Ingestion" --description "Data loading"
/fabric:create-notebook <ws-id> "2_Data_Processing" --description "Data transformation"
/fabric:create-notebook <ws-id> "3_Analysis" --description "Data analysis"
/fabric:create-notebook <ws-id> "4_Visualization" --description "Charts and reports"
```

## Output Example

```
✅ Notebook created successfully

╔═══════════════════════════════════════════════════════════╗
║              NOTEBOOK CREATED                             ║"
╚═══════════════════════════════════════════════════════════╝

Name:         Sales Analysis
Notebook ID:  abc123-def456-ghi789-jkl012
Workspace ID: workspace-abc123-def456
Description:  Monthly sales data analysis

═══════════════════════════════════════════════════════════

💡 Next steps:
  • View notebook: /fabric:get-notebook workspace-id notebook-id
  • Edit definition: /fabric:update-notebook-definition workspace-id notebook-id <file>
  ...
```

## Notebook Features

**Supported Languages:**
- Python (PySpark, Pandas, etc.)
- Scala
- R
- SQL (Spark SQL)

**Default Configuration:**
- Empty notebook with no cells
- Ready for cell addition via definition update
- Linked to workspace's default lakehouse (if available)

## Related Commands
- `/fabric:list-notebooks <workspace-id>` - List all notebooks
- `/fabric:get-notebook <workspace-id> <notebook-id>` - View details
- `/fabric:update-notebook-definition <workspace-id> <notebook-id>` - Add cells/code
- `/fabric:import-notebook <workspace-id> <file>` - Import from .ipynb file

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items`
- **Response**: 201 Created or 202 Accepted (LRO)
- **Permissions**: Contributor, Member, or Admin role

## Notes
- New notebooks are created empty (no cells)
- Use update-notebook-definition to add code cells
- Notebooks can be edited in Fabric portal or via API
- Maximum name length: 256 characters
- LRO handling included for workspace with many items
