---
description: Update a pipeline schedule
argument-hint: <workspace-id> <pipeline-id> <schedule-id> [--cron <expr>] [--timezone <tz>]
---

# /fabric:update-schedule

## Purpose
Modify an existing pipeline schedule's timing, timezone, or configuration.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `schedule-id`: Required. GUID of the schedule
- `--cron <expression>`: Optional. New cron expression
- `--timezone <tz>`: Optional. New timezone

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
schedule_id="$3"
cron_expression=""
timezone=""

# Parse optional arguments
shift 3
while [[ $# -gt 0 ]]; do
  case $1 in
    --cron)
      cron_expression="$2"
      shift 2
      ;;
    --timezone)
      timezone="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:update-schedule <workspace-id> <pipeline-id> <schedule-id> [--cron <expr>] [--timezone <tz>]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ] || [ -z "$schedule_id" ]; then
  echo "❌ Workspace ID, pipeline ID, and schedule ID are required"
  echo "Usage: /fabric:update-schedule <workspace-id> <pipeline-id> <schedule-id> [--cron <expr>] [--timezone <tz>]"
  exit 1
fi

# Validate at least one update parameter
if [ -z "$cron_expression" ] && [ -z "$timezone" ]; then
  echo "❌ At least one update parameter is required"
  echo "Usage: /fabric:update-schedule <workspace-id> <pipeline-id> <schedule-id> [--cron <expr>] [--timezone <tz>]"
  echo ""
  echo "Examples:"
  echo "  # Change to run every hour"
  echo "  /fabric:update-schedule <ws-id> <pipe-id> <sched-id> --cron \"0 * * * *\""
  echo ""
  echo "  # Change timezone to EST"
  echo "  /fabric:update-schedule <ws-id> <pipe-id> <sched-id> --timezone \"America/New_York\""
  echo ""
  echo "  # Change both"
  echo "  /fabric:update-schedule <ws-id> <pipe-id> <sched-id> --cron \"0 9 * * 1-5\" --timezone \"America/New_York\""
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

# Validate cron expression if provided
if [ -n "$cron_expression" ] && ! [[ "$cron_expression" =~ ^[0-9\*,\-/\ ]+$ ]]; then
  echo "❌ Invalid cron expression format"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📅 Fetching current schedule configuration..."

# Get current schedule to merge with updates
get_response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/Pipeline/schedules/$schedule_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

get_http_code=$(echo "$get_response" | tail -n1)
get_body=$(echo "$get_response" | head -n-1)

if [ "$get_http_code" != "200" ]; then
  echo "❌ Failed to get current schedule (HTTP $get_http_code)"
  error_msg=$(echo "$get_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  echo ""
  echo "💡 List schedules: /fabric:list-schedules $workspace_id $pipeline_id"
  exit 1
fi

# Extract current values
current_enabled=$(echo "$get_body" | jq -r '.enabled')
current_cron=$(echo "$get_body" | jq -r '.configuration.cronExpression')
current_tz=$(echo "$get_body" | jq -r '.configuration.timezone // "UTC"')

# Use new values if provided, otherwise keep current
final_cron="${cron_expression:-$current_cron}"
final_tz="${timezone:-$current_tz}"

echo "📝 Updating schedule..."

# Build update request
request_body=$(jq -n \
  --argjson enabled "$current_enabled" \
  --arg cron "$final_cron" \
  --arg tz "$final_tz" \
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
  echo "✅ Schedule updated successfully"
  echo ""
  echo "╔═══════════════════════════════════════════════════════════╗"
  echo "║              SCHEDULE UPDATE SUMMARY                      ║"
  echo "╚═══════════════════════════════════════════════════════════╝"
  echo ""

  # Show what changed
  if [ -n "$cron_expression" ]; then
    echo "Cron Expression:"
    echo "  Before: $current_cron"
    echo "  After:  $final_cron"
    echo ""
  fi

  if [ -n "$timezone" ]; then
    echo "Timezone:"
    echo "  Before: $current_tz"
    echo "  After:  $final_tz"
    echo ""
  fi

  next_run=$(echo "$response_body" | jq -r '.nextRunTime // "N/A"')
  echo "Next Scheduled Run: $next_run"
  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo ""
  echo "💡 Next steps:"
  echo "  • View all schedules: /fabric:list-schedules $workspace_id $pipeline_id"
  echo "  • Toggle status: /fabric:toggle-schedule $workspace_id $pipeline_id $schedule_id"
  echo "  • View executions: /fabric:get-run-history $workspace_id $pipeline_id"
else
  echo "❌ Failed to update schedule (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"

  if [[ "$error_msg" == *"cron"* ]]; then
    echo ""
    echo "💡 Valid cron format: minute hour day month dayofweek"
    echo "   Example: \"0 2 * * *\" (daily at 2 AM)"
  fi

  exit 1
fi
```

## Update Scenarios

### Change Schedule Timing
```bash
# Change from daily to hourly
/fabric:update-schedule <ws-id> <pipe-id> <sched-id> --cron "0 * * * *"

# Change to weekdays only at 9 AM
/fabric:update-schedule <ws-id> <pipe-id> <sched-id> --cron "0 9 * * 1-5"

# Change to every 4 hours
/fabric:update-schedule <ws-id> <pipe-id> <sched-id> --cron "0 */4 * * *"
```

### Change Timezone
```bash
# Switch to Eastern Time
/fabric:update-schedule <ws-id> <pipe-id> <sched-id> --timezone "America/New_York"

# Switch to London Time
/fabric:update-schedule <ws-id> <pipe-id> <sched-id> --timezone "Europe/London"

# Switch to Tokyo Time
/fabric:update-schedule <ws-id> <pipe-id> <sched-id> --timezone "Asia/Tokyo"
```

### Update Both
```bash
# Change to daily at 3 AM EST
/fabric:update-schedule <ws-id> <pipe-id> <sched-id> \
  --cron "0 3 * * *" \
  --timezone "America/New_York"
```

## Common Cron Expressions

| Schedule | Expression | Description |
|----------|-----------|-------------|
| Every 30 minutes | `*/30 * * * *` | Twice per hour |
| Every 2 hours | `0 */2 * * *` | 00:00, 02:00, 04:00... |
| Business hours | `0 9-17 * * 1-5` | 9 AM - 5 PM weekdays |
| Night batch | `0 0 * * *` | Midnight daily |
| Weekend only | `0 8 * * 0,6` | 8 AM Sat/Sun |
| Quarterly | `0 0 1 */3 *` | 1st day of quarter |

## Timezone Considerations

**Common Timezones:**
- `UTC` - Coordinated Universal Time (no DST)
- `America/New_York` - US Eastern Time (with DST)
- `America/Chicago` - US Central Time (with DST)
- `America/Los_Angeles` - US Pacific Time (with DST)
- `Europe/London` - UK Time (with DST)
- `Europe/Paris` - Central European Time (with DST)
- `Asia/Tokyo` - Japan Time (no DST)
- `Australia/Sydney` - Australian Eastern Time (with DST)

**Daylight Saving Time:**
Timezones with DST automatically adjust schedule execution times.

## Related Commands
- `/fabric:list-schedules <workspace-id> <pipeline-id>` - View all schedules
- `/fabric:create-schedule <workspace-id> <pipeline-id>` - Create new schedule
- `/fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-id>` - Remove schedule
- `/fabric:toggle-schedule <workspace-id> <pipeline-id> <schedule-id>` - Enable/disable

## API Reference
- **Endpoint**: `PATCH https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/Pipeline/schedules/{scheduleId}`
- **Response**: 200 OK
- **Permissions**: Contributor, Member, or Admin role

## Notes
- Updates take effect immediately
- Next run time is recalculated based on new configuration
- Schedule enabled/disabled status is preserved (use toggle-schedule to change)
- Previous scheduled runs are not affected
- Partial updates are supported (change only what you need)
- Invalid cron expressions will be rejected before update
