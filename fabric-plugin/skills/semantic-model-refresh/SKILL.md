---
name: semantic-model-refresh
description: Trigger a refresh of a semantic model (Power BI dataset)
---

# semantic-model-refresh Skill

## Purpose
Trigger an asynchronous Full refresh of a semantic model. Use refresh-history to check progress.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/semantic-model-refresh/semantic_model_refresh.py" "$@"
```

## Usage

```
semantic_model_refresh.py <workspace> <semanticmodel>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<semanticmodel>` (required): Semantic model **name or GUID**

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/semantic-model-refresh/semantic_model_refresh.py" "My Workspace" "Sales Analysis"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/semantic-model-refresh/semantic_model_refresh.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, refresh triggered (asynchronous) + request ID
- Error: Exit code 1-3, error message (1 if model not refreshable or refresh already in progress)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, not refreshable, refresh in progress)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
