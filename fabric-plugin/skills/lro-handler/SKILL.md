---
name: lro-handler
description: Handle Microsoft Fabric long-running operations (LRO) with intelligent polling and progress reporting
---

# LRO Handler (infrastructure)

**Do not invoke this skill directly** — it is infrastructure used by the other fabric-plugin skills.

## Implementation

Since the fabric_base migration, the LRO logic lives in the shared modules:

- `skills/_shared/fabric_base.py`:
  - `fabric_request()` — returns the raw response so callers can read the
    `Location` / `Retry-After` headers of a 202 Accepted response
  - skill scripts poll the `Location` URL with `fabric_request_json()` until
    status is `Succeeded` / `Failed` / `Cancelled`
- `skills/_shared/retry_handler.py` — exponential backoff on transient errors

## Usage by skills

```python
from fabric_base import fabric_request, fabric_request_json
resp = fabric_request(url, method='POST', data=body)
if resp.status == 202:
    location = resp.headers.get('Location')
    # poll fabric_request_json(location) until terminal status
```
