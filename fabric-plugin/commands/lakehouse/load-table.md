---
description: Load data into a lakehouse table
argument-hint: <workspace-id> <lakehouse-id> <table-name> <file-path>
---

# /fabric:load-table

## Purpose
Load data from a file into a lakehouse table (LRO).

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `table-name`: Required. Target table name
- `file-path`: Required. Path to data file (CSV, Parquet, JSON)

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
table_name="$3"
file_path="$4"

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ] || [ -z "$table_name" ] || [ -z "$file_path" ]; then
  echo "❌ All arguments required"; exit 1
fi

if [ ! -f "$file_path" ]; then
  echo "❌ File not found: $file_path"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📤 Uploading data to table: $table_name"

# Build load request
request_body=$(jq -n \
  --arg path "$file_path" \
  --arg table "$table_name" \
  '{
    relativePath: $path,
    pathType: "File",
    mode: "Overwrite"
  }')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/tables/$table_name/load" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" != "202" ]; then
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi

operation_id=$(echo "$response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')
echo "⏳ Loading data..."

for ((i=0; i<60; i++)); do
  sleep 5

  status_response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  status=$(echo "$status_response" | jq -r '.status')
  percent=$(echo "$status_response" | jq -r '.percentComplete // 0')

  echo "   Progress: $percent%"

  if [ "$status" = "Succeeded" ]; then
    echo "✅ Data loaded successfully"
    echo ""
    echo "Table: $table_name"
    echo "File:  $file_path"
    echo ""
    echo "💡 Next: /fabric:query-lakehouse $workspace_id $lakehouse_id \"SELECT * FROM $table_name LIMIT 10\""
    exit 0
  elif [ "$status" = "Failed" ]; then
    echo "❌ Load failed"; exit 1
  fi
done

echo "❌ Timeout"; exit 1
```

## API Reference
- **Endpoint**: `POST .../lakehouses/{id}/tables/{tableName}/load` (LRO)
- **Response**: 202 Accepted
- **Permissions**: Contributor, Member, or Admin
