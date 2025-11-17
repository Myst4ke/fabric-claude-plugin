---
description: Cancel a running notebook execution
argument-hint: <workspace-id> <notebook-id> <job-instance-id>
---

# /fabric:cancel-notebook-run

## Purpose
Cancel a currently running notebook execution.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `notebook-id`: Required. GUID of the notebook
- `job-instance-id`: Required. Job instance ID from run-notebook

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"
job_instance_id="$3"

if [ -z "$workspace_id" ] || [ -z "$notebook_id" ] || [ -z "$job_instance_id" ]; then
  echo "❌ All arguments required"
  echo "Usage: /fabric:cancel-notebook-run <workspace-id> <notebook-id> <job-instance-id>"
  exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

if ! [[ "$notebook_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid notebook ID"; exit 1
fi

if ! [[ "$job_instance_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid job instance ID"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🛑 Cancelling execution..."

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$notebook_id/jobs/instances/$job_instance_id/cancel" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ] || [ "$http_code" = "202" ]; then
  echo "✅ Cancellation request sent"
  echo ""
  echo "Job Instance ID: $job_instance_id"
  echo ""
  echo "⚠️  Note: Cancellation may take a few moments to complete."
  echo ""
  echo "💡 Check status:"
  echo "   /fabric:get-notebook-run-history $workspace_id $notebook_id"

else
  echo "❌ Failed to cancel (HTTP $http_code)"
  response_body=$(echo "$response" | head -n-1)
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown"')
  echo "Error: $error_msg"

  if [ "$http_code" = "404" ]; then
    echo ""
    echo "💡 Job may have already completed or been cancelled."
  fi

  exit 1
fi
```

## Use Cases

### Cancel Long-Running Execution
```bash
# Start execution
job_id=$(/fabric:run-notebook <ws-id> <nb-id> | grep "Job Instance ID" | cut -d: -f2)

# Cancel if taking too long
/fabric:cancel-notebook-run <ws-id> <nb-id> $job_id
```

### Cancel All Running
```bash
# Get running executions
running_jobs=$(/fabric:get-notebook-run-history <ws-id> <nb-id> --format json | \
  jq -r '.[] | select(.status == "Running") | .id')

# Cancel each
for job_id in $running_jobs; do
  /fabric:cancel-notebook-run <ws-id> <nb-id> $job_id
done
```

## Related Commands
- `/fabric:run-notebook` - Start execution
- `/fabric:get-notebook-run-history` - View all executions
- `/fabric:get-notebook-run-details` - Check specific execution status

## API Reference
- **Endpoint**: `POST .../items/{id}/jobs/instances/{jobId}/cancel`
- **Response**: 200 OK or 202 Accepted
- **Permissions**: Contributor, Member, or Admin

## Notes
- Cancellation is not instant - may take seconds/minutes
- Already completed jobs cannot be cancelled
- Cancelled jobs show status "Cancelled" in history
- Partial execution results may be available
