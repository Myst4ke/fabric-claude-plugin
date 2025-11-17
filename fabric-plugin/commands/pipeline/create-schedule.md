---
description: Create a pipeline schedule
argument-hint: <workspace-id> <pipeline-id> --cron <expression> [--timezone <tz>] [--enabled]
---

# /fabric:create-schedule

## Purpose
Create a scheduled trigger for automatic pipeline execution at specified intervals.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `--cron <expression>`: Required. Cron expression for schedule timing
- `--timezone <tz>`: Optional. Timezone for schedule (default: UTC)
- `--enabled`: Optional. Enable schedule immediately (default: disabled)

## Instructions

```bash
workspace_id=""
pipeline_id=""
cron_expression=""
timezone="UTC"
enabled="false"

# Parse arguments
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
    --enabled)
      enabled="true"
      shift
      ;;
    *)
      if [ -z "$workspace_id" ]; then
        workspace_id="$1"
      elif [ -z "$pipeline_id" ]; then
        pipeline_id="$1"
      else
        echo "❌ Unknown argument: $1"
        echo "Usage: /fabric:create-schedule <workspace-id> <pipeline-id> --cron <expression> [--timezone <tz>] [--enabled]"
        exit 1
      fi
      shift
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ] || [ -z "$cron_expression" ]; then
  echo "❌ Workspace ID, pipeline ID, and cron expression are required"
  echo "Usage: /fabric:create-schedule <workspace-id> <pipeline-id> --cron <expression> [--timezone <tz>] [--enabled]"
  echo ""
  echo "Examples:"
  echo "  # Run every day at 2 AM UTC"
  echo "  /fabric:create-schedule <ws-id> <pipe-id> --cron \"0 2 * * *\""
  echo ""
  echo "  # Run every hour, enabled immediately, EST timezone"
  echo "  /fabric:create-schedule <ws-id> <pipe-id> --cron \"0 * * * *\" --timezone \"America/New_York\" --enabled"
  echo ""
  echo "  # Run every Monday at 9 AM"
  echo "  /fabric:create-schedule <ws-id> <pipe-id> --cron \"0 9 * * 1\""
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

# Validate cron expression format (basic validation)
if ! [[ "$cron_expression" =~ ^[0-9\*,\-/\ ]+$ ]]; then
  echo "❌ Invalid cron expression format"
  echo "   Expected format: minute hour day month dayofweek"
  echo "   Example: \"0 2 * * *\" (daily at 2 AM)"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📅 Creating pipeline schedule..."

# Create schedule configuration
request_body=$(jq -n \
  --arg cron "$cron_expression" \
  --arg tz "$timezone" \
  --argjson enabled "$enabled" \
  '{
    enabled: $enabled,
    configuration: {
      type: "Cron",
      cronExpression: $cron,
      timezone: $tz
    }
  }')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/Pipeline/schedules" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
  schedule_id=$(echo "$response_body" | jq -r '.id // "N/A"')
  schedule_enabled=$(echo "$response_body" | jq -r '.enabled')

  echo "✅ Schedule created successfully"
  echo ""
  echo "╔═══════════════════════════════════════════════════════════╗"
  echo "║              PIPELINE SCHEDULE CREATED                    ║"
  echo "╚═══════════════════════════════════════════════════════════╝"
  echo ""
  echo "Schedule ID:     $schedule_id"
  echo "Cron Expression: $cron_expression"
  echo "Timezone:        $timezone"
  echo "Status:          $([ "$schedule_enabled" = "true" ] && echo "Enabled ✓" || echo "Disabled")"
  echo ""
  echo "═══════════════════════════════════════════════════════════"

  if [ "$schedule_enabled" = "false" ]; then
    echo ""
    echo "💡 Schedule is disabled. Enable it with:"
    echo "   /fabric:toggle-schedule $workspace_id $pipeline_id $schedule_id --enable"
  fi

  echo ""
  echo "💡 Next steps:"
  echo "  • List all schedules: /fabric:list-schedules $workspace_id $pipeline_id"
  echo "  • Modify schedule: /fabric:update-schedule $workspace_id $pipeline_id $schedule_id"
  echo "  • Delete schedule: /fabric:delete-schedule $workspace_id $pipeline_id $schedule_id"
  echo "  • View executions: /fabric:get-run-history $workspace_id $pipeline_id"
else
  echo "❌ Failed to create schedule (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"

  if [[ "$error_msg" == *"cron"* ]] || [[ "$error_msg" == *"expression"* ]]; then
    echo ""
    echo "💡 Cron expression format: minute hour day month dayofweek"
    echo "   Examples:"
    echo "   • \"0 2 * * *\"      - Daily at 2 AM"
    echo "   • \"0 */4 * * *\"    - Every 4 hours"
    echo "   • \"0 9 * * 1-5\"    - Weekdays at 9 AM"
    echo "   • \"30 14 1 * *\"    - 1st of month at 2:30 PM"
  fi

  exit 1
fi
```

## Cron Expression Format

**Format**: `minute hour day month dayofweek`
- **minute**: 0-59
- **hour**: 0-23 (24-hour format)
- **day**: 1-31
- **month**: 1-12
- **dayofweek**: 0-6 (0 = Sunday)

**Special Characters:**
- `*` - Any value
- `,` - Value list separator (e.g., "1,3,5")
- `-` - Range (e.g., "1-5")
- `/` - Step values (e.g., "*/15" = every 15)

## Common Schedule Examples

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every hour | `0 * * * *` | Top of every hour |
| Every 6 hours | `0 */6 * * *` | 00:00, 06:00, 12:00, 18:00 |
| Daily at 2 AM | `0 2 * * *` | Once per day |
| Weekdays at 9 AM | `0 9 * * 1-5` | Monday-Friday |
| First of month | `0 0 1 * *` | Monthly at midnight |
| Every 15 minutes | `*/15 * * * *` | Four times per hour |

## Timezone Support

Specify timezone using IANA timezone identifiers:
- `UTC` (default)
- `America/New_York`
- `Europe/London`
- `Asia/Tokyo`
- Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## Related Commands
- `/fabric:list-schedules <workspace-id> <pipeline-id>` - View all schedules
- `/fabric:update-schedule <workspace-id> <pipeline-id> <schedule-id>` - Modify schedule
- `/fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-id>` - Remove schedule
- `/fabric:toggle-schedule <workspace-id> <pipeline-id> <schedule-id>` - Enable/disable

## API Reference
- **Endpoint**: `POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/Pipeline/schedules`
- **Response**: 201 Created
- **Permissions**: Contributor, Member, or Admin role

## Notes
- Schedules are created in disabled state by default (use `--enabled` to activate immediately)
- Minimum interval: 1 minute (consider rate limits for frequent executions)
- Schedules use UTC by default; specify timezone if needed
- Failed executions don't stop future scheduled runs
- Multiple schedules can be configured per pipeline
- Schedule times are in 24-hour format
