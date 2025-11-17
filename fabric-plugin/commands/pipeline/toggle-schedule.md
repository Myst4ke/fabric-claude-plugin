---
description: Enable or disable a pipeline schedule
argument-hint: <workspace-id> <pipeline-id> <schedule-id> [--enable|--disable]
---

# /fabric:toggle-schedule

## Purpose
Enable or disable a pipeline schedule without deleting it. Useful for temporarily pausing scheduled executions while preserving schedule configuration.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `schedule-id`: Required. GUID of the schedule
- `--enable`: Enable the schedule
- `--disable`: Disable the schedule

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
schedule_id="$3"
action=""

# Parse action flag
shift 3
while [[ $# -gt 0 ]]; do
  case $1 in
    --enable)
      action="enable"
      shift
      ;;
    --disable)
      action="disable"
      shift
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:toggle-schedule <workspace-id> <pipeline-id> <schedule-id> [--enable|--disable]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ] || [ -z "$schedule_id" ]; then
  echo "❌ Workspace ID, pipeline ID, and schedule ID are required"
  echo "Usage: /fabric:toggle-schedule <workspace-id> <pipeline-id> <schedule-id> [--enable|--disable]"
  exit 1
fi

if [ -z "$action" ]; then
  echo "❌ Must specify --enable or --disable"
  echo "Usage: /fabric:toggle-schedule <workspace-id> <pipeline-id> <schedule-id> [--enable|--disable]"
  echo ""
  echo "Examples:"
  echo "  # Enable schedule"
  echo "  /fabric:toggle-schedule <ws-id> <pipe-id> <sched-id> --enable"
  echo ""
  echo "  # Disable schedule"
  echo "  /fabric:toggle-schedule <ws-id> <pipe-id> <sched-id> --disable"
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

enabled_value="false"
if [ "$action" = "enable" ]; then
  enabled_value="true"
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📅 Fetching current schedule..."

# Get current schedule configuration
get_response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/Pipeline/schedules/$schedule_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

get_http_code=$(echo "$get_response" | tail -n1)
get_body=$(echo "$get_response" | head -n-1)

if [ "$get_http_code" != "200" ]; then
  echo "❌ Failed to get schedule (HTTP $get_http_code)"
  error_msg=$(echo "$get_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  echo ""
  echo "💡 List schedules: /fabric:list-schedules $workspace_id $pipeline_id"
  exit 1
fi

current_enabled=$(echo "$get_body" | jq -r '.enabled')
current_cron=$(echo "$get_body" | jq -r '.configuration.cronExpression')
current_tz=$(echo "$get_body" | jq -r '.configuration.timezone // "UTC"')

# Check if already in desired state
if [ "$current_enabled" = "$enabled_value" ]; then
  status_word="enabled"
  if [ "$enabled_value" = "false" ]; then
    status_word="disabled"
  fi

  echo "ℹ️  Schedule is already $status_word"
  echo ""
  echo "Schedule Details:"
  echo "  Cron Expression: $current_cron"
  echo "  Timezone:        $current_tz"
  echo "  Status:          $([ "$current_enabled" = "true" ] && echo "✓ Enabled" || echo "⊗ Disabled")"
  exit 0
fi

# Update enabled status
echo "🔄 $([ "$action" = "enable" ] && echo "Enabling" || echo "Disabling") schedule..."

request_body=$(jq -n \
  --argjson enabled "$enabled_value" \
  --arg cron "$current_cron" \
  --arg tz "$current_tz" \
  '{
    enabled: $enabled,
    configuration: {
      type: "Cron",
      cronExpression: $cron,
      timezone: $tz
    }
  }')

response=$(curl -s -w "\n%{http_code}" -X PATCH \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/Pipeline/schedules/$schedule_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  next_run=$(echo "$response_body" | jq -r '.nextRunTime // "N/A"')

  if [ "$action" = "enable" ]; then
    echo "✅ Schedule enabled successfully"
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║              SCHEDULE ENABLED                             ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Schedule ID:     $schedule_id"
    echo "Cron Expression: $current_cron"
    echo "Timezone:        $current_tz"
    echo "Status:          ✓ Enabled"
    echo "Next Run:        $next_run"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Pipeline will now execute automatically according to schedule."
  else
    echo "✅ Schedule disabled successfully"
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║              SCHEDULE DISABLED                            ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Schedule ID:     $schedule_id"
    echo "Cron Expression: $current_cron"
    echo "Timezone:        $current_tz"
    echo "Status:          ⊗ Disabled"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Pipeline will NOT execute automatically while disabled."
    echo "Schedule configuration is preserved and can be re-enabled anytime."
  fi

  echo ""
  echo "💡 Next steps:"
  echo "  • View all schedules: /fabric:list-schedules $workspace_id $pipeline_id"
  if [ "$action" = "enable" ]; then
    echo "  • View execution history: /fabric:get-run-history $workspace_id $pipeline_id"
    echo "  • Disable schedule: /fabric:toggle-schedule $workspace_id $pipeline_id $schedule_id --disable"
  else
    echo "  • Re-enable schedule: /fabric:toggle-schedule $workspace_id $pipeline_id $schedule_id --enable"
    echo "  • Delete schedule: /fabric:delete-schedule $workspace_id $pipeline_id $schedule_id"
  fi
else
  echo "❌ Failed to toggle schedule (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Use Cases

### Temporarily Pause Scheduled Executions
```bash
# Disable during maintenance window
/fabric:toggle-schedule <ws-id> <pipe-id> <sched-id> --disable

# Re-enable after maintenance
/fabric:toggle-schedule <ws-id> <pipe-id> <sched-id> --enable
```

### Testing Pipeline Changes
```bash
# Disable schedule before modifying pipeline
/fabric:toggle-schedule <ws-id> <pipe-id> <sched-id> --disable

# Update pipeline definition
/fabric:update-definition <ws-id> <pipe-id> <definition-file>

# Test manually
/fabric:run-pipeline <ws-id> <pipe-id>

# Re-enable after successful test
/fabric:toggle-schedule <ws-id> <pipe-id> <sched-id> --enable
```

### Seasonal/Temporary Schedules
```bash
# Enable during business season
/fabric:toggle-schedule <ws-id> <pipe-id> <sched-id> --enable

# Disable during off-season
/fabric:toggle-schedule <ws-id> <pipe-id> <sched-id> --disable
```

## Enable vs Disable vs Delete

| Action | Config Preserved | Reversible | Executions | Use Case |
|--------|-----------------|------------|------------|----------|
| **Enable** | ✓ | Yes | Will run | Activate schedule |
| **Disable** | ✓ | Yes | Won't run | Temporary pause |
| **Delete** | ✗ | No | Won't run | Permanent removal |

## Advantages Over Delete

**Preserves Configuration:**
- Cron expression retained
- Timezone setting retained
- Can instantly re-enable
- No need to recreate schedule

**Quick Toggle:**
- Instant enable/disable
- No confirmation required
- Safe operation (fully reversible)

**Testing Workflow:**
- Disable during pipeline development
- Test manually
- Enable when ready for production

## Status Indicators

### Enabled Schedule
```
✓ Enabled
Next Run: 2024-01-15T02:00:00Z
Pipeline will execute automatically
```

### Disabled Schedule
```
⊗ Disabled
Next Run: N/A
Pipeline will NOT execute automatically
```

## Related Commands
- `/fabric:list-schedules <workspace-id> <pipeline-id>` - View all schedules with status
- `/fabric:create-schedule <workspace-id> <pipeline-id>` - Create new schedule
- `/fabric:update-schedule <workspace-id> <pipeline-id> <schedule-id>` - Modify timing
- `/fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-id>` - Permanently remove
- `/fabric:get-run-history <workspace-id> <pipeline-id>` - View execution history

## API Reference
- **Endpoint**: `PATCH https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/Pipeline/schedules/{scheduleId}`
- **Response**: 200 OK
- **Permissions**: Contributor, Member, or Admin role

## Best Practices

### When to Disable
- **Before pipeline changes**: Prevent executions during modifications
- **During testing**: Avoid automatic runs while debugging
- **Maintenance windows**: Pause during system maintenance
- **Resource management**: Temporarily reduce execution load
- **Seasonal operations**: Pause during off-season

### When to Delete
- **Obsolete schedules**: No longer needed permanently
- **Wrong configuration**: Easier to recreate than fix
- **Cleanup**: Remove test/temporary schedules
- **Consolidation**: Replacing with different schedule

### Quick Reference
```bash
# Workflow: Modify pipeline safely
/fabric:toggle-schedule <ws> <pipe> <sched> --disable
# ... make changes ...
/fabric:run-pipeline <ws> <pipe>  # test manually
/fabric:toggle-schedule <ws> <pipe> <sched> --enable

# Workflow: Temporary pause
/fabric:toggle-schedule <ws> <pipe> <sched> --disable
# ... wait for some condition ...
/fabric:toggle-schedule <ws> <pipe> <sched> --enable
```

## Notes
- Changes take effect immediately
- Next run time updates when enabled
- Disabled schedules show "N/A" for next run
- Schedule configuration is fully preserved when disabled
- No confirmation required (operation is reversible)
- Command is idempotent (safe to run multiple times)
