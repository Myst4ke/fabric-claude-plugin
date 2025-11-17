---
description: Get logs from a pipeline execution
argument-hint: <workspace-id> <pipeline-id> <job-instance-id>
---

# /fabric:get-run-logs

## Purpose
Retrieve execution logs for troubleshooting and monitoring pipeline runs.

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
  echo "Usage: /fabric:get-run-logs <workspace-id> <pipeline-id> <job-instance-id>"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📜 Fetching execution logs..."

# Note: Log retrieval endpoint may vary by pipeline type
# This is a placeholder - actual endpoint depends on Fabric API documentation
response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/instances/$job_instance_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to get logs (HTTP $http_code)"
  echo ""
  echo "Note: Logs may not be available for all execution types."
  echo "Try viewing run details: /fabric:get-run-details $workspace_id $pipeline_id $job_instance_id"
  exit 1
fi

# Display execution information
status=$(echo "$response_body" | jq -r '.status')
error_msg=$(echo "$response_body" | jq -r '.failureReason // ""')

echo "✅ Execution information retrieved"
echo ""
echo "Status: $status"

if [ -n "$error_msg" ]; then
  echo ""
  echo "Error Details:"
  echo "────────────────────────────────────────────────────────"
  echo "$error_msg"
  echo "────────────────────────────────────────────────────────"
fi

echo ""
echo "ℹ️  Note: Detailed activity-level logs require Azure Data Factory"
echo "   integration or log analytics configuration."
```

## Related Commands
- `/fabric:get-run-details <workspace-id> <pipeline-id> <job-id>` - View execution status
- `/fabric:get-run-history <workspace-id> <pipeline-id>` - View all executions

## API Reference
- **Note**: Full log retrieval may require additional Data Factory APIs
- **Permissions**: Any workspace role
