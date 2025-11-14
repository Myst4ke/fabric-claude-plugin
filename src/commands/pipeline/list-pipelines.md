---
description: List all data pipelines in a workspace
argument-hint: <workspace-id> [--format table|json]
---

# /fabric:list-pipelines

## Purpose
List all data pipelines in a Microsoft Fabric workspace with pagination support.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `--format <format>`: Optional. Output format - `table` (default) or `json`

## Prerequisites
- Access to the workspace (any role)
- Configured credentials

## Instructions

### 1. Validate and Authenticate
```bash
workspace_id="$1"
output_format="table"

if [ -z "$workspace_id" ]; then
  echo "❌ Workspace ID is required"
  echo "Usage: /fabric:list-pipelines <workspace-id> [--format table|json]"
  exit 1
fi

shift
while [ "$#" -gt 0 ]; do
  case "$1" in
    --format)
      output_format="$2"
      if [[ ! "$output_format" =~ ^(table|json)$ ]]; then
        echo "❌ Invalid format: $output_format"
        exit 1
      fi
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      exit 1
      ;;
  esac
done

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)
```

### 2. Fetch Pipelines with Pagination
```bash
echo "📋 Fetching pipelines..."

ENDPOINT="https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items"

# Initial request with type filter
response=$(curl -s -w "\n%{http_code}" -X GET \
  "${ENDPOINT}?type=DataPipeline" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to fetch pipelines (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi

# Collect all results with pagination
all_pipelines=$(echo "$response_body" | jq -r '.value')
continuation_token=$(echo "$response_body" | jq -r '.continuationToken // empty')

while [ -n "$continuation_token" ] && [ "$continuation_token" != "null" ]; do
  response=$(curl -s -w "\n%{http_code}" -X GET \
    "${ENDPOINT}?type=DataPipeline&continuationToken=${continuation_token}" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  http_code=$(echo "$response" | tail -n1)
  response_body=$(echo "$response" | head -n-1)

  if [ "$http_code" = "200" ]; then
    page_results=$(echo "$response_body" | jq -r '.value')
    all_pipelines=$(echo "$all_pipelines $page_results" | jq -s 'add')
    continuation_token=$(echo "$response_body" | jq -r '.continuationToken // empty')
  else
    break
  fi
done

pipeline_count=$(echo "$all_pipelines" | jq 'length')
echo "✅ Found $pipeline_count pipeline(s)"
```

### 3. Display Results
```bash
if [ "$pipeline_count" -eq 0 ]; then
  echo ""
  echo "ℹ️  No pipelines found in this workspace"
  echo ""
  echo "Create a pipeline: /fabric:create-pipeline $workspace_id <name>"
  exit 0
fi

if [ "$output_format" = "table" ]; then
  echo ""
  echo "Data Pipelines ($pipeline_count total)"
  echo "════════════════════════════════════════════════════════════════"
  echo ""

  echo "$all_pipelines" | jq -r '
    ["NAME", "ID", "DESCRIPTION"],
    ["────", "──", "───────────"],
    (.[] | [
      .displayName,
      .id[0:36],
      (.description // "No description")[0:40]
    ])
    | @tsv
  ' | column -t -s $'\t'

  echo ""
  echo "════════════════════════════════════════════════════════════════"
  echo ""
  echo "💡 Next steps:"
  echo "  • View details: /fabric:get-pipeline $workspace_id <pipeline-id>"
  echo "  • Run pipeline: /fabric:run-pipeline $workspace_id <pipeline-id>"
  echo "  • Get run history: /fabric:get-run-history $workspace_id <pipeline-id>"
else
  echo "$all_pipelines" | jq '.'
fi
```

## Example Output
```
/fabric:list-pipelines abc-123-def-456

🔐 Authenticating...
📋 Fetching pipelines...
✅ Found 5 pipeline(s)

Data Pipelines (5 total)
════════════════════════════════════════════════════════════════

NAME                    ID                                    DESCRIPTION
────                    ──                                    ───────────
Sales ETL Pipeline      def-456-ghi-789-jkl-012-mno-345      Daily sales data extraction
Customer Analytics      ghi-789-jkl-012-mno-345-pqr-678      Customer behavior analysis
Inventory Sync          jkl-012-mno-345-pqr-678-stu-901      Sync inventory from ERP
Marketing Data Load     mno-345-pqr-678-stu-901-vwx-234      Load marketing campaign data
Report Generation       pqr-678-stu-901-vwx-234-yz0-567      Generate monthly reports

════════════════════════════════════════════════════════════════

💡 Next steps:
  • View details: /fabric:get-pipeline abc-123-def-456 <pipeline-id>
  • Run pipeline: /fabric:run-pipeline abc-123-def-456 <pipeline-id>
  • Get run history: /fabric:get-run-history abc-123-def-456 <pipeline-id>
```

## Related Commands
- `/fabric:get-pipeline <workspace-id> <pipeline-id>` - View pipeline details
- `/fabric:create-pipeline <workspace-id> <name>` - Create new pipeline
- `/fabric:run-pipeline <workspace-id> <pipeline-id>` - Execute pipeline

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items?type=DataPipeline`
- **Pagination**: Automatic via continuationToken
- **Permissions**: Any workspace role
