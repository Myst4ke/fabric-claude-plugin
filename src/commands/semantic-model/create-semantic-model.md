---
description: Create a semantic model
argument-hint: <workspace-id> <name> [--description <desc>]
---

# /fabric:create-semantic-model

## Purpose
Create a new semantic model.

## Instructions

```bash
workspace_id="$1"
name="$2"
description=""

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --description) description="$2"; shift 2 ;;
    *) echo "❌ Unknown: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$name" ]; then
  echo "❌ Workspace ID and name required"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

if [ -n "$description" ]; then
  body=$(jq -n --arg n "$name" --arg d "$description" '{displayName:$n,description:$d,type:"SemanticModel"}')
else
  body=$(jq -n --arg n "$name" '{displayName:$n,type:"SemanticModel"}')
fi

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$body")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "201" ]; then
  model_id=$(echo "$response" | head -n-1 | jq -r '.id')
  echo "✅ Created: $model_id"
else
  echo "❌ Failed"; exit 1
fi
```

## API Reference
- **Endpoint**: `POST .../items`
- **Permissions**: Contributor, Member, or Admin
