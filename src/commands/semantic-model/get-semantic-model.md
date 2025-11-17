---
description: Get semantic model details
argument-hint: <workspace-id> <model-id>
---

# /fabric:get-semantic-model

## Purpose
Get detailed information about a semantic model.

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

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/semanticModels/$model_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  name=$(echo "$response_body" | jq -r '.displayName')
  desc=$(echo "$response_body" | jq -r '.description // "No description"')

  echo "✅ Semantic Model"
  echo ""
  echo "Name:        $name"
  echo "ID:          $model_id"
  echo "Description: $desc"
  echo ""
  echo "💡 Operations:"
  echo "  • Refresh: /fabric:refresh-semantic-model $workspace_id $model_id"
  echo "  • Get datasources: /fabric:get-datasources $workspace_id $model_id"
  echo "  • Execute query: /fabric:execute-dax-query $workspace_id $model_id <query>"
else
  echo "❌ Failed"; exit 1
fi
```

## API Reference
- **Endpoint**: `GET .../semanticModels/{id}`
- **Permissions**: Any workspace role
