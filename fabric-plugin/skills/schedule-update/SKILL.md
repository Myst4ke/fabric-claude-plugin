---
name: schedule-update
description: Update a pipeline schedule's cron expression
---

# schedule-update Skill

## Purpose
Update the cron expression of an existing pipeline schedule (other settings are preserved).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-update/schedule_update.py" "$@"
```

## Usage

```
schedule_update.py <workspace> <pipeline> <schedule_id> <cron_expression>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<schedule_id>` (required): The schedule GUID
- `<cron_expression>` (required): New cron expression, quoted

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-update/schedule_update.py" "My Workspace" "Daily ETL" c3d4e5f6-... "0 6 * * *"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-update/schedule_update.py" a1b2c3d4-... b2c3d4e5-... c3d4e5f6-... "0 */6 * * *"
```

## Returns
- Success: Exit code 0, update confirmation (schedule ID, new cron)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, invalid cron)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
