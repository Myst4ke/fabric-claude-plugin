---
name: resolve-name
description: Resolve resource names to GUIDs with fuzzy matching
version: 1.0.0
author: Fabric Plugin
---

# Resolve Name Skill

Resolve Microsoft Fabric resource names to their GUIDs with fuzzy matching support.

## Purpose

Allows users to use human-readable names instead of GUIDs when working with Fabric resources. Supports typo tolerance, partial matching, and disambiguation.

## Usage

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/resolve-name/resolve_name.py" <resource-type> <name> [options]
```

## Resource Types

| Type | Description | Required Context |
|------|-------------|------------------|
| workspace | Workspace | None |
| notebook | Notebook | --workspace |
| pipeline | Data Pipeline | --workspace |
| lakehouse | Lakehouse | --workspace |
| warehouse | Warehouse | --workspace |
| table | Lakehouse Table | --workspace --lakehouse |

## Options

| Option | Description |
|--------|-------------|
| --workspace | Workspace name or ID (required for most types) |
| --lakehouse | Lakehouse name or ID (required for tables) |
| --json | Output as JSON |
| --quiet | Only output the resolved ID |

## Examples

```bash
# Resolve workspace by name
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/resolve-name/resolve_name.py" workspace "My Workspace"

# Resolve notebook (needs workspace context)
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/resolve-name/resolve_name.py" notebook "Sales Analysis" --workspace "My Workspace"

# Fuzzy match with typo
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/resolve-name/resolve_name.py" notebook "Saels Analaysis" --workspace "My Workspace"

# Resolve table (needs workspace + lakehouse)
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/resolve-name/resolve_name.py" table "customers" --workspace "Production" --lakehouse "Bronze"

# JSON output for scripting
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/resolve-name/resolve_name.py" notebook "Sales" --workspace "Prod" --json

# Quiet mode (just the ID)
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/resolve-name/resolve_name.py" workspace "My Workspace" --quiet
```

## Output Format

### Standard Output
```
Resolved 'My Workspace' -> a1b2c3d4-e5f6-7890-abcd-ef1234567890
  Match type: exact
  Display name: My Workspace
```

### JSON Output (--json)
```json
{
  "status": "resolved",
  "type": "workspace",
  "query": "My Workspace",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "displayName": "My Workspace",
  "matchType": "exact",
  "score": 1.0
}
```

### Ambiguous Match Output
```
Multiple matches found for 'Sales':
  1. Sales Analysis (score: 0.85)
     ID: a1b2c3d4-...
  2. Sales Report (score: 0.80)
     ID: b2c3d4e5-...

Use a more specific name or the full ID.
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Resolved successfully |
| 1 | No matches found |
| 2 | Multiple matches (disambiguation needed) |
| 3 | Authentication error |
| 4 | API or other error |

## Fuzzy Matching

The resolver uses a priority-based matching algorithm:

1. **Exact match** (score: 1.0) - Case-insensitive exact match
2. **Starts with** (score: 0.7-0.95) - Name begins with query
3. **Contains** (score: 0.6-0.85) - Name contains query
4. **Fuzzy** (score: 0.5-0.8) - Similar names (typo tolerance)

If the top match has a score > 0.9, it's automatically selected.
Otherwise, disambiguation may be required.

## Caching

Results are cached for 5 minutes to reduce API calls:
- Cache location: `{TEMP}/fabric-resolver-cache.json`
- Separate cache entries per workspace/resource type

## Integration with Other Skills

This skill is used internally by other skills when they detect a name instead of a GUID. You can also use it directly for resolution before calling other skills.
