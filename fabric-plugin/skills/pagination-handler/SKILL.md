---
name: pagination-handler
description: Handle Microsoft Fabric API pagination for list operations with continuationToken
---

# Pagination Handler (infrastructure)

**Do not invoke this skill directly** — it is infrastructure used by the other fabric-plugin skills.

## Implementation

Since the fabric_base migration, the pagination logic lives in the shared module:

- `skills/_shared/fabric_base.py`:
  - `fabric_list(url, limit=None, item_key='value')` — fetches ALL pages of a
    Fabric list endpoint, following `continuationToken` (URL-encoded) until
    exhausted, with the same retry/refresh guarantees as `fabric_request()`.
    Stops early when `limit` is reached.

## Usage by skills

```python
from fabric_base import FABRIC_API_BASE, fabric_list
items = fabric_list(f"{FABRIC_API_BASE}/workspaces/{ws_id}/lakehouses", limit=10)
```
