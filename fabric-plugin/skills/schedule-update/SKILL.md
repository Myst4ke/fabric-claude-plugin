---
name: schedule-update
description: Update a pipeline schedule (recurrence, window, timezone, enabled)
---

# schedule-update Skill

## Purpose
Update an existing pipeline schedule via the Fabric job scheduler API:
change the recurrence, the start/end window, the timezone or the enabled
state. Note: Fabric does **not** accept unix cron expressions.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-update/schedule_update.py" "$@"
```

## Usage

```
schedule_update.py <workspace> <pipeline> <schedule_id>
                   [--every MINUTES | --daily HH:MM [...] | --weekly DAYS HH:MM [...]]
                   [--start ISO] [--end ISO] [--timezone TZ] [--enable | --disable]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<schedule_id>` (required): Schedule ID (see `fabric-plugin:schedule-list`)
- Recurrence options replace the whole recurrence; window/timezone options alone patch only those fields

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-update/schedule_update.py" "My Workspace" "Daily ETL" <schedule-id> --daily 07:30
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-update/schedule_update.py" "My Workspace" "Daily ETL" <schedule-id> --timezone "Romance Standard Time"
```

## Returns
- Success: Exit code 0, updated schedule summary
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, invalid options)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
