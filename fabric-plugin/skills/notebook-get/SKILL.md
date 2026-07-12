---
name: notebook-get
description: Get detailed information about a notebook
---

# notebook-get Skill

## Purpose
Get detailed information about a notebook (name, ID, description, workspace) plus raw JSON.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-get/notebook_get.py" "$@"
```

## Usage

```
notebook_get.py <workspace> <notebook>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Notebook **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-get/notebook_get.py" "My Workspace" "Sales Analysis"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-get/notebook_get.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, notebook details + raw JSON
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
