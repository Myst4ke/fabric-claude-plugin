---
description: Get table schema
argument-hint: <workspace-id> <lakehouse-id> <table-name>
---

# /fabric:get-table-schema

## Purpose
Get schema information for a lakehouse table.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `table-name`: Required. Table name

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
table_name="$3"

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ] || [ -z "$table_name" ]; then
  echo "❌ All arguments required"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📋 Fetching schema..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/tables/$table_name/schema" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  echo "✅ Schema retrieved"
  echo ""
  echo "Table: $table_name"
  echo ""
  echo "$response_body" | jq -r '.columns[] | "  \(.name): \(.type)"'
else
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi
```

## API Reference
- **Endpoint**: `GET .../lakehouses/{id}/tables/{tableName}/schema`
- **Response**: 200 OK with schema
- **Permissions**: Any workspace role
