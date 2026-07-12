#!/usr/bin/env python3
"""
Skill: email-to-guid
Description: Convert user email address to Azure AD Object ID (GUID)
using Microsoft Graph API. GUIDs pass through unchanged.

Outputs the resolved GUID on stdout (single line) for programmatic use.
"""

import json
import sys
import os
import urllib.request
import urllib.parse
import urllib.error

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from cli_args import SkillCLI
from fabric_base import get_graph_token
from fabric_resolver import is_guid


def log_verbose(verbose, message):
    """Log verbose debug message to stderr."""
    if verbose:
        print(f"[DEBUG]: {message}", file=sys.stderr)


def lookup_user_by_email(email, verbose=False):
    """Lookup user in Microsoft Graph by email address. Returns Object ID."""
    log_verbose(verbose, f"Looking up user by email: {email}")

    graph_token = get_graph_token()  # exits 3 on auth failure

    url = f"https://graph.microsoft.com/v1.0/users/{urllib.parse.quote(email)}"
    log_verbose(verbose, f"Calling Graph API: {url}")

    request = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {graph_token}',
            'Content-Type': 'application/json'
        }
    )

    try:
        with urllib.request.urlopen(request) as response:
            user_data = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"[ERROR] User not found: {email}", file=sys.stderr)
            print("Possible reasons:", file=sys.stderr)
            print("  - Email address doesn't exist in your Azure AD", file=sys.stderr)
            print("  - User is from external organization (guest users may have different UPN)", file=sys.stderr)
            print("  - Typo in email address", file=sys.stderr)
            sys.exit(1)
        elif e.code == 429:
            retry_after = e.headers.get('Retry-After', '30')
            print(f"[ERROR] Rate limited. Retry after {retry_after} seconds.", file=sys.stderr)
            sys.exit(2)
        else:
            print(f"[ERROR] Graph API error (HTTP {e.code})", file=sys.stderr)
            try:
                error_data = json.loads(e.read().decode())
                msg = error_data.get('error', {}).get('message', 'Unknown')
                print(f"Details: {msg}", file=sys.stderr)
            except Exception:
                pass
            sys.exit(2)

    object_id = user_data.get('id')
    if not object_id:
        print("[ERROR] No Object ID found for user", file=sys.stderr)
        sys.exit(1)

    log_verbose(verbose, "[OK] Found user:")
    log_verbose(verbose, f"   - Display Name: {user_data.get('displayName')}")
    log_verbose(verbose, f"   - UPN: {user_data.get('userPrincipalName')}")
    log_verbose(verbose, f"   - Object ID: {object_id}")

    return object_id


def main():
    cli = SkillCLI('resolve_user.py',
                   'Convert email to Azure AD Object ID (GUID)')
    cli.positional('input', help='Email address or GUID')
    cli.flag('--verbose', help='Verbose debugging')
    args = cli.parse()

    # GUID passes through unchanged
    if is_guid(args.input):
        log_verbose(args.verbose, f"Input is already a GUID: {args.input}")
        print(args.input)
        sys.exit(0)

    object_id = lookup_user_by_email(args.input, verbose=args.verbose)
    print(object_id)
    sys.exit(0)


if __name__ == '__main__':
    main()
