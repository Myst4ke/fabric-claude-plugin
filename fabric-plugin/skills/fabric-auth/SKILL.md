---
name: fabric-auth
description: Authenticate with Microsoft Fabric API using Entra ID OAuth 2.0 (service principal or delegated user auth)
---

# Fabric Auth (infrastructure)

**Do not invoke this skill directly** — it is infrastructure used by the other fabric-plugin skills. For interactive sign-in, use the `fabric-login` skill (`/fabric-plugin:\setup:login`).

## Implementation

Since the fabric_base migration, the token logic lives in the shared modules:

- `skills/_shared/token_manager.py` — multi-audience token management:
  one shared refresh token, exchanged silently for access tokens per audience
  (fabric, sql, storage, graph, kusto). The refresh token is only deleted on
  proven-terminal AADSTS errors; cache writes are atomic and audience-validated.
- `skills/_shared/fabric_base.py` — `get_token(audience=...)` plus
  `fabric_request()` (retry + transparent 401 refresh).

## Token caches (in `~/.fabric-plugin`, override with `FABRIC_PLUGIN_CACHE_DIR`)

- `fabric-plugin-token-delegated.json` (fabric), `-sql`, `-storage`,
  `-graph`, `-kusto` — per-audience access tokens
- `fabric-plugin-refresh-token.json` — shared refresh token

## Usage by skills

```python
from fabric_base import get_token
token = get_token()              # fabric audience
token = get_token(audience='sql')
```
