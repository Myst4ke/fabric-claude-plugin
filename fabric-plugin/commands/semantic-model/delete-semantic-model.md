---
description: Delete a semantic model
argument-hint: <workspace-id> <model-id> [--force]
---

# /fabric:delete-semantic-model

## Purpose
Delete a semantic model.

## Instructions

```bash
workspace_id="$1"
model_id="$2"
force=false

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --force) force=true; shift ;;
    *) echo "❌ Unknown: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$model_id" ]; then
  echo "❌ Both IDs required"; exit 1
fi

if [ "$force" = false ]; then
  read -p "Type 'DELETE' to confirm: " conf
  [ "$conf" != "DELETE" ] && echo "❌ Cancelled" && exit 0
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/semanticModels/$model_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

[ "$(echo "$response" | tail -n1)" = "200" ] && echo "✅ Deleted" || echo "❌ Failed"
```

## API Reference
- **Endpoint**: `DELETE .../semanticModels/{id}`
- **Permissions**: Contributor, Member, or Admin
