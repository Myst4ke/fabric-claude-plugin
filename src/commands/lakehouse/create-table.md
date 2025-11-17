---
description: Create a new table in lakehouse
argument-hint: <workspace-id> <lakehouse-id> <table-name> <schema-file>
---

# /fabric:create-table

## Purpose
Create a new Delta Lake table with specified schema.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `table-name`: Required. Table name
- `schema-file`: Required. JSON file with schema definition

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
table_name="$3"
schema_file="$4"

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ] || [ -z "$table_name" ] || [ -z "$schema_file" ]; then
  echo "❌ All arguments required"; exit 1
fi

if [ ! -f "$schema_file" ]; then
  echo "❌ Schema file not found"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

schema=$(cat "$schema_file" | jq -c '.')

request_body=$(jq -n \
  --arg name "$table_name" \
  --argjson schema "$schema" \
  '{name: $name, schema: $schema}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/tables" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

if [ "$(echo "$response" | tail -n1)" = "201" ]; then
  echo "✅ Table created: $table_name"
else
  echo "❌ Failed"; exit 1
fi
```

## Schema Example

```json
{
  "columns": [
    {"name": "id", "type": "integer"},
    {"name": "name", "type": "string"},
    {"name": "amount", "type": "decimal"}
  ]
}
```

## API Reference
- **Endpoint**: `POST .../lakehouses/{id}/tables`
- **Response**: 201 Created
- **Permissions**: Contributor, Member, or Admin
