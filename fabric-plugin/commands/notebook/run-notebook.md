---
description: Execute a notebook
argument-hint: <workspace-id> <notebook-id>
---

# /fabric:run-notebook

## Purpose
Trigger execution of a Fabric notebook. Returns job instance ID for tracking.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `notebook-id`: Required. GUID of the notebook

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"

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

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "▶️  Starting notebook execution..."

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$notebook_id/jobs/instances?jobType=RunNotebook" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "202" ] || [ "$http_code" = "200" ]; then
  job_id=$(echo "$response_body" | jq -r '.id')

  echo "✅ Notebook execution started"
  echo ""
  echo "╔═══════════════════════════════════════════════════════════╗"
  echo "║           NOTEBOOK EXECUTION STARTED                      ║"
  echo "╚═══════════════════════════════════════════════════════════╝"
  echo ""
  echo "Job Instance ID: $job_id"
  echo "Notebook ID:     $notebook_id"
  echo "Workspace ID:    $workspace_id"
  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo ""
  echo "💡 Monitor execution:"
  echo "   /fabric:get-notebook-run-details $workspace_id $notebook_id $job_id"
  echo ""
  echo "💡 View history:"
  echo "   /fabric:get-notebook-run-history $workspace_id $notebook_id"

else
  echo "❌ Failed to start execution (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Use Cases

### Manual Execution
```bash
# Run notebook once
/fabric:run-notebook <workspace-id> <notebook-id>
```

### Testing After Update
```bash
# Update then test
/fabric:update-notebook-definition <ws-id> <nb-id> notebook.ipynb
/fabric:run-notebook <ws-id> <nb-id>
```

### Batch Execution
```bash
# Run multiple notebooks
for nb_id in $notebook_ids; do
  /fabric:run-notebook <workspace-id> $nb_id
done
```

## Related Commands
- `/fabric:get-notebook-run-details` - Check execution status
- `/fabric:get-notebook-run-history` - View all executions
- `/fabric:cancel-notebook-run` - Cancel running execution

## API Reference
- **Endpoint**: `POST .../items/{id}/jobs/instances?jobType=RunNotebook`
- **Response**: 202 Accepted with job instance ID
- **Permissions**: Contributor, Member, or Admin

## Notes
- Execution is asynchronous
- Job ID returned immediately for tracking
- Actual execution may take minutes to hours
- Monitor with get-notebook-run-details command
