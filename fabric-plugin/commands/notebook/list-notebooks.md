---
description: List all notebooks in a workspace
argument-hint: <workspace-id> [--format table|json]
---

# /fabric:list-notebooks

## Purpose
List all Fabric notebooks in a workspace with pagination support. Notebooks are interactive documents combining code, text, and visualizations for data analysis and development.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `--format <type>`: Optional. Output format: table (default) or json

## Instructions

```bash
workspace_id="$1"
format="table"

# Parse optional format argument
shift 1
while [[ $# -gt 0 ]]; do
  case $1 in
    --format)
      format="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:list-notebooks <workspace-id> [--format table|json]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ]; then
  echo "❌ Workspace ID is required"
  echo "Usage: /fabric:list-notebooks <workspace-id> [--format table|json]"
  exit 1
fi

# Validate workspace GUID
if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format (must be GUID)"
  exit 1
fi

# Validate format
if [ "$format" != "table" ] && [ "$format" != "json" ]; then
  echo "❌ Invalid format. Use 'table' or 'json'"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📓 Fetching notebooks..."

# Fetch items filtered by type=Notebook with pagination
all_notebooks="[]"
continuation_token=""
page=1

while true; do
  if [ -z "$continuation_token" ]; then
    endpoint="https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items?type=Notebook"
  else
    endpoint="https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items?type=Notebook&continuationToken=$continuation_token"
  fi

  response=$(curl -s -w "\n%{http_code}" -X GET "$endpoint" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  http_code=$(echo "$response" | tail -n1)
  response_body=$(echo "$response" | head -n-1)

  if [ "$http_code" != "200" ]; then
    echo "❌ Failed to list notebooks (HTTP $http_code)"
    error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
    echo "Error: $error_msg"
    exit 1
  fi

  # Merge current page results
  page_notebooks=$(echo "$response_body" | jq '.value')
  all_notebooks=$(jq -s '.[0] + .[1]' <(echo "$all_notebooks") <(echo "$page_notebooks"))

  # Check for continuation token
  continuation_token=$(echo "$response_body" | jq -r '.continuationToken // empty')

  if [ -z "$continuation_token" ]; then
    break
  fi

  page=$((page + 1))
  echo "   Fetching page $page..."
done

notebook_count=$(echo "$all_notebooks" | jq 'length')

echo "✅ Found $notebook_count notebook(s)"
echo ""

if [ "$notebook_count" -eq 0 ]; then
  echo "No notebooks in this workspace."
  echo ""
  echo "💡 Create a notebook:"
  echo "   /fabric:create-notebook $workspace_id \"My Notebook\""
  exit 0
fi

if [ "$format" = "json" ]; then
  echo "$all_notebooks" | jq '.'
  exit 0
fi

# Table format
echo "Notebooks in Workspace"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "$all_notebooks" | jq -r '
  ["NAME", "ID", "DESCRIPTION"],
  ["────────────────────", "────────────────────────", "────────────────────"],
  (.[] | [
    .displayName[0:35] + (if (.displayName | length) > 35 then "..." else "" end),
    .id[0:24] + "...",
    (.description // "No description")[0:35] + (if ((.description // "") | length) > 35 then "..." else "" end)
  ])
  | @tsv
' | column -t -s $'\t'

echo ""
echo "══════════════════════════════════════════════════════════"
echo ""
echo "Total: $notebook_count notebook(s)"
echo ""
echo "💡 Next steps:"
echo "  • View notebook: /fabric:get-notebook $workspace_id <notebook-id>"
echo "  • Create notebook: /fabric:create-notebook $workspace_id \"New Notebook\""
echo "  • Execute notebook: /fabric:run-notebook $workspace_id <notebook-id>"
echo "  • Export notebook: /fabric:export-notebook $workspace_id <notebook-id>"
```

## Use Cases

### Development Workflow
```bash
# List all notebooks to find one to work on
/fabric:list-notebooks <workspace-id>

# Get details of specific notebook
/fabric:get-notebook <workspace-id> <notebook-id>

# Execute notebook
/fabric:run-notebook <workspace-id> <notebook-id>
```

### Inventory Management
```bash
# Export list as JSON for processing
/fabric:list-notebooks <workspace-id> --format json > notebooks.json

# Count notebooks
/fabric:list-notebooks <workspace-id> --format json | jq 'length'
```

### Batch Operations
```bash
# Get all notebook IDs
notebook_ids=$(/fabric:list-notebooks <ws-id> --format json | jq -r '.[].id')

# Process each notebook
for notebook_id in $notebook_ids; do
  /fabric:get-notebook <ws-id> $notebook_id
done
```

## Output Formats

### Table Format (Default)
```
Notebooks in Workspace
══════════════════════════════════════════════════════════

NAME                  ID                        DESCRIPTION
────────────────────  ────────────────────────  ────────────────────
Data Analysis         abc123-def456-ghi789...   Sales data analysis
ETL Processing        xyz789-abc123-def456...   Daily ETL notebook
ML Training           mno456-pqr789-stu012...   Model training

══════════════════════════════════════════════════════════

Total: 3 notebook(s)
```

### JSON Format
```json
[
  {
    "id": "abc123-def456-ghi789",
    "displayName": "Data Analysis",
    "description": "Sales data analysis",
    "type": "Notebook",
    "workspaceId": "workspace-id"
  },
  {
    "id": "xyz789-abc123-def456",
    "displayName": "ETL Processing",
    "description": "Daily ETL notebook",
    "type": "Notebook",
    "workspaceId": "workspace-id"
  }
]
```

## Related Commands
- `/fabric:get-notebook <workspace-id> <notebook-id>` - Get notebook details
- `/fabric:create-notebook <workspace-id> <name>` - Create new notebook
- `/fabric:run-notebook <workspace-id> <notebook-id>` - Execute notebook
- `/fabric:list-items <workspace-id>` - List all items (includes notebooks)

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items?type=Notebook`
- **Response**: 200 OK with notebook array
- **Pagination**: Uses continuationToken for large result sets
- **Permissions**: Any workspace role

## Notes
- Results are automatically paginated for large workspaces
- Notebooks are a subtype of Fabric items
- Empty workspaces return an empty array (not an error)
- Notebook type filter is applied server-side for efficiency
- Use JSON format for programmatic processing
