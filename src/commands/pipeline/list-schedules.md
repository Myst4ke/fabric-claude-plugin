---
description: List all schedules for a pipeline
argument-hint: <workspace-id> <pipeline-id> [--format table|json]
---

# /fabric:list-schedules

## Purpose
View all configured schedules for a data pipeline, including their status, timing, and configuration.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `pipeline-id`: Required. GUID of the pipeline
- `--format <type>`: Optional. Output format: table (default) or json

## Instructions

```bash
workspace_id="$1"
pipeline_id="$2"
format="table"

# Parse optional format argument
shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --format)
      format="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:list-schedules <workspace-id> <pipeline-id> [--format table|json]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$pipeline_id" ]; then
  echo "❌ Workspace ID and pipeline ID are required"
  echo "Usage: /fabric:list-schedules <workspace-id> <pipeline-id> [--format table|json]"
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

# Validate format
if [ "$format" != "table" ] && [ "$format" != "json" ]; then
  echo "❌ Invalid format. Use 'table' or 'json'"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📅 Fetching pipeline schedules..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$pipeline_id/jobs/Pipeline/schedules" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to get schedules (HTTP $http_code)"
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi

schedule_count=$(echo "$response_body" | jq '.value | length')

echo "✅ Found $schedule_count schedule(s)"
echo ""

if [ "$schedule_count" -eq 0 ]; then
  echo "No schedules configured for this pipeline."
  echo ""
  echo "💡 Create a schedule:"
  echo "   /fabric:create-schedule $workspace_id $pipeline_id --cron \"0 2 * * *\""
  exit 0
fi

if [ "$format" = "json" ]; then
  echo "$response_body" | jq '.'
  exit 0
fi

# Table format
echo "Pipeline Schedules"
echo "══════════════════════════════════════════════════════════"
echo ""

# Count enabled vs disabled
enabled_count=$(echo "$response_body" | jq '[.value[] | select(.enabled == true)] | length')
disabled_count=$((schedule_count - enabled_count))

echo "Status Summary: $enabled_count enabled, $disabled_count disabled"
echo ""

echo "$response_body" | jq -r '
  ["SCHEDULE ID", "STATUS", "CRON EXPRESSION", "TIMEZONE", "NEXT RUN"],
  ["────────────", "──────", "───────────────", "────────", "────────"],
  (.value[] | [
    .id[0:24] + "...",
    (if .enabled then "✓ Enabled" else "⊗ Disabled" end),
    .configuration.cronExpression,
    .configuration.timezone // "UTC",
    (.nextRunTime[0:19] // "N/A")
  ])
  | @tsv
' | column -t -s $'\t'

echo ""
echo "══════════════════════════════════════════════════════════"

# Show schedule details if only 1-2 schedules
if [ "$schedule_count" -le 2 ]; then
  echo ""
  echo "Schedule Details:"
  echo ""

  echo "$response_body" | jq -r '.value[] |
    "─────────────────────────────────────────────────────────\n" +
    "Schedule ID:     \(.id)\n" +
    "Status:          \(if .enabled then "✓ Enabled" else "⊗ Disabled" end)\n" +
    "Cron Expression: \(.configuration.cronExpression)\n" +
    "Timezone:        \(.configuration.timezone // "UTC")\n" +
    "Next Run:        \(.nextRunTime // "N/A")\n" +
    "Last Modified:   \(.lastModifiedTime // "N/A")\n"
  '
fi

echo ""
echo "💡 Manage schedules:"
echo "  • Enable/disable: /fabric:toggle-schedule $workspace_id $pipeline_id <schedule-id>"
echo "  • Update timing: /fabric:update-schedule $workspace_id $pipeline_id <schedule-id>"
echo "  • Delete: /fabric:delete-schedule $workspace_id $pipeline_id <schedule-id>"
echo "  • View executions: /fabric:get-run-history $workspace_id $pipeline_id"
```

## Output Formats

### Table Format (Default)
```
Pipeline Schedules
══════════════════════════════════════════════════════════

Status Summary: 2 enabled, 1 disabled

SCHEDULE ID                 STATUS       CRON EXPRESSION  TIMEZONE  NEXT RUN
────────────────────────────────────────────────────────────────────────────
abc123...                   ✓ Enabled    0 2 * * *        UTC       2024-01-15T02:00:00
def456...                   ✓ Enabled    0 */6 * * *      UTC       2024-01-14T18:00:00
ghi789...                   ⊗ Disabled   0 9 * * 1-5      EST       N/A
```

### JSON Format
```json
{
  "value": [
    {
      "id": "abc123-schedule-id",
      "enabled": true,
      "configuration": {
        "type": "Cron",
        "cronExpression": "0 2 * * *",
        "timezone": "UTC"
      },
      "nextRunTime": "2024-01-15T02:00:00Z",
      "lastModifiedTime": "2024-01-10T12:00:00Z"
    }
  ]
}
```

## Schedule Status Indicators
- **✓ Enabled**: Schedule is active and will trigger automatically
- **⊗ Disabled**: Schedule exists but won't trigger (manually disabled)

## Common Cron Patterns

| Pattern | Expression | Description |
|---------|-----------|-------------|
| Hourly | `0 * * * *` | Every hour at :00 |
| Daily | `0 2 * * *` | Every day at 2 AM |
| Weekly | `0 9 * * 1` | Every Monday at 9 AM |
| Monthly | `0 0 1 * *` | 1st of month at midnight |
| Weekdays | `0 9 * * 1-5` | Monday-Friday at 9 AM |
| Every 6 hours | `0 */6 * * *` | 00:00, 06:00, 12:00, 18:00 |

## Related Commands
- `/fabric:create-schedule <workspace-id> <pipeline-id>` - Create new schedule
- `/fabric:update-schedule <workspace-id> <pipeline-id> <schedule-id>` - Modify schedule
- `/fabric:delete-schedule <workspace-id> <pipeline-id> <schedule-id>` - Remove schedule
- `/fabric:toggle-schedule <workspace-id> <pipeline-id> <schedule-id>` - Enable/disable
- `/fabric:get-run-history <workspace-id> <pipeline-id>` - View execution history

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}/jobs/Pipeline/schedules`
- **Response**: 200 OK with schedule array
- **Permissions**: Any workspace role

## Notes
- Next run time is calculated based on cron expression and timezone
- Disabled schedules don't show next run time
- Last modified time tracks schedule configuration changes
- Schedules persist even when pipeline is not running
- Maximum recommended schedules per pipeline: 5-10
