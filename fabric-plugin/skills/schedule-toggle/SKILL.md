---
name: schedule-toggle
description: Enable or disable a pipeline schedule
---

# schedule-toggle Skill

## Purpose
Flip (or force) the enabled state of a pipeline schedule. The schedule id is
optional when the pipeline has exactly one schedule.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-toggle/schedule_toggle.py" "$@"
```

## Usage

```
schedule_toggle.py <workspace> <pipeline> [<schedule_id>] [--enable | --disable]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<schedule_id>` (optional): Schedule ID; required only if the pipeline has several schedules
- `--enable` / `--disable`: force the state instead of flipping it

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-toggle/schedule_toggle.py" "My Workspace" "Daily ETL"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-toggle/schedule_toggle.py" "My Workspace" "Daily ETL" <schedule-id> --disable
```

## Returns
- Success: Exit code 0, new enabled state
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
