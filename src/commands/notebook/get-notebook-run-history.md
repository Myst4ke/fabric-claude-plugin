---
description: Get notebook execution history
argument-hint: <workspace-id> <notebook-id> [--format table|json]
---

# /fabric:get-notebook-run-history

## Purpose
View execution history for a notebook including status, duration, and timestamps.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `notebook-id`: Required. GUID of the notebook
- `--format <type>`: Optional. Output format: table (default) or json

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"
format="table"

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --format) format="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$notebook_id" ]; then
  echo "❌ Workspace ID and notebook ID required"
  exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

if ! [[ "$notebook_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid notebook ID"; exit 1
fi

if [ "$format" != "table" ] && [ "$format" != "json" ]; then
  echo "❌ Invalid format"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📋 Fetching execution history..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$notebook_id/jobs/instances" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed (HTTP $http_code)"
  exit 1
fi

executions=$(echo "$response_body" | jq '.value')
count=$(echo "$executions" | jq 'length')

echo "✅ Found $count execution(s)"
echo ""

if [ "$count" -eq 0 ]; then
  echo "No executions found."
  echo ""
  echo "💡 Run notebook: /fabric:run-notebook $workspace_id $notebook_id"
  exit 0
fi

if [ "$format" = "json" ]; then
  echo "$executions" | jq '.'
  exit 0
fi

echo "Notebook Execution History"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "$executions" | jq -r '
  ["JOB ID", "STATUS", "START TIME", "DURATION"],
  ["──────────────────", "──────────", "────────────────────", "────────"],
  (.[] | [
    .id[0:18] + "...",
    .status,
    .startTimeUtc[0:19],
    (.endTimeUtc // "Running")
  ])
  | @tsv
' | column -t -s $'\t'

echo ""
echo "══════════════════════════════════════════════════════════"
echo ""
echo "💡 View details: /fabric:get-notebook-run-details $workspace_id $notebook_id <job-id>"
```

## Output Formats

### Table Format
```
Notebook Execution History
══════════════════════════════════════════════════════════

JOB ID              STATUS      START TIME            DURATION
──────────────────  ──────────  ────────────────────  ────────
abc123-def456...    Completed   2024-01-15T10:30:00   5m 23s
xyz789-abc123...    Failed      2024-01-15T09:15:00   2m 45s
mno456-pqr789...    Running     2024-01-15T11:00:00   Running

══════════════════════════════════════════════════════════
```

### JSON Format
```json
[
  {
    "id": "abc123-def456",
    "status": "Completed",
    "startTimeUtc": "2024-01-15T10:30:00Z",
    "endTimeUtc": "2024-01-15T10:35:23Z"
  }
]
```

## Related Commands
- `/fabric:run-notebook` - Start execution
- `/fabric:get-notebook-run-details` - Get specific execution details
- `/fabric:cancel-notebook-run` - Cancel running execution

## API Reference
- **Endpoint**: `GET .../items/{id}/jobs/instances`
- **Response**: 200 OK with execution array
- **Permissions**: Any workspace role
