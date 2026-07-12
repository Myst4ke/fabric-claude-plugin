---
name: error-handler
description: Handle Microsoft Fabric API errors with retry logic and user-friendly messages
---

# Error Handler (infrastructure)

**Do not invoke this skill directly** — it is infrastructure used by the other fabric-plugin skills.

## Implementation

Since the fabric_base migration, the error-handling logic lives in the shared modules:

- `skills/_shared/fabric_base.py`:
  - `handle_http_error(error, resource_type)` — the full error matrix
    (401 -> exit 3, 403/404 -> exit 1, 429/5xx -> exit 2, details for the rest)
  - `fabric_request()` — automatic retry (429/500/502/503/504 with backoff and
    Retry-After support) and transparent token refresh on 401
- `skills/_shared/retry_handler.py` — exponential backoff implementation

## Usage by skills

```python
from fabric_base import fabric_request_json, handle_http_error
try:
    data = fabric_request_json(url)
except urllib.error.HTTPError as e:
    sys.exit(handle_http_error(e, "Notebook"))
```
