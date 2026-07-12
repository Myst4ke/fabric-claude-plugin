---
name: semantic-model-get
description: Get detailed information about a semantic model (Power BI dataset)
---

# semantic-model-get Skill

## Purpose
Get detailed information about a semantic model (name, ID, description, storage mode, refreshability).

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/semantic-model-get/semantic_model_get.py" "$@"
```

## Usage

```
semantic_model_get.py <workspace> <semanticmodel>
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `<semanticmodel>` (required): Semantic model **name or GUID**

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/semantic-model-get/semantic_model_get.py" "My Workspace" "Sales Analysis"
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/semantic-model-get/semantic_model_get.py" a1b2c3d4-... b2c3d4e5-...
```

## Returns
- Success: Exit code 0, semantic model details
- Error: Exit code 1-3, error message

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
