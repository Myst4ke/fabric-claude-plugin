---
name: kql-database-create
description: Create a new KQL database in a workspace
---

# kql-database-create Skill

## Purpose
Create a KQL database (long-running operation polled automatically).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/kql-database-create/kql_database_create.py" "$@"
```

## Usage

```
kql_database_create.py <workspace> <name> [description] [--eventhouse-id ID]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<name>` (required): KQL database display name
- `[description]` (optional): Database description
- `--eventhouse-id ID` (optional): Parent eventhouse item ID (GUID)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/kql-database-create/kql_database_create.py" "My Workspace" "EventsDB"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/kql-database-create/kql_database_create.py" a1b2c3d4-... "EventsDB" --eventhouse-id e5f6a7b8-...
```

## Returns
- Success: Exit code 0, created database name + ID
- Error: Exit code 1-3, error message (1 on name conflict)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, conflict, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
