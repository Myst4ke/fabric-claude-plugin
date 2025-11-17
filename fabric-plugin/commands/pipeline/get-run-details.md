---
description: Get detailed information about a pipeline execution
argument-hint: <workspace-id> <pipeline-id> <job-instance-id>
---

# /fabric:get-run-details

## Purpose
Retrieve detailed information about a specific pipeline execution including status, duration, and error details.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `job-instance-id`: Required. ID of the job instance

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
job_instance_id="$3"

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ] || [ -z "$job_instance_id" ]; then
  echo "❌ All arguments are required"
  echo "Usage: /fabric:get-run-details <workspace-id> <pipeline-id> <job-instance-id>"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📋 Fetching execution details..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/instances/$job_instance_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to get run details (HTTP $http_code)"
  exit 1
fi

status=$(echo "$response_body" | jq -r '.status')
start_time=$(echo "$response_body" | jq -r '.startTimeUtc')
end_time=$(echo "$response_body" | jq -r '.endTimeUtc // "Still running"')
error_msg=$(echo "$response_body" | jq -r '.failureReason // "N/A"')

echo "✅ Execution details retrieved"
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║            PIPELINE EXECUTION DETAILS                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Job Instance ID: $job_instance_id"
echo "Status:          $status"
echo "Start Time:      $start_time"
echo "End Time:        $end_time"

if [ "$error_msg" != "N/A" ]; then
  echo ""
  echo "Error Details:"
  echo "  $error_msg"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"

if [ "$status" = "Running" ] || [ "$status" = "InProgress" ]; then
  echo ""
  echo "⏳ Execution still in progress..."
  echo "   Check again: /fabric:get-run-details $workspace_id $pipeline_id $job_instance_id"
fi
```

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/instances/{jobInstanceId}`
- **Permissions**: Any workspace role
