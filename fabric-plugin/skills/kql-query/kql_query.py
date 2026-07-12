#!/usr/bin/env python3
"""
Skill: kql-query
Description: Execute a KQL query against a KQL database

Uses the Fabric API (Fabric token) to discover the Kusto query service URI,
then the Kusto query REST API (Kusto-audience token) to run the query.
"""

import sys
import json
import os
import urllib.request
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import (FABRIC_API_BASE, fabric_request_json,
                         get_kusto_token, check_security, handle_http_error)


def get_query_uri(workspace_id, db_id):
    """Get the KQL query service URI from database properties (Fabric API)."""
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/kqlDatabases/{db_id}"
    data = fabric_request_json(url)
    props = data.get('properties', {})
    return props.get('queryServiceUri', ''), data.get('displayName', db_id)


def display_results(data):
    """Display Kusto v1 query results."""
    tables = data.get('Tables', data.get('tables', []))
    if not tables:
        print("Query returned no results.")
        return

    primary = tables[0]
    columns = [c.get('ColumnName', f'col_{i}') for i, c in enumerate(primary.get('Columns', []))]
    rows = primary.get('Rows', [])

    print(f"\nKQL Query Results ({len(rows)} row(s)):\n")

    if not rows:
        print("(empty result set)")
        return

    # Calculate column widths
    widths = [len(c) for c in columns]
    for row in rows[:100]:
        for i, val in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], min(len(str(val)), 40))

    # Header
    header = "  ".join(f"{columns[i]:<{widths[i]}}" for i in range(len(columns)))
    print(header)
    print("  ".join("-" * w for w in widths))

    # Rows (limit display to 100)
    for row in rows[:100]:
        line = "  ".join(f"{str(row[i] if i < len(row) else '')[:40]:<{widths[i]}}" for i in range(len(columns)))
        print(line)

    if len(rows) > 100:
        print(f"\n... showing 100 of {len(rows)} rows")


def execute_kql(workspace_id, db_id, query):
    """Execute a KQL query via the Kusto query service."""
    check_security(workspace_id, "kql:query")

    # Get query URI (Fabric API, Fabric token)
    try:
        query_uri, db_name = get_query_uri(workspace_id, db_id)
    except urllib.error.HTTPError as e:
        return handle_http_error(e, "KQL database")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    if not query_uri:
        print("[ERROR] No query service URI found for this database.")
        print("        The database may not be fully provisioned yet.")
        return 1

    # Execute KQL query via Kusto REST API (requires a Kusto-audience token;
    # the Fabric API token is rejected by the queryservice endpoint)
    kusto_token = get_kusto_token()
    kusto_url = f"{query_uri}/v1/rest/query"
    headers = {
        'Authorization': f'Bearer {kusto_token}',
        'Content-Type': 'application/json'
    }

    body = json.dumps({'db': db_name, 'csl': query}).encode('utf-8')

    try:
        req = urllib.request.Request(kusto_url, data=body, headers=headers, method='POST')
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("[ERROR] Unauthorized on Kusto endpoint. Run /fabric-plugin:setup:login")
            return 3
        elif e.code == 400:
            try:
                err = json.loads(e.read().decode('utf-8'))
                msg = err.get('error', {}).get('message', str(err))
                print(f"[ERROR] KQL syntax error: {msg[:500]}")
            except Exception:
                print("[ERROR] Bad KQL query.")
            return 1
        elif e.code == 429:
            retry_after = e.headers.get('Retry-After', '30')
            print(f"[ERROR] Rate limited. Retry after {retry_after} seconds.")
            return 2
        else:
            print(f"[ERROR] HTTP {e.code}: {e.reason}")
            return 2
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return 2

    display_results(data)
    return 0


def main():
    cli = SkillCLI('kql_query.py',
                   'Execute a KQL query against a KQL database')
    cli.workspace()
    cli.item('database', 'kqldatabase', help='KQL database name or GUID')
    cli.positional('query', help='KQL query string')
    args = cli.parse()

    sys.exit(execute_kql(args.workspace_id, args.database_id, args.query))


if __name__ == "__main__":
    main()
