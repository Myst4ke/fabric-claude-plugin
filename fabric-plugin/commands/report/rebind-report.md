---
description: Rebind report to different dataset
argument-hint: <workspace-id> <report-id> <new-dataset-id>
---

# /fabric:rebind-report

## Instructions

```bash
workspace_id="$1"
report_id="$2"
dataset_id="$3"

[ -z "$workspace_id" ] || [ -z "$report_id" ] || [ -z "$dataset_id" ] && echo "❌ All required" && exit 1

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

body=$(jq -n --arg d "$dataset_id" '{datasetId:$d}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/reports/$report_id/rebind" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$body")

[ "$(echo "$response" | tail -n1)" = "200" ] && echo "✅ Rebound to dataset: $dataset_id" || echo "❌ Failed"
```

## API Reference
- **Endpoint**: `POST .../reports/{id}/rebind`
- **Permissions**: Contributor, Member, or Admin
