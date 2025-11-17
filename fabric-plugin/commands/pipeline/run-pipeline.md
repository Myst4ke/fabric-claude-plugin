---
description: Execute a data pipeline
argument-hint: <workspace-id> <pipeline-id>
---

# /fabric:run-pipeline

## Purpose
Trigger execution of a data pipeline. Returns a job instance ID for tracking.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ]; then
  echo "❌ Workspace ID and pipeline ID are required"
  echo "Usage: /fabric:run-pipeline <workspace-id> <pipeline-id>"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "▶️  Starting pipeline execution..."

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/instances?jobType=Pipeline" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "202" ] || [ "$http_code" = "200" ]; then
  job_instance_id=$(echo "$response_body" | jq -r '.id // empty')

  if [ -n "$job_instance_id" ]; then
    echo "✅ Pipeline execution started"
    echo ""
    echo "Job Instance ID: $job_instance_id"
    echo ""
    echo "💡 Track progress:"
    echo "  • Get status: /fabric:get-run-details $workspace_id $pipeline_id $job_instance_id"
    echo "  • View logs: /fabric:get-run-logs $workspace_id $pipeline_id $job_instance_id"
    echo "  • Cancel: /fabric:cancel-run $workspace_id $pipeline_id $job_instance_id"
  else
    echo "✅ Pipeline execution started (instance ID not available)"
  fi
else
  echo "❌ Failed to start pipeline (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Related Commands
- `/fabric:get-run-history <workspace-id> <pipeline-id>` - View execution history
- `/fabric:get-run-details <workspace-id> <pipeline-id> <job-id>` - Check run status
- `/fabric:cancel-run <workspace-id> <pipeline-id> <job-id>` - Cancel execution

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/instances?jobType=Pipeline`
- **Response**: 202 Accepted with job instance ID
- **Permissions**: Contributor, Member, or Admin role
