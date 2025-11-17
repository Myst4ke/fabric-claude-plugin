---
description: Get semantic model data sources
argument-hint: <workspace-id> <model-id>
---

# /fabric:get-datasources

## Purpose
Get data source connections for a semantic model.

## Instructions

```bash
workspace_id="$1"
model_id="$2"

if [ -z "$workspace_id" ] || [ -z "$model_id" ]; then
  echo "❌ Both IDs required"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/semanticModels/$model_id/datasources" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  sources=$(echo "$response_body" | jq '.value')
  count=$(echo "$sources" | jq 'length')

  echo "✅ Found $count datasource(s)"
  echo ""

  [ "$count" -eq 0 ] && echo "No datasources configured." && exit 0

  echo "$sources" | jq -r '.[] | "  \(.datasourceType): \(.connectionDetails.server // .connectionDetails.path // "N/A")"'
else
  echo "❌ Failed"; exit 1
fi
```

## API Reference
- **Endpoint**: `GET .../semanticModels/{id}/datasources`
- **Permissions**: Any workspace role
