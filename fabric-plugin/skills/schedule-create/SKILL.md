---
name: schedule-create
description: Create a new schedule for a data pipeline
---

# schedule-create Skill

## Purpose
Create a cron schedule for a data pipeline (enabled, UTC timezone).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-create/schedule_create.py" "$@"
```

## Usage

```
schedule_create.py <workspace> <pipeline> <cron_expression>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<cron_expression>` (required): Cron expression, quoted (format: `minute hour day-of-month month day-of-week`)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-create/schedule_create.py" "My Workspace" "Daily ETL" "0 0 * * *"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-create/schedule_create.py" a1b2c3d4-... b2c3d4e5-... "0 9 * * 1-5"
```

## Returns
- Success: Exit code 0, schedule confirmation (cron, enabled, timezone)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, invalid cron)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
