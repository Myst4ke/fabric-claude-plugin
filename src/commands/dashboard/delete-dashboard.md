---
description: Delete a dashboard
argument-hint: <workspace-id> <dashboard-id> [--force]
---

# /fabric:delete-dashboard

## Instructions

```bash
workspace_id="$1"
dashboard_id="$2"
force=false

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --force) force=true; shift ;;
    *) echo "❌ Unknown: $1"; exit 1 ;;
  esac
done

[ -z "$workspace_id" ] || [ -z "$dashboard_id" ] && echo "❌ Both IDs required" && exit 1

if [ "$force" = false ]; then
  read -p "Type 'DELETE': " conf
  [ "$conf" != "DELETE" ] && echo "❌ Cancelled" && exit 0
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/dashboards/$dashboard_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

[ "$(echo "$response" | tail -n1)" = "200" ] && echo "✅ Deleted" || echo "❌ Failed"
```

## API Reference
- **Endpoint**: `DELETE .../dashboards/{id}`
- **Permissions**: Contributor, Member, or Admin
