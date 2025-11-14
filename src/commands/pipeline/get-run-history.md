---
description: Get pipeline execution history
argument-hint: <workspace-id> <pipeline-id>
---

# /fabric:get-run-history

## Purpose
Retrieve execution history for a data pipeline, showing recent runs with their status.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ]; then
  echo "❌ Workspace ID and pipeline ID are required"
  echo "Usage: /fabric:get-run-history <workspace-id> <pipeline-id>"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📊 Fetching execution history..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/instances" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to get run history (HTTP $http_code)"
  exit 1
fi

run_count=$(echo "$response_body" | jq '.value | length')

echo "✅ Found $run_count execution(s)"
echo ""

if [ "$run_count" -eq 0 ]; then
  echo "No executions found. Run pipeline: /fabric:run-pipeline $workspace_id $pipeline_id"
  exit 0
fi

echo "Pipeline Execution History"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "$response_body" | jq -r '
  ["JOB ID", "STATUS", "START TIME", "DURATION"],
  ["──────", "──────", "──────────", "────────"],
  (.value[] | [
    .id[0:20] + "...",
    .status,
    .startTimeUtc[0:19],
    (.endTimeUtc // "Running")
  ])
  | @tsv
' | column -t -s $'\t'

echo ""
echo "══════════════════════════════════════════════════════════"
echo ""
echo "💡 View details: /fabric:get-run-details $workspace_id $pipeline_id <job-id>"
```

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/instances`
- **Permissions**: Any workspace role
