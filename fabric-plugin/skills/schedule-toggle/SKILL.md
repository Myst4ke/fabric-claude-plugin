---
name: schedule-toggle
description: Enable or disable a pipeline schedule
---

# schedule-toggle Skill

## Purpose
Enable or disable a pipeline schedule without deleting it (existing configuration is preserved).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-toggle/schedule_toggle.py" "$@"
```

## Usage

```
schedule_toggle.py <workspace> <pipeline> <schedule_id> {true,false}
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `<schedule_id>` (required): The schedule GUID
- `<enabled>` (required): `true` to enable, `false` to disable

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-toggle/schedule_toggle.py" "My Workspace" "Daily ETL" c3d4e5f6-... false
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/schedule-toggle/schedule_toggle.py" a1b2c3d4-... b2c3d4e5-... c3d4e5f6-... true
```

## Returns
- Success: Exit code 0, status confirmation (ENABLED/DISABLED)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, no configuration to enable)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
