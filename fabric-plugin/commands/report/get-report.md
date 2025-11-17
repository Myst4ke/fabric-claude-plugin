---
description: Get report details
argument-hint: <workspace-id> <report-id>
---

# /fabric:get-report

## Purpose
Get details about a Power BI report.

## Instructions

```bash
workspace_id="$1"
report_id="$2"

[ -z "$workspace_id" ] || [ -z "$report_id" ] || echo "❌ Both IDs required" && exit 1

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/reports/$report_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

[ "$(echo "$response" | tail -n1)" != "200" ] && echo "❌ Failed" && exit 1

body=$(echo "$response" | head -n-1)
echo "✅ Report"
echo ""
echo "Name: $(echo "$body" | jq -r '.displayName')"
echo "ID:   $report_id"
echo ""
echo "💡 Clone: /fabric:clone-report $workspace_id $report_id <new-name>"
```

## API Reference
- **Endpoint**: `GET .../reports/{id}`
- **Permissions**: Any workspace role
