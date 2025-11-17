---
description: Clone a report
argument-hint: <workspace-id> <report-id> <new-name>
---

# /fabric:clone-report

## Instructions

```bash
workspace_id="$1"
report_id="$2"
new_name="$3"

[ -z "$workspace_id" ] || [ -z "$report_id" ] || [ -z "$new_name" ] && echo "❌ All required" && exit 1

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

body=$(jq -n --arg n "$new_name" '{name:$n}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/reports/$report_id/clone" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$body")

[ "$(echo "$response" | tail -n1)" = "200" ] && echo "✅ Cloned: $(echo "$response" | head -n-1 | jq -r '.id')" || echo "❌ Failed"
```

## API Reference
- **Endpoint**: `POST .../reports/{id}/clone`
- **Permissions**: Contributor, Member, or Admin
