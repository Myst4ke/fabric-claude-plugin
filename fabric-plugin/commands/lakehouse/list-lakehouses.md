---
description: List all lakehouses in a workspace
argument-hint: <workspace-id> [--format table|json]
---

# /fabric:list-lakehouses

## Purpose
List all Fabric lakehouses in a workspace with pagination support.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `--format <type>`: Optional. Output format: table (default) or json

## Instructions

```bash
workspace_id="$1"
format="table"

shift 1
while [[ $# -gt 0 ]]; do
  case $1 in
    --format) format="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ]; then
  echo "❌ Workspace ID required"; exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🏞️  Fetching lakehouses..."

all_lakehouses="[]"
continuation_token=""

while true; do
  if [ -z "$continuation_token" ]; then
    endpoint="https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses"
  else
    endpoint="https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses?continuationToken=$continuation_token"
  fi

  response=$(curl -s -w "\n%{http_code}" -X GET "$endpoint" -H "Authorization: Bearer $ACCESS_TOKEN")

  http_code=$(echo "$response" | tail -n1)
  response_body=$(echo "$response" | head -n-1)

  if [ "$http_code" != "200" ]; then
    echo "❌ Failed (HTTP $http_code)"; exit 1
  fi

  page_lakehouses=$(echo "$response_body" | jq '.value')
  all_lakehouses=$(jq -s '.[0] + .[1]' <(echo "$all_lakehouses") <(echo "$page_lakehouses"))

  continuation_token=$(echo "$response_body" | jq -r '.continuationToken // empty')
  [ -z "$continuation_token" ] && break
done

count=$(echo "$all_lakehouses" | jq 'length')

echo "✅ Found $count lakehouse(s)"
echo ""

if [ "$count" -eq 0 ]; then
  echo "No lakehouses in this workspace."
  echo ""
  echo "💡 Create: /fabric:create-lakehouse $workspace_id \"My Lakehouse\""
  exit 0
fi

if [ "$format" = "json" ]; then
  echo "$all_lakehouses" | jq '.'
  exit 0
fi

echo "Lakehouses in Workspace"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "$all_lakehouses" | jq -r '
  ["NAME", "ID", "DESCRIPTION"],
  ["────────────────", "────────────────────────", "────────────────"],
  (.[] | [
    .displayName[0:30],
    .id[0:24] + "...",
    (.description // "No description")[0:30]
  ])
  | @tsv
' | column -t -s $'\t'

echo ""
echo "══════════════════════════════════════════════════════════"
echo ""
echo "💡 Next steps:"
echo "  • View tables: /fabric:list-lakehouse-tables $workspace_id <lakehouse-id>"
echo "  • Query data: /fabric:query-lakehouse $workspace_id <lakehouse-id>"
```

## API Reference
- **Endpoint**: `GET .../workspaces/{id}/lakehouses`
- **Response**: 200 OK with lakehouse array
- **Permissions**: Any workspace role
