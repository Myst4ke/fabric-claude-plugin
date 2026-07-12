#!/usr/bin/env python3
"""
cli_args - Standard CLI layer for all fabric-plugin skills.

Guarantees a uniform contract across every skill script:
- Positional arguments in a fixed order: workspace, then item(s), then extras
- Every workspace/item argument accepts BOTH a display name and a GUID
  (names are resolved via SmartResolver, GUIDs pass through at zero cost)
- Working `-h/--help` everywhere (argparse)
- Uniform exit codes: 1 = usage/permanent error, 2 = retryable,
  3 = authentication, plus resolver codes (1 not-found, 2 ambiguous, 3 auth)

Usage pattern (the ONLY pattern skills should use):

    from cli_args import SkillCLI

    cli = SkillCLI('notebook_run.py', 'Execute a notebook in Microsoft Fabric')
    cli.workspace()                # positional: name or GUID
    cli.item('notebook')           # positional: name or GUID, resolved in ws
    cli.opt('--limit', type=int, help='Maximum rows')
    cli.flag('--verbose', help='Enable debug output')
    args = cli.parse()

    # args.workspace_id and args.notebook_id are guaranteed GUIDs
    # original inputs remain in args.workspace / args.notebook
"""

import argparse
import os
import sys

_shared_dir = os.path.dirname(os.path.abspath(__file__))
if _shared_dir not in sys.path:
    sys.path.insert(0, _shared_dir)


class _Parser(argparse.ArgumentParser):
    """argparse with uniform error behavior: usage errors exit 1 (permanent),
    never 2 (which is reserved for retryable errors)."""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"[ERROR] {message}", file=sys.stderr)
        sys.exit(1)


class SkillCLI:
    """Declarative CLI builder with automatic name->GUID resolution."""

    def __init__(self, prog, description, epilog=None):
        self.parser = _Parser(
            prog=prog, description=description, epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self._workspace_dest = None
        self._items = []   # (dest, item_type)
        self._lakehouse_dest = None

    # ----- declaration -------------------------------------------------

    def workspace(self, help='Workspace name or GUID'):
        """Positional workspace argument (name or GUID)."""
        self.parser.add_argument('workspace', help=help)
        self._workspace_dest = 'workspace'
        return self

    def item(self, name, item_type=None, help=None):
        """Positional item argument (name or GUID), resolved within the
        workspace. item_type defaults to the argument name (e.g. 'notebook').
        Supported types: notebook, pipeline, lakehouse, warehouse,
        semanticmodel, environment, kqldatabase, eventhouse,
        sparkjobdefinition, mlmodel, mlexperiment."""
        itype = (item_type or name).lower()
        self.parser.add_argument(name, help=help or f'{name.capitalize()} name or GUID')
        self._items.append((name, itype))
        if itype == 'lakehouse':
            self._lakehouse_dest = name
        return self

    def positional(self, name, help=None, **kwargs):
        """Plain positional argument, no resolution (e.g. table name, query,
        file path, job/schedule ID)."""
        self.parser.add_argument(name, help=help, **kwargs)
        return self

    def opt(self, *flags, **kwargs):
        """Optional argument, e.g. cli.opt('--limit', type=int)."""
        self.parser.add_argument(*flags, **kwargs)
        return self

    def flag(self, *flags, help=None):
        """Boolean flag, e.g. cli.flag('--force')."""
        self.parser.add_argument(*flags, action='store_true', help=help)
        return self

    # ----- parsing + resolution ----------------------------------------

    def parse(self, argv=None):
        """Parse argv and resolve names to GUIDs. On resolver failure,
        prints a clear message and exits with the standard code."""
        args = self.parser.parse_args(argv)

        try:
            from fabric_resolver import is_guid
        except ImportError:
            print("[ERROR] Shared module fabric_resolver not found "
                  "(corrupted plugin install).")
            sys.exit(1)

        needs_resolution = False
        if self._workspace_dest:
            if not is_guid(getattr(args, self._workspace_dest)):
                needs_resolution = True
        for dest, _ in self._items:
            if not is_guid(getattr(args, dest)):
                needs_resolution = True

        resolver = None
        if needs_resolution:
            try:
                from smart_args import SmartResolver
                resolver = SmartResolver()
            except ImportError:
                print("[ERROR] Name resolution unavailable "
                      "(smart_args module missing). Pass GUIDs instead.")
                sys.exit(1)

        try:
            if self._workspace_dest:
                value = getattr(args, self._workspace_dest)
                if is_guid(value):
                    args.workspace_id = value
                else:
                    print(f"[INFO] Resolving workspace '{value}'...")
                    args.workspace_id = resolver.workspace(value)

            for dest, itype in self._items:
                value = getattr(args, dest)
                if is_guid(value):
                    setattr(args, f'{dest}_id', value)
                else:
                    if not self._workspace_dest:
                        print(f"[ERROR] Cannot resolve '{value}' without a "
                              f"workspace argument. Pass a GUID.")
                        sys.exit(1)
                    print(f"[INFO] Resolving {itype} '{value}'...")
                    setattr(args, f'{dest}_id',
                            resolver.item(value, args.workspace_id, itype))
        except SystemExit:
            raise
        except Exception as e:
            try:
                from smart_args import handle_resolution_error
                sys.exit(handle_resolution_error(e))
            except ImportError:
                print(f"[ERROR] Resolution failed: {e}")
                sys.exit(1)

        return args
