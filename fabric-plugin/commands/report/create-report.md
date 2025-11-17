---
description: Create a report
argument-hint: <workspace-id> <name> <dataset-id>
---

# /fabric:create-report

## Purpose
Create a new Power BI report.

## Instructions

```bash
workspace_id="$1"
name="$2"
dataset_id="$3"

[ -z "$workspace_id" ] || [ -z "$name" ] || [ -z "$dataset_id" ] && echo "❌ All required" && exit 1

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

body=$(jq -n --arg n "$name" --arg d "$dataset_id" '{displayName:$n,type:"Report",datasetId:$d}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$body")

[ "$(echo "$response" | tail -n1)" = "201" ] && echo "✅ Created: $(echo "$response" | head -n-1 | jq -r '.id')" || echo "❌ Failed"
```

## API Reference
- **Endpoint**: `POST .../items`
- **Permissions**: Contributor, Member, or Admin
