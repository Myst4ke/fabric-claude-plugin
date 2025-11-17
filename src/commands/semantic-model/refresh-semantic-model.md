---
description: Refresh a semantic model
argument-hint: <workspace-id> <model-id>
---

# /fabric:refresh-semantic-model

## Purpose
Trigger a refresh of a semantic model.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `model-id`: Required. GUID of the semantic model

## Instructions

```bash
workspace_id="$1"
model_id="$2"

if [ -z "$workspace_id" ] || [ -z "$model_id" ]; then
  echo "❌ Both IDs required"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🔄 Starting refresh..."

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/semanticModels/$model_id/refreshes" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "202" ] || [ "$http_code" = "200" ]; then
  refresh_id=$(echo "$response_body" | jq -r '.id // "N/A"')

  echo "✅ Refresh started"
  echo ""
  echo "Refresh ID: $refresh_id"
  echo "Model ID:   $model_id"
  echo ""
  echo "💡 Monitor: /fabric:get-refresh-history $workspace_id $model_id"
else
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi
```

## API Reference
- **Endpoint**: `POST .../semanticModels/{id}/refreshes`
- **Response**: 202 Accepted
- **Permissions**: Contributor, Member, or Admin
