---
description: Get dashboard details
argument-hint: <workspace-id> <dashboard-id>
---

# /fabric:get-dashboard

## Instructions

```bash
workspace_id="$1"
dashboard_id="$2"

[ -z "$workspace_id" ] || [ -z "$dashboard_id" ] && echo "❌ Both IDs required" && exit 1

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/dashboards/$dashboard_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

[ "$(echo "$response" | tail -n1)" != "200" ] && echo "❌ Failed" && exit 1

body=$(echo "$response" | head -n-1)
echo "✅ Dashboard"
echo ""
echo "Name: $(echo "$body" | jq -r '.displayName')"
echo "ID:   $dashboard_id"
```

## API Reference
- **Endpoint**: `GET .../dashboards/{id}`
- **Permissions**: Any workspace role
