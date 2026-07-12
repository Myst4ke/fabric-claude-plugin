---
name: notebook-definition-get
description: Get notebook definition (.ipynb format)
---

# notebook-definition-get Skill

## Purpose
Retrieve and display the decoded definition (notebook content parts) of a notebook.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-definition-get/notebook_definition_get.py" "$@"
```

## Usage

```
notebook_definition_get.py <workspace> <notebook>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<notebook>` (required): Notebook **name or GUID** (names are resolved automatically)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-definition-get/notebook_definition_get.py" "My Workspace" "Sales Analysis"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/notebook-definition-get/notebook_definition_get.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, decoded definition parts (base64 payloads decoded and pretty-printed)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
