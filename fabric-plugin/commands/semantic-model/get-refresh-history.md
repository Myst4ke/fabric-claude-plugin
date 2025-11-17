---
description: Get semantic model refresh history
argument-hint: <workspace-id> <model-id>
---

# /fabric:get-refresh-history

## Purpose
View refresh history for a semantic model.

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
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/semanticModels/$model_id/refreshes" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  refreshes=$(echo "$response_body" | jq '.value')
  count=$(echo "$refreshes" | jq 'length')

  echo "✅ Found $count refresh(es)"
  echo ""

  [ "$count" -eq 0 ] && echo "No refreshes found." && exit 0

  echo "$refreshes" | jq -r '.[] | "  \(.id[0:24])... \(.status) \(.startTime // "N/A")"'
else
  echo "❌ Failed"; exit 1
fi
```

## API Reference
- **Endpoint**: `GET .../semanticModels/{id}/refreshes`
- **Permissions**: Any workspace role
