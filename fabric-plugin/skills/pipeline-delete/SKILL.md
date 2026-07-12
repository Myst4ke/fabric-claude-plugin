---
name: pipeline-delete
description: Delete a data pipeline from a Microsoft Fabric workspace
---

# pipeline-delete Skill

## Purpose
Permanently delete a data pipeline from a workspace.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-delete/pipeline_delete.py" "$@"
```

## Usage

```
pipeline_delete.py <workspace> <pipeline> [--force]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<pipeline>` (required): Pipeline **name or GUID** (names are resolved automatically)
- `--force` (optional): Skip confirmation warning

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-delete/pipeline_delete.py" "My Workspace" "Old Pipeline"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/pipeline-delete/pipeline_delete.py" a1b2c3d4-... b2c3d4e5-... --force
```

## Returns
- Success: Exit code 0, deletion confirmation
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
