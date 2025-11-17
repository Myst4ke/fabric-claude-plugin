---
description: List all reports in a workspace
argument-hint: <workspace-id> [--format table|json]
---

# /fabric:list-reports

## Purpose
List all Power BI reports in a workspace.

## Instructions

```bash
workspace_id="$1"
format="table"

shift 1
while [[ $# -gt 0 ]]; do
  case $1 in
    --format) format="$2"; shift 2 ;;
    *) echo "❌ Unknown: $1"; exit 1 ;;
  esac
done

[ -z "$workspace_id" ] && echo "❌ Workspace ID required" && exit 1

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/reports" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

[ "$http_code" != "200" ] && echo "❌ Failed" && exit 1

reports=$(echo "$response_body" | jq '.value')
count=$(echo "$reports" | jq 'length')

echo "✅ Found $count report(s)"
echo ""

[ "$count" -eq 0 ] && echo "No reports." && exit 0

if [ "$format" = "json" ]; then
  echo "$reports" | jq '.'
else
  echo "$reports" | jq -r '.[] | "  \(.displayName[0:40]) (\(.id[0:24])...)"'
fi
```

## API Reference
- **Endpoint**: `GET .../workspaces/{id}/reports`
- **Permissions**: Any workspace role
