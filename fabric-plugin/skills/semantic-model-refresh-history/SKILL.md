---
name: semantic-model-refresh-history
description: Get refresh history of a semantic model (Power BI dataset)
---

# semantic-model-refresh-history Skill

## Purpose
Show the refresh history of a semantic model: past and ongoing refreshes with status and duration.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/semantic-model-refresh-history/semantic_model_refresh_history.py" "$@"
```

## Usage

```
semantic_model_refresh_history.py <workspace> <semanticmodel> [--top N]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<semanticmodel>` (required): Semantic model **name or GUID**
- `--top N` (optional): Number of recent refreshes to show (default: 10)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/semantic-model-refresh-history/semantic_model_refresh_history.py" "My Workspace" "Sales Analysis"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/semantic-model-refresh-history/semantic_model_refresh_history.py" a1b2-... b2c3-... --top 5
```

## Returns
- Success: Exit code 0, formatted table of refreshes (status, type, start/end, duration)
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:setup:login)
