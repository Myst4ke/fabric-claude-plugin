---
description: Cancel a running pipeline execution
argument-hint: <workspace-id> <pipeline-id> <job-instance-id>
---

# /fabric:cancel-run

## Purpose
Cancel an in-progress pipeline execution.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `job-instance-id`: Required. ID of the job instance to cancel

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
job_instance_id="$3"

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ] || [ -z "$job_instance_id" ]; then
  echo "❌ All arguments are required"
  echo "Usage: /fabric:cancel-run <workspace-id> <pipeline-id> <job-instance-id>"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "⏸️  Cancelling pipeline execution..."

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/instances/$job_instance_id/cancel" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ] || [ "$http_code" = "202" ]; then
  echo "✅ Cancellation request sent"
  echo ""
  echo "Note: It may take a few moments for the pipeline to stop."
  echo "Check status: /fabric:get-run-details $workspace_id $pipeline_id $job_instance_id"
else
  echo "❌ Failed to cancel execution (HTTP $http_code)"
  exit 1
fi
```

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/instances/{jobInstanceId}/cancel`
- **Permissions**: Contributor, Member, or Admin role
