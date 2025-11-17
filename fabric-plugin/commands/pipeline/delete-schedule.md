---
description: Delete a pipeline schedule
argument-hint: <workspace-id> <pipeline-id> <schedule-id> [--force]
---

# /fabric:delete-schedule

## Purpose
Permanently remove a pipeline schedule. Requires confirmation unless --force flag is used.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `schedule-id`: Required. GUID of the schedule
- `--force`: Optional. Skip confirmation prompt

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
schedule_id="$3"
force_delete=false

# Parse optional force flag
shift 3
while [[ $# -gt 0 ]]; do
  case $1 in
    --force)
      force_delete=true
      shift
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-id> [--force]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ] || [ -z "$schedule_id" ]; then
  echo "❌ Workspace ID, pipeline ID, and schedule ID are required"
  echo "Usage: /fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-id> [--force]"
  exit 1
fi

# Validate GUID formats
if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format (must be GUID)"
  exit 1
fi

if ! [[ "$pipeline_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid pipeline ID format (must be GUID)"
  exit 1
fi

if ! [[ "$schedule_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid schedule ID format (must be GUID)"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

# Get schedule details before deletion
echo "📅 Fetching schedule details..."

get_response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/Pipeline/schedules/$schedule_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

get_http_code=$(echo "$get_response" | tail -n1)
get_body=$(echo "$get_response" | head -n-1)

if [ "$get_http_code" != "200" ]; then
  echo "❌ Schedule not found or inaccessible (HTTP $get_http_code)"
  error_msg=$(echo "$get_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  echo ""
  echo "💡 List schedules: /fabric:list-schedules $workspace_id $pipeline_id"
  exit 1
fi

schedule_enabled=$(echo "$get_body" | jq -r '.enabled')
schedule_cron=$(echo "$get_body" | jq -r '.configuration.cronExpression')
schedule_tz=$(echo "$get_body" | jq -r '.configuration.timezone // "UTC"')

# Show schedule details
echo ""
echo "Schedule to be deleted:"
echo "══════════════════════════════════════════════════════════"
echo "Schedule ID:     $schedule_id"
echo "Status:          $([ "$schedule_enabled" = "true" ] && echo "Enabled" || echo "Disabled")"
echo "Cron Expression: $schedule_cron"
echo "Timezone:        $schedule_tz"
echo "══════════════════════════════════════════════════════════"
echo ""

# Confirmation prompt unless --force
if [ "$force_delete" = false ]; then
  echo "⚠️  This action cannot be undone."
  echo ""
  read -p "Type 'DELETE' to confirm: " confirmation

  if [ "$confirmation" != "DELETE" ]; then
    echo "❌ Deletion cancelled"
    exit 0
  fi
  echo ""
fi

echo "🗑️  Deleting schedule..."

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/Pipeline/schedules/$schedule_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ] || [ "$http_code" = "204" ]; then
  echo "✅ Schedule deleted successfully"
  echo ""
  echo "The schedule has been permanently removed."
  echo "Pipeline will no longer execute automatically on this schedule."

  if [ "$schedule_enabled" = "true" ]; then
    echo ""
    echo "⚠️  Note: This schedule was ENABLED when deleted."
    echo "   Pipeline executions based on this schedule have stopped."
  fi

  echo ""
  echo "💡 Next steps:"
  echo "  • View remaining schedules: /fabric:list-schedules $workspace_id $pipeline_id"
  echo "  • Create new schedule: /fabric:create-schedule $workspace_id $pipeline_id --cron \"0 2 * * *\""
  echo "  • Run manually: /fabric:run-pipeline $workspace_id $pipeline_id"
else
  echo "❌ Failed to delete schedule (HTTP $http_code)"
  response_body=$(echo "$response" | head -n-1)
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Safety Features

### Confirmation Prompt
By default, the command requires typing 'DELETE' to confirm:
```
Schedule to be deleted:
══════════════════════════════════════════════════════════
Schedule ID:     abc123-def456-ghi789
Status:          Enabled
Cron Expression: 0 2 * * *
Timezone:        UTC
══════════════════════════════════════════════════════════

⚠️  This action cannot be undone.

Type 'DELETE' to confirm: DELETE
```

### Force Flag
Skip confirmation for automation or scripts:
```bash
/fabric:delete-schedule <ws-id> <pipe-id> <sched-id> --force
```

## Use Cases

### Remove Temporary Schedule
```bash
# Delete one-time or test schedule
/fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-id>
```

### Clean Up Unused Schedules
```bash
# List schedules first
/fabric:list-schedules <workspace-id> <pipeline-id>

# Delete each unused schedule
/fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-1-id>
/fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-2-id>
```

### Automation Script
```bash
# Delete with force flag for scripts
/fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-id> --force
```

## Important Notes

### What Happens When Deleted
- **Schedule Removed**: Schedule configuration is permanently deleted
- **Future Executions**: No future automatic executions will occur
- **Past Executions**: Historical execution records are NOT affected
- **Pipeline Intact**: Pipeline itself is not modified or deleted
- **Other Schedules**: Other schedules on the same pipeline continue working

### Cannot Be Undone
- Deletion is permanent
- Schedule configuration (cron, timezone) is lost
- Must recreate schedule if needed later
- Consider disabling instead if you might re-enable later

## Alternative: Disable Instead of Delete

If you might need the schedule again, consider disabling instead:
```bash
# Disable schedule (preserves configuration)
/fabric:toggle-schedule <workspace-id> <pipeline-id> <schedule-id> --disable

# Can be re-enabled later
/fabric:toggle-schedule <workspace-id> <pipeline-id> <schedule-id> --enable
```

### Delete vs Disable Comparison

| Action | Schedule Config | Can Restore | Use Case |
|--------|----------------|-------------|----------|
| **Disable** | Preserved | Yes, instantly | Temporary pause |
| **Delete** | Lost | No, must recreate | Permanent removal |

## Related Commands
- `/fabric:list-schedules <workspace-id> <pipeline-id>` - View all schedules
- `/fabric:toggle-schedule <workspace-id> <pipeline-id> <schedule-id>` - Disable instead
- `/fabric:create-schedule <workspace-id> <pipeline-id>` - Create new schedule
- `/fabric:update-schedule <workspace-id> <pipeline-id> <schedule-id>` - Modify schedule

## API Reference
- **Endpoint**: `DELETE https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/Pipeline/schedules/{scheduleId}`
- **Response**: 200 OK or 204 No Content
- **Permissions**: Contributor, Member, or Admin role

## Best Practices
1. **List First**: Always list schedules to verify the correct schedule ID
2. **Review Details**: Confirm cron expression and status before deleting
3. **Document Changes**: Note why schedule was deleted for team awareness
4. **Prefer Disable**: Use disable for temporary changes, delete for permanent removal
5. **Backup Configuration**: Export schedule config before deleting if might need later
