---
description: List all tables in a lakehouse
argument-hint: <workspace-id> <lakehouse-id> [--format table|json]
---

# /fabric:list-lakehouse-tables

## Purpose
List all Delta Lake tables in a lakehouse.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `--format <type>`: Optional. Output format: table (default) or json

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
format="table"

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --format) format="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ]; then
  echo "❌ Both IDs required"; exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]] || \
   ! [[ "$lakehouse_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid ID format"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📋 Fetching tables..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/tables" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi

tables=$(echo "$response_body" | jq '.value')
count=$(echo "$tables" | jq 'length')

echo "✅ Found $count table(s)"
echo ""

if [ "$count" -eq 0 ]; then
  echo "No tables in this lakehouse."
  echo ""
  echo "💡 Create: /fabric:create-table $workspace_id $lakehouse_id <table-name>"
  exit 0
fi

if [ "$format" = "json" ]; then
  echo "$tables" | jq '.'
  exit 0
fi

echo "Lakehouse Tables"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "$tables" | jq -r '
  ["TABLE NAME", "TYPE", "LOCATION"],
  ["────────────────", "──────────", "────────────────"],
  (.[] | [
    .name[0:25],
    .type // "Managed",
    (.location // "Default")[0:25]
  ])
  | @tsv
' | column -t -s $'\t'

echo ""
echo "══════════════════════════════════════════════════════════"
echo ""
echo "💡 Next steps:"
echo "  • Get schema: /fabric:get-table-schema $workspace_id $lakehouse_id <table-name>"
echo "  • Query data: /fabric:query-lakehouse $workspace_id $lakehouse_id"
echo "  • Load data: /fabric:load-table $workspace_id $lakehouse_id <table-name> <file>"
```

## API Reference
- **Endpoint**: `GET .../lakehouses/{id}/tables`
- **Response**: 200 OK with table array
- **Permissions**: Any workspace role
