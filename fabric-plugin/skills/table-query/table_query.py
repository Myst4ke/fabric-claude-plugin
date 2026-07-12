#!/usr/bin/env python3
"""
Skill: table-query
Description: Execute SQL query against lakehouse

Supports both GUIDs and names for workspace and lakehouse arguments.
Names are resolved via fuzzy matching.
"""

import sys
import json
import os
import urllib.request
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

# Configuration
FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
try:
    from token_manager import CACHE_DIR
except ImportError:
    CACHE_DIR = os.getenv("TEMP", "/tmp")
TOKEN_FILE = f"{CACHE_DIR}/fabric-plugin-token-delegated.json"


def load_token():
    """Load access token with automatic refresh via fabric_base."""
    try:
        from fabric_base import get_token
        return get_token()
    except ImportError:
        # Fallback: legacy direct file read
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
            return token_data['access_token']
        except FileNotFoundError:
            print("[ERROR] Not authenticated. Run /fabric-plugin:setup:login")
            sys.exit(3)
        except Exception as e:
            print(f"[ERROR] Failed to load token: {e}")
            sys.exit(1)


def resolve_args(workspace_arg, lakehouse_arg):
    """Resolve workspace and lakehouse arguments to GUIDs."""
    try:
        from smart_args import SmartResolver, handle_resolution_error
        from fabric_resolver import is_guid, AmbiguousMatchError, NotFoundError, AuthenticationError

        if is_guid(workspace_arg) and is_guid(lakehouse_arg):
            return workspace_arg, lakehouse_arg

        resolver = SmartResolver()

        if not is_guid(workspace_arg):
            print(f"[INFO] Resolving workspace '{workspace_arg}'...")
        workspace_id = resolver.workspace(workspace_arg)

        if not is_guid(lakehouse_arg):
            print(f"[INFO] Resolving lakehouse '{lakehouse_arg}'...")
        lakehouse_id = resolver.lakehouse(lakehouse_arg, workspace_id)

        return workspace_id, lakehouse_id

    except ImportError:
        return workspace_arg, lakehouse_arg
    except (AmbiguousMatchError, NotFoundError, AuthenticationError) as e:
        from smart_args import handle_resolution_error
        sys.exit(handle_resolution_error(e))
    except Exception as e:
        print(f"[ERROR] Resolution failed: {e}")
        return workspace_arg, lakehouse_arg


def execute_query(workspace_id, lakehouse_id, query):
    """Execute SQL query."""
    token = load_token()
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/query"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    body = {
        'query': query
    }

    print(f"Executing query...")
    print(f"  {query[:100]}{'...' if len(query) > 100 else ''}")
    print("")

    try:
        data = json.dumps(body).encode('utf-8')
        request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        response = urllib.request.urlopen(request)

        if response.status == 200:
            result = json.loads(response.read().decode('utf-8'))
            display_results(result)
            return 0
        else:
            print(f"[ERROR] Unexpected status: {response.status}")
            return 2

    except urllib.error.HTTPError as e:
        return handle_http_error(e)
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2


def handle_http_error(error):
    """Handle HTTP errors."""
    if error.code == 401:
        print("[ERROR] Unauthorized. Token expired. Run /fabric-plugin:setup:login")
        return 3
    elif error.code == 403:
        print("[ERROR] Forbidden. Check workspace permissions.")
        return 1
    elif error.code == 404:
        print("[ERROR] Lakehouse not found.")
        return 1
    elif error.code == 400:
        try:
            error_body = json.loads(error.read().decode('utf-8'))
            message = error_body.get('error', {}).get('message', 'Invalid query')
            print(f"[ERROR] Query error: {message}")
        except:
            print("[ERROR] Invalid query syntax")
        return 1
    elif error.code == 429:
        print("[ERROR] Rate limited. Please retry after a moment.")
        return 2
    else:
        try:
            error_body = json.loads(error.read().decode('utf-8'))
            message = error_body.get('error', {}).get('message', error.reason)
            print(f"[ERROR] HTTP {error.code}: {message}")
        except:
            print(f"[ERROR] HTTP {error.code}: {error.reason}")
        return 2


def display_results(result):
    """Display query results in tabular format."""
    columns = result.get('columns', [])
    rows = result.get('rows', [])

    row_count = len(rows)
    col_count = len(columns)

    print(f"Query Results ({row_count} rows, {col_count} columns):")
    print("")

    if row_count == 0:
        print("(No rows returned)")
        return

    # Calculate column widths
    col_names = [col.get('name', f'col{i}') for i, col in enumerate(columns)]
    col_widths = [len(name) for name in col_names]

    for row in rows:
        for i, val in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(val)[:50]))

    # Cap widths
    col_widths = [min(w, 50) for w in col_widths]

    # Print header
    header = ' | '.join(name[:w].ljust(w) for name, w in zip(col_names, col_widths))
    print(header)
    print('-+-'.join('-' * w for w in col_widths))

    # Print rows (limit to 100)
    display_rows = rows[:100]
    for row in display_rows:
        values = []
        for i, val in enumerate(row):
            if i < len(col_widths):
                val_str = str(val)[:col_widths[i]]
                values.append(val_str.ljust(col_widths[i]))
        print(' | '.join(values))

    if row_count > 100:
        print(f"\n... and {row_count - 100} more rows (showing first 100)")

    print(f"\nTotal: {row_count} row(s)")


def main():
    """Main execution."""
    if len(sys.argv) < 4:
        print("Usage: table_query.py <workspace> <lakehouse> \"<query>\"")
        print("")
        print("Arguments:")
        print("  workspace    Workspace name or GUID")
        print("  lakehouse    Lakehouse name or GUID")
        print("  query        SQL query to execute (in quotes)")
        print("")
        print("Examples:")
        print("  table_query.py 'My Workspace' 'Bronze' \"SELECT * FROM sales LIMIT 10\"")
        print("  table_query.py a1b2c3d4-... b2c3d4e5-... \"SELECT COUNT(*) FROM customers\"")
        sys.exit(1)

    workspace_arg = sys.argv[1]
    lakehouse_arg = sys.argv[2]
    query = sys.argv[3]

    # Resolve names to IDs
    workspace_id, lakehouse_id = resolve_args(workspace_arg, lakehouse_arg)

    sys.exit(execute_query(workspace_id, lakehouse_id, query))


if __name__ == "__main__":
    main()
