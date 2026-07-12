---
name: schedule-create
description: Create a new schedule for a data pipeline
---

# schedule-create Skill

## Purpose
Create a schedule for a data pipeline via the Fabric job scheduler API.
Note: Fabric does **not** accept unix cron expressions — recurrence is
expressed as an interval (`--every`), daily times (`--daily`) or weekly
days + times (`--weekly`).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-create/schedule_create.py" "$@"
```

## Usage

```
schedule_create.py <workspace> <pipeline> (--every MINUTES | --daily HH:MM [HH:MM ...] | --weekly DAYS HH:MM [HH:MM ...])
                   [--start ISO] [--end ISO] [--timezone TZ] [--disabled]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `--every MINUTES`: run every N minutes
- `--daily HH:MM [...]`: run daily at the given time(s)
- `--weekly DAYS HH:MM [...]`: DAYS is comma-separated (Mon,Fri or Monday,Friday), followed by time(s)
- `--start` / `--end`: schedule window `YYYY-MM-DDTHH:MM:SS` (defaults: now → +5 years)
- `--timezone TZ`: time zone id (default `UTC`, e.g. `Romance Standard Time`)
- `--disabled`: create the schedule disabled

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-create/schedule_create.py" "My Workspace" "Daily ETL" --daily 06:00
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-create/schedule_create.py" "My Workspace" "Hourly sync" --every 60
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-create/schedule_create.py" a1b2c3d4-... b2c3d4e5-... --weekly Mon,Fri 08:30
```

## Returns
- Success: Exit code 0, schedule id + recurrence summary
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, invalid options)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
