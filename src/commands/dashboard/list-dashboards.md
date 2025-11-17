---
description: List all dashboards
argument-hint: <workspace-id>
---

# /fabric:list-dashboards

## Instructions

```bash
workspace_id="$1"

[ -z "$workspace_id" ] && echo "❌ Workspace ID required" && exit 1

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/dashboards" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

[ "$(echo "$response" | tail -n1)" != "200" ] && echo "❌ Failed" && exit 1

dashboards=$(echo "$response" | head -n-1 | jq '.value')
count=$(echo "$dashboards" | jq 'length')

echo "✅ Found $count dashboard(s)"
echo ""

[ "$count" -eq 0 ] && echo "No dashboards." && exit 0

echo "$dashboards" | jq -r '.[] | "  \(.displayName) (\(.id[0:24])...)"'
```

## API Reference
- **Endpoint**: `GET .../workspaces/{id}/dashboards`
- **Permissions**: Any workspace role
