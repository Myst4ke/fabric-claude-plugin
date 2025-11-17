---
description: Execute DAX query on semantic model
argument-hint: <workspace-id> <model-id> <query>
---

# /fabric:execute-dax-query

## Purpose
Execute DAX queries against a semantic model.

## Instructions

```bash
workspace_id="$1"
model_id="$2"
query="$3"

if [ -z "$workspace_id" ] || [ -z "$model_id" ] || [ -z "$query" ]; then
  echo "❌ All arguments required"
  echo "Example: /fabric:execute-dax-query <ws-id> <model-id> \"EVALUATE Sales\""
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

body=$(jq -n --arg q "$query" '{queries:[{query:$q}]}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/semanticModels/$model_id/executeQueries" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  echo "✅ Query executed"
  echo ""
  echo "$response_body" | jq '.'
else
  echo "❌ Failed"; exit 1
fi
```

## Examples
```bash
# Evaluate table
/fabric:execute-dax-query <ws-id> <model-id> "EVALUATE Sales"

# Aggregation
/fabric:execute-dax-query <ws-id> <model-id> "EVALUATE SUMMARIZE(Sales, Sales[Region], \"Total\", SUM(Sales[Amount]))"
```

## API Reference
- **Endpoint**: `POST .../semanticModels/{id}/executeQueries`
- **Permissions**: Any workspace role
