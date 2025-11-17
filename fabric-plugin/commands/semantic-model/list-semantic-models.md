---
description: List all semantic models in a workspace
argument-hint: <workspace-id> [--format table|json]
---

# /fabric:list-semantic-models

## Purpose
List all semantic models (formerly datasets) in a workspace.

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

echo "📊 Fetching semantic models..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/semanticModels" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi

models=$(echo "$response_body" | jq '.value')
count=$(echo "$models" | jq 'length')

echo "✅ Found $count semantic model(s)"
echo ""

if [ "$count" -eq 0 ]; then
  echo "No semantic models in this workspace."
  exit 0
fi

if [ "$format" = "json" ]; then
  echo "$models" | jq '.'
  exit 0
fi

echo "Semantic Models"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "$models" | jq -r '
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
echo "💡 Next: /fabric:get-semantic-model $workspace_id <model-id>"
```

## API Reference
- **Endpoint**: `GET .../workspaces/{id}/semanticModels`
- **Response**: 200 OK
- **Permissions**: Any workspace role
