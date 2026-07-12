#!/usr/bin/env python3
"""
Skill: resolve-name
Description: Resolve resource names to GUIDs with fuzzy matching

Usage:
    python3 resolve_name.py <type> <name> [--workspace <ws>] [--lakehouse <lh>] [--json] [--quiet]

Types: workspace, notebook, pipeline, lakehouse, warehouse, table
"""

import sys
import os
import json
import argparse

# Add parent directory to path for shared module import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from fabric_resolver import (
    resolve_workspace,
    resolve_item,
    resolve_table,
    is_guid,
    load_token,
    FabricCache,
    AuthenticationError,
    NotFoundError,
    AmbiguousMatchError,
    ResolverError,
    ITEM_TYPE_ENDPOINTS
)


def main():
    parser = argparse.ArgumentParser(
        description='Resolve Fabric resource names to GUIDs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s workspace "My Workspace"
  %(prog)s notebook "Sales Analysis" --workspace "My Workspace"
  %(prog)s table "customers" --workspace "Prod" --lakehouse "Bronze"
  %(prog)s notebook "Sales" --workspace "Prod" --json
        """
    )

    parser.add_argument('type', choices=['workspace', 'notebook', 'pipeline',
                                         'lakehouse', 'warehouse', 'table',
                                         'semanticmodel', 'report', 'dashboard',
                                         'dataflow', 'dataset'],
                        help='Resource type to resolve')
    parser.add_argument('name', help='Resource name (or GUID) to resolve')
    parser.add_argument('--workspace', '-w', help='Workspace name or ID')
    parser.add_argument('--lakehouse', '-l', help='Lakehouse name or ID (for tables)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only output the ID')

    args = parser.parse_args()

    # Validate required context
    if args.type != 'workspace' and not args.workspace:
        print(f"[ERROR] --workspace is required for {args.type}")
        sys.exit(4)

    if args.type == 'table' and not args.lakehouse:
        print(f"[ERROR] --lakehouse is required for table")
        sys.exit(4)

    try:
        # If already a GUID, just return it
        if is_guid(args.name):
            result = {
                'status': 'passthrough',
                'type': args.type,
                'query': args.name,
                'id': args.name,
                'displayName': None,
                'matchType': 'guid',
                'score': 1.0
            }
            output_result(result, args.json, args.quiet)
            return 0

        token = load_token()
        cache = FabricCache()

        # Resolve based on type
        if args.type == 'workspace':
            resolved = resolve_workspace(args.name, token, cache)
            result = format_result(args.type, args.name, resolved)

        elif args.type == 'table':
            # Need to resolve workspace and lakehouse first
            workspace_id = resolve_context(args.workspace, 'workspace', token, cache)
            lakehouse_id = resolve_context(args.lakehouse, 'lakehouse', token, cache,
                                           workspace_id=workspace_id)

            resolved = resolve_table(args.name, workspace_id, lakehouse_id, token, cache)
            result = format_table_result(args.name, resolved, workspace_id, lakehouse_id)

        else:
            # Resolve workspace first
            workspace_id = resolve_context(args.workspace, 'workspace', token, cache)

            resolved = resolve_item(args.name, workspace_id, args.type, token, cache)
            result = format_result(args.type, args.name, resolved, workspace_id)

        output_result(result, args.json, args.quiet)
        return 0

    except AuthenticationError as e:
        if args.json:
            print(json.dumps({'status': 'error', 'error': 'auth', 'message': str(e)}))
        else:
            print(f"[AUTH ERROR] {e}")
        return 3

    except NotFoundError as e:
        if args.json:
            print(json.dumps({'status': 'not_found', 'query': args.name, 'message': str(e)}))
        else:
            print(f"[NOT FOUND] {e}")
        return 1

    except AmbiguousMatchError as e:
        if args.json:
            print(json.dumps({
                'status': 'ambiguous',
                'query': args.name,
                'matches': e.matches,
                'message': str(e)
            }))
        else:
            print(f"[AMBIGUOUS] {e}")
            print("\nMatches:")
            for i, m in enumerate(e.matches, 1):
                name = m.get('name') or m.get('displayName', 'Unknown')
                print(f"  {i}. {name} (score: {m['score']:.2f})")
                if 'id' in m:
                    print(f"     ID: {m['id']}")
            print("\nUse a more specific name or the full ID.")
        return 2

    except ResolverError as e:
        if args.json:
            print(json.dumps({'status': 'error', 'message': str(e)}))
        else:
            print(f"[ERROR] {e}")
        return 4


def resolve_context(name_or_id: str, resource_type: str, token: str, cache: FabricCache,
                    workspace_id: str = None) -> str:
    """Resolve a context parameter (workspace or lakehouse) to ID."""
    if is_guid(name_or_id):
        return name_or_id

    if resource_type == 'workspace':
        resolved = resolve_workspace(name_or_id, token, cache)
    elif resource_type == 'lakehouse':
        if not workspace_id:
            raise ResolverError("workspace_id required to resolve lakehouse")
        resolved = resolve_item(name_or_id, workspace_id, 'lakehouse', token, cache)
    else:
        raise ResolverError(f"Cannot resolve context type: {resource_type}")

    return resolved['id']


def format_result(resource_type: str, query: str, resolved: dict,
                  workspace_id: str = None) -> dict:
    """Format resolution result."""
    return {
        'status': 'resolved',
        'type': resource_type,
        'query': query,
        'id': resolved['id'],
        'displayName': resolved.get('displayName'),
        'matchType': resolved.get('_resolved_by', 'unknown'),
        'score': resolved.get('_match_score', 1.0),
        'workspaceId': workspace_id
    }


def format_table_result(query: str, resolved: dict, workspace_id: str,
                        lakehouse_id: str) -> dict:
    """Format table resolution result."""
    return {
        'status': 'resolved',
        'type': 'table',
        'query': query,
        'name': resolved.get('name'),
        'matchType': resolved.get('_resolved_by', 'unknown'),
        'score': resolved.get('_match_score', 1.0),
        'workspaceId': workspace_id,
        'lakehouseId': lakehouse_id
    }


def output_result(result: dict, as_json: bool, quiet: bool):
    """Output the resolution result."""
    if as_json:
        print(json.dumps(result, indent=2))
    elif quiet:
        # Just output the ID (or name for tables)
        print(result.get('id') or result.get('name'))
    else:
        # Human-readable output
        resource_id = result.get('id') or result.get('name')
        print(f"\nResolved '{result['query']}' -> {resource_id}")
        print(f"  Match type: {result['matchType']}")
        if result.get('displayName'):
            print(f"  Display name: {result['displayName']}")
        if result.get('name') and result['type'] == 'table':
            print(f"  Table name: {result['name']}")
        if result.get('score') and result['score'] < 1.0:
            print(f"  Confidence: {result['score']:.0%}")
        print()


if __name__ == "__main__":
    sys.exit(main())
