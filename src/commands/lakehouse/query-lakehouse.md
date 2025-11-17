---
description: Execute SQL query on lakehouse
argument-hint: <workspace-id> <lakehouse-id> <query>
---

# /fabric:query-lakehouse

## Purpose
Execute SQL queries against lakehouse tables.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `query`: Required. SQL query string

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
query="$3"

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ] || [ -z "$query" ]; then
  echo "❌ All arguments required"
  echo "Usage: /fabric:query-lakehouse <workspace-id> <lakehouse-id> <query>"
  echo ""
  echo "Example:"
  echo "  /fabric:query-lakehouse <ws-id> <lh-id> \"SELECT * FROM sales LIMIT 10\""
  exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]] || \
   ! [[ "$lakehouse_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid ID format"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🔍 Executing query..."

request_body=$(jq -n --arg q "$query" '{query: $q}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/query" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  echo "✅ Query executed"
  echo ""
  echo "$response_body" | jq '.'
else
  echo "❌ Query failed (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Use Cases

### Explore Data
```bash
/fabric:query-lakehouse <ws-id> <lh-id> "SELECT * FROM sales LIMIT 10"
```

### Aggregate Queries
```bash
/fabric:query-lakehouse <ws-id> <lh-id> "SELECT region, SUM(amount) FROM sales GROUP BY region"
```

### Join Tables
```bash
/fabric:query-lakehouse <ws-id> <lh-id> "SELECT * FROM sales s JOIN customers c ON s.customer_id = c.id"
```

## API Reference
- **Endpoint**: `POST .../lakehouses/{id}/query`
- **Response**: 200 OK with query results
- **Permissions**: Any workspace role with read access
