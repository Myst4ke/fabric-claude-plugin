#!/usr/bin/env python3
"""
Fabric Name Resolver Module

Provides fuzzy name-to-ID resolution for Microsoft Fabric resources.
Supports workspaces, notebooks, pipelines, lakehouses, tables, and more.

Features:
- GUID passthrough (if already a GUID, returns as-is)
- Fuzzy matching with difflib (typo tolerance)
- Caching with TTL (5 minutes default)
- Hierarchical resolution (workspace -> item -> sub-item)
"""

import os
import sys
import json
import re
import time
import urllib.request
import urllib.error
from difflib import SequenceMatcher
from typing import Optional, List, Dict, Tuple, Any

# Configuration
FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
try:
    from token_manager import CACHE_DIR
except ImportError:
    CACHE_DIR = os.getenv("TEMP", "/tmp")
TOKEN_FILE = f"{CACHE_DIR}/fabric-plugin-token-delegated.json"
CACHE_FILE = f"{CACHE_DIR}/fabric-resolver-cache.json"
CACHE_TTL = 300  # 5 minutes

# GUID pattern (8-4-4-4-12 hex format)
GUID_PATTERN = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
)

# Item type to API endpoint mapping
ITEM_TYPE_ENDPOINTS = {
    'notebook': 'notebooks',
    'pipeline': 'dataPipelines',
    'lakehouse': 'lakehouses',
    'warehouse': 'warehouses',
    'semanticmodel': 'semanticModels',
    'report': 'reports',
    'dashboard': 'dashboards',
    'dataflow': 'dataflows',
    'dataset': 'datasets',
    'environment': 'environments',
    'kqldatabase': 'kqlDatabases',
    'eventhouse': 'eventhouses',
    'sparkjobdefinition': 'sparkJobDefinitions',
    'mlmodel': 'mlModels',
    'mlexperiment': 'mlExperiments',
}


class ResolverError(Exception):
    """Base exception for resolver errors."""
    pass


class AuthenticationError(ResolverError):
    """Authentication failed or token expired."""
    pass


class NotFoundError(ResolverError):
    """Resource not found."""
    pass


class AmbiguousMatchError(ResolverError):
    """Multiple matches found, disambiguation needed."""
    def __init__(self, message: str, matches: List[Dict]):
        super().__init__(message)
        self.matches = matches


def is_guid(value: str) -> bool:
    """Check if a string is a valid GUID."""
    if not value or not isinstance(value, str):
        return False
    return bool(GUID_PATTERN.match(value.strip()))


def load_token() -> str:
    """Load access token with automatic silent refresh via token_manager."""
    try:
        from token_manager import get_fabric_token
        return get_fabric_token()
    except SystemExit:
        raise AuthenticationError("Not authenticated. Run /fabric-plugin:setup:login")
    except ImportError:
        # Degraded fallback: read the cache file directly (no refresh)
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
            if token_data.get('expires_at', 0) < time.time():
                raise AuthenticationError("Token expired. Run /fabric-plugin:setup:login")
            return token_data['access_token']
        except FileNotFoundError:
            raise AuthenticationError("Not authenticated. Run /fabric-plugin:setup:login")
        except json.JSONDecodeError:
            raise AuthenticationError("Invalid token file. Run /fabric-plugin:setup:login")


class FabricCache:
    """Simple TTL-based cache for API responses."""

    def __init__(self, cache_file: str = CACHE_FILE, ttl: int = CACHE_TTL):
        self.cache_file = cache_file
        self.ttl = ttl
        self._cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load cache from file."""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except Exception:
            pass  # Cache save failures are non-fatal

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if time.time() > entry.get('expires_at', 0):
            del self._cache[key]
            return None

        return entry.get('data')

    def set(self, key: str, data: Any):
        """Set cached value with TTL."""
        self._cache[key] = {
            'data': data,
            'expires_at': time.time() + self.ttl,
            'cached_at': time.time()
        }
        self._save_cache()

    def clear(self):
        """Clear all cached data."""
        self._cache = {}
        self._save_cache()


def fuzzy_match(query: str, items: List[Dict], key: str = 'displayName',
                threshold: float = 0.6) -> List[Tuple[Dict, str, float]]:
    """
    Find best matches for a query string among items.

    Args:
        query: Search string
        items: List of dicts with 'displayName' (or custom key)
        key: Dict key containing the name to match
        threshold: Minimum similarity ratio for fuzzy matches

    Returns:
        List of (item, match_type, score) tuples, sorted by score descending
    """
    if not query or not items:
        return []

    query_lower = query.lower().strip()
    results = []

    for item in items:
        name = item.get(key, '')
        if not name:
            continue

        name_lower = name.lower()

        # Priority 1: Exact match (case-insensitive)
        if name_lower == query_lower:
            results.append((item, 'exact', 1.0))
            continue

        # Priority 2: Starts with
        if name_lower.startswith(query_lower):
            # Score based on how much of the name is matched
            score = len(query_lower) / len(name_lower) * 0.95
            results.append((item, 'starts_with', score))
            continue

        # Priority 3: Contains
        if query_lower in name_lower:
            # Score based on query length relative to name
            score = len(query_lower) / len(name_lower) * 0.85
            results.append((item, 'contains', score))
            continue

        # Priority 4: Fuzzy match using SequenceMatcher
        ratio = SequenceMatcher(None, query_lower, name_lower).ratio()
        if ratio >= threshold:
            results.append((item, 'fuzzy', ratio * 0.8))

    # Sort by score descending
    results.sort(key=lambda x: x[2], reverse=True)
    return results


def api_request(url: str, token: str) -> Dict:
    """Make authenticated API request."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    try:
        request = urllib.request.Request(url, headers=headers, method='GET')
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise AuthenticationError("Token expired. Run /fabric-plugin:setup:login")
        elif e.code == 403:
            raise ResolverError(f"Access forbidden: {url}")
        elif e.code == 404:
            raise NotFoundError(f"Resource not found: {url}")
        elif e.code == 429:
            retry_after = e.headers.get('Retry-After', '30')
            raise ResolverError(f"Rate limited. Retry after {retry_after} seconds.")
        else:
            raise ResolverError(f"API error {e.code}: {e.reason}")


def list_workspaces(token: str, cache: Optional[FabricCache] = None) -> List[Dict]:
    """List all accessible workspaces."""
    cache_key = 'workspaces'

    if cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    url = f"{FABRIC_API_BASE}/workspaces"
    all_workspaces = []

    while url:
        data = api_request(url, token)
        all_workspaces.extend(data.get('value', []))

        # Handle pagination
        continuation = data.get('continuationUri') or data.get('continuationToken')
        if continuation:
            if continuation.startswith('http'):
                url = continuation
            else:
                url = f"{FABRIC_API_BASE}/workspaces?continuationToken={continuation}"
        else:
            url = None

    if cache:
        cache.set(cache_key, all_workspaces)

    return all_workspaces


def list_items(workspace_id: str, item_type: str, token: str,
               cache: Optional[FabricCache] = None) -> List[Dict]:
    """List items of a specific type in a workspace."""
    endpoint = ITEM_TYPE_ENDPOINTS.get(item_type.lower())
    if not endpoint:
        raise ResolverError(f"Unknown item type: {item_type}")

    cache_key = f"workspace_{workspace_id}_{item_type}"

    if cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/{endpoint}"
    all_items = []

    while url:
        data = api_request(url, token)
        all_items.extend(data.get('value', []))

        # Handle pagination
        continuation = data.get('continuationUri') or data.get('continuationToken')
        if continuation:
            if continuation.startswith('http'):
                url = continuation
            else:
                url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/{endpoint}?continuationToken={continuation}"
        else:
            url = None

    if cache:
        cache.set(cache_key, all_items)

    return all_items


def list_tables(workspace_id: str, lakehouse_id: str, token: str,
                cache: Optional[FabricCache] = None) -> List[Dict]:
    """List tables in a lakehouse."""
    cache_key = f"lakehouse_{lakehouse_id}_tables"

    if cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/tables"
    all_tables = []

    while url:
        data = api_request(url, token)
        all_tables.extend(data.get('value', []))

        continuation = data.get('continuationUri') or data.get('continuationToken')
        if continuation:
            if continuation.startswith('http'):
                url = continuation
            else:
                url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/tables?continuationToken={continuation}"
        else:
            url = None

    if cache:
        cache.set(cache_key, all_tables)

    return all_tables


def resolve_workspace(name_or_id: str, token: Optional[str] = None,
                      cache: Optional[FabricCache] = None) -> Dict:
    """
    Resolve workspace name to full workspace object.

    Args:
        name_or_id: Workspace name or GUID
        token: Access token (loaded automatically if not provided)
        cache: Optional cache instance

    Returns:
        Workspace dict with 'id', 'displayName', etc.

    Raises:
        NotFoundError: If no match found
        AmbiguousMatchError: If multiple matches found
    """
    # GUID passthrough
    if is_guid(name_or_id):
        return {'id': name_or_id, 'displayName': None, '_resolved_by': 'guid'}

    if token is None:
        token = load_token()

    if cache is None:
        cache = FabricCache()

    workspaces = list_workspaces(token, cache)
    matches = fuzzy_match(name_or_id, workspaces)

    if not matches:
        raise NotFoundError(f"No workspace found matching '{name_or_id}'")

    # If top match is exact or very high confidence, use it
    top_match, match_type, score = matches[0]
    if match_type == 'exact' or score > 0.9:
        top_match['_resolved_by'] = match_type
        top_match['_match_score'] = score
        return top_match

    # If multiple close matches, raise ambiguity error
    close_matches = [(m, t, s) for m, t, s in matches if s > 0.5]
    if len(close_matches) > 1:
        raise AmbiguousMatchError(
            f"Multiple workspaces match '{name_or_id}'",
            [{'name': m['displayName'], 'id': m['id'], 'score': s}
             for m, t, s in close_matches[:5]]
        )

    # Return best match
    top_match['_resolved_by'] = match_type
    top_match['_match_score'] = score
    return top_match


def resolve_item(name_or_id: str, workspace_id: str, item_type: str,
                 token: Optional[str] = None,
                 cache: Optional[FabricCache] = None) -> Dict:
    """
    Resolve item name to full item object.

    Args:
        name_or_id: Item name or GUID
        workspace_id: Workspace GUID (must already be resolved)
        item_type: Type of item (notebook, pipeline, lakehouse, etc.)
        token: Access token
        cache: Optional cache instance

    Returns:
        Item dict with 'id', 'displayName', etc.
    """
    # GUID passthrough
    if is_guid(name_or_id):
        return {'id': name_or_id, 'displayName': None, '_resolved_by': 'guid'}

    if token is None:
        token = load_token()

    if cache is None:
        cache = FabricCache()

    items = list_items(workspace_id, item_type, token, cache)
    matches = fuzzy_match(name_or_id, items)

    if not matches:
        raise NotFoundError(f"No {item_type} found matching '{name_or_id}' in workspace")

    top_match, match_type, score = matches[0]
    if match_type == 'exact' or score > 0.9:
        top_match['_resolved_by'] = match_type
        top_match['_match_score'] = score
        return top_match

    close_matches = [(m, t, s) for m, t, s in matches if s > 0.5]
    if len(close_matches) > 1:
        raise AmbiguousMatchError(
            f"Multiple {item_type}s match '{name_or_id}'",
            [{'name': m['displayName'], 'id': m['id'], 'score': s}
             for m, t, s in close_matches[:5]]
        )

    top_match['_resolved_by'] = match_type
    top_match['_match_score'] = score
    return top_match


def resolve_table(name_or_id: str, workspace_id: str, lakehouse_id: str,
                  token: Optional[str] = None,
                  cache: Optional[FabricCache] = None) -> Dict:
    """
    Resolve table name to full table object.

    Args:
        name_or_id: Table name or identifier
        workspace_id: Workspace GUID
        lakehouse_id: Lakehouse GUID
        token: Access token
        cache: Optional cache instance

    Returns:
        Table dict with 'name', etc.
    """
    if token is None:
        token = load_token()

    if cache is None:
        cache = FabricCache()

    tables = list_tables(workspace_id, lakehouse_id, token, cache)

    # Tables use 'name' instead of 'displayName'
    matches = fuzzy_match(name_or_id, tables, key='name')

    if not matches:
        raise NotFoundError(f"No table found matching '{name_or_id}' in lakehouse")

    top_match, match_type, score = matches[0]
    if match_type == 'exact' or score > 0.9:
        top_match['_resolved_by'] = match_type
        top_match['_match_score'] = score
        return top_match

    close_matches = [(m, t, s) for m, t, s in matches if s > 0.5]
    if len(close_matches) > 1:
        raise AmbiguousMatchError(
            f"Multiple tables match '{name_or_id}'",
            [{'name': m['name'], 'score': s} for m, t, s in close_matches[:5]]
        )

    top_match['_resolved_by'] = match_type
    top_match['_match_score'] = score
    return top_match


def resolve_full_path(workspace: str, item_type: str, item_name: str,
                      sub_type: Optional[str] = None, sub_name: Optional[str] = None,
                      token: Optional[str] = None) -> Dict:
    """
    Resolve a full resource path with all parent contexts.

    Example:
        resolve_full_path("My Workspace", "lakehouse", "Bronze", "table", "customers")

    Returns:
        Dict with all resolved IDs
    """
    if token is None:
        token = load_token()

    cache = FabricCache()
    result = {}

    # Resolve workspace
    ws = resolve_workspace(workspace, token, cache)
    result['workspace_id'] = ws['id']
    result['workspace_name'] = ws.get('displayName')

    # Resolve item
    item = resolve_item(item_name, ws['id'], item_type, token, cache)
    result[f'{item_type}_id'] = item['id']
    result[f'{item_type}_name'] = item.get('displayName')

    # Resolve sub-item if specified
    if sub_type and sub_name:
        if sub_type == 'table' and item_type == 'lakehouse':
            sub = resolve_table(sub_name, ws['id'], item['id'], token, cache)
            result['table_name'] = sub.get('name')
        else:
            raise ResolverError(f"Unsupported sub-type: {sub_type} under {item_type}")

    return result


# Convenience function for command-line usage
def resolve(resource_type: str, name: str, **context) -> str:
    """
    Simple resolver that returns just the ID.

    Args:
        resource_type: 'workspace', 'notebook', 'pipeline', etc.
        name: Name or GUID to resolve
        **context: Additional context (workspace_id, lakehouse_id, etc.)

    Returns:
        Resolved GUID string
    """
    token = load_token()
    cache = FabricCache()

    if resource_type == 'workspace':
        result = resolve_workspace(name, token, cache)
    elif resource_type in ITEM_TYPE_ENDPOINTS:
        workspace_id = context.get('workspace_id') or context.get('workspace')
        if not workspace_id:
            raise ResolverError(f"workspace_id required to resolve {resource_type}")

        # Resolve workspace if it's a name
        if not is_guid(workspace_id):
            ws = resolve_workspace(workspace_id, token, cache)
            workspace_id = ws['id']

        result = resolve_item(name, workspace_id, resource_type, token, cache)
    elif resource_type == 'table':
        workspace_id = context.get('workspace_id') or context.get('workspace')
        lakehouse_id = context.get('lakehouse_id') or context.get('lakehouse')

        if not workspace_id or not lakehouse_id:
            raise ResolverError("workspace_id and lakehouse_id required to resolve table")

        # Resolve workspace if name
        if not is_guid(workspace_id):
            ws = resolve_workspace(workspace_id, token, cache)
            workspace_id = ws['id']

        # Resolve lakehouse if name
        if not is_guid(lakehouse_id):
            lh = resolve_item(lakehouse_id, workspace_id, 'lakehouse', token, cache)
            lakehouse_id = lh['id']

        result = resolve_table(name, workspace_id, lakehouse_id, token, cache)
        return result.get('name')  # Tables don't have GUIDs
    else:
        raise ResolverError(f"Unknown resource type: {resource_type}")

    return result['id']


if __name__ == "__main__":
    # Simple test/demo
    import sys

    if len(sys.argv) < 3:
        print("Usage: fabric_resolver.py <type> <name> [--workspace <ws>] [--lakehouse <lh>]")
        print("")
        print("Types: workspace, notebook, pipeline, lakehouse, table")
        print("")
        print("Examples:")
        print("  fabric_resolver.py workspace 'My Workspace'")
        print("  fabric_resolver.py notebook 'Sales' --workspace 'My Workspace'")
        sys.exit(1)

    resource_type = sys.argv[1]
    name = sys.argv[2]

    # Parse optional arguments
    context = {}
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--workspace' and i + 1 < len(sys.argv):
            context['workspace'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--lakehouse' and i + 1 < len(sys.argv):
            context['lakehouse'] = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    try:
        result_id = resolve(resource_type, name, **context)
        print(f"Resolved: {result_id}")
    except AmbiguousMatchError as e:
        print(f"[AMBIGUOUS] {e}")
        print("Matches:")
        for m in e.matches:
            print(f"  - {m['name']} (ID: {m['id']}, Score: {m['score']:.2f})")
        sys.exit(2)
    except NotFoundError as e:
        print(f"[NOT FOUND] {e}")
        sys.exit(1)
    except AuthenticationError as e:
        print(f"[AUTH ERROR] {e}")
        sys.exit(3)
    except ResolverError as e:
        print(f"[ERROR] {e}")
        sys.exit(4)
